#!/usr/bin/env python3
"""
Compare Poetry-BERT vs EEBO-BERT on Shakespeare Sonnets

Rerun trajectory tortuosity analysis using poetry-trained BERT
to see if poetry specialization changes semantic representations.

Baseline (EEBO-BERT):
- Mean tortuosity: 59.52
- SD: 11.45
- Word coverage: 95.9%
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from transformers import BertModel, BertTokenizer
import torch
from tqdm import tqdm

# Paths
POETRY_BERT = "/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive/poetry_bert_trained"
EEBO_BERT = "/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive/AI and Poetry/Databases/Historical Embeddings/EEBO_1595-1700/eebo_bert_finetuned"
SONNETS_PATH = "Data/poetry_corpus/shakespeare_complete_works.jsonl"
OUTPUT_DIR = "results"

def load_model(model_path, model_name):
    """Load BERT model and tokenizer."""
    print(f"\nLoading {model_name}...")
    print(f"Path: {model_path}")

    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertModel.from_pretrained(model_path)
    model.eval()

    # Use MPS if available
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)

    print(f"✓ Loaded on {device}")
    return model, tokenizer, device


def get_embeddings(text, model, tokenizer, device):
    """Get contextualized embeddings for text."""
    tokens = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    tokens = {k: v.to(device) for k, v in tokens.items()}

    with torch.no_grad():
        outputs = model(**tokens)

    # Return mean of last hidden layer (excluding [CLS] and [SEP])
    embeddings = outputs.last_hidden_state[0, 1:-1, :].mean(dim=0)
    return embeddings.cpu().numpy()


def calculate_tortuosity(embeddings):
    """Calculate trajectory tortuosity from sequence of embeddings."""
    if len(embeddings) < 2:
        return 0.0

    # Calculate cumulative angular deviation
    total_angle = 0.0
    for i in range(len(embeddings) - 2):
        v1 = embeddings[i+1] - embeddings[i]
        v2 = embeddings[i+2] - embeddings[i+1]

        # Normalize
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-8)
        v2_norm = v2 / (np.linalg.norm(v2) + 1e-8)

        # Calculate angle
        cos_angle = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
        angle = np.arccos(cos_angle)
        total_angle += angle

    # Euclidean distance
    euclidean = np.linalg.norm(embeddings[-1] - embeddings[0])

    # Tortuosity = angular deviation / straight-line distance
    if euclidean < 1e-8:
        return 0.0

    return total_angle / euclidean


def analyze_sonnet(sonnet_text, model, tokenizer, device):
    """Analyze a single sonnet."""
    lines = [line.strip() for line in sonnet_text.split('\n') if line.strip()]

    # Get embeddings for each line
    embeddings = []
    words_found = 0
    words_missing = 0

    for line in lines:
        try:
            emb = get_embeddings(line, model, tokenizer, device)
            embeddings.append(emb)
            # Count tokens (rough approximation)
            tokens = tokenizer.tokenize(line)
            words_found += len([t for t in tokens if not t.startswith('##')])
        except Exception as e:
            print(f"Error processing line: {line[:50]}... - {e}")
            words_missing += len(line.split())

    if len(embeddings) < 2:
        return None

    # Calculate overall tortuosity
    overall_tort = calculate_tortuosity(embeddings)

    # Calculate per-line tortuosity
    line_torts = []
    for i in range(len(embeddings) - 1):
        line_tort = np.linalg.norm(embeddings[i+1] - embeddings[i])
        line_torts.append(line_tort)

    mean_line_tort = np.mean(line_torts) if line_torts else 0.0
    max_line_tort = np.max(line_torts) if line_torts else 0.0

    # Couplet tortuosity (last 2 lines)
    couplet_tort = 0.0
    if len(embeddings) >= 2:
        couplet_tort = np.linalg.norm(embeddings[-1] - embeddings[-2])

    return {
        'overall_tortuosity': overall_tort,
        'mean_line_tortuosity': mean_line_tort,
        'max_line_tortuosity': max_line_tort,
        'couplet_tortuosity': couplet_tort,
        'words_found': words_found,
        'words_missing': words_missing
    }


def load_sonnets():
    """Load Shakespeare sonnets."""
    print("\nLoading Shakespeare sonnets...")
    sonnets = []

    with open(SONNETS_PATH, 'r') as f:
        for line in f:
            work = json.loads(line)
            if 'sonnet' in work.get('title', '').lower():
                sonnets.append({
                    'title': work['title'],
                    'text': work.get('text', ''),
                    'lines': work.get('lines', [])
                })

    # Sort by sonnet number
    sonnets.sort(key=lambda x: int(x['title'].split()[-1]) if x['title'].split()[-1].isdigit() else 999)

    print(f"✓ Loaded {len(sonnets)} sonnets")
    return sonnets


def analyze_all_sonnets(model, tokenizer, device, model_name):
    """Analyze all Shakespeare sonnets with given model."""
    sonnets = load_sonnets()

    results = []
    print(f"\nAnalyzing with {model_name}...")

    for i, sonnet in enumerate(tqdm(sonnets, desc=f"{model_name}")):
        sonnet_num = i + 1

        # Get full text
        if sonnet['text']:
            text = sonnet['text']
        else:
            text = '\n'.join(sonnet['lines'])

        # Analyze
        result = analyze_sonnet(text, model, tokenizer, device)

        if result:
            result['sonnet'] = sonnet_num
            results.append(result)

    return pd.DataFrame(results)


def print_comparison(df_eebo, df_poetry):
    """Print comparison statistics."""
    print("\n" + "="*60)
    print("COMPARISON: EEBO-BERT vs POETRY-BERT")
    print("="*60)

    print("\nOVERALL TORTUOSITY:")
    print(f"  EEBO-BERT:   Mean={df_eebo['overall_tortuosity'].mean():.2f}, SD={df_eebo['overall_tortuosity'].std():.2f}")
    print(f"  Poetry-BERT: Mean={df_poetry['overall_tortuosity'].mean():.2f}, SD={df_poetry['overall_tortuosity'].std():.2f}")

    diff_mean = df_poetry['overall_tortuosity'].mean() - df_eebo['overall_tortuosity'].mean()
    diff_sd = df_poetry['overall_tortuosity'].std() - df_eebo['overall_tortuosity'].std()
    print(f"\n  Difference:  Mean={diff_mean:+.2f}, SD={diff_sd:+.2f}")

    print("\nWORD COVERAGE:")
    eebo_coverage = df_eebo['words_found'].sum() / (df_eebo['words_found'].sum() + df_eebo['words_missing'].sum()) * 100
    poetry_coverage = df_poetry['words_found'].sum() / (df_poetry['words_found'].sum() + df_poetry['words_missing'].sum()) * 100
    print(f"  EEBO-BERT:   {eebo_coverage:.1f}%")
    print(f"  Poetry-BERT: {poetry_coverage:.1f}%")

    print("\nCOUPLET COMPLEXITY:")
    print(f"  EEBO-BERT:   Mean={df_eebo['couplet_tortuosity'].mean():.2f}")
    print(f"  Poetry-BERT: Mean={df_poetry['couplet_tortuosity'].mean():.2f}")

    # Top 5 most different sonnets
    merged = df_eebo.merge(df_poetry, on='sonnet', suffixes=('_eebo', '_poetry'))
    merged['diff'] = abs(merged['overall_tortuosity_poetry'] - merged['overall_tortuosity_eebo'])
    top_diff = merged.nlargest(5, 'diff')[['sonnet', 'overall_tortuosity_eebo', 'overall_tortuosity_poetry', 'diff']]

    print("\nTOP 5 SONNETS WITH BIGGEST DIFFERENCE:")
    print(top_diff.to_string(index=False))

    print("\n" + "="*60)


def main():
    print("="*60)
    print("SHAKESPEARE SONNETS: POETRY-BERT COMPARISON")
    print("="*60)

    # Check if EEBO-BERT results already exist
    eebo_results_path = Path(OUTPUT_DIR) / "shakespeare_sonnets_tortuosity.csv"

    if eebo_results_path.exists():
        print("\n✓ Loading existing EEBO-BERT results...")
        df_eebo = pd.read_csv(eebo_results_path)
    else:
        print("\n✗ EEBO-BERT results not found, running analysis...")
        model_eebo, tokenizer_eebo, device = load_model(EEBO_BERT, "EEBO-BERT")
        df_eebo = analyze_all_sonnets(model_eebo, tokenizer_eebo, device, "EEBO-BERT")
        df_eebo.to_csv(eebo_results_path, index=False)
        print(f"✓ Saved to {eebo_results_path}")

    # Run Poetry-BERT analysis
    model_poetry, tokenizer_poetry, device = load_model(POETRY_BERT, "Poetry-BERT")
    df_poetry = analyze_all_sonnets(model_poetry, tokenizer_poetry, device, "Poetry-BERT")

    # Save results
    output_path = Path(OUTPUT_DIR) / "shakespeare_sonnets_poetry_bert.csv"
    df_poetry.to_csv(output_path, index=False)
    print(f"\n✓ Saved Poetry-BERT results to {output_path}")

    # Print comparison
    print_comparison(df_eebo, df_poetry)

    # Save comparison
    comparison_path = Path(OUTPUT_DIR) / "bert_model_comparison.csv"
    merged = df_eebo.merge(df_poetry, on='sonnet', suffixes=('_eebo', '_poetry'))
    merged.to_csv(comparison_path, index=False)
    print(f"\n✓ Saved comparison to {comparison_path}")


if __name__ == "__main__":
    main()
