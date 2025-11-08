#!/usr/bin/env python3
"""
Scrape all poets and poems from poetryplatform.org
"""

import requests
import json
import time
import sys
from pathlib import Path

# Force unbuffered output
sys.stdout = sys.stdout
sys.stderr = sys.stderr

# Output paths
OUTPUT_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_scraped")
POETS_FILE = OUTPUT_DIR / "poets_index.jsonl"
POEMS_DIR = OUTPUT_DIR / "poems"

OUTPUT_DIR.mkdir(exist_ok=True)
POEMS_DIR.mkdir(exist_ok=True)

# API endpoints
BASE_URL = "https://www.poetryplatform.org"
POETS_API = f"{BASE_URL}/api/poets_full"

def fetch_all_poets():
    """Fetch all poets from the API with pagination."""
    all_poets = []
    page = 1

    print("Fetching poets from Poetry Platform...")
    sys.stdout.flush()

    while True:
        try:
            print(f"  Fetching page {page}...")
            sys.stdout.flush()
            response = requests.get(POETS_API, params={'page': page}, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'poets' in data:
                poets = data['poets']
                if not poets:
                    break

                all_poets.extend(poets)
                print(f"    Found {len(poets)} poets (total: {len(all_poets)})")
                sys.stdout.flush()

                # Check if there are more pages
                total_pages = data.get('total_pages', 1)
                if page >= total_pages:
                    break

                page += 1
                time.sleep(0.5)  # Be nice to the server
            else:
                # Might be a single list
                if isinstance(data, list):
                    all_poets.extend(data)
                    break
                else:
                    print(f"Unexpected response format: {list(data.keys())}")
                    break

        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return all_poets

def fetch_poet_details(poet_id, poet_name):
    """Fetch detailed information about a specific poet."""
    try:
        url = f"{BASE_URL}/api/poet/{poet_id}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  Error fetching poet {poet_name}: {e}")
        return None

def save_poets_index(poets):
    """Save poets index to JSONL."""
    print(f"\nSaving poets index to {POETS_FILE}...")
    with open(POETS_FILE, 'w', encoding='utf-8') as f:
        for poet in poets:
            f.write(json.dumps(poet, ensure_ascii=False) + '\n')
    print(f"✓ Saved {len(poets)} poets")

def download_all_poems(poets):
    """Download all poems for each poet."""
    total_poems = 0

    print(f"\nSaving poems for {len(poets)} poets...")
    sys.stdout.flush()

    for i, poet in enumerate(poets, 1):
        poet_name = poet.get('name', 'Unknown').strip()
        poems = poet.get('poems', [])

        if poems:
            print(f"[{i}/{len(poets)}] {poet_name}: {len(poems)} poems")
            sys.stdout.flush()

            # Save each poem
            for poem in poems:
                poem_title = poem.get('title', 'Untitled').strip()
                poem_text = poem.get('content', poem.get('text', '')).strip()

                if poem_text:
                    # Create safe filename with aggressive truncation
                    safe_name = "".join(c for c in poet_name if c.isalnum() or c in ' -_').strip()[:40]
                    safe_title = "".join(c for c in poem_title if c.isalnum() or c in ' -_').strip()[:80]

                    # Build filename and ensure it's not too long
                    filename = f"{safe_title}_{safe_name}.txt"

                    # If still too long, truncate more aggressively
                    if len(filename) > 150:
                        safe_title = safe_title[:60]
                        safe_name = safe_name[:30]
                        filename = f"{safe_title}_{safe_name}.txt"

                    filepath = POEMS_DIR / filename

                    # Write poem file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"{poem_title}\n\n{poem_text}")

                    total_poems += 1

    return total_poems

def main():
    print("=" * 80)
    print("POETRY PLATFORM SCRAPER")
    print("=" * 80)

    # Check if we already have poets index
    if POETS_FILE.exists():
        print(f"\nLoading existing poets index from {POETS_FILE}...")
        poets = []
        with open(POETS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                poets.append(json.loads(line.strip()))
        print(f"✓ Loaded {len(poets)} poets from existing index")
    else:
        # Fetch all poets
        poets = fetch_all_poets()

        if not poets:
            print("No poets found!")
            return

        print(f"\n✓ Found {len(poets)} total poets")

        # Save poets index
        save_poets_index(poets)

    # Download all poems
    total_poems = download_all_poems(poets)

    print("\n" + "=" * 80)
    print("SCRAPING COMPLETE")
    print("=" * 80)
    print(f"Poets collected:  {len(poets):,}")
    print(f"Poems downloaded: {total_poems:,}")
    print(f"\nData saved to: {OUTPUT_DIR}")
    print(f"  - Poets index: {POETS_FILE}")
    print(f"  - Poems: {POEMS_DIR}/")
    print("=" * 80)

if __name__ == '__main__':
    main()
