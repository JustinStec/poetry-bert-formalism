#!/usr/bin/env python3
"""
Train Word2Vec embeddings on EEBO-TCP corpus (1595-1700)
for historically-accurate semantic analysis of early modern poetry.
"""

import os
import re
from pathlib import Path
from typing import List, Iterator
import zipfile
import logging

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import multiprocessing

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)

# Configuration
EEBO_ZIP = "EEBO_TCP_SimpleText.zip"
EEBO_EXTRACT_DIR = "EEBO_TCP_Texts"
CLEANED_CORPUS_FILE = "eebo_cleaned_corpus.txt"
MODEL_OUTPUT = "Historical_Embeddings/EEBO_1595-1700/eebo_word2vec.model"

# Word2Vec parameters (matching Google News architecture)
VECTOR_SIZE = 300
WINDOW = 5
MIN_COUNT = 5
SG = 1  # Skip-gram (1) vs CBOW (0)
NEGATIVE = 5
HS = 0
WORKERS = multiprocessing.cpu_count()
EPOCHS = 5


def extract_eebo_corpus(zip_path: str, extract_dir: str) -> Path:
    """Extract EEBO-TCP ZIP file."""
    extract_path = Path(extract_dir)

    if extract_path.exists():
        logging.info(f"EEBO corpus already extracted to {extract_path}")
        return extract_path

    logging.info(f"Extracting {zip_path} to {extract_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    logging.info(f"Extraction complete: {len(list(extract_path.rglob('*.txt')))} text files")
    return extract_path


def clean_text(text: str) -> str:
    """Clean early modern text for Word2Vec training."""
    # Convert to lowercase
    text = text.lower()

    # Remove XML/HTML tags that might remain
    text = re.sub(r'<[^>]+>', ' ', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters but keep apostrophes (for contractions)
    text = re.sub(r"[^a-z'\s]", ' ', text)

    # Remove standalone apostrophes
    text = re.sub(r"\s'\s|^'|'$", ' ', text)

    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def process_eebo_texts(extract_dir: Path, output_file: str) -> None:
    """
    Process all EEBO texts into a single cleaned corpus file.
    Each line = one sentence (approximate, for Word2Vec training).
    """
    logging.info(f"Processing EEBO texts from {extract_dir}...")

    txt_files = list(extract_dir.rglob('*.txt'))
    logging.info(f"Found {len(txt_files)} text files")

    processed_count = 0
    total_words = 0

    with open(output_file, 'w', encoding='utf-8') as out:
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()

                # Clean text
                cleaned = clean_text(text)

                # Split into approximate sentences (period, question, exclamation)
                sentences = re.split(r'[.?!]+', cleaned)

                for sent in sentences:
                    sent = sent.strip()
                    if len(sent) > 10:  # Skip very short fragments
                        out.write(sent + '\n')
                        total_words += len(sent.split())

                processed_count += 1
                if processed_count % 1000 == 0:
                    logging.info(f"Processed {processed_count}/{len(txt_files)} files...")

            except Exception as e:
                logging.warning(f"Error processing {txt_file}: {e}")
                continue

    logging.info(f"Corpus creation complete:")
    logging.info(f"  Files processed: {processed_count}")
    logging.info(f"  Total words: {total_words:,}")
    logging.info(f"  Output: {output_file}")


def train_word2vec(corpus_file: str, output_model: str) -> Word2Vec:
    """Train Word2Vec model on cleaned EEBO corpus."""
    logging.info(f"Training Word2Vec model on {corpus_file}...")
    logging.info(f"Parameters: size={VECTOR_SIZE}, window={WINDOW}, min_count={MIN_COUNT}, sg={SG}")

    # Create output directory
    Path(output_model).parent.mkdir(parents=True, exist_ok=True)

    # Load corpus as sentences
    sentences = LineSentence(corpus_file)

    # Train model
    model = Word2Vec(
        sentences=sentences,
        vector_size=VECTOR_SIZE,
        window=WINDOW,
        min_count=MIN_COUNT,
        workers=WORKERS,
        sg=SG,
        negative=NEGATIVE,
        hs=HS,
        epochs=EPOCHS,
        compute_loss=True
    )

    # Save model
    model.save(output_model)
    logging.info(f"Model saved to {output_model}")

    # Log model statistics
    logging.info(f"Vocabulary size: {len(model.wv):,}")
    logging.info(f"Total training examples: {model.corpus_total_words:,}")

    return model


def test_model(model: Word2Vec) -> None:
    """Test the trained model with early modern vocabulary."""
    logging.info("\n" + "="*60)
    logging.info("TESTING MODEL WITH EARLY MODERN VOCABULARY")
    logging.info("="*60)

    test_words = ['thou', 'thee', 'thy', 'lord', 'love', 'death', 'heaven',
                  'king', 'nature', 'beauty', 'time', 'virtue']

    for word in test_words:
        if word in model.wv:
            similar = model.wv.most_similar(word, topn=5)
            logging.info(f"\n'{word}' similar words:")
            for sim_word, score in similar:
                logging.info(f"  {sim_word}: {score:.3f}")
        else:
            logging.info(f"\n'{word}': NOT IN VOCABULARY")


def main():
    """Main training pipeline."""
    logging.info("="*60)
    logging.info("EEBO-TCP WORD2VEC TRAINING")
    logging.info("Period: 1595-1700 (Early Modern English)")
    logging.info("="*60)

    # Step 1: Extract corpus
    extract_dir = extract_eebo_corpus(EEBO_ZIP, EEBO_EXTRACT_DIR)

    # Step 2: Clean and process texts
    if not Path(CLEANED_CORPUS_FILE).exists():
        process_eebo_texts(extract_dir, CLEANED_CORPUS_FILE)
    else:
        logging.info(f"Using existing cleaned corpus: {CLEANED_CORPUS_FILE}")

    # Step 3: Train Word2Vec
    model = train_word2vec(CLEANED_CORPUS_FILE, MODEL_OUTPUT)

    # Step 4: Test model
    test_model(model)

    logging.info("\n" + "="*60)
    logging.info("TRAINING COMPLETE!")
    logging.info(f"Model saved to: {MODEL_OUTPUT}")
    logging.info("="*60)


if __name__ == "__main__":
    main()
