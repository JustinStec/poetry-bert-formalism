#!/bin/bash
# Continuous training monitor - logs progress every 5 minutes

LOG_FILE=~/Repos/AI\ Project/logs/training_monitor.log

echo "Starting training monitor at $(date)" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"

while true; do
    if pgrep -f "finetune_bert_eebo_local.py" > /dev/null; then
        echo "" >> "$LOG_FILE"
        echo "[$(date)] Training is running" >> "$LOG_FILE"

        # Log memory usage
        echo "Memory usage:" >> "$LOG_FILE"
        top -l 1 | grep PhysMem >> "$LOG_FILE"

        # Log uptime
        UPTIME=$(ps -o etime= -p $(pgrep -f finetune_bert_eebo_local.py))
        echo "Training uptime: $UPTIME" >> "$LOG_FILE"
    else
        echo "[$(date)] Training stopped" >> "$LOG_FILE"
        break
    fi

    sleep 300  # Check every 5 minutes
done

echo "Monitor stopped at $(date)" >> "$LOG_FILE"
