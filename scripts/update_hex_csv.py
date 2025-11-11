#!/usr/bin/env python3
"""
Update CSV metadata after hex folder cleanup.
"""

import csv
import re
from pathlib import Path

BASE_DIR = Path("/Users/justin/Repos/AI Project")
CSV_PATH = BASE_DIR / "data/metadata/corpus_final_metadata.csv"

# Mapping of old hex prefixes to new names
HEX_MAPPING = {
    "56D205E3Abb9F, Robert Thomas": "Robert Thomas",
    "56D205F03Dc5A, Lee Upton": "Lee Upton",
    "56D20616A9Bf3, David Hernandez": "David Hernandez",
    "56D2070387548, Kit Robinson": "Kit Robinson",
    "56D207070306A, Ko Un": "Ko Un",
    "56D20714Eb2Bc, Julia Shipley": "Julia Shipley",
    "56D20738Bc0, Constance Quarterman Bridges": "Constance Quarterman Bridges",
    "5Aa950F8Df1C6, Elizabeth Acevedo": "Elizabeth Acevedo",
    "5Dfbc1B2D8A94, Destiny Hemphill": "Destiny Hemphill",
    "5F4D733Cda5D3, Alvin Feinman": "Alvin Feinman",
    "5Fb6D9928Fc9B, Lewis Macadams": "Lewis Macadams",
    "60E5Ea55108F4, Sasha Pimentel": "Sasha Pimentel",
    "6161Ff74A720C, Isabel Duarte Gray": "Isabel Duarte Gray",
    "622Ab5536C412, Nick Carbo": "Nick Carbo",
    "628D10E0Af8Eb, Kathleen Tankersley Young": "Kathleen Tankersley Young",
    "62Dea41Fc3959, Jorge Carrera Andrade": "Jorge Carrera Andrade",
    "62E2Ad9C4B136, Rachel Long": "Rachel Long",
    "636566560Aef3, Norman Finkelstein": "Norman Finkelstein",
    "642454B3942Ad, Elizabeth Theriot": "Elizabeth Theriot",
    "6442A0Fd2630E, Gabrielle Joy Lessans": "Gabrielle Joy Lessans",
    "64C0102E6047C, Maya Abu Al Hayyat": "Maya Abu Al Hayyat",
    "64D4Fedb224Cd, Nathan Mcclain": "Nathan Mcclain",
    "64E3B3002F355, Jjjjjerome Ellis": "Jjjjjerome Ellis",
}

def main():
    print(f"Reading CSV: {CSV_PATH}")

    # Read CSV
    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"Loaded {len(rows)} rows")

    # Update paths
    updated = 0
    for row in rows:
        filepath = row['filepath']

        # Check if path contains any hex prefix
        for old_name, new_name in HEX_MAPPING.items():
            if old_name in filepath:
                row['filepath'] = filepath.replace(old_name, new_name)
                updated += 1
                break

    print(f"Updated {updated} rows")

    # Write back
    print(f"Writing updated CSV...")
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ CSV updated successfully!")

if __name__ == '__main__':
    main()
