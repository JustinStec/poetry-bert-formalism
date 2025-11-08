#!/usr/bin/env python3
"""
Web-based manual review interface for poetry attribution.
Much easier than command-line!
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import json
import os
from pathlib import Path

app = Flask(__name__)

# Paths
RESULTS_FILE = "/Users/justin/Repos/AI Project/scripts/ai_attribution_results.jsonl"
MANUAL_REVIEWS_FILE = "/Users/justin/Repos/AI Project/scripts/manual_reviews.jsonl"
CORPUS_DIR = "/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author"

# Load data
def load_results():
    results = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                results.append(json.loads(line.strip()))
    return results

def load_manual_reviews():
    reviews = []
    if os.path.exists(MANUAL_REVIEWS_FILE):
        with open(MANUAL_REVIEWS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                reviews.append(json.loads(line.strip()))
    return reviews

def save_review(review):
    with open(MANUAL_REVIEWS_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(review) + '\n')

def read_poem(file_path, max_lines=50):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()[:max_lines]
            return ''.join(lines)
    except Exception as e:
        return f"[Error reading file: {e}]"

def read_full_poem(file_path):
    """Read entire poem text without line limit."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]"

def get_available_authors():
    if os.path.exists(CORPUS_DIR):
        return sorted([d for d in os.listdir(CORPUS_DIR)
                      if os.path.isdir(os.path.join(CORPUS_DIR, d))])
    return []

# Global state
results = load_results()
manual_reviews = load_manual_reviews()
reviewed_ids = {r['poem_id'] for r in manual_reviews}
available_authors = get_available_authors()

