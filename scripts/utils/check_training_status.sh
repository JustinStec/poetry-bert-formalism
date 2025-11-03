#!/bin/bash
# Quick BERT training status checker

echo "===== BERT Training Status ====="
echo ""

# Check if training is running
if pgrep -f "finetune_bert_eebo_local.py" > /dev/null; then
    echo "✓ Training is RUNNING"
    echo ""

    # Find the log file
    LOG_FILE=$(ls -t ~/Repos/AI\ Project/logs/bert_training_*.log 2>/dev/null | head -1)

    if [ -f "$LOG_FILE" ]; then
        echo "Latest log: $LOG_FILE"
        echo ""

        # Show last progress update
        echo "--- Latest Progress ---"
        grep "Progress:" "$LOG_FILE" | tail -3
        echo ""

        # Show last loss value
        echo "--- Latest Loss ---"
        grep "Loss:" "$LOG_FILE" | tail -1
        echo ""

        # Show training config
        echo "--- Training Config ---"
        grep "Total steps:" "$LOG_FILE" | head -1
        grep "Device:" "$LOG_FILE" | head -1
        echo ""

        # Show how long it's been running
        START_TIME=$(stat -f "%m" "$LOG_FILE")
        CURRENT_TIME=$(date +%s)
        ELAPSED=$((CURRENT_TIME - START_TIME))
        HOURS=$((ELAPSED / 3600))
        MINS=$(((ELAPSED % 3600) / 60))
        echo "Running for: ${HOURS}h ${MINS}m"
    else
        echo "⚠ No log file found yet"
    fi
else
    echo "✗ Training is NOT running"
    echo ""

    # Check if it completed
    LOG_FILE=$(ls -t ~/Repos/AI\ Project/logs/bert_training_*.log 2>/dev/null | head -1)
    if [ -f "$LOG_FILE" ]; then
        if grep -q "TRAINING COMPLETE" "$LOG_FILE"; then
            echo "✓ Training COMPLETED!"
            grep "Total time:" "$LOG_FILE" | tail -1
        else
            echo "⚠ Training stopped unexpectedly"
            echo "Last 5 lines of log:"
            tail -5 "$LOG_FILE"
        fi
    fi
fi

echo ""
echo "================================"
