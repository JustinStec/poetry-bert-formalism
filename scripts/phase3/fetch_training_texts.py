#!/usr/bin/env python3
"""
Fetch full poem texts for the 457 training poems.

Strategy:
1. For 53 gold-standard poems: Use Poetry Foundation URLs
2. For 404 colab-classified poems: Try multiple sources
   - Poetry Foundation search
   - Project Gutenberg
   - Public domain collections
   - Manual collection for difficult cases
"""

import pandas as pd
import requests
from pathlib import Path
import time
import re
from bs4 import BeautifulSoup
import json

BASE_DIR = Path("/Users/justin/Repos/AI Project")
TRAINING_FILE = BASE_DIR / "Data/phase3/training_set_456_poems.csv"
OUTPUT_FILE = BASE_DIR / "Data/phase3/training_poems_with_texts.csv"
MANUAL_NEEDED_LOG = BASE_DIR / "Data/phase3/poems_need_manual_collection.csv"

def fetch_poetry_foundation(url):
    """Fetch poem text from Poetry Foundation URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find poem div
        poem_div = soup.find('div', class_='c-feature-bd')
        if not poem_div:
            poem_div = soup.find('div', class_='poem')
        if not poem_div:
            return None

        # Extract text
        lines = []
        for line in poem_div.find_all(['p', 'div']):
            text = line.get_text().strip()
            if text:
                lines.append(text)

        return '\n'.join(lines)

    except Exception as e:
        print(f"  ✗ Poetry Foundation fetch failed: {e}")
        return None

def search_poetry_foundation(title, author):
    """Search Poetry Foundation for poem."""
    try:
        # Clean up title for search
        search_title = title.split('(')[0].strip()

        search_url = "https://www.poetryfoundation.org/search"
        params = {
            'query': f'{search_title} {author}',
            'refinement': 'poems'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(search_url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for first result link
            result = soup.find('a', class_='c-vr-text')
            if result and 'href' in result.attrs:
                poem_url = 'https://www.poetryfoundation.org' + result['href']
                return fetch_poetry_foundation(poem_url)

        return None

    except Exception as e:
        print(f"  ✗ Poetry Foundation search failed: {e}")
        return None

def main():
    print("="*80)
    print("PHASE 3B: FETCH TRAINING POEM TEXTS")
    print("="*80)

    # Load training dataset
    print("\n1. Loading training dataset...")
    df = pd.read_csv(TRAINING_FILE)
    print(f"   ✓ Loaded {len(df)} training poems")

    # Analyze sources
    print("\n2. Analyzing sources...")
    with_urls = df[df['source_url'].notna()]
    without_urls = df[df['source_url'].isna()]

    print(f"   With Poetry Foundation URLs: {len(with_urls)}")
    print(f"   Without URLs (need fetching): {len(without_urls)}")

    # Fetch texts
    print("\n3. Fetching poem texts...")
    print("\n   Phase A: Fetching from existing URLs...")

    texts_collected = []
    fetch_failures = []

    for idx, row in with_urls.iterrows():
        print(f"   [{idx+1}/{len(df)}] {row['title'][:50]}...", end=' ')

        text = fetch_poetry_foundation(row['source_url'])

        if text:
            texts_collected.append({
                'training_idx': idx,
                'title': row['title'],
                'author': row['author'],
                'year_approx': row['year_approx'],
                'period': row['period'],
                'source': row['source'],
                'text': text,
                'text_source': 'poetry_foundation_url',
                'source_url': row['source_url']
            })
            print("✓")
        else:
            fetch_failures.append({
                'training_idx': idx,
                'title': row['title'],
                'author': row['author'],
                'year_approx': row['year_approx'],
                'period': row['period'],
                'source_url': row['source_url'],
                'reason': 'URL fetch failed'
            })
            print("✗")

        # Rate limiting
        time.sleep(1)

    print(f"\n   ✓ Fetched {len(texts_collected)} from URLs")
    print(f"   ✗ Failed {len(fetch_failures)} URL fetches")

    print("\n   Phase B: Searching for poems without URLs...")

    search_count = 0
    search_limit = 20  # Limit searches to avoid rate limiting

    for idx, row in without_urls.head(search_limit).iterrows():
        print(f"   [{idx+1}/{len(df)}] {row['title'][:50]}...", end=' ')

        text = search_poetry_foundation(row['title'], row['author'])

        if text:
            texts_collected.append({
                'training_idx': idx,
                'title': row['title'],
                'author': row['author'],
                'year_approx': row['year_approx'],
                'period': row['period'],
                'source': row['source'],
                'text': text,
                'text_source': 'poetry_foundation_search',
                'source_url': None
            })
            print("✓")
            search_count += 1
        else:
            fetch_failures.append({
                'training_idx': idx,
                'title': row['title'],
                'author': row['author'],
                'year_approx': row['year_approx'],
                'period': row['period'],
                'source_url': None,
                'reason': 'Search failed'
            })
            print("✗")

        # Rate limiting
        time.sleep(2)

    print(f"\n   ✓ Found {search_count} via search")

    # Save collected texts
    print("\n4. Saving collected texts...")
    if texts_collected:
        texts_df = pd.DataFrame(texts_collected)
        texts_df.to_csv(OUTPUT_FILE, index=False)
        print(f"   ✓ Saved {len(texts_collected)} texts to {OUTPUT_FILE}")

        # Stats
        avg_length = texts_df['text'].str.len().mean()
        print(f"\n   Average text length: {avg_length:.0f} characters")
        print(f"   Shortest: {texts_df['text'].str.len().min()} characters")
        print(f"   Longest: {texts_df['text'].str.len().max()} characters")

    # Save poems needing manual collection
    print("\n5. Logging poems needing manual collection...")
    if fetch_failures:
        failures_df = pd.DataFrame(fetch_failures)
        failures_df.to_csv(MANUAL_NEEDED_LOG, index=False)
        print(f"   ✓ Saved {len(fetch_failures)} poems needing manual work to {MANUAL_NEEDED_LOG}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal training poems: {len(df)}")
    print(f"Texts collected: {len(texts_collected)}")
    print(f"  - From URLs: {len([t for t in texts_collected if t['text_source'] == 'poetry_foundation_url'])}")
    print(f"  - From search: {len([t for t in texts_collected if t['text_source'] == 'poetry_foundation_search'])}")
    print(f"\nStill needed: {len(fetch_failures)}")
    print(f"  - URL fetch failed: {len([f for f in fetch_failures if f['source_url'] is not None])}")
    print(f"  - Search failed: {len([f for f in fetch_failures if f['source_url'] is None])}")

    if len(texts_collected) < 100:
        print("\n" + "="*80)
        print("⚠ WARNING: Only collected {len(texts_collected)} texts")
        print("   This is insufficient for fine-tuning.")
        print("   Consider:")
        print("   1. Manual collection from Gutenberg Project")
        print("   2. Using existing poetry datasets")
        print("   3. Web scraping with selenium for dynamic content")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("NEXT STEP: Format instruction-tuning dataset")
        print("="*80)

if __name__ == "__main__":
    main()