# Filter poems to review
filter_type = 'unknown'  # Can change to 'error', 'low', 'all'
to_review = [r for r in results
             if r['poem_id'] not in reviewed_ids
             and r['author'] == 'Unknown']

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Poetry Attribution Review</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .progress {
            background: #e0e0e0;
            border-radius: 4px;
            height: 30px;
            margin: 10px 0;
            position: relative;
        }
        .progress-bar {
            background: #4CAF50;
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }
        .progress-text {
            position: absolute;
            width: 100%;
            text-align: center;
            line-height: 30px;
            font-weight: bold;
            color: #333;
        }
        .poem-card {
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .poem-meta {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            border-left: 4px solid #2196F3;
        }
        .poem-text {
            background: #fafafa;
            padding: 20px;
            border-radius: 4px;
            font-family: "Courier New", monospace;
            white-space: pre-wrap;
            max-height: 500px;
            overflow-y: auto;
            line-height: 1.6;
            border: 1px solid #ddd;
        }
        .actions {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            bottom: 20px;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s;
            flex: 1;
            min-width: 120px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .btn-junk {
            background: #f44336;
            color: white;
        }
        .btn-skip {
            background: #9E9E9E;
            color: white;
        }
        .btn-keep {
            background: #2196F3;
            color: white;
        }
        .btn-submit {
            background: #4CAF50;
            color: white;
        }
        .btn-split {
            background: #FF9800;
            color: white;
        }
        .split-form {
            background: #fff3e0;
            padding: 20px;
            border-radius: 4px;
            margin-top: 15px;
            border: 2px solid #FF9800;
            display: none;
        }
        .split-form.active {
            display: block;
        }
        .split-section {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            border-left: 4px solid #FF9800;
        }
        textarea {
            width: 100%;
            min-height: 300px;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-family: "Courier New", monospace;
            resize: vertical;
            font-size: 14px;
            line-height: 1.5;
        }
        .author-input {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #4CAF50;
        }
        .suggestions {
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 5px;
        }
        .suggestion-item {
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
        }
        .suggestion-item:hover {
            background: #f5f5f5;
        }
        .label {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 8px;
        }
        .label-high { background: #4CAF50; color: white; }
        .label-medium { background: #FF9800; color: white; }
        .label-low { background: #f44336; color: white; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-box {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 Poetry Attribution Review</h1>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{{ current + 1 }}</div>
                <div class="stat-label">Current Poem</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ total }}</div>
                <div class="stat-label">Total to Review</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ reviewed }}</div>
                <div class="stat-label">Already Reviewed</div>
            </div>
        </div>
        <div class="progress">
            <div class="progress-bar" style="width: {{ progress }}%"></div>
            <div class="progress-text">{{ progress }}% Complete</div>
        </div>
    </div>

    {% if poem %}
    <div class="poem-card">
        <div class="poem-meta">
            <h2>Poem #{{ poem.poem_id }}</h2>
            <p><strong>Current Folder:</strong> {{ poem.old_folder }}</p>
            <p><strong>GPT-4o Says:</strong> {{ poem.author }}
               <span class="label label-{{ poem.confidence }}">{{ poem.confidence }} confidence</span>
            </p>
            {% if poem.title and poem.title != 'Unknown' %}
            <p><strong>Title:</strong> {{ poem.title }}</p>
            {% endif %}
            <p><strong>File:</strong> {{ poem.file_path | basename }}</p>
            {% if poem.reasoning %}
            <p><strong>GPT-4o Reasoning:</strong> {{ poem.reasoning }}</p>
            {% endif %}
        </div>

        <h3>Poem Text (showing first 50 lines):</h3>
        <div class="poem-text" id="poem-display">{{ poem_text }}</div>

        <div class="btn-group" style="margin-top: 10px;">
            <button type="button" onclick="showFullText()" id="show-full-btn" class="btn" style="background: #2196F3; color: white;">
                📄 Show Full Text
            </button>
            <button type="button" onclick="enableEdit()" class="btn" style="background: #FF9800; color: white;">
                ✏️ Edit Text
            </button>
        </div>

        <div id="full-text" style="display: none;">
            <h3>Complete Poem Text:</h3>
            <div class="poem-text">{{ full_poem_text }}</div>
        </div>

        <div id="edit-text" style="display: none; margin-top: 15px;">
            <h3>Edit Poem Text:</h3>
            <textarea id="edited-text" style="width: 100%; min-height: 400px;">{{ full_poem_text }}</textarea>
            <div class="btn-group" style="margin-top: 10px;">
                <button type="button" onclick="saveEdit()" class="btn" style="background: #4CAF50; color: white;">
                    ✓ Save Edits
                </button>
                <button type="button" onclick="cancelEdit()" class="btn btn-skip">
                    Cancel
                </button>
            </div>
        </div>
    </div>

    <div class="actions">
        <h3>What should we do with this poem?</h3>

        <form method="POST" action="/review" id="review-form">
            <input type="hidden" name="poem_id" value="{{ poem.poem_id }}">
            <input type="hidden" name="edited_text" id="edited-text-input" value="">

            <div class="btn-group">
                <button type="submit" name="action" value="junk" class="btn btn-junk">
                    🗑️ Delete as Junk
                </button>
                <button type="submit" name="action" value="skip" class="btn btn-skip">
                    ⏭️ Skip for Now
                </button>
                <button type="submit" name="action" value="keep" class="btn btn-keep">
                    ✓ Keep in Current Folder
                </button>
                <button type="button" onclick="toggleSplit()" class="btn btn-split">
                    ✂️ Split into Multiple Poems
                </button>
            </div>

            <div class="author-input">
                <input type="text"
                       name="title"
                       id="title-input"
                       placeholder="Poem title (optional)"
                       style="flex: 1; margin-bottom: 10px;">
            </div>

            <div class="author-input">
                <input type="text"
                       name="author"
                       id="author-input"
                       placeholder="Author name (e.g., 'Robert Burns')"
                       list="authors"
                       autocomplete="off">
                <button type="submit" name="action" value="move" class="btn btn-submit">
                    → Assign to Author
                </button>
            </div>

            <datalist id="authors">
                {% for author in authors[:100] %}
                <option value="{{ author }}">
                {% endfor %}
            </datalist>
        </form>

        <!-- Split Form (hidden by default) -->
        <div class="split-form" id="split-form">
            <h3>✂️ Split into Multiple Poems</h3>
            <p><strong>Instructions:</strong> The full text is pre-loaded in Poem 1. Edit each textarea to isolate individual poems, then assign authors. The original file will be deleted and replaced with separate files for each poem.</p>

            <form method="POST" action="/split">
                <input type="hidden" name="poem_id" value="{{ poem.poem_id }}">

                <div id="split-sections">
                    <div class="split-section">
                        <h4>Poem 1</h4>
                        <input type="text" name="title_1" placeholder="Poem title (optional)" style="width: 100%; margin-bottom: 10px;">
                        <input type="text" name="author_1" placeholder="Author name" list="authors" style="width: 100%; margin-bottom: 10px;">
                        <textarea name="text_1" placeholder="Copy/paste the first poem text here...">{{ full_poem_text }}</textarea>
                    </div>
                    <div class="split-section">
                        <h4>Poem 2</h4>
                        <input type="text" name="title_2" placeholder="Poem title (optional)" style="width: 100%; margin-bottom: 10px;">
                        <input type="text" name="author_2" placeholder="Author name" list="authors" style="width: 100%; margin-bottom: 10px;">
                        <textarea name="text_2" placeholder="Copy/paste the second poem text here..."></textarea>
                    </div>
                </div>

                <div class="btn-group">
                    <button type="button" onclick="addSplitSection()" class="btn" style="background: #9E9E9E; color: white;">
                        + Add Another Poem
                    </button>
                    <button type="submit" class="btn btn-split">
                        ✂️ Save Split Poems
                    </button>
                    <button type="button" onclick="toggleSplit()" class="btn btn-skip">
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    </div>
    {% else %}
    <div class="poem-card">
        <h2>🎉 All Done!</h2>
        <p>You've reviewed all {{ filter_type }} poems!</p>
        <p>Great work! Check the results in <code>manual_reviews.jsonl</code></p>
        <a href="/stats" class="btn btn-submit">View Statistics</a>
    </div>
    {% endif %}

    <script>
        // Auto-focus on author input
        document.getElementById('author-input').focus();

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            if (e.key === 'j') {
                document.querySelector('[value="junk"]').click();
            } else if (e.key === 's') {
                document.querySelector('[value="skip"]').click();
            } else if (e.key === 'k') {
                document.querySelector('[value="keep"]').click();
            }
        });

        // Show full text
        function showFullText() {
            const fullText = document.getElementById('full-text');
            fullText.style.display = 'block';
            document.getElementById('show-full-btn').style.display = 'none';
        }

        // Edit text functionality
        let editedTextValue = null;

        function enableEdit() {
            document.getElementById('edit-text').style.display = 'block';
            document.getElementById('poem-display').style.display = 'none';
            document.getElementById('show-full-btn').style.display = 'none';
            window.scrollTo(0, document.getElementById('edit-text').offsetTop - 100);
        }

        function cancelEdit() {
            document.getElementById('edit-text').style.display = 'none';
            document.getElementById('poem-display').style.display = 'block';
            document.getElementById('show-full-btn').style.display = 'inline-block';
        }

        function saveEdit() {
            editedTextValue = document.getElementById('edited-text').value;
            document.getElementById('edited-text-input').value = editedTextValue;

            // Update display
            document.getElementById('poem-display').innerText = editedTextValue.substring(0, 2000) + '...';
            document.getElementById('edit-text').style.display = 'none';
            document.getElementById('poem-display').style.display = 'block';
            document.getElementById('show-full-btn').style.display = 'inline-block';

            // Show confirmation
            const editBtn = event.target;
            const originalText = editBtn.innerText;
            editBtn.innerText = '✓ Edits Saved!';
            editBtn.style.background = '#4CAF50';
            setTimeout(() => {
                editBtn.innerText = originalText;
                editBtn.style.background = '';
            }, 2000);
        }

        // Split form functions
        let splitCount = 2;

        function toggleSplit() {
            const splitForm = document.getElementById('split-form');
            splitForm.classList.toggle('active');
        }

        function addSplitSection() {
            splitCount++;
            const container = document.getElementById('split-sections');
            const newSection = document.createElement('div');
            newSection.className = 'split-section';
            newSection.innerHTML = `
                <h4>Poem ${splitCount}</h4>
                <input type="text" name="title_${splitCount}" placeholder="Poem title (optional)" style="width: 100%; margin-bottom: 10px;">
                <input type="text" name="author_${splitCount}" placeholder="Author name" list="authors" style="width: 100%; margin-bottom: 10px;">
                <textarea name="text_${splitCount}" placeholder="Paste poem text here..."></textarea>
            `;
            container.appendChild(newSection);
        }
    </script>
