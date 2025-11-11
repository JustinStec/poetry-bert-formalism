#!/bin/bash
RESULTS="/Users/justin/Repos/AI Project/scripts/ai_attribution_results.jsonl"
LOG="/Users/justin/Repos/AI Project/scripts/ai_attribution_fixes.log"

PROCESSED=$(wc -l < "$RESULTS" 2>/dev/null || echo 0)
TOTAL=46899
PERCENT=$(echo "scale=2; $PROCESSED * 100 / $TOTAL" | bc)

echo "=================================="
echo "GPT-4o Poetry Attribution Progress"
echo "=================================="
echo "Processed: $PROCESSED / $TOTAL poems"
echo "Progress:  $PERCENT%"
echo ""
echo "Recent attributions (last 15):"
tail -15 "$LOG" 2>/dev/null || echo "No log yet"
