"""Daily vocab sync: read _vocab_pending.md, update vocabBook in index.html, clear markdown."""

import re
import os
import subprocess
import sys
from datetime import datetime

MD_PATH = os.path.join(os.path.dirname(__file__), '_vocab_pending.md')
INDEX_PATH = os.path.join(os.path.dirname(__file__), 'index.html')
LESSONS_DIR = os.path.join(os.path.dirname(__file__), 'lessons')

def parse_pending_words(md_path):
    """Parse _vocab_pending.md, return list of (date, word) tuples."""
    if not os.path.exists(md_path):
        return []
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    words = []
    current_date = None
    for line in content.split('\n'):
        line = line.strip()
        # Match date headings like "## 2026-07-13"
        date_match = re.match(r'^##\s*(\d{4}-\d{2}-\d{2})', line)
        if date_match:
            current_date = date_match.group(1)
            continue
        # Match word lines (non-empty, not a comment/heading)
        if current_date and line and not line.startswith('#') and not line.startswith('- ') and not line.startswith('Words '):
            words.append((current_date, line.lower().strip()))
    return words

def read_index(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_index(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def clear_pending_md(path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('# Vocab Book - Pending Words\n\nWords added by Lance that have not been synced yet.\n\n')

def find_vocabbook_array(content):
    """Find the vocabBook array and return its start/end positions."""
    m = re.search(r'var vocabBook=\[', content)
    if not m:
        return None
    start = m.start()
    # Find matching closing bracket
    depth = 1
    i = m.end()
    while i < len(content) and depth > 0:
        if content[i] == '[':
            depth += 1
        elif content[i] == ']':
            depth -= 1
        i += 1
    end = i
    return start, end

def word_in_array(content, word):
    """Check if word already exists in vocabBook or lessons array."""
    # Check vocabBook
    if re.search(r"w:'"+re.escape(word)+r"'", content):
        return True
    # Check lessons
    if re.search(r"t:'"+re.escape(word)+r"'", content):
        return True
    return False

def generate_wotd_html(word, date):
    """Generate a basic WOTD HTML file for the word."""
    name = word.capitalize()
    y, m, d = date.split('-')
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    month_name = months[int(m)-1]
    filename = f'{date}_wotd_{word}.html'
    filepath = os.path.join(LESSONS_DIR, filename)

    if os.path.exists(filepath):
        # Use existing file
        return filename

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Word of the Day · {word}</title>
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;font-size:16px;line-height:1.7;color:#1a1a2e;background:#f8f9fa;padding:0;-webkit-font-smoothing:antialiased}}
  .container{{max-width:640px;margin:0 auto;padding:20px 16px 60px}}
  .header{{text-align:center;padding:28px 0 20px;border-bottom:2px solid #e9ecef;margin-bottom:20px}}
  .header .label{{font-size:12px;font-weight:600;color:#6c757d;text-transform:uppercase;letter-spacing:1px}}
  .header h1{{font-size:32px;font-weight:800;color:#1a1a2e;margin:4px 0 2px}}
  .header .ipa{{font-size:15px;color:#6c757d;font-weight:400}}
  .header .part-of-speech{{font-size:14px;color:#4a90d9;font-weight:600;margin-top:4px}}
  .section{{background:#fff;border-radius:12px;padding:18px 16px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}}
  .section-title{{font-size:15px;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:8px;color:#1a1a2e}}
  .section-title .icon{{font-size:18px}}
  .def-box{{background:#f8f9fa;border-radius:8px;padding:12px 14px}}
  .example-box{{border-left:3px solid #e53935;background:#fff5f5;padding:12px 14px;margin-bottom:8px;border-radius:0 8px 8px 0}}
  .example-box .en{{font-size:15px}}
  .example-box .highlight{{color:#e53935;font-weight:600}}
  .task-box{{background:#fff8e1;border:1px solid #ffe082;border-radius:10px;padding:14px 16px}}
  .task-box .task-title{{font-weight:700;color:#e65100;font-size:14px;margin-bottom:8px}}
  .footer{{text-align:center;padding:20px 0;font-size:12px;color:#adb5bd}}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="label">Word of the Day</div>
    <h1>{word}</h1>
    <div class="part-of-speech">verb</div>
  </div>
  <div class="section">
    <div class="section-title"><span class="icon">📖</span> Definition</div>
    <div class="def-box">
      <p>Definition pending. This word was added to your vocab book for review.</p>
    </div>
  </div>
  <div class="section">
    <div class="section-title"><span class="icon">✍️</span> Practice</div>
    <div class="task-box">
      <div class="task-title">Coming Soon</div>
      <p>A full lesson for <strong>{word}</strong> will be generated soon. For now, review the word's meaning and try to use it in a sentence.</p>
    </div>
  </div>
  <div class="footer">Echo · Word of the Day · {month_name} {d}, {y}</div>
</div>
</body>
</html>'''

    os.makedirs(LESSONS_DIR, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename

def sync():
    words = parse_pending_words(MD_PATH)
    if not words:
        print("No pending words found.")
        return

    content = read_index(INDEX_PATH)
    changes = False
    new_entries = []

    for date, word in words:
        if word_in_array(content, word):
            print(f"  Already exists: {word}")
            continue
        # Add to vocabBook
        new_entry = f"  {{w:'{word}',d:'{date}',m:0}}"
        new_entries.append((date, word, new_entry))
        # Generate WOTD HTML
        filename = generate_wotd_html(word, date)
        changes = True
        print(f"  Added: {word} ({date})")

    if not changes:
        print("No new words to add.")
        return

    # Insert new entries into vocabBook array
    for date, word, entry in reversed(new_entries):
        # Find the closing ] of vocabBook
        m = re.search(r'var vocabBook=\[', content)
        if m:
            start = m.start()
            depth = 1
            i = m.end()
            while i < len(content) and depth > 0:
                if content[i] == '[': depth += 1
                elif content[i] == ']': depth -= 1
                i += 1
            end = i - 1  # position of ]
            # Insert before the closing ]
            content = content[:end] + ',\n' + entry + content[end:]

    write_index(INDEX_PATH, content)
    print(f"\nSynced {len(new_entries)} word(s) to vocabBook.")

    # Clear pending markdown
    clear_pending_md(MD_PATH)
    print("Cleared _vocab_pending.md")

    # Git commit and push
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        subprocess.run(['git', 'add', '-A'], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'http.sslVerify=false', 'commit', '-m', f'chore: sync {len(new_entries)} word(s) to vocab book'],
                       cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'http.sslVerify=false', '-c', 'http.sslBackend=openssl', '-c', 'http.version=HTTP/1.1', 'push'],
                       cwd=repo_dir, check=True, capture_output=True)
        print("Git push successful.")
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr.decode() if e.stderr else str(e)}")

if __name__ == '__main__':
    sync()
