"""Daily sync: vocab pending words + review note injection into lesson HTML files."""

import re
import os
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

def parse_pending_words(md_path):
    if not os.path.exists(md_path):
        return []
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    words = []
    current_date = None
    for line in content.split('\n'):
        line = line.strip()
        date_match = re.match(r'^##\s*(\d{4}-\d{2}-\d{2})', line)
        if date_match:
            current_date = date_match.group(1)
            continue
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

def word_in_array(content, word):
    if re.search(r"w:'"+re.escape(word)+r"'", content):
        return True
    if re.search(r"t:'"+re.escape(word)+r"'", content):
        return True
    return False

def generate_wotd_html(word, date):
    name = word.capitalize()
    y, m, d = date.split('-')
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    month_name = months[int(m)-1]
    filename = f'{date}_wotd_{word}.html'
    filepath = os.path.join(LESSONS_DIR, filename)
    if os.path.exists(filepath):
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

def sync_vocab():
    words = parse_pending_words(MD_PATH)
    if not words:
        print("No pending words found.")
        return False
    content = read_index(INDEX_PATH)
    changes = False
    new_entries = []
    for date, word in words:
        if word_in_array(content, word):
            print(f"  Already exists: {word}")
            continue
        new_entry = f"  {{w:'{word}',d:'{date}',m:0}}"
        new_entries.append((date, word, new_entry))
        filename = generate_wotd_html(word, date)
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

# ─── REVIEW NOTE SYNC (new) ─────────────────────────────

def parse_review_notes(path):
    """Parse _review_notes.md, return dict: date -> list of entry dicts."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r'^##\s+', content, flags=re.MULTILINE)
    result = {}
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split('\n')
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', lines[0])
        if not date_match:
            continue
        date = date_match.group(1)
        entries = []
        current = None
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            if line.startswith('word:'):
                if current:
                    entries.append(current)
                current = {'type':'word','word':line[5:].strip(),'file':'','note':'','sentence':'','correction':'','key_point':''}
            elif line.startswith('lesson:'):
                if current:
                    entries.append(current)
                current = {'type':'lesson','title':line[7:].strip(),'file':'','note':'','sentence':'','correction':'','key_point':''}
            elif line.startswith('file:'):
                if current:
                    current['file'] = line[5:].strip()
            elif line.startswith('note:'):
                if current:
                    current['note'] = line[5:].strip()
            elif line.startswith('sentence:'):
                if current:
                    current['sentence'] = line[9:].strip()
            elif line.startswith('correction:'):
                if current:
                    current['correction'] = line[11:].strip()
            elif line.startswith('key_point:'):
                if current:
                    current['key_point'] = line[10:].strip()
        if current:
            entries.append(current)
        if entries:
            result[date] = entries
    return result

def find_yesterday_lessons(content, date):
    """Find entries in the lessons array matching a given date."""
    pattern = r"\{d:'" + re.escape(date) + r"',[^}]+?\}"
    matches = re.findall(pattern, content)
    result = []
    for m in matches:
        title = re.search(r"t:'([^']+)'", m)
        typ = re.search(r"g:'([^']+)'", m)
        f = re.search(r"f:'([^']+)'", m)
        result.append({'title': title.group(1) if title else '',
                       'type': typ.group(1) if typ else '',
                       'file': f.group(1) if f else ''})
    return result

def file_has_review_note(filepath):
    if not os.path.exists(filepath):
        return True
    with open(filepath, 'r', encoding='utf-8') as f:
        return 'id="review-note"' in f.read()

def inject_review_note(filepath, entry, date, is_placeholder=False):
    if not os.path.exists(filepath):
        print(f"  File not found: {filepath}")
        return False
    if file_has_review_note(filepath):
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    display_date = format_date_display(date)

    if is_placeholder:
        note_block = f'''
<div class="section review-note" id="review-note">
  <div class="section-title"><span class="icon">📝</span> Review Note <span style="font-size:11px;color:#6c757d;font-weight:400;margin-left:6px;">&middot; {display_date}</span></div>
  <div class="task-box">
    <p>No review recorded for this session.</p>
    <p style="margin-top:6px;">&#128161; Consider revisiting this material and jotting down your key takeaways.</p>
  </div>
</div>'''
    else:
        parts = []
        if entry.get('note'):
            parts.append(f'<p><strong>Your understanding:</strong> {entry["note"]}</p>')
        if entry.get('sentence'):
            parts.append(f'<p style="margin-top:6px;"><strong>Your sentence:</strong> &ldquo;{entry["sentence"]}&rdquo;</p>')
        if entry.get('correction'):
            parts.append(f'<p style="margin-top:6px;"><strong>Refined:</strong> {entry["correction"]}</p>')
        if entry.get('key_point'):
            sep = '<p style="margin-top:6px;border-top:1px solid #ffe082;padding-top:6px;">' if len(parts) > 0 else '<p>'
            parts.append(f'{sep}&#128161; <strong>Key takeaway:</strong> {entry["key_point"]}</p>')
        body = '\n    '.join(parts) if parts else '<p>Review notes from our conversation.</p>'
        note_block = f'''
<div class="section review-note" id="review-note">
  <div class="section-title"><span class="icon">📝</span> Review Note <span style="font-size:11px;color:#6c757d;font-weight:400;margin-left:6px;">&middot; {display_date}</span></div>
  <div class="task-box">
    {body}
  </div>
</div>'''

    content = content.replace('</body>', note_block + '\n\n</body>')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def cleanup_notes_file(path, yesterday):
    """Remove yesterday's date block from _review_notes.md."""
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    result = []
    skip = False
    for line in lines:
        if re.match(r'^##\s+' + re.escape(yesterday) + r'\b', line):
            skip = True
            continue
        if re.match(r'^##\s+\d{4}-\d{2}-\d{2}', line):
            skip = False
        if not skip:
            result.append(line)
    new_content = '\n'.join(result).strip()
    if not new_content:
        new_content = '# Review Notes - Daily Conversation Records\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content + '\n')
    print("  Cleaned up yesterday's entries from _review_notes.md")

