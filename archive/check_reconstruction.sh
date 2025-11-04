#!/bin/bash
# Check Gutenberg reconstruction progress

echo "================================================"
echo "GUTENBERG RECONSTRUCTION STATUS"
echo "================================================"
echo ""

# Check if process is running
PID=$(ps aux | grep "[p]ython3 scripts/reconstruct_gutenberg_works.py" | awk '{print $2}' | head -1)

if [ -n "$PID" ]; then
    echo "✓ Reconstruction is RUNNING"
    echo "  PID: $PID"
    echo "  CPU: $(ps -p $PID -o %cpu | tail -1)%"
    echo "  Memory: $(ps -p $PID -o %mem | tail -1)%"
    echo "  Runtime: $(ps -p $PID -o etime | tail -1)"
else
    echo "✗ Reconstruction process NOT running"
    echo ""
    echo "Check if it completed successfully:"
    echo "  ls -lh Data/gutenberg_reconstructed.jsonl"
    exit 0
fi

echo ""
echo "------------------------------------------------"
echo "PROGRESS"
echo "------------------------------------------------"

OUTPUT_FILE="/Users/justin/Repos/AI Project/Data/gutenberg_reconstructed.jsonl"

# Check output file progress
if [ -f "$OUTPUT_FILE" ]; then
    WORKS_DONE=$(wc -l < "$OUTPUT_FILE")
    PERCENT=$((WORKS_DONE * 100 / 1191))
    echo "✓ Works reconstructed: $WORKS_DONE / 1191 ($PERCENT%)"
    echo "  File size: $(du -h "$OUTPUT_FILE" | awk '{print $1}')"
    echo "  Last updated: $(stat -f "%Sm" -t "%H:%M:%S" "$OUTPUT_FILE")"

    # Estimate time remaining
    RUNTIME_SECS=$(ps -p $PID -o etime= | awk -F: '{ if (NF==3) print ($1 * 3600) + ($2 * 60) + $3; else if (NF==2) print ($1 * 60) + $2; else print $1 }')
    if [ "$WORKS_DONE" -gt 0 ] && [ "$RUNTIME_SECS" -gt 0 ]; then
        RATE=$(echo "scale=2; $WORKS_DONE / $RUNTIME_SECS" | bc)
        REMAINING=$((1191 - WORKS_DONE))
        ETA_SECS=$(echo "scale=0; $REMAINING / $RATE" | bc)
        ETA_MINS=$((ETA_SECS / 60))
        echo "  Rate: $(echo "scale=1; $RATE * 60" | bc) works/min"
        echo "  ETA: ~$ETA_MINS minutes"
    fi

    echo ""
    echo "Last work:"
    tail -1 "$OUTPUT_FILE" | python3 -c "import sys, json; w=json.load(sys.stdin); print(f\"  {w.get('title', 'Unknown')} (ID {w['gutenberg_id']})\")" 2>/dev/null || echo "  (parsing...)"
else
    echo "⏳ Still grouping lines (no output yet)"
    echo "   Found 1191 unique Gutenberg IDs"
    echo "   Starting metadata fetching soon..."
fi

echo ""
echo "================================================"
echo ""
