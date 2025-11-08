#!/usr/bin/env python3
"""
Analyze project structure and categorize scripts for cleanup.
"""

from pathlib import Path
from datetime import datetime
import json

BASE_DIR = Path("/Users/justin/Repos/AI Project")
SCRIPTS_DIR = BASE_DIR / "scripts"

# Define categories
CATEGORIES = {
    'active_cleanup': {
        'name': 'Active Cleanup Scripts (Keep)',
        'files': [
            'corpus_final_summary.py',
            'remove_redundant_titles.py',
            'detect_non_english_conservative.py',
            'remove_non_english_conservative.py',
        ]
    },
    'training': {
        'name': 'Training & Data Preparation (Keep)',
        'files': [
            'train_hierarchical_bert.py',
            'prepare_hierarchical_training_data.py',
        ]
    },
    'data_collection': {
        'name': 'Data Collection (Archive - completed)',
        'files': [
            'scrape_poetry_platform.py',
        ]
    },
    'detection_analysis': {
        'name': 'Detection & Analysis Scripts (Archive - completed)',
        'files': [
            'detect_multi_poem_files.py',
            'detect_verse_drama.py',
            'detect_prose_commentary.py',
            'detect_lineation_issues.py',
            'detect_and_remove_metadata.py',
            'detect_non_english_redux.py',
            'split_files_dry_run.py',
        ]
    },
    'metadata_cleanup': {
        'name': 'Metadata Cleanup Scripts (Archive - completed)',
        'files': [
            'clean_metadata.py',
            'second_metadata_sweep.py',
            'third_metadata_sweep.py',
            'final_metadata_scan.py',
        ]
    },
    'content_cleanup': {
        'name': 'Content Cleanup Scripts (Archive - completed)',
        'files': [
            'clean_content_formatting.py',
            'remove_foreign_and_translations.py',
            'remove_verse_drama.py',
        ]
    },
    'review_tools': {
        'name': 'Review/Manual Tools (Archive - completed)',
        'files': [
            'review_web_app.py',
            'lineation_review_app.py',
            'prose_review_app.py',
            'generate_prose_review.py',
            'apply_prose_decisions.py',
            'review_non_english_samples.py',
        ]
    },
    'reports': {
        'name': 'Report Files (Archive - historical)',
        'pattern': '*_report.*',
        'keep_latest': ['corpus_final_summary.md']
    },
    'lists': {
        'name': 'Detection Lists (Archive - historical)',
        'pattern': '*_list.txt',
    },
    'decisions': {
        'name': 'Decision Files (Archive - historical)',
        'pattern': '*_decisions.json',
    },
    'plans': {
        'name': 'Plan Files (Archive - historical)',
        'pattern': '*_plan.json',
    }
}

def get_file_info(filepath):
    """Get file modification time and size."""
    stat = filepath.stat()
    return {
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
        'modified_ts': stat.st_mtime
    }

def categorize_files():
    """Categorize all files in scripts directory."""
    categorized = {cat: [] for cat in CATEGORIES.keys()}
    categorized['uncategorized'] = []

    all_files = list(SCRIPTS_DIR.glob('*'))

    for filepath in all_files:
        if filepath.is_dir():
            continue

        filename = filepath.name
        found_category = False

        # Check explicit file lists
        for cat_name, cat_info in CATEGORIES.items():
            if 'files' in cat_info and filename in cat_info['files']:
                categorized[cat_name].append({
                    'name': filename,
                    'path': filepath,
                    **get_file_info(filepath)
                })
                found_category = True
                break

        if not found_category:
            # Check pattern matches
            for cat_name, cat_info in CATEGORIES.items():
                if 'pattern' in cat_info:
                    if filepath.match(cat_info['pattern']):
                        # Check if it should be kept
                        if 'keep_latest' in cat_info and filename in cat_info['keep_latest']:
                            categorized['active_cleanup'].append({
                                'name': filename,
                                'path': filepath,
                                **get_file_info(filepath)
                            })
                        else:
                            categorized[cat_name].append({
                                'name': filename,
                                'path': filepath,
                                **get_file_info(filepath)
                            })
                        found_category = True
                        break

        if not found_category:
            categorized['uncategorized'].append({
                'name': filename,
                'path': filepath,
                **get_file_info(filepath)
            })

    return categorized