def sync_review_notes():
    yesterday = get_yesterday_bjt()
    print(f"\n=== Review Notes for {yesterday} ===")

    notes = parse_review_notes(REVIEW_PATH)
    yesterday_notes = notes.get(yesterday, [])

    word_notes = {e['word']: e for e in yesterday_notes if e['type'] == 'word' and e.get('word')}
    lesson_notes = {e['title']: e for e in yesterday_notes if e['type'] == 'lesson' and e.get('title')}
    file_notes = {e['file']: e for e in yesterday_notes if e.get('file')}

    changes = []

    # 1. Inject by explicit file path
    for filepath, entry in file_notes.items():
        fullpath = os.path.join(BASE_DIR, filepath)
        if inject_review_note(fullpath, entry, yesterday, False):
            changes.append(filepath)
            print(f"  Injected: {filepath}")

    # 2. Inject word entries by auto-derived path
    for word, entry in word_notes.items():
        if entry.get('file') and entry['file'] in file_notes:
            continue
        filepath = os.path.join(LESSONS_DIR, f'{yesterday}_wotd_{word}.html')
        if inject_review_note(filepath, entry, yesterday, False):
            rel = f'lessons/{yesterday}_wotd_{word}.html'
            changes.append(rel)
            print(f"  Injected: {rel}")

    # 3. Inject placeholders for yesterday's unmatched items
    if os.path.exists(INDEX_PATH):
        content = read_index(INDEX_PATH)
        yesterday_items = find_yesterday_lessons(content, yesterday)
        for item in yesterday_items:
            filepath = os.path.normpath(os.path.join(BASE_DIR, item['file']))
            if file_has_review_note(filepath):
                continue
            # Check if this item already has a note
            has_note = False
            if item['type'] == 'word' and item['title'].lower() in word_notes:
                has_note = True
            elif item['type'] == 'lesson' and item['title'] in lesson_notes:
                has_note = True
            if not has_note:
                # Also check file_notes
                if item['file'] in file_notes:
                    has_note = True
            if not has_note:
                if inject_review_note(filepath, {}, yesterday, True):
                    changes.append(item['file'])
                    print(f"  Placeholder: {item['file']}")

    # 4. Clean up
    if changes:
        cleanup_notes_file(REVIEW_PATH, yesterday)
    else:
        print("  No changes to inject.")
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
    r = sync_review_notes()
    if v or r:
        print("\nPushing changes...")
        git_push()
    else:
        print("\nNothing to push.")

if __name__ == '__main__':
    main()
