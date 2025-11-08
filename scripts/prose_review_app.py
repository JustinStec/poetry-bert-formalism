#!/usr/bin/env python3
"""
Web interface for reviewing prose commentary detections.
Card carousel with full text display and highlighting.
"""

from flask import Flask, render_template_string, jsonify, request
import json
import csv
from pathlib import Path

app = Flask(__name__)

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
DECISIONS_FILE = Path("/Users/justin/Repos/AI Project/scripts/prose_review_decisions.json")

# Global storage for detection results
DETECTIONS = []
DECISIONS = {}

def get_file_path(row):
    """Get full file path from metadata row."""
    filename = row['filename']

    if 'gutenberg' in filename.lower():
        for author_dir in GUTENBERG_DIR.iterdir():
            if author_dir.is_dir():
                test_path = author_dir / filename
                if test_path.exists():
                    return test_path
    else:
        author = row['author']
        filepath = POETRY_PLATFORM_DIR / author / filename
        if filepath.exists():
            return filepath

    return None

def load_detections():
    """Load detection results."""
    print("Loading detections...")

    from detect_prose_commentary import analyze_file

    # Load metadata
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Run detection
    detections = []
    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Processed {i:,}/{len(rows):,}...")

        result = analyze_file(row)
        if result:
            # Load full file text
            try:
                with open(result['filepath'], 'r', encoding='utf-8') as f:
                    full_text = f.read()
                result['full_text'] = full_text
                # Convert filepath to string for JSON serialization
                result['filepath'] = str(result['filepath'])
                detections.append(result)
            except:
                pass

    print(f"✓ Loaded {len(detections)} detections")
    return detections

