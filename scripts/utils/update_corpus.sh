#!/bin/bash
# One-command corpus update: scan new poems and update all metadata

echo "======================================"
echo "   UPDATE CORPUS METADATA"
echo "======================================"
echo ""

cd /Users/justin/Repos/AI\ Project

# Step 1: Scan for new poems
echo "Step 1: Scanning for new poems..."
echo ""
python3 scripts/utils/smart_scan_poems.py

echo ""
echo "======================================"
echo ""

# Step 2: Update Excel file (if Python script exists)
if [ -f "Metadata/update_metadata.py" ]; then
    echo "Step 2: Updating Excel file..."
    echo ""
    cd Metadata
    python3 update_metadata.py
    cd ..
    echo ""
    echo "✓ Excel file updated!"
else
    echo "Step 2: Skipped (update_metadata.py not found)"
fi

echo ""
echo "======================================"
echo "   CORPUS UPDATE COMPLETE"
echo "======================================"
echo ""
echo "View/edit metadata:"
echo "  CSV: Metadata/corpus_metadata.csv"
echo "  Excel: Metadata/corpus_metadata.xlsx"
echo ""
echo "Don't forget to set collected=TRUE for poems you want to analyze!"
