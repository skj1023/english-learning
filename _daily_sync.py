"""Daily sync: vocab pending words + review note injection into lesson HTML files."""

import re
import os
import html
import subprocess
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(BASE_DIR, '_vocab_pending.md')
REVIEW_PATH = os.path.join(BASE_DIR, '_review_notes.md')
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
LESSONS_DIR = os.path.join(BASE_DIR, 'lessons')

BJT = timezone(timedelta(hours=8))

# ─── helpers ─────────────────────────────────────────────

def get_yesterday_bjt():
    return (datetime.now(BJT) - timedelta(days=1)).strftime('%Y-%m-%d')

def format_date_display(date_str):
    y, m, d = date_str.split('-')
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    return f"{months[int(m)-1]} {int(d)}, {y}"

# ─── VOCAB SYNC (original) ──────────────────────────────

def normalize_pending_line(line):
    line = line.strip()
    line = re.sub(r'^[-*]\s+', '', line)
    if not line:
        return '', ''
    # Allow Lance to write: hive — 蜂巢；a hive of activity...
    # Only the clean English headword goes into vocabBook/file names.
    parts = re.split(r'\s+[—–-]\s+|：|:', line, maxsplit=1)
    word = parts[0].strip().lower()
    note = parts[1].strip() if len(parts) > 1 else ''
    return word, note

def parse_pending_words(md_path):
    if not os.path.exists(md_path):
        return []
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    words = []
    current_date = None
    for line in content.split('\n'):
        raw = line.strip()
        date_match = re.match(r'^##\s*(\d{4}-\d{2}-\d{2})', raw)
        if date_match:
            current_date = date_match.group(1)
            continue
        if current_date and raw and not raw.startswith('#') and not raw.startswith('Words '):
            word, note = normalize_pending_line(raw)
            if word:
                words.append((current_date, word, note))
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

def word_in_array(content, word):
    if re.search(r"w:'"+re.escape(word)+r"'", content):
        return True
    if re.search(r"t:'"+re.escape(word)+r"'", content):
        return True
    return False

def js_escape(value):
    return value.replace('\\', '\\\\').replace("'", "\\'")

def filename_slug(word):
    slug = re.sub(r'[^a-z0-9]+', '_', word.lower()).strip('_')
    return slug or 'word'

def generate_wotd_html(word, date, note=""):
    name = word.capitalize()
    note_html = html.escape(note)
    y, m, d = date.split('-')
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    month_name = months[int(m)-1]
    filename = f'{date}_wotd_{filename_slug(word)}.html'
    filepath = os.path.join(LESSONS_DIR, filename)
    if os.path.exists(filepath):
        return filename
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Saved Vocabulary · {word}</title>
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
    <div class="label">Saved Vocabulary</div>
    <h1>{word}</h1>
    <div class="part-of-speech">saved word</div>
  </div>
  <div class="section">
    <div class="section-title"><span class="icon">📖</span> Definition</div>
    <div class="def-box">
      <p>This word was saved to your vocab book for review. A detailed note can be added later.</p>
      <p style="margin-top:6px;font-size:14px;color:#6c757d;">{note_html}</p>
    </div>
  </div>
  <div class="section">
    <div class="section-title"><span class="icon">✍️</span> Practice</div>
    <div class="task-box">
      <div class="task-title">Coming Soon</div>
      <p>Review <strong>{word}</strong> and try to use it in one sentence from your work or daily life.</p>
    </div>
  </div>
  <div class="footer">Echo · Vocab Book · {month_name} {d}, {y}</div>
</div>
</body>
</html>'''
    os.makedirs(LESSONS_DIR, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename

def sync_vocab():
    words = parse_pending_words(MD_PATH)
    if not words:
        print("No pending words found.")
        return False
    content = read_index(INDEX_PATH)
    changes = False
    new_entries = []
    for date, word, note in words:
        if word_in_array(content, word):
            print(f"  Already exists: {word}")
            continue
        new_entry = f"  {{w:'{js_escape(word)}',d:'{date}',m:0}}"
        new_entries.append((date, word, new_entry))
        filename = generate_wotd_html(word, date, note)
        changes = True
        print(f"  Added: {word} ({date})")
    if not changes:
        print("No new words to add.")
        return False
    for date, word, entry in reversed(new_entries):
        m = re.search(r'var vocabBook=\[', content)
        if m:
            start = m.start()
            depth = 1
            i = m.end()
            while i < len(content) and depth > 0:
                if content[i] == '[': depth += 1
                elif content[i] == ']': depth -= 1
                i += 1
            end = i - 1
            content = content[:end] + ',\n' + entry + content[end:]
    write_index(INDEX_PATH, content)
    print(f"Synced {len(new_entries)} word(s) to vocabBook.")
    clear_pending_md(MD_PATH)
    print("Cleared _vocab_pending.md")
    return True

# ─── PLACEHOLDER SYNC (03:00 fallback) ──────────────────

def find_yesterday_lessons(content, date):
    pattern = r"\{d:'" + re.escape(date) + r"',[^}]+?\}"
    matches = re.findall(pattern, content)
    result = []
    for m in matches:
        f = re.search(r"f:'([^']+)'", m)
        result.append({'file': f.group(1) if f else ''})
    return result

def file_has_review_note(filepath):
    if not os.path.exists(filepath):
        return True
    with open(filepath, 'r', encoding='utf-8') as f:
        return 'id="review-note"' in f.read()

def inject_placeholder(filepath, date):
    if not os.path.exists(filepath) or file_has_review_note(filepath):
        return False
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    display_date = format_date_display(date)
    note = f'''
<div class="section review-note" id="review-note">
  <div class="section-title"><span class="icon">📝</span> Review Note <span style="font-size:11px;color:#6c757d;font-weight:400;margin-left:6px;">&middot; {display_date}</span></div>
  <div class="task-box">
    <p>No review recorded for this session.</p>
    <p style="margin-top:6px;">&#128161; Consider revisiting this material and jotting down your key takeaways.</p>
  </div>
</div>'''
    content = content.replace('</body>', note + '\n\n</body>')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def sync_placeholders():
    yesterday = get_yesterday_bjt()
    print(f"\n=== Checking placeholders for {yesterday} ===")
    if not os.path.exists(INDEX_PATH):
        return False
    content = read_index(INDEX_PATH)
    items = find_yesterday_lessons(content, yesterday)
    changes = False
    for item in items:
        fp = os.path.normpath(os.path.join(BASE_DIR, item['file']))
        if inject_placeholder(fp, yesterday):
            print(f"  Placeholder: {item['file']}")
            changes = True
    if not changes:
        print("  All reviewed or no lessons found.")
    return changes

# ─── GIT PUSH ────────────────────────────────────────────

def git_push():
    try:
        subprocess.run(['git', 'add', '-A'], cwd=BASE_DIR, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'http.sslVerify=false', 'commit', '-m', 'chore: daily sync - vocab + review notes'],
                       cwd=BASE_DIR, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'http.sslVerify=false', '-c', 'http.sslBackend=openssl', '-c', 'http.version=HTTP/1.1', 'push'],
                       cwd=BASE_DIR, check=True, capture_output=True)
        print("Git push successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr.decode() if e.stderr else str(e)}")
        return False

# ─── MAIN ────────────────────────────────────────────────

def main():
    print("=== Daily Sync ===")
    v = sync_vocab()
    r = sync_placeholders()
    if v or r:
        print("\nPushing changes...")
        git_push()
    else:
        print("\nNothing to push.")

if __name__ == '__main__':
    main()
