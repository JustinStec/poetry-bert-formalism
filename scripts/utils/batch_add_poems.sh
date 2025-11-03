#!/bin/bash
# Batch add multiple poems to corpus

CORPUS_DIR=/Users/justin/Repos/AI\ Project/Data/corpus_texts

echo "======================================"
echo "   BATCH ADD POEMS TO CORPUS"
echo "======================================"
echo ""
echo "This script will help you add multiple poems."
echo "Place your poem files in: ~/Desktop/poems_to_add/"
echo "Name them like: AuthorName_PoemTitle.txt"
echo ""
echo "Press Enter when ready (or Ctrl+C to cancel)..."
read

# Check if source directory exists
SOURCE_DIR=~/Desktop/poems_to_add
if [ ! -d "$SOURCE_DIR" ]; then
    mkdir -p "$SOURCE_DIR"
    echo "Created directory: $SOURCE_DIR"
    echo "Please add your poem files there and run this script again."
    exit 0
fi

# Count files
FILE_COUNT=$(ls "$SOURCE_DIR"/*.txt 2>/dev/null | wc -l | xargs)

if [ "$FILE_COUNT" -eq 0 ]; then
    echo "No .txt files found in $SOURCE_DIR"
    echo "Add your poems there and run this script again."
    exit 0
fi

echo "Found $FILE_COUNT poem files"
echo ""

# Get next poem number
LAST_NUM=$(ls "$CORPUS_DIR" | grep -E '^[0-9]+' | sed 's/_.*//' | sort -n | tail -1)
NEXT_NUM=$((10#$LAST_NUM + 1))

echo "Will number starting from: $(printf "%03d" $NEXT_NUM)"
echo ""
echo "Processing poems..."
echo ""

# Process each file
COUNTER=0
for POEM_FILE in "$SOURCE_DIR"/*.txt; do
    if [ -f "$POEM_FILE" ]; then
        FILENAME=$(basename "$POEM_FILE")
        POEM_NUM=$(printf "%03d" $((NEXT_NUM + COUNTER)))

        # Create new filename with number prefix
        NEW_FILENAME="${POEM_NUM}_${FILENAME}"
        NEW_PATH="$CORPUS_DIR/$NEW_FILENAME"

        # Copy file
        cp "$POEM_FILE" "$NEW_PATH"

        echo "✓ Added: $NEW_FILENAME"
        COUNTER=$((COUNTER + 1))
    fi
done

echo ""
echo "======================================"
echo "✓ Added $COUNTER poems to corpus!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Run: ~/Repos/AI\ Project/scripts/utils/smart_scan_poems.py"
echo "   (This will create metadata entries)"
echo "2. Edit metadata in Metadata/corpus_metadata.xlsx"
echo "3. Mark collected=TRUE for poems you want to analyze"
echo ""
echo "Original files remain in: $SOURCE_DIR"
echo "(You can delete them when done)"
