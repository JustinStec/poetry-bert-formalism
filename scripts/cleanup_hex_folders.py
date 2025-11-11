#!/usr/bin/env python3
"""
Clean up hex-prefixed author folder names.
Changes: "5Aa950F8Df1C6, Elizabeth Acevedo" -> "Acevedo, Elizabeth"
"""

import os
import shutil
from pathlib import Path
import re

BASE_DIR = Path("/Users/justin/Repos/AI Project")
CORPUS_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"

def main():
    print("Finding hex-prefixed folders...")
    hex_pattern = re.compile(r'^([0-9A-Fa-f]{8,}),\s*(.+)$')

    folders = sorted([f for f in CORPUS_DIR.iterdir() if f.is_dir()])
    hex_folders = []

    for folder in folders:
        match = hex_pattern.match(folder.name)
        if match:
            hex_prefix, author_name = match.groups()
            hex_folders.append((folder, author_name))

    print(f"\nFound {len(hex_folders)} hex-prefixed folders:\n")

    for folder, author_name in hex_folders:
        new_name = author_name.strip()
        new_path = folder.parent / new_name

        print(f"  {folder.name}")
        print(f"  -> {new_name}")

        # Check if target already exists
        if new_path.exists():
            print(f"  ⚠️  WARNING: '{new_name}' already exists! Skipping.")
            print()
            continue

        # Rename
        folder.rename(new_path)
        print(f"  ✓ Renamed")
        print()

    print(f"\n✓ Cleanup complete! Renamed {len(hex_folders)} folders.")
    print("\nNote: You'll need to update the CSV metadata to match the new folder names.")

if __name__ == '__main__':
    main()