</body>
</html>
'''

STATS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Review Statistics</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f9f9f9;
            font-weight: 600;
        }
        .btn {
            padding: 12px 24px;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>📊 Review Statistics</h1>
        <p><strong>Total Reviewed:</strong> {{ total_reviewed }}</p>

        <h2>Actions Taken</h2>
        <table>
            <tr>
                <th>Action</th>
                <th>Count</th>
            </tr>
            {% for action, count in actions.items() %}
            <tr>
                <td>{{ action }}</td>
                <td>{{ count }}</td>
            </tr>
            {% endfor %}
        </table>

        {% if top_authors %}
        <h2>Top Attributed Authors</h2>
        <table>
            <tr>
                <th>Author</th>
                <th>Poems</th>
            </tr>
            {% for author, count in top_authors %}
            <tr>
                <td>{{ author }}</td>
                <td>{{ count }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}

        <br>
        <a href="/" class="btn">← Back to Review</a>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    global to_review, reviewed_ids, manual_reviews

    # Reload in case new reviews were added
    manual_reviews = load_manual_reviews()
    reviewed_ids = {r['poem_id'] for r in manual_reviews}
    to_review = [r for r in results
                 if r['poem_id'] not in reviewed_ids
                 and r['author'] == 'Unknown']

    if not to_review:
        return render_template_string(HTML_TEMPLATE,
                                     poem=None,
                                     current=0,
                                     total=0,
                                     reviewed=len(manual_reviews),
                                     progress=100,
                                     filter_type=filter_type)

    poem = to_review[0]
    poem_text = read_poem(poem['file_path'])
    full_poem_text = read_full_poem(poem['file_path'])

    return render_template_string(HTML_TEMPLATE,
                                 poem=poem,
                                 poem_text=poem_text,
                                 full_poem_text=full_poem_text,
                                 current=len(manual_reviews),
                                 total=len(to_review) + len(manual_reviews),
                                 reviewed=len(manual_reviews),
                                 progress=int(100 * len(manual_reviews) / (len(to_review) + len(manual_reviews))),
                                 authors=available_authors,
                                 filter_type=filter_type)

@app.route('/review', methods=['POST'])
def review():
    poem_id = request.form['poem_id']
    action = request.form['action']
    edited_text = request.form.get('edited_text', '').strip()
    title = request.form.get('title', '').strip()

    # Find the poem
    poem = next((r for r in to_review if r['poem_id'] == poem_id), None)
    if not poem:
        return redirect(url_for('index'))

    # Create review record
    review = {
        'poem_id': poem['poem_id'],
        'old_folder': poem['old_folder'],
        'file_path': poem['file_path'],
        'gpt4o_author': poem['author'],
        'gpt4o_confidence': poem['confidence'],
        'manual_action': action,
        'manual_author': '',
        'manual_title': title if title else None,
        'notes': '',
        'edited_text': edited_text if edited_text else None
    }

    if action == 'move':
        author = request.form.get('author', '').strip()
        if not author:
            return redirect(url_for('index'))
        review['manual_author'] = author

        # Handle text editing and/or title removal
        try:
            import re
            # Sanitize author name
            safe_author = re.sub(r'[<>:"/\\|?*]', '_', author)
            author_dir = os.path.join(CORPUS_DIR, safe_author)
            os.makedirs(author_dir, exist_ok=True)

            # Determine text to save
            if edited_text:
                text_to_save = edited_text
            elif title:
                # If title provided but no edit, read original and remove title
                text_to_save = read_full_poem(poem['file_path'])
            else:
                text_to_save = None

            # Remove title from text if provided
            if text_to_save and title:
                lines = text_to_save.split('\n')
                if lines and title.lower() in lines[0].lower():
                    text_to_save = '\n'.join(lines[1:]).lstrip()

            # Write text if modified
            if text_to_save:
                with open(poem['file_path'], 'w', encoding='utf-8') as f:
                    f.write(text_to_save)
        except Exception as e:
            review['notes'] = f'Error saving text: {e}'

    elif action == 'junk':
        review['manual_author'] = 'JUNK'
    elif action == 'keep':
        review['manual_author'] = poem['old_folder']

        # Handle text editing and/or title removal
        try:
            # Determine text to save
            if edited_text:
                text_to_save = edited_text
            elif title:
                # If title provided but no edit, read original and remove title
                text_to_save = read_full_poem(poem['file_path'])
            else:
                text_to_save = None

            # Remove title from text if provided
            if text_to_save and title:
                lines = text_to_save.split('\n')
                if lines and title.lower() in lines[0].lower():
                    text_to_save = '\n'.join(lines[1:]).lstrip()

            # Write text if modified
            if text_to_save:
                with open(poem['file_path'], 'w', encoding='utf-8') as f:
                    f.write(text_to_save)
        except Exception as e:
            review['notes'] = f'Error saving text: {e}'

    elif action == 'skip':
        review['manual_action'] = 'skip'
        # Don't save skips
        return redirect(url_for('index'))

    # Save review
    save_review(review)

    return redirect(url_for('index'))

@app.route('/split', methods=['POST'])
def split_poems():
    poem_id = request.form['poem_id']

    # Find the original poem
    poem = next((r for r in to_review if r['poem_id'] == poem_id), None)
    if not poem:
        return redirect(url_for('index'))

    # Extract all the split poems from form data
    splits = []
    i = 1
    while f'author_{i}' in request.form:
        author = request.form.get(f'author_{i}', '').strip()
        text = request.form.get(f'text_{i}', '').strip()
        title = request.form.get(f'title_{i}', '').strip()

        if author and text:
            splits.append({
                'author': author,
                'text': text,
                'title': title if title else None,
                'section': i
            })
        i += 1

    if len(splits) < 2:
        # Need at least 2 poems to split
        return redirect(url_for('index'))

    # Create new files for each split
    import time
    import re
    timestamp = int(time.time())

    for idx, split in enumerate(splits, 1):
        # Sanitize author name for filesystem
        author = split['author']
        if not author or author.lower() in ['n/a', 'na', 'unknown', '']:
            author = 'Unknown'

        # Remove invalid filesystem characters
        safe_author = re.sub(r'[<>:"/\\|?*]', '_', author)
        safe_author = safe_author.strip()

        new_poem_id = f"{poem_id}_split{idx}_{timestamp}"
        author_dir = os.path.join(CORPUS_DIR, safe_author)
        os.makedirs(author_dir, exist_ok=True)

        # Create filename
        filename = f"{new_poem_id}_{safe_author.replace(' ', '_')}_split{idx}.txt"
        filepath = os.path.join(author_dir, filename)

        # Remove title from text if provided
        text_to_save = split['text']
        if split.get('title'):
            # Remove title from beginning of text (case-insensitive)
            lines = text_to_save.split('\n')
            if lines and split['title'].lower() in lines[0].lower():
                text_to_save = '\n'.join(lines[1:]).lstrip()

        # Write poem text
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_to_save)

    # Save review record for the original (now split)
    review = {
        'poem_id': poem['poem_id'],
        'old_folder': poem['old_folder'],
        'file_path': poem['file_path'],
        'gpt4o_author': poem['author'],
        'gpt4o_confidence': poem['confidence'],
        'manual_action': 'split',
        'manual_author': f"SPLIT into {len(splits)} poems: " + ", ".join(s['author'] for s in splits),
        'manual_title': [{'author': s['author'], 'title': s['title']} for s in splits],
        'notes': f'Original file split into {len(splits)} separate poems'
    }

    save_review(review)

    return redirect(url_for('index'))

@app.route('/stats')
def stats():
    reviews = load_manual_reviews()

    from collections import Counter
    actions = Counter(r['manual_action'] for r in reviews)

    top_authors = Counter(r['manual_author'] for r in reviews
                         if r['manual_action'] == 'move').most_common(20)

    return render_template_string(STATS_TEMPLATE,
                                 total_reviewed=len(reviews),
                                 actions=dict(actions),
                                 top_authors=top_authors)

@app.template_filter('basename')
def basename_filter(path):
    return os.path.basename(path)

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 Starting Poetry Review Web Interface")
    print("="*80)
    print(f"\nReview mode: {filter_type}")
    print(f"Poems to review: {len(to_review):,}")
    print(f"Already reviewed: {len(manual_reviews):,}")
    print("\n📱 Open in your browser:")
    print("   http://localhost:5001")
    print("\n⌨️  Keyboard shortcuts:")
    print("   j - Mark as junk")
    print("   s - Skip")
    print("   k - Keep")
    print("\nPress Ctrl+C to stop the server")
    print("="*80 + "\n")

    app.run(debug=True, port=5001, host='0.0.0.0')