def generate_report(categorized):
    """Generate organization report."""
    report = []
    report.append("# Project Scripts Organization Analysis")
    report.append("")
    report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    # Summary
    total_files = sum(len(files) for files in categorized.values())
    files_to_keep = len(categorized.get('active_cleanup', [])) + len(categorized.get('training', []))
    files_to_archive = total_files - files_to_keep

    report.append("## Summary")
    report.append("")
    report.append(f"- Total files: {total_files}")
    report.append(f"- Files to keep: {files_to_keep}")
    report.append(f"- Files to archive: {files_to_archive}")
    report.append("")

    # Recommendations
    report.append("## Recommendations")
    report.append("")
    report.append("### Keep in `/scripts`")
    report.append("")
    for cat_name in ['active_cleanup', 'training']:
        if cat_name in categorized and categorized[cat_name]:
            cat_info = CATEGORIES[cat_name]
            report.append(f"**{cat_info['name']}:**")
            for file in sorted(categorized[cat_name], key=lambda x: x['name']):
                report.append(f"- {file['name']} ({file['size']:,} bytes, modified {file['modified']})")
            report.append("")

    report.append("### Move to `/archive/cleanup_scripts`")
    report.append("")
    archive_cats = ['data_collection', 'detection_analysis', 'metadata_cleanup',
                    'content_cleanup', 'review_tools', 'reports', 'lists', 'decisions', 'plans']

    for cat_name in archive_cats:
        if cat_name in categorized and categorized[cat_name]:
            cat_info = CATEGORIES[cat_name]
            report.append(f"**{cat_info['name']}:**")
            report.append(f"- {len(categorized[cat_name])} files")
            report.append("")

    # Uncategorized
    if categorized.get('uncategorized'):
        report.append("### Uncategorized Files (Review Needed)")
        report.append("")
        for file in sorted(categorized['uncategorized'], key=lambda x: x['name']):
            report.append(f"- {file['name']} ({file['size']:,} bytes, modified {file['modified']})")
        report.append("")

    # Detailed breakdown
    report.append("## Detailed File Listing")
    report.append("")

    for cat_name, cat_info in CATEGORIES.items():
        if categorized.get(cat_name):
            report.append(f"### {cat_info['name']}")
            report.append("")
            for file in sorted(categorized[cat_name], key=lambda x: x['name']):
                report.append(f"- `{file['name']}`")
                report.append(f"  - Size: {file['size']:,} bytes")
                report.append(f"  - Modified: {file['modified']}")
            report.append("")

    return '\n'.join(report)

def main():
    print("Analyzing project structure...")
    categorized = categorize_files()

    print("\nGenerating report...")
    report = generate_report(categorized)

    output_file = BASE_DIR / "PROJECT_ORGANIZATION_ANALYSIS.md"
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"\n✓ Report saved to: {output_file}")

    # Also save categorization as JSON for automation
    json_output = BASE_DIR / "scripts_categorization.json"
    json_data = {}
    for cat, files in categorized.items():
        json_data[cat] = [f['name'] for f in files]

    with open(json_output, 'w') as f:
        json.dump(json_data, f, indent=2)

    print(f"✓ Categorization saved to: {json_output}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_files = sum(len(files) for files in categorized.values())
    files_to_keep = len(categorized.get('active_cleanup', [])) + len(categorized.get('training', []))
    files_to_archive = total_files - files_to_keep

    print(f"\nTotal files: {total_files}")
    print(f"Files to keep: {files_to_keep}")
    print(f"Files to archive: {files_to_archive}")
    print(f"\nReview the report for details: {output_file}")

if __name__ == '__main__':
    main()
