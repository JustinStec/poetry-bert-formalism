#!/usr/bin/env python3
"""
Web interface for reviewing lineation issues.
Similar to prose commentary review - load detections and allow manual decisions.
"""

from flask import Flask, jsonify, request, send_from_directory
import json
import csv
from pathlib import Path
from detect_lineation_issues import analyze_lineation, get_file_path

app = Flask(__name__)

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
DECISIONS_FILE = Path("/Users/justin/Repos/AI Project/scripts/lineation_review_decisions.json")

# Load or create decisions
decisions = {}
if DECISIONS_FILE.exists():
    with open(DECISIONS_FILE, 'r') as f:
        decisions = json.load(f)

# Store detections in memory
detections = []

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Lineation Issue Review</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            margin-bottom: 10px;
            color: #fff;
            font-size: 28px;
        }

        .stats {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .stat {
            text-align: center;
        }

        .stat-label {
            color: #999;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #333;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 20px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            width: 0%;
            transition: width 0.3s;
        }

        .card {
            background: #2a2a2a;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
        }

        .card-header {
            margin-bottom: 20px;
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
        }

        .card-title {
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 5px;
        }

        .card-meta {
            color: #999;
            font-size: 14px;
        }

        .source-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }

        .source-gutenberg {
            background: #3f51b5;
            color: white;
        }

        .source-scraper {
            background: #009688;
            color: white;
        }

        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            background: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .metric {
            text-align: center;
        }

        .metric-label {
            color: #999;
            font-size: 12px;
            margin-bottom: 5px;
        }

        .metric-value {
            font-size: 20px;
            font-weight: bold;
            color: #fff;
        }

        .text-container {
            background: #1e1e1e;
            border-radius: 8px;
            padding: 25px;
            max-height: 700px;
            overflow-y: auto;
            margin-bottom: 25px;
            line-height: 1.9;
            font-family: 'Georgia', serif;
            font-size: 16px;
        }

        .text-container pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: inherit;
            color: #e0e0e0;
        }

        .long-line {
            background: rgba(255, 152, 0, 0.2);
            border-left: 3px solid #ff9800;
            padding-left: 10px;
        }

        .very-long-line {
            background: rgba(244, 67, 54, 0.2);
            border-left: 3px solid #f44336;
            padding-left: 10px;
        }

        .actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            position: sticky;
            bottom: 0;
            background: #2a2a2a;
            padding: 20px 0;
            z-index: 100;
            box-shadow: 0 -2px 8px rgba(0,0,0,0.3);
        }

        button {
            padding: 10px 25px;
            font-size: 14px;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            min-width: 120px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .btn-keep {
            background: #4CAF50;
            color: white;
        }

        .btn-keep:hover {
            background: #45a049;
        }

        .btn-prose {
            background: #2196F3;
            color: white;
        }

        .btn-prose:hover {
            background: #0b7dda;
        }

        .btn-delete {
            background: #f44336;
            color: white;
        }

        .btn-delete:hover {
            background: #da190b;
        }

        .btn-skip {
            background: #757575;
            color: white;
        }

        .btn-skip:hover {
            background: #616161;
        }

        .btn-nav {
            background: #333;
            color: white;
        }

        .btn-nav:hover {
            background: #444;
        }

        .keyboard-hint {
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 10px;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Lineation Issue Review</h1>

        <div class="stats">
            <div class="stat">
                <div class="stat-label">Total</div>
                <div class="stat-value" id="totalCount">-</div>
            </div>
            <div class="stat">
                <div class="stat-label">Reviewed</div>
                <div class="stat-value" id="reviewedCount">-</div>
            </div>
            <div class="stat">
                <div class="stat-label">Remaining</div>
                <div class="stat-value" id="remainingCount">-</div>
            </div>
            <div class="stat">
                <div class="stat-label">Keep</div>
                <div class="stat-value" id="keepCount" style="color: #4CAF50;">-</div>
            </div>
            <div class="stat">
                <div class="stat-label">Prose Poem</div>
                <div class="stat-value" id="proseCount" style="color: #2196F3;">-</div>
            </div>
            <div class="stat">
                <div class="stat-label">Delete</div>
                <div class="stat-value" id="deleteCount" style="color: #f44336;">-</div>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" id="progressBar"></div>
        </div>

        <div id="cardContainer">
            <div class="loading">Loading detections...</div>
        </div>
    </div>

    <script>
        let detections = [];
        let decisions = {};
        let currentIndex = 0;

        // Load data
        async function loadData() {
            const response = await fetch('/api/detections');
            const data = await response.json();
            detections = data.detections;
            decisions = data.decisions;
            renderCard();
            updateStats();
        }

        function renderCard() {
            if (currentIndex >= detections.length) {
                document.getElementById('cardContainer').innerHTML = `
                    <div class="card">
                        <h2 style="text-align: center; color: #4CAF50;">All Done!</h2>
                        <p style="text-align: center; margin-top: 20px;">
                            You've reviewed all ${detections.length} detections.
                        </p>
                    </div>
                `;
                return;
            }

            const detection = detections[currentIndex];
            const isGutenberg = detection.filename.toLowerCase().includes('gutenberg');
            const sourceClass = isGutenberg ? 'source-gutenberg' : 'source-scraper';
            const sourceName = isGutenberg ? 'Gutenberg' : 'Poetry Platform';

            // Read file and highlight long lines
            const lines = detection.full_text.split('\\n');
            let highlightedText = lines.map(line => {
                const len = line.trim().length;
                if (len > 400) {
                    return `<div class="very-long-line">${escapeHtml(line)}</div>`;
                } else if (len > 200) {
                    return `<div class="long-line">${escapeHtml(line)}</div>`;
                } else {
                    return escapeHtml(line);
                }
            }).join('\\n');

            document.getElementById('cardContainer').innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            ${detection.title}
                            <span class="source-badge ${sourceClass}">${sourceName}</span>
                        </div>
                        <div class="card-meta">
                            ${detection.author} • ${detection.filename}
                        </div>
                        <div class="card-meta" style="margin-top: 5px;">
                            Card ${currentIndex + 1} of ${detections.length}
                        </div>
                    </div>

                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-label">Max Line</div>
                            <div class="metric-value">${detection.max_length} chars</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Avg Line</div>
                            <div class="metric-value">${detection.avg_length} chars</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Total Lines</div>
                            <div class="metric-value">${detection.total_lines}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Long Lines (>200)</div>
                            <div class="metric-value">${detection.long_lines}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Very Long (>400)</div>
                            <div class="metric-value">${detection.very_long_lines}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Variation (CV)</div>
                            <div class="metric-value">${detection.cv}</div>
                        </div>
                    </div>

                    <div class="text-container" id="textContainer">
                        <pre>${highlightedText}</pre>
                    </div>

                    <div class="actions">
                        <button class="btn-nav" onclick="prev()">← Previous</button>
                        <button class="btn-keep" onclick="makeDecision('keep')">Keep (K)</button>
                        <button class="btn-prose" onclick="makeDecision('prose_poem')">Prose Poem (P)</button>
                        <button class="btn-delete" onclick="makeDecision('delete_file')">Delete (X)</button>
                        <button class="btn-skip" onclick="skip()">Skip (S)</button>
                        <button class="btn-nav" onclick="next()">Next →</button>
                    </div>

                    <div class="keyboard-hint">
                        K = Keep • P = Prose Poem • X = Delete • S = Skip • ← → = Navigate
                    </div>
                </div>
            `;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        async function makeDecision(decision) {
            const detection = detections[currentIndex];
            decisions[detection.filename] = decision;

            // Save decision
            await fetch('/api/decide', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    filename: detection.filename,
                    decision: decision
                })
            });

            updateStats();
            next();
        }

        function skip() {
            next();
        }

        function next() {
            if (currentIndex < detections.length - 1) {
                currentIndex++;
                renderCard();
            }
        }

        function prev() {
            if (currentIndex > 0) {
                currentIndex--;
                renderCard();
            }
        }

        function updateStats() {
            const reviewed = Object.keys(decisions).length;
            const remaining = detections.length - reviewed;
            const kept = Object.values(decisions).filter(d => d === 'keep').length;
            const prose = Object.values(decisions).filter(d => d === 'prose_poem').length;
            const deleted = Object.values(decisions).filter(d => d === 'delete_file').length;

            document.getElementById('totalCount').textContent = detections.length;
            document.getElementById('reviewedCount').textContent = reviewed;
            document.getElementById('remainingCount').textContent = remaining;
            document.getElementById('keepCount').textContent = kept;
            document.getElementById('proseCount').textContent = prose;
            document.getElementById('deleteCount').textContent = deleted;

            const progress = (reviewed / detections.length) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            if (e.key === 'k' || e.key === 'K') {
                makeDecision('keep');
            } else if (e.key === 'p' || e.key === 'P') {
                makeDecision('prose_poem');
            } else if (e.key === 'x' || e.key === 'X') {
                makeDecision('delete_file');
            } else if (e.key === 's' || e.key === 'S') {
                skip();
            } else if (e.key === 'ArrowLeft') {
                prev();
            } else if (e.key === 'ArrowRight') {
                next();
            }
        });

        // Load on start
        loadData();
    </script>
</body>
</html>
    '''

@app.route('/api/detections')
def get_detections():
    """Return all detections and existing decisions."""
    return jsonify({
        'detections': detections,
        'decisions': decisions
    })

@app.route('/api/decide', methods=['POST'])
def decide():
    """Save a decision."""
    data = request.json
    filename = data['filename']
    decision = data['decision']

    decisions[filename] = decision

    # Save to file
    with open(DECISIONS_FILE, 'w') as f:
        json.dump(decisions, f, indent=2)

    return jsonify({'success': True})

def load_detections():
    """Load all lineation issue detections."""
    global detections

    print("=" * 80)
    print("LINEATION ISSUE REVIEW INTERFACE")
    print("=" * 80)
    print(f"Loaded {len(decisions)} previous decisions")

    print("Loading detections...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    flagged = []
    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Processed {i:,}/{len(rows):,}...")

        filepath = get_file_path(row)
        if not filepath:
            continue

        result = analyze_lineation(filepath)
        if result:
            # Read full text
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    full_text = f.read()
            except:
                full_text = ""

            flagged.append({
                'filename': row['filename'],
                'title': row['title'],
                'author': row['author'],
                'full_text': full_text,
                **result
            })

    # Sort by severity (most severe first)
    flagged.sort(key=lambda x: (-x['max_length'], -x['long_lines']))

    detections = flagged

    print(f"✓ Loaded {len(detections):,} detections")
    print()
    print("=" * 80)
    print(f"Starting web interface on http://localhost:5003")
    print("=" * 80)
    print()
    print("Keyboard shortcuts:")
    print("  K - Keep (legitimate formatting)")
    print("  P - Prose poem (legitimate)")
    print("  X - Delete file (broken beyond repair)")
    print("  S - Skip to next")
    print("  ← - Previous card")
    print("  → - Next card")
    print()

if __name__ == '__main__':
    load_detections()
    app.run(debug=False, port=5003)
