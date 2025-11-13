# Parallel Classification Instructions

## Setup (One Time Only)

Copy script to M4 Max:
```bash
scp ~/Repos/AI\ Project/scripts/phase3/classify_range.py justin@100.65.21.63:~/poetry-bert-formalism/scripts/
```

## Running Parallel Sessions

Open **5 separate Claude Code web tabs** at claude.ai

### Tab 1 (Session 1): Poems 0-23,334
Paste this command:
```
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 0 23334 session1"
```

### Tab 2 (Session 2): Poems 23,334-46,668
Paste this command:
```
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 23334 46668 session2"
```

### Tab 3 (Session 3): Poems 46,668-69,002
Paste this command:
```
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 46668 69002 session3"
```

### Tab 4 (Session 4): Poems 69,002-93,336
Paste this command:
```
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 69002 93336 session4"
```

### Tab 5 (Session 5): Poems 93,336-116,674
Paste this command:
```
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 93336 116674 session5"
```

## What Happens

1. Each session loads 100 poems
2. Claude classifies them
3. Results saved automatically
4. Script runs again for next 100
5. Repeats until session's range is complete

## Progress Tracking

Check progress anytime:
```bash
ssh justin@100.65.21.63 "ls -lh ~/poetry-bert-formalism/data/classifications/*progress.txt && cat ~/poetry-bert-formalism/data/classifications/*progress.txt"
```

## When All Sessions Complete

Merge results:
```bash
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/merge_classifications.py"
```

This creates final output: `classified_poems_complete.csv`

## Estimated Time

- Each session: ~20-30 batches of 100 poems
- With 5 parallel sessions: **Complete in 4-6 hours**
- vs. sequential: would take 20-30 hours

## Current Session (This One)

This session is already running! It's handling part of the work too.
