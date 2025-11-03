#!/bin/bash
# Detailed BERT training progress checker

echo "======================================"
echo "   BERT TRAINING PROGRESS"
echo "======================================"
echo ""

# Check if training is running
if ! pgrep -f "finetune_bert_eebo_local.py" > /dev/null; then
    echo "✗ Training is NOT running"

    # Check for checkpoints to see how far it got
    CHECKPOINT_DIR=~/Repos/AI\ Project/Data/Historical_Embeddings/EEBO_1595-1700/bert_checkpoints
    if [ -d "$CHECKPOINT_DIR" ]; then
        LAST_CHECKPOINT=$(ls -t "$CHECKPOINT_DIR"/checkpoint-* 2>/dev/null | head -1)
        if [ -n "$LAST_CHECKPOINT" ]; then
            STEP=$(basename "$LAST_CHECKPOINT" | sed 's/checkpoint-//')
            echo "Last checkpoint: Step $STEP"
        fi
    fi

    # Check if completed
    OUTPUT_DIR=~/Repos/AI\ Project/Data/Historical_Embeddings/EEBO_1595-1700/eebo_bert_finetuned
    if [ -d "$OUTPUT_DIR" ] && [ -f "$OUTPUT_DIR/config.json" ]; then
        echo "✓ TRAINING COMPLETED!"
        echo "Model saved at: $OUTPUT_DIR"
    fi

    exit 0
fi

echo "✓ Training is RUNNING"
echo ""

# Get process info
PID=$(pgrep -f "finetune_bert_eebo_local.py")
ELAPSED=$(ps -o etime= -p $PID | xargs)
echo "Process ID: $PID"
echo "Running for: $ELAPSED"
echo ""

# Check checkpoint directory for progress
CHECKPOINT_DIR=~/Repos/AI\ Project/Data/Historical_Embeddings/EEBO_1595-1700/bert_checkpoints

if [ -d "$CHECKPOINT_DIR" ]; then
    # Count checkpoints
    CHECKPOINT_COUNT=$(ls -1 "$CHECKPOINT_DIR"/checkpoint-* 2>/dev/null | wc -l | xargs)

    if [ "$CHECKPOINT_COUNT" -gt 0 ]; then
        # Get latest checkpoint
        LAST_CHECKPOINT=$(ls -t "$CHECKPOINT_DIR"/checkpoint-* 2>/dev/null | head -1)
        CURRENT_STEP=$(basename "$LAST_CHECKPOINT" | sed 's/checkpoint-//')

        # Estimate total steps (61315 samples / 8 batch size * 3 epochs)
        TOTAL_STEPS=22993

        # Calculate progress
        PERCENT=$(echo "scale=2; ($CURRENT_STEP / $TOTAL_STEPS) * 100" | bc)
        REMAINING_STEPS=$((TOTAL_STEPS - CURRENT_STEP))

        echo "--- Progress ---"
        echo "Current Step: $CURRENT_STEP / $TOTAL_STEPS"
        echo "Progress: $PERCENT%"
        echo "Remaining: $REMAINING_STEPS steps"
        echo "Checkpoints saved: $CHECKPOINT_COUNT"
        echo ""

        # Estimate time remaining (rough estimate: 2.5 seconds per step on Apple Silicon)
        SECONDS_PER_STEP=2.5
        REMAINING_SECONDS=$(echo "$REMAINING_STEPS * $SECONDS_PER_STEP" | bc)
        REMAINING_HOURS=$(echo "scale=1; $REMAINING_SECONDS / 3600" | bc)

        echo "--- ETA ---"
        echo "Estimated remaining: ${REMAINING_HOURS} hours"
        echo "(Based on ~2.5 sec/step estimate)"
        echo ""

        # Show last checkpoint age
        CHECKPOINT_AGE=$((($(date +%s) - $(stat -f %m "$LAST_CHECKPOINT")) / 60))
        echo "Last checkpoint: $CHECKPOINT_AGE minutes ago"

    else
        echo "--- Status ---"
        echo "Still in early training (no checkpoints yet)"
        echo "First checkpoint at step 1000"
        echo ""
    fi

    # Check if training logs directory exists
    if [ -d "$CHECKPOINT_DIR/logs" ]; then
        echo "--- Training Logs ---"
        echo "Logs available at: $CHECKPOINT_DIR/logs"
    fi
else
    echo "--- Status ---"
    echo "Initializing... (checkpoint directory not created yet)"
    echo "This is normal in the first few minutes"
fi

echo ""
echo "======================================"
echo "Refresh this script to see updates!"
echo "======================================"