def load_decisions():
    """Load previous decisions if they exist."""
    if DECISIONS_FILE.exists():
        with open(DECISIONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_decisions():
    """Save decisions to file."""
    with open(DECISIONS_FILE, 'w') as f:
        json.dump(DECISIONS, f, indent=2)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Prose Commentary Review</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .progress {
            background: #333;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px auto;
            max-width: 600px;
        }

        .progress-bar {
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            height: 100%;
            transition: width 0.3s;
        }

        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin: 20px 0;
            font-size: 14px;
            color: #999;
        }

        .stat {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .stat-value {
            font-weight: bold;
            color: #4CAF50;
            font-size: 18px;
        }

        .card {
            max-width: 1200px;
            margin: 0 auto;
            background: #2a2a2a;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .card-header {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px solid #3a3a3a;
        }

        .card-title {
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 8px;
        }

        .card-author {
            font-size: 18px;
            color: #999;
            margin-bottom: 15px;
        }

        .card-meta {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #666;
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

        .text-container::-webkit-scrollbar {
            width: 10px;
        }

        .text-container::-webkit-scrollbar-track {
            background: #2a2a2a;
            border-radius: 5px;
        }

        .text-container::-webkit-scrollbar-thumb {
            background: #4a4a4a;
            border-radius: 5px;
        }

        .text-container::-webkit-scrollbar-thumb:hover {
            background: #5a5a5a;
        }

        .verse-text {
            white-space: pre-wrap;
            color: #e0e0e0;
        }

        .prose-text {
            white-space: pre-wrap;
            background: rgba(255, 152, 0, 0.15);
            border-left: 4px solid #ff9800;
            padding-left: 15px;
            margin-left: -15px;
            color: #ffb74d;
            position: relative;
        }

        .boundary-divider {
            position: absolute;
            top: -8px;
            left: -15px;
            right: 0;
            height: 16px;
            background: linear-gradient(to bottom, transparent, #ff9800, transparent);
            cursor: ns-resize;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
        }

        .boundary-divider:hover {
            background: linear-gradient(to bottom, rgba(255, 152, 0, 0.3), #ff9800, rgba(255, 152, 0, 0.3));
        }

        .boundary-divider::after {
            content: '⋮⋮⋮';
            color: #ff9800;
            font-weight: bold;
            font-size: 16px;
            letter-spacing: 2px;
        }

        .prose-label {
            display: inline-block;
            background: #ff9800;
            color: #000;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin: 15px 0 5px 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        .boundary-controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #1e1e1e;
            border-radius: 8px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }

        .boundary-info {
            font-size: 14px;
            color: #999;
            padding: 0 20px;
        }

        .btn-boundary {
            background: #444;
            color: white;
            padding: 8px 20px;
            font-size: 14px;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-boundary:hover {
            background: #555;
            transform: translateY(-1px);
        }

        .actions {
            display: flex;
            gap: 15px;
            justify-content: center;
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
            background: #66BB6A;
        }

        .btn-discard {
            background: #f44336;
            color: white;
        }

        .btn-discard:hover {
            background: #ef5350;
        }

        .btn-delete-file {
            background: #9c27b0;
            color: white;
        }

        .btn-delete-file:hover {
            background: #ab47bc;
        }

        .btn-multi-poem {
            background: #00acc1;
            color: white;
        }

        .btn-multi-poem:hover {
            background: #00bcd4;
        }

        .btn-skip {
            background: #666;
            color: white;
        }

        .btn-skip:hover {
            background: #777;
        }

        .navigation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #3a3a3a;
        }

        .btn-nav {
            background: #444;
            color: white;
            padding: 10px 20px;
            min-width: 100px;
        }

        .btn-nav:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }

        .card-number {
            font-size: 14px;
            color: #999;
        }

        .completion {
            text-align: center;
            padding: 60px 20px;
        }

        .completion h2 {
            font-size: 32px;
            margin-bottom: 20px;
            color: #4CAF50;
        }

        .completion p {
            font-size: 18px;
            color: #999;
            margin-bottom: 30px;
        }

        .btn-export {
            background: #2196F3;
            color: white;
            padding: 15px 40px;
        }

        .btn-export:hover {
            background: #42A5F5;
        }

        .loading {
            text-align: center;
            padding: 60px 20px;
            font-size: 18px;
            color: #999;
        }

        .keyboard-hint {
            text-align: center;
            margin-top: 15px;
            font-size: 12px;
            color: #666;
        }

        .keyboard-hint kbd {
            background: #3a3a3a;
            padding: 3px 8px;
            border-radius: 3px;
            font-family: monospace;
            margin: 0 3px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Prose Commentary Review</h1>
        <div class="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        <div class="stats">
            <div class="stat">
                <span>Reviewed:</span>
                <span class="stat-value" id="reviewedCount">0</span>
            </div>
            <div class="stat">
                <span>Remaining:</span>
                <span class="stat-value" id="remainingCount">0</span>
            </div>
            <div class="stat">
                <span>Keep:</span>
                <span class="stat-value" id="keepCount" style="color: #4CAF50;">0</span>
            </div>
            <div class="stat">
                <span>Discard:</span>
                <span class="stat-value" id="discardCount" style="color: #f44336;">0</span>
            </div>
            <div class="stat">
                <span>Delete File:</span>
                <span class="stat-value" id="deleteCount" style="color: #9c27b0;">0</span>
            </div>
            <div class="stat">
                <span>Multi-Poem:</span>
                <span class="stat-value" id="multiPoemCount" style="color: #00acc1;">0</span>
            </div>
        </div>
    </div>

    <div id="cardContainer"></div>

    <script>
        let currentIndex = 0;
        let detections = [];
        let decisions = {};
        let customBoundaries = {};  // Track custom prose_start for each file

        // Load data on startup
        async function loadData() {
            const container = document.getElementById('cardContainer');
            container.innerHTML = '<div class="loading">Loading detections...</div>';

            const response = await fetch('/api/detections');
            const data = await response.json();

            detections = data.detections;
            decisions = data.decisions;

            // Find first unreviewed
            currentIndex = detections.findIndex(d => !decisions[d.filename]);
            if (currentIndex === -1) currentIndex = 0;

            renderCard();
        }

        function renderCard() {
            const container = document.getElementById('cardContainer');

            if (currentIndex >= detections.length) {
                showCompletion();
                return;
            }

            const detection = detections[currentIndex];
            const decision = decisions[detection.filename] || null;

            // Split text into verse and prose
            const fullText = detection.full_text;
            const lines = fullText.split('\\n');

            // Use custom boundary if set, otherwise use detected boundary
            const proseStart = customBoundaries[detection.filename] !== undefined
                ? customBoundaries[detection.filename]
                : detection.prose_start;

            const verseLines = lines.slice(0, proseStart);
            const proseLines = lines.slice(proseStart);

            const verseText = verseLines.join('\\n');
            const proseText = proseLines.join('\\n');

            // Determine source
            const isGutenberg = detection.filename.toLowerCase().includes('gutenberg');
            const sourceClass = isGutenberg ? 'source-gutenberg' : 'source-scraper';
            const sourceName = isGutenberg ? 'Gutenberg' : 'Poetry Platform';

            container.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            ${escapeHtml(detection.title)}
                            <span class="source-badge ${sourceClass}">${sourceName}</span>
                        </div>
                        <div class="card-author">${escapeHtml(detection.author)}</div>
                        <div class="card-meta">
                            <span>📄 ${escapeHtml(detection.filename)}</span>
                            <span>📏 Verse avg: ${detection.avg_verse_length} chars</span>
                            <span>📏 Prose avg: ${detection.avg_prose_length} chars</span>
                            <span>🗑️ ${detection.lines_removed} lines to remove</span>
                        </div>
                    </div>

                    <div class="text-container" id="textContainer">
                        <div class="verse-text">${escapeHtml(verseText)}</div>
                        <div class="prose-text" id="proseSection">
                            <div class="boundary-divider" id="boundaryDivider"></div>
                            ${escapeHtml(proseText)}
                        </div>
                    </div>

                    <div class="boundary-controls">
                        <button class="btn-boundary" onclick="adjustBoundary(-1)" title="Move boundary up (include less prose)">
                            ▲ Move Up
                        </button>
                        <span class="boundary-info">Prose starts at line ${proseStart + 1}</span>
                        <button class="btn-boundary" onclick="adjustBoundary(1)" title="Move boundary down (include more prose)">
                            ▼ Move Down
                        </button>
                    </div>

                    <div class="actions">
                        <button class="btn-keep" onclick="makeDecision('keep')">
                            ✓ Keep Prose
                        </button>
                        <button class="btn-discard" onclick="makeDecision('discard')">
                            ✗ Remove Prose
                        </button>
                        <button class="btn-delete-file" onclick="makeDecision('delete_file')">
                            🗑️ Delete File
                        </button>
                        <button class="btn-multi-poem" onclick="makeDecision('multi_poem')">
                            📚 Multiple Poems
                        </button>
                        <button class="btn-skip" onclick="skip()">
                            → Skip
                        </button>
                    </div>

                    <div class="navigation">
                        <button class="btn-nav" onclick="prev()" ${currentIndex === 0 ? 'disabled' : ''}>
                            ← Previous
                        </button>
                        <span class="card-number">
                            ${currentIndex + 1} / ${detections.length}
                        </span>
                        <button class="btn-nav" onclick="next()" ${currentIndex >= detections.length - 1 ? 'disabled' : ''}>
                            Next →
                        </button>
                    </div>

                    <div class="keyboard-hint">
                        Keyboard: <kbd>K</kbd> Keep · <kbd>D</kbd> Discard · <kbd>X</kbd> Delete · <kbd>M</kbd> Multi-Poem · <kbd>S</kbd> Skip · <kbd>←</kbd> Previous · <kbd>→</kbd> Next
                    </div>
                </div>
            `;

            updateStats();

            // Auto-scroll to prose section after rendering
            requestAnimationFrame(() => {
                const proseSection = document.getElementById('proseSection');
                if (proseSection) {
                    // Scroll to show some context before the prose (about 3 lines up)
                    const container = document.getElementById('textContainer');
                    if (container) {
                        const proseTop = proseSection.offsetTop;
                        // Scroll to show a bit of verse context before the prose
                        container.scrollTop = Math.max(0, proseTop - 100);
                    }
                }
            });

            // Setup drag functionality for boundary divider
            setupBoundaryDrag();
        }

        function setupBoundaryDrag() {
            const divider = document.getElementById('boundaryDivider');
            const container = document.getElementById('textContainer');
            if (!divider || !container) return;

            let isDragging = false;
            let startY = 0;

            divider.addEventListener('mousedown', (e) => {
                isDragging = true;
                startY = e.clientY;
                divider.style.background = 'linear-gradient(to bottom, rgba(255, 152, 0, 0.5), #ff9800, rgba(255, 152, 0, 0.5))';
                e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;

                const detection = detections[currentIndex];
                const fullText = detection.full_text;
                const lines = fullText.split('\\n');

                // Calculate which line we're over based on mouse position
                // Require 60px of movement per line to make it less sensitive
                const deltaY = e.clientY - startY;
                const linesMoved = Math.round(deltaY / 60);

                if (linesMoved === 0) return;

                // Get current boundary
                let currentBoundary = customBoundaries[detection.filename] !== undefined
                    ? customBoundaries[detection.filename]
                    : detection.prose_start;

                // Calculate new boundary
                let newBoundary = currentBoundary + linesMoved;
                newBoundary = Math.max(1, Math.min(lines.length - 1, newBoundary));

                if (newBoundary !== currentBoundary) {
                    // Save current scroll position
                    const scrollPos = container.scrollTop;

                    // Update boundary
                    customBoundaries[detection.filename] = newBoundary;
                    startY = e.clientY; // Reset start position

                    // Re-render
                    renderCard();

                    // Restore scroll
                    requestAnimationFrame(() => {
                        requestAnimationFrame(() => {
                            requestAnimationFrame(() => {
                                const newContainer = document.getElementById('textContainer');
                                if (newContainer) {
                                    newContainer.scrollTop = scrollPos;
                                }
                            });
                        });
                    });
                }
            });

            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    const newDivider = document.getElementById('boundaryDivider');
                    if (newDivider) {
                        newDivider.style.background = '';
                    }
                }
            });
        }

        async function makeDecision(decision) {
            const detection = detections[currentIndex];
            const customBoundary = customBoundaries[detection.filename];

            decisions[detection.filename] = {
                decision: decision,
                custom_boundary: customBoundary
            };

            // Save decision
            await fetch('/api/decide', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    filename: detection.filename,
                    decision: decision,
                    custom_boundary: customBoundary
                })
            });

            // Move to next unreviewed
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

        function adjustBoundary(direction) {
            const detection = detections[currentIndex];
            const fullText = detection.full_text;
            const lines = fullText.split('\\n');

            // Save current scroll position
            const textContainer = document.getElementById('textContainer');
            if (!textContainer) return;

            const scrollPos = textContainer.scrollTop;

            // Get current boundary
            let currentBoundary = customBoundaries[detection.filename] !== undefined
                ? customBoundaries[detection.filename]
                : detection.prose_start;

            // Adjust boundary
            let newBoundary = currentBoundary + direction;

            // Constrain to valid range (at least 1 line of verse, at least 1 line of prose)
            newBoundary = Math.max(1, Math.min(lines.length - 1, newBoundary));

            // If no change, return
            if (newBoundary === currentBoundary) return;

            // Save custom boundary
            customBoundaries[detection.filename] = newBoundary;

            // Re-render the card
            renderCard();

            // Force restore scroll position after all rendering is complete
            // Use multiple RAF to ensure DOM is fully updated
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        const newTextContainer = document.getElementById('textContainer');
                        if (newTextContainer) {
                            newTextContainer.scrollTop = scrollPos;
                        }
                    });
                });
            });
        }

        function updateStats() {
            const reviewed = Object.keys(decisions).length;
            const remaining = detections.length - reviewed;
            const kept = Object.values(decisions).filter(d => d.decision === 'keep').length;
            const discarded = Object.values(decisions).filter(d => d.decision === 'discard').length;
            const deleted = Object.values(decisions).filter(d => d.decision === 'delete_file').length;
            const multiPoem = Object.values(decisions).filter(d => d.decision === 'multi_poem').length;

            document.getElementById('reviewedCount').textContent = reviewed;
            document.getElementById('remainingCount').textContent = remaining;
            document.getElementById('keepCount').textContent = kept;
            document.getElementById('discardCount').textContent = discarded;
            document.getElementById('deleteCount').textContent = deleted;
            document.getElementById('multiPoemCount').textContent = multiPoem;

            const progress = (reviewed / detections.length) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
        }

        function showCompletion() {
            const kept = Object.values(decisions).filter(d => d.decision === 'keep').length;
            const discarded = Object.values(decisions).filter(d => d.decision === 'discard').length;
            const deleted = Object.values(decisions).filter(d => d.decision === 'delete_file').length;
            const multiPoem = Object.values(decisions).filter(d => d.decision === 'multi_poem').length;

            document.getElementById('cardContainer').innerHTML = `
                <div class="card completion">
                    <h2>🎉 Review Complete!</h2>
                    <p>
                        You've reviewed all ${detections.length} detections.<br>
                        <strong>${kept}</strong> kept · <strong>${discarded}</strong> prose removed · <strong>${deleted}</strong> files deleted · <strong>${multiPoem}</strong> multi-poem files
                    </p>
                    <button class="btn-export" onclick="exportDecisions()">
                        Export Decisions
                    </button>
                </div>
            `;

            updateStats();
        }

        async function exportDecisions() {
            const response = await fetch('/api/export');
            const data = await response.json();

            alert('Decisions saved to: ' + data.file);
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            if (e.key === 'k' || e.key === 'K') {
                makeDecision('keep');
            } else if (e.key === 'd' || e.key === 'D') {
                makeDecision('discard');
            } else if (e.key === 'x' || e.key === 'X') {
                makeDecision('delete_file');
            } else if (e.key === 'm' || e.key === 'M') {
                makeDecision('multi_poem');
            } else if (e.key === 's' || e.key === 'S') {
                skip();
            } else if (e.key === 'ArrowLeft') {
                prev();
            } else if (e.key === 'ArrowRight') {
                next();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault(); // Prevent page scrolling
                adjustBoundary(-1);
            } else if (e.key === 'ArrowDown') {
                e.preventDefault(); // Prevent page scrolling
                adjustBoundary(1);
            }
        });

        // Load on startup
        loadData();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/detections')
def get_detections():
    return jsonify({
        'detections': DETECTIONS,
        'decisions': DECISIONS
    })

@app.route('/api/decide', methods=['POST'])
def make_decision():
    data = request.json
    filename = data['filename']
    decision = data['decision']
    custom_boundary = data.get('custom_boundary')

    DECISIONS[filename] = {
        'decision': decision,
        'custom_boundary': custom_boundary
    }
    save_decisions()

    return jsonify({'status': 'ok'})

@app.route('/api/export')
def export_decisions():
    save_decisions()
    return jsonify({
        'file': str(DECISIONS_FILE),
        'decisions': DECISIONS
    })

if __name__ == '__main__':
    print("=" * 80)
    print("PROSE COMMENTARY REVIEW INTERFACE")
    print("=" * 80)

    # Load previous decisions
    DECISIONS = load_decisions()
    print(f"Loaded {len(DECISIONS)} previous decisions")

    # Load detections
    DETECTIONS = load_detections()

    print("\n" + "=" * 80)
    print(f"Starting web interface on http://localhost:5002")
    print("=" * 80)
    print("\nKeyboard shortcuts:")
    print("  K - Keep prose")
    print("  D - Discard prose (remove)")
    print("  S - Skip to next")
    print("  ← - Previous card")
    print("  → - Next card")
    print("\n")

    app.run(host='127.0.0.1', port=5002, debug=False)
