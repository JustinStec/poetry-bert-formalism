#!/bin/bash
# Scan corpus for new poems and generate basic metadata

CORPUS_DIR=/Users/justin/Repos/AI\ Project/Data/corpus_texts
METADATA_DIR=/Users/justin/Repos/AI\ Project/Metadata

echo "======================================"
echo "   SCAN FOR NEW POEMS"
echo "======================================"
echo ""

# Count total poems in corpus
TOTAL_POEMS=$(ls "$CORPUS_DIR"/*.txt 2>/dev/null | wc -l | xargs)
echo "Total poems in corpus: $TOTAL_POEMS"

# Create a simple CSV if it doesn't exist
CSV_FILE="$METADATA_DIR/corpus_metadata.csv"

if [ ! -f "$CSV_FILE" ]; then
    echo "Creating new metadata CSV..."
    echo "id,filename,author,title,year,period,form,lines,words,collected" > "$CSV_FILE"
fi

# Count existing entries in CSV (excluding header)
EXISTING_ENTRIES=$(tail -n +2 "$CSV_FILE" 2>/dev/null | wc -l | xargs)
echo "Existing metadata entries: $EXISTING_ENTRIES"

NEW_COUNT=0

# Check each poem file
for POEM_FILE in "$CORPUS_DIR"/*.txt; do
    if [ -f "$POEM_FILE" ]; then
        FILENAME=$(basename "$POEM_FILE")

        # Check if already in CSV
        if grep -q "$FILENAME" "$CSV_FILE"; then
            continue
        fi

        # Extract info from filename
        # Format: NNN_Author_Title.txt
        POEM_NUM=$(echo "$FILENAME" | sed 's/_.*//')
        REST=$(echo "$FILENAME" | sed 's/^[0-9]*_//' | sed 's/\.txt$//')

        # Try to split author and title (first underscore-separated part is author)
        AUTHOR=$(echo "$REST" | sed 's/_/ /g' | awk '{print $1, $2}' | sed 's/ $//')
        TITLE=$(echo "$REST" | sed 's/^[^_]*_//' | sed 's/_/ /g')

        # Count lines and words
        LINES=$(wc -l < "$POEM_FILE" | xargs)
        WORDS=$(wc -w < "$POEM_FILE" | xargs)

        # Add to CSV with placeholder values
        echo "$POEM_NUM,$FILENAME,$AUTHOR,$TITLE,UNKNOWN,UNKNOWN,UNKNOWN,$LINES,$WORDS,FALSE" >> "$CSV_FILE"

        echo "✓ Added metadata entry: $FILENAME"
        NEW_COUNT=$((NEW_COUNT + 1))
    fi
done

echo ""
if [ $NEW_COUNT -eq 0 ]; then
    echo "No new poems found. All poems have metadata entries."
else
    echo "======================================"
    echo "✓ Created $NEW_COUNT new metadata entries"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Edit: $CSV_FILE"
    echo "2. Fill in: year, period, form for new poems"
    echo "3. Set collected=TRUE for poems to analyze"
    echo ""
    echo "Or edit the Excel file instead:"
    echo "open $METADATA_DIR/corpus_metadata.xlsx"
fi

echo ""
echo "Total: $TOTAL_POEMS poems, $((EXISTING_ENTRIES + NEW_COUNT)) with metadata"
