#!/usr/bin/env python3
"""
Detect verse drama (plays in verse) for removal.
Focus on: ACT/SCENE markers, character names + dialogue, stage directions.
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/verse_drama_report.md")

def get_file_path(row):
    """Get full file path from metadata row."""
    filename = row['filename']

    if 'gutenberg' in filename.lower():
        for author_dir in GUTENBERG_DIR.iterdir():
            if author_dir.is_dir():
                test_path = author_dir / filename
                if test_path.exists():
                    return test_path
    else:
        author = row['author']
        filepath = POETRY_PLATFORM_DIR / author / filename
        if filepath.exists():
            return filepath

    return None

def detect_verse_drama(filepath):
    """Detect if file is verse drama."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = [line.strip() for line in content.split('\n') if line.strip()]
    except:
        return None

    if len(lines) < 5:
        return None

    # Evidence counters
    evidence = {
        'act_scene': 0,
        'character_dialogue': 0,
        'stage_directions': 0,
        'dramatis_personae': 0,
        'exit_enter': 0,
    }

    # 1. ACT/SCENE markers
    act_scene_pattern = r'^(ACT|SCENE)\s+[IVX0-9]+\.?'
    for line in lines:
        if re.match(act_scene_pattern, line, re.IGNORECASE):
            evidence['act_scene'] += 1

    # 2. Character names followed by dialogue
    # Pattern: ALL CAPS NAME at start of line, possibly followed by punctuation or text
    character_pattern = r'^[A-Z][A-Z\s]{2,}[A-Z]\s*[\.:]'  # e.g., "HAMLET.", "LADY MACBETH:"
    consecutive_characters = 0
    max_consecutive = 0

    for line in lines:
        if re.match(character_pattern, line):
            evidence['character_dialogue'] += 1
            consecutive_characters += 1
            max_consecutive = max(max_consecutive, consecutive_characters)
        else:
            consecutive_characters = 0

    # 3. Stage directions [in brackets] or (in parentheses)
    stage_pattern = r'^\s*[\[\(](?:Enter|Exit|Exeunt|Aside|To|Scene|Stage|Curtain|Act)'
    for line in lines:
        if re.search(stage_pattern, line, re.IGNORECASE):
            evidence['stage_directions'] += 1

    # 4. DRAMATIS PERSONAE
    if re.search(r'DRAMATIS\s+PERSONAE', content, re.IGNORECASE):
        evidence['dramatis_personae'] = 1

    # 5. Exit/Enter commands
    exit_enter_pattern = r'\b(Enter|Exit|Exeunt)\b\s+[A-Z]'
    for line in lines:
        if re.search(exit_enter_pattern, line):
            evidence['exit_enter'] += 1

    # Scoring: is this verse drama?
    # Strong indicators:
    # - Any ACT/SCENE markers (very strong)
    # - 3+ character dialogue markers + stage directions
    # - DRAMATIS PERSONAE
    # - Multiple exit/enter commands

    is_drama = False
    confidence = "low"
    reasons = []

    if evidence['act_scene'] > 0:
        is_drama = True
        confidence = "very_high"
        reasons.append(f"ACT/SCENE markers ({evidence['act_scene']})")

    if evidence['dramatis_personae'] > 0:
        is_drama = True
        if confidence == "low":
            confidence = "very_high"
        reasons.append("DRAMATIS PERSONAE")

    if evidence['character_dialogue'] >= 5 and evidence['stage_directions'] >= 2:
        is_drama = True
        if confidence == "low":
            confidence = "high"
        reasons.append(f"Character dialogue ({evidence['character_dialogue']}) + stage directions ({evidence['stage_directions']})")

    if evidence['exit_enter'] >= 3:
        is_drama = True
        if confidence == "low":
            confidence = "high"
        reasons.append(f"Exit/Enter commands ({evidence['exit_enter']})")

    # Also check for many consecutive character names (dialogue exchange)
    if max_consecutive >= 4:
        is_drama = True
        if confidence == "low":
            confidence = "medium"
        reasons.append(f"Dialogue exchange ({max_consecutive} consecutive character names)")

    if not is_drama:
        return None

    return {
        'evidence': evidence,
        'confidence': confidence,
        'reasons': reasons,
        'total_lines': len(lines)
    }

