#!/bin/bash
# Easy poem addition script for corpus

CORPUS_DIR=~/Repos/AI\ Project/Data/corpus_texts

echo "======================================"
echo "   ADD POEM TO CORPUS"
echo "======================================"
echo ""

# Count existing poems to get next number
LAST_NUM=$(ls "$CORPUS_DIR" | grep -E '^[0-9]+' | sed 's/_.*//' | sort -n | tail -1)
NEXT_NUM=$(printf "%03d" $((10#$LAST_NUM + 1)))

echo "Next poem number: $NEXT_NUM"
echo ""

# Get poem metadata
read -p "Author name: " AUTHOR
read -p "Poem title: " TITLE

# Clean up for filename (replace spaces with underscores, remove special chars)
AUTHOR_CLEAN=$(echo "$AUTHOR" | sed 's/ /_/g' | sed 's/[^a-zA-Z0-9_]//g')
TITLE_CLEAN=$(echo "$TITLE" | sed 's/ /_/g' | sed 's/[^a-zA-Z0-9_]//g')

FILENAME="${NEXT_NUM}_${AUTHOR_CLEAN}_${TITLE_CLEAN}.txt"
FILEPATH="$CORPUS_DIR/$FILENAME"

echo ""
echo "Will create: $FILENAME"
echo ""
echo "Now paste the poem text (press Ctrl+D when done):"
echo "---"

# Read poem text from stdin
cat > "$FILEPATH"

echo ""
echo "---"
echo "✓ Poem saved to: $FILEPATH"
echo ""

# Show what was saved
echo "Preview:"
head -5 "$FILEPATH"
if [ $(wc -l < "$FILEPATH") -gt 5 ]; then
    echo "..."
fi

echo ""
echo "✓ Done! Poem added to corpus."