def scan_corpus():
    """Scan entire corpus for verse drama."""
    print("=" * 80)
    print("VERSE DRAMA DETECTION")
    print("=" * 80)
    print("Detecting: ACT/SCENE, character dialogue, stage directions")
    print("=" * 80)

    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows):,} entries")

    print("\nScanning for verse drama...")
    flagged = []
    confidence_counts = Counter()

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Scanned {i:,}/{len(rows):,}...")

        filepath = get_file_path(row)
        if not filepath:
            continue

        result = detect_verse_drama(filepath)
        if result:
            flagged.append({
                'filename': row['filename'],
                'title': row['title'],
                'author': row['author'],
                'filepath': filepath,
                **result
            })
            confidence_counts[result['confidence']] += 1

    print(f"\n✓ Found {len(flagged):,} verse drama files")

    # Statistics
    print(f"\nConfidence levels:")
    for conf in ['very_high', 'high', 'medium', 'low']:
        if conf in confidence_counts:
            print(f"  {conf}: {confidence_counts[conf]:,} files")

    return flagged, confidence_counts

def generate_report(flagged, confidence_counts):
    """Generate markdown report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    # Sort by confidence
    conf_order = {'very_high': 0, 'high': 1, 'medium': 2, 'low': 3}
    flagged_sorted = sorted(flagged, key=lambda x: (conf_order[x['confidence']], -x['evidence']['act_scene']))

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Verse Drama Detection Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Total verse drama detected:** {len(flagged):,}\n")
        f.write(f"- **Total corpus:** 167,442 files\n")
        f.write(f"- **Poetry files:** {167442 - len(flagged):,}\n\n")

        f.write("## Confidence Levels\n\n")
        for conf in ['very_high', 'high', 'medium', 'low']:
            if conf in confidence_counts:
                f.write(f"- **{conf.replace('_', ' ').title()}:** {confidence_counts[conf]:,} files\n")
        f.write("\n")

        # Examples by confidence level
        for conf_level in ['very_high', 'high', 'medium', 'low']:
            conf_files = [item for item in flagged_sorted if item['confidence'] == conf_level]
            if not conf_files:
                continue

            f.write(f"## {conf_level.replace('_', ' ').title()} Confidence ({len(conf_files):,} files)\n\n")

            for i, item in enumerate(conf_files[:50], 1):  # First 50
                f.write(f"### {i}. `{item['filename']}`\n\n")
                f.write(f"- **Title:** {item['title']}\n")
                f.write(f"- **Author:** {item['author']}\n")
                f.write(f"- **Total lines:** {item['total_lines']}\n\n")

                f.write("**Evidence:**\n")
                for key, value in item['evidence'].items():
                    if value > 0:
                        f.write(f"- {key.replace('_', ' ').title()}: {value}\n")
                f.write("\n")

                f.write("**Reasons:**\n")
                for reason in item['reasons']:
                    f.write(f"- {reason}\n")
                f.write("\n")

            if len(conf_files) > 50:
                f.write(f"\n... and {len(conf_files) - 50} more files\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/verse_drama_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Verse Drama Files ({len(flagged):,} files)\n")
        f.write("=" * 100 + "\n\n")

        for i, item in enumerate(flagged_sorted, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Confidence: {item['confidence']}\n")
            f.write(f"   Reasons: {'; '.join(item['reasons'])}\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def main():
    print("Verse Drama Detection")
    print("Identifies plays in verse for removal\n")

    # Scan corpus
    flagged, confidence_counts = scan_corpus()

    if not flagged:
        print("\n✓ No verse drama found!")
        return

    # Generate report
    generate_report(flagged, confidence_counts)

    print("\n" + "=" * 80)
    print("DETECTION COMPLETE")
    print("=" * 80)
    print(f"✓ Total verse drama detected: {len(flagged):,}")
    print(f"✓ Review report at: {REPORT_FILE}")

if __name__ == '__main__':
    main()
