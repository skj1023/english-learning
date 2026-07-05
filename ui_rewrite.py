from pathlib import Path
import re, subprocess
p = Path('index.html')
html = p.read_text(encoding='utf-8')

# Required helper function style

def hi(s, old, new):
    if old not in s:
        print('WARN: not found:', old[:60])
        return s
    s = s.replace(old, new)
    return s

# ===== HTML =====

# 1. Toolbar: remove vocabBtn, phraseBtn, pastBtn; keep only todayBtn
html = hi(html,
    '<button class="today-btn" id="vocabBtn">📕 Vocab</button>\n'
    '        <button class="today-btn" id="phraseBtn">🧩 Phrases</button>\n'
    '        <button class="today-btn" id="pastBtn">📜 Past</button>\n'
    '        <button class="today-btn" id="todayBtn">📅 Today</button>',
    '<button class="today-btn" id="todayBtn">📅 Today</button>'
)

# 2. Remove old float-actions
html = hi(html,
    '<div class="float-actions" id="floatActions">\n'
    '  <button class="float-btn back-float-btn" id="backFloatBtn" style="display:none">← Back</button>\n'
    '  <span style="flex:1"></span>\n'
    '  <button class="float-btn" id="darkBtn" title="Dark mode">🌙</button>\n'
    '  <button class="float-btn" id="fsBtn" title="Fullscreen">⛶</button>\n'
    '</div>',
    ''
)

# 3. Add bottom tab bar after vocabView/phraseView/pastView
btm_bar = '''
<div class="btm-bar" id="btmBar">
  <div class="btm-tabs" id="btmTabs">
    <button class="btm-btn active" data-tab="home">🏠<span class="btm-lbl">Home</span></button>
    <button class="btm-btn" data-tab="vocab">📕<span class="btm-lbl">Words</span></button>
    <button class="btm-btn" data-tab="phrases">🧩<span class="btm-lbl">Phrases</span></button>
    <button class="btm-btn" data-tab="past">📜<span class="btm-lbl">Past</span></button>
  </div>
  <div class="btm-right">
    <button class="btm-icon" id="darkBtn">🌙</button>
    <button class="btm-icon" id="fsBtn">⛶</button>
  </div>
  <div class="btm-back-detail" id="backDetail" style="display:none">
    <span class="back-pill" id="backPillBtn">← Back</span>
  </div>
</div>
'''
# Insert before </body>
html = html.replace('</body>', btm_bar + '\n</body>')

# 4. Add bottom padding to content views that lack it
html = hi(html,
    '#vocabView,#phraseView,#pastView{display:none;max-width:640px;margin:0 auto;padding:0 0 60px}',
    '#vocabView,#phraseView,#pastView{display:none;max-width:640px;margin:0 auto;padding:0 0 76px}'
)
html = hi(html,
    '#vocabView{display:none;max-width:640px;margin:0 auto;padding:0 0 60px}',
    '#vocabView,#phraseView,#pastView{display:none;max-width:640px;margin:0 auto;padding:0 0 76px}'
)
html = html.replace('#content{display:none;max-width:640px;margin:0 auto;padding:0 0 60px}', '#content{display:none;max-width:640px;margin:0 auto;padding:0 0 76px}')
html = html.replace('.detail-bottom{padding:0 0 60px}', '.detail-bottom{padding:0 0 76px}')
# detail view margin-bottom
html = html.replace('.lesson-frame{border:1px solid #e0e0e0;border-radius:12px;overflow:hidden;background:#fff;margin:0 16px 16px}', '.lesson-frame{border:1px solid #e0e0e0;border-radius:12px;overflow:hidden;background:#fff;margin:0 16px 16px}')

# ===== CSS: Replace float-actions CSS with btm-bar CSS =====
float_css = '''  /* ── Float Actions (Dark / Fullscreen) ── */
  .float-actions{position:fixed;bottom:28px;left:28px;right:28px;display:flex;align-items:center;gap:12px;z-index:9999;opacity:.35;transition:opacity .35s;pointer-events:none}
  .float-actions:hover,.float-actions:focus-within{opacity:1}
  .float-btn{width:44px;height:44px;border-radius:50%;border:none;background:rgba(74,144,217,.12);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);color:#555;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 14px rgba(0,0,0,.1);transition:all .25s;user-select:none;pointer-events:auto}
  .float-btn:hover{background:rgba(74,144,217,.25);transform:scale(1.12);box-shadow:0 4px 20px rgba(0,0,0,.18)}
  .float-btn:active{transform:scale(.95)}
  body.dark .float-btn{background:rgba(108,180,238,.1);color:#bbb;box-shadow:0 2px 14px rgba(0,0,0,.35)}
  body.dark .float-btn:hover{background:rgba(108,180,238,.22);color:#e8e8e8}
  .back-float-btn{width:auto;padding:0 18px;border-radius:22px;background:rgba(108,180,238,.25)!important;color:#222!important;font-size:14px!important;font-weight:600;box-shadow:0 2px 14px rgba(0,0,0,.12)!important}
  .back-float-btn:hover{background:rgba(108,180,238,.4)!important;transform:scale(1.06)}
  body.dark .back-float-btn{background:rgba(108,180,238,.2)!important;color:#e8e8e8!important}
  body.dark .back-float-btn:hover{background:rgba(108,180,238,.35)!important}
  @media(max-width:480px){
    .float-actions{bottom:20px;left:20px;right:20px;gap:10px}
    .float-btn{width:40px;height:40px;font-size:18px}
    .back-float-btn{height:36px;padding:0 14px;font-size:13px!important}
    .toolbar h1{font-size:18px}
    .week-btn{padding:6px 10px;font-size:12px}
    .top-bar{padding:10px 12px 0}
    .item{padding:10px 12px}
    .item .title{font-size:13px}
  }'''

btm_css = '''  /* ── Bottom Tab Bar ── */
  .btm-bar{position:fixed;bottom:0;left:0;right:0;z-index:9998;background:#fff;border-top:1px solid #e9ecef;display:flex;align-items:stretch;height:56px;padding-bottom:env(safe-area-inset-bottom,0);transition:background .3s}
  .btm-tabs{display:flex;flex:1;align-items:stretch;gap:0}
  .btm-btn{flex:1;border:none;background:none;font-size:10px;font-weight:600;color:#999;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;padding:4px 0;transition:color .2s;user-select:none;font-family:inherit}
  .btm-btn:active{opacity:.7}
  .btm-btn .btm-lbl{font-size:10px;margin-top:-1px}
  .btm-btn.active{color:#4a90d9}
  body.dark .btm-btn{color:#666}
  body.dark .btm-btn.active{color:#6cb4ee}
  .btm-right{display:flex;align-items:center;gap:2px;padding:0 6px}
  .btm-icon{width:34px;height:34px;border-radius:50%;border:none;background:none;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;color:#999;transition:background .2s;flex-shrink:0}
  .btm-icon:active{background:#f0f0f0}
  body.dark .btm-icon{color:#777}
  body.dark .btm-icon:active{background:#1a1a2e}
  body.dark .btm-bar{background:#0f0f1a;border-top-color:#2d2d5e}
  .btm-back-detail{display:none;flex:1;align-items:center;padding:0 8px 0 12px}
  .back-pill{padding:7px 16px;border-radius:20px;background:rgba(108,180,238,.25);color:#222;font-size:14px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:4px;transition:all .2s;user-select:none}
  .back-pill:active{background:rgba(108,180,238,.4);transform:scale(.96)}
  body.dark .back-pill{background:rgba(108,180,238,.2);color:#e8e8e8}
  @media(max-width:480px){
    .btm-bar{height:50px}
    .btm-btn{font-size:9px}.btm-btn .btm-lbl{font-size:9px}
    .btm-icon{width:30px;height:30px;font-size:14px}
    .toolbar h1{font-size:18px}
    .week-btn{padding:6px 10px;font-size:12px}
    .top-bar{padding:10px 12px 0}
    .item{padding:10px 12px}
    .item .title{font-size:13px}
  }'''

html = html.replace(float_css, btm_css)

# ===== JS =====

# 5. Remove toggleHistory function and history-btn logic from buildWeeks
html = html.replace(
    '\nfunction toggleHistory(){\n'
    '  showHistory=!showHistory;\n'
    '  if(!showHistory && _realWeek){\n'
    '    currentWeek=_realWeek;\n'
    '  }\n'
    '  buildWeeks();\n'
    '  render();\n'
    '}\n',
    '\n'
)

# Remove history-btn in buildWeeks
html = html.replace(
    '  // History button\n'
    '  if(pastKeys.length>0){\n'
    '    var hb=document.createElement(\'button\');\n'
    '    hb.className=\'history-btn\';\n'
    '    hb.textContent=\'📜 Past\';\n'
    '    hb.addEventListener(\'click\',function(){showPastView()});\n'
    '    tabs.appendChild(hb);\n'
    '  }\n',
    ''
)

# Remove history-btn CSS rules
html = html.replace(
    '  body.dark .history-btn{background:#1a1a2e;border-color:#2d2d5e;color:#999}\n'
    '  body.dark .history-btn:hover{background:#2d2d5e}\n',
    ''
)
html = html.replace(
    '  .history-btn{flex-shrink:0;padding:8px 10px;font-size:11px;font-weight:600;background:#fff;border:1px solid #e0e0e0;border-radius:6px;cursor:pointer;color:#999;white-space:nowrap;position:sticky;right:0;z-index:2;margin-left:auto}\n',
    ''
)

# Remove showHistory arg from buildWeeks call
html = html.replace(
    '  buildWeeks();\n'
    '  render();\n'
    '}',
    '  buildWeeks();\n'
    '  render();\n'
    '}'  # same
)

# Remove showHistory=false in switchWeek
html = html.replace(
    '  currentWeek=w;showHistory=false;saveState();render();',
    '  currentWeek=w;saveState();render();'
)

# 6. Remove toolbar button event listeners
html = html.replace(
    "\ndocument.getElementById('vocabBtn').addEventListener('click',showVocabBook);\n",
    "\n"
)
# (phraseBtn and pastBtn event listeners already removed when buttons were removed)

# 7. Replace navigation JS

# Add _prevView variable
html = html.replace(
    'var _fromPast=false,_pastTab=\'unlearned\',_pastSort=\'date\';',
    'var _prevView=\'home\',_pastTab=\'unlearned\',_pastSort=\'date\';'
)

# Remove _fromVocab in vocab-related JS
html = html.replace(
    'var _fromVocab=false,_fromPhrase=false,_fromPast=false,_vocabTab=\'lern\',_vocabSort=\'date\';',
    'var _vocabTab=\'lern\',_vocabSort=\'date\';'
)
html = html.replace(
    'var _fromVocab=false,_vocabTab=\'lern\',_vocabSort=\'date\';',
    'var _vocabTab=\'lern\',_vocabSort=\'date\';'
)
# Remove _fromPhrase
html = html.replace(
    'var _fromPhrase=false,_phraseTab=\'lern\',_phraseSort=\'date\';',
    'var _phraseTab=\'lern\',_phraseSort=\'date\';'
)

# 8. Replace openItem to capture _prevView and hide all views
old_openitem = '''function openItem(item){
  _currentItem=item;
  document.getElementById('content').classList.remove('show');
  var d=document.getElementById('detail');
  d.classList.add('show');
  updateBackBtn();'''

new_openitem = '''function openItem(item){
  _currentItem=item;
  // Save current view for back navigation
  if(document.getElementById('vocabView').classList.contains('show')) _prevView='vocab';
  else if(document.getElementById('phraseView').classList.contains('show')) _prevView='phrases';
  else if(document.getElementById('pastView').classList.contains('show')) _prevView='past';
  else _prevView='home';
  ['content','vocabView','phraseView','pastView'].forEach(function(v){
    document.getElementById(v).classList.remove('show');
  });
  var d=document.getElementById('detail');
  d.classList.add('show');
  updateBtmBar();'''

html = html.replace(old_openitem, new_openitem)

# 9. Replace updateBackBtn with updateBtmBar
html = html.replace(
    '''function updateBackBtn(){
  var show=document.getElementById('detail').classList.contains('show')||document.getElementById('vocabView').classList.contains('show')||document.getElementById('phraseView').classList.contains('show')||document.getElementById('pastView').classList.contains('show');
  document.getElementById('backFloatBtn').style.display=show?'flex':'none';
}''',
    '''function updateBtmBar(){
  var inDetail=document.getElementById('detail').classList.contains('show');
  document.getElementById('btmTabs').style.display=inDetail?'none':'flex';
  document.getElementById('backDetail').style.display=inDetail?'flex':'none';
  document.getElementById('btmRight').style.display='flex';
}'''
)

# 10. Replace back button click handler
old_back = (
    "document.getElementById('backFloatBtn').addEventListener('click',function(){\n"
    "  if(document.getElementById('detail').classList.contains('show')){\n"
    "    document.getElementById('detail').classList.remove('show');\n"
    "    document.getElementById('todaySwitch').style.display='none';\n"
    "    if(_fromVocab){_fromVocab=false;document.getElementById('vocabView').classList.add('show')}\n"
    "    else if(_fromPhrase){_fromPhrase=false;document.getElementById('phraseView').classList.add('show')}\n"
    "    else if(_fromPast){_fromPast=false;document.getElementById('pastView').classList.add('show')}\n"
    "    else{document.getElementById('content').classList.add('show')}\n"
    "  }else if(document.getElementById('vocabView').classList.contains('show')){\n"
    "    document.getElementById('vocabView').classList.remove('show');\n"
    "    document.getElementById('content').classList.add('show');\n"
    "  }else if(document.getElementById('phraseView').classList.contains('show')){\n"
    "    document.getElementById('phraseView').classList.remove('show');\n"
    "    document.getElementById('content').classList.add('show');\n"
    "  }else if(document.getElementById('pastView').classList.contains('show')){\n"
    "    document.getElementById('pastView').classList.remove('show');\n"
    "    document.getElementById('content').classList.add('show');\n"
    "  }\n"
    "  updateBackBtn();\n"
    "});"
)

new_back = (
    "document.getElementById('backPillBtn').addEventListener('click',function(){\n"
    "  document.getElementById('detail').classList.remove('show');\n"
    "  document.getElementById('todaySwitch').style.display='none';\n"
    "  _tdL=null;_tdW=null;\n"
    "  switchTab(_prevView);\n"
    "});"
)
html = html.replace(old_back, new_back)

# 11. Replace hideVocabBook (simplify to just switchTab)
html = html.replace(
    "function hideVocabBook(){\n"
    "  document.getElementById('vocabView').classList.remove('show');\n"
    "  document.getElementById('content').classList.add('show');\n"
    "  updateBackBtn();\n"
    "}",
    "function hideVocabBook(){switchTab('home');}"
)
html = html.replace(
    "function hidePhraseBook(){\n  document.getElementById('phraseView').classList.remove('show');\n  document.getElementById('content').classList.add('show');\n  updateBackBtn();\n}",
    "function hidePhraseBook(){switchTab('home');}"
)

# 12. Add switchTab function
switch_tab_js = (
    "\n/* ===== TAB SWITCHING ===== */\n"
    "function switchTab(tab){\n"
    "  document.getElementById('detail').classList.remove('show');\n"
    "  ['content','vocabView','phraseView','pastView'].forEach(function(v){\n"
    "    document.getElementById(v).classList.remove('show');\n"
    "  });\n"
    "  if(tab==='home'){\n"
    "    document.getElementById('content').classList.add('show');\n"
    "  }else if(tab==='vocab'){\n"
    "    document.getElementById('vocabView').classList.add('show');\n"
    "    renderVocab();\n"
    "  }else if(tab==='phrases'){\n"
    "    document.getElementById('phraseView').classList.add('show');\n"
    "    renderPhraseBook();\n"
    "  }else if(tab==='past'){\n"
    "    document.getElementById('pastView').classList.add('show');\n"
    "    renderPastView();\n"
    "  }\n"
    "  document.querySelectorAll('.btm-btn').forEach(function(b){\n"
    "    b.classList.toggle('active',b.dataset.tab===tab);\n"
    "  });\n"
    "  _prevView=tab;\n"
    "  updateBtmBar();\n"
    "  try{sessionStorage.setItem('et',tab)}catch(e){}\n"
    "}\n"
)

# Insert after var declarations, before saveState/restoreState
html = html.replace(
    "\n/* ===== SWITCH ===== */",
    switch_tab_js + "\n/* ===== SWITCH ===== */"
)

# 13. Add tab button click handlers
tab_handlers = (
    "\ndocument.getElementById('btmTabs').addEventListener('click',function(e){\n"
    "  var b=e.target.closest('button');\n"
    "  if(!b||!b.dataset.tab)return;\n"
    "  var tab=b.dataset.tab;\n"
    "  if(tab==='home'&&_prevView==='home'){render();return;}\n"
    "  switchTab(tab);\n"
    "});\n"
)
html = html.replace(
    "\ndocument.getElementById('fsBtn').addEventListener('click',goFullscreen);\n",
    tab_handlers + "\ndocument.getElementById('fsBtn').addEventListener('click',goFullscreen);\n"
)

# 14. Modify showVocabBook / showPhraseBook to use switchTab
html = html.replace(
    "function showVocabBook(){\n"
    "  document.getElementById('content').classList.remove('show');\n"
    "  document.getElementById('vocabView').classList.add('show');\n"
    "  renderVocab();\n"
    "  updateBackBtn();\n"
    "}",
    "function showVocabBook(){switchTab('vocab');}"
)
html = html.replace(
    "function showPhraseBook(){\n"
    "  document.getElementById('content').classList.remove('show');\n"
    "  document.getElementById('phraseView').classList.add('show');\n"
    "  renderPhraseBook();\n"
    "  updateBackBtn();\n"
    "}",
    "function showPhraseBook(){switchTab('phrases');}"
)
html = html.replace(
    "function showPastView(){\n"
    "  document.getElementById('content').classList.remove('show');\n"
    "  document.getElementById('pastView').classList.add('show');\n"
    "  renderPastView();\n"
    "  updateBackBtn();\n"
    "}",
    "function showPastView(){switchTab('past');}"
)

# 15. Remove _fromVocab/_fromPhrase/_fromPast from card click handlers
# Vocab card click
html = html.replace(
    "    card.addEventListener('click',function(){\n"
    "      _fromVocab=true;\n"
    "      var item={t:v.w,i:'💡',g:'word',f:'lessons/'+v.d+'_wotd_'+vocabSlug(v.w)+'.html'};\n"
    "      openItem(item);\n"
    "    });",
    "    card.addEventListener('click',function(){\n"
    "      var item={t:v.w,i:'💡',g:'word',f:'lessons/'+v.d+'_wotd_'+vocabSlug(v.w)+'.html'};\n"
    "      openItem(item);\n"
    "    });"
)
# Phrase card click
html = html.replace(
    "    card.addEventListener('click',function(){\n"
    "      _fromPhrase=true;\n"
    "      var item={t:v.p,i:'🧩',g:'phrase',f:'lessons/'+v.d+'_phrase_'+phraseSlug(v.p)+'.html'};\n"
    "      openItem(item);\n"
    "    });",
    "    card.addEventListener('click',function(){\n"
    "      var item={t:v.p,i:'🧩',g:'phrase',f:'lessons/'+v.d+'_phrase_'+phraseSlug(v.p)+'.html'};\n"
    "      openItem(item);\n"
    "    });"
)

# 16. Past view render: add date section labels
old_past_render = (
    "function renderPastView(){\n"
    "  var list=document.getElementById('pastList');\n"
    "  var items=lessons.filter(function(l){return l.d<todayStr});\n"
    "  items=items.filter(function(l){return _pastTab==='learned'?isLearned(l):!isLearned(l)});\n"
    "  if(items.length===0){\n"
    "    list.innerHTML='<div class=\"vocab-empty\"><div class=\"big\">📭</div>'+(_pastTab==='learned'?'No learned past content yet':'No unlearned past content')+'</div>';\n"
    "    return;\n"
    "  }\n"
    "  var sorted=[].concat(items);\n"
    "  if(_pastSort==='az'){sorted.sort(function(a,b){return a.t<b.t?-1:1})}\n"
    "  else{sorted.sort(function(a,b){if(a.d!==b.d)return a.d<b.d?1:-1;return a.g==='lesson'?-1:1})}\n"
    "  list.innerHTML='';\n"
    "  sorted.forEach(function(l){\n"
    "    var card=document.createElement('div');\n"
    "    card.className='vocab-card';\n"
    "    card.addEventListener('click',function(){_fromPast=true;openItem(l)});\n"
    "    var tag=_pastTab==='learned'?'mast':'lern';\n"
    "    var dayNames=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];\n"
    "    var dt=new Date(l.d+'T12:00:00');\n"
    "    card.innerHTML='<div class=\"vw\">'+l.i+'</div>'+\n"
    "      '<div class=\"vi\"><div class=\"vt\">'+l.t+'</div><div class=\"vm\">'+l.d+' · '+dayNames[dt.getDay()]+' · '+(l.g==='word'?'Word':'Lesson')+'</div></div>'+\n"
    "      '<div class=\"vs '+tag+'\">'+(_pastTab==='learned'?'✅ Learned':'🔴 Not Learned')+'</div>';\n"
    "    list.appendChild(card);\n"
    "  });\n"
    "}"
)
new_past_render = (
    "function renderPastView(){\n"
    "  var list=document.getElementById('pastList');\n"
    "  var items=lessons.filter(function(l){return l.d<todayStr});\n"
    "  items=items.filter(function(l){return _pastTab==='learned'?isLearned(l):!isLearned(l)});\n"
    "  if(items.length===0){\n"
    "    list.innerHTML='<div class=\"vocab-empty\"><div class=\"big\">📭</div>'+(_pastTab==='learned'?'No learned past content yet':'No unlearned past content')+'</div>';\n"
    "    return;\n"
    "  }\n"
    "  var sorted=[].concat(items);\n"
    "  if(_pastSort==='az'){sorted.sort(function(a,b){return a.t<b.t?-1:1})}\n"
    "  else{sorted.sort(function(a,b){if(a.d!==b.d)return a.d<b.d?1:-1;return a.g==='lesson'?-1:1})}\n"
    "  list.innerHTML='';\n"
    "  var currentDate='';\n"
    "  var dayNames=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];\n"
    "  sorted.forEach(function(l){\n"
    "    if(l.d!==currentDate){\n"
    "      currentDate=l.d;\n"
    "      var sep=document.createElement('div');\n"
    "      sep.className='section-label';\n"
    "      var dt=new Date(l.d+'T12:00:00');\n"
    "      sep.textContent=l.d+' · '+dayNames[dt.getDay()];\n"
    "      list.appendChild(sep);\n"
    "    }\n"
    "    var card=document.createElement('div');\n"
    "    card.className='vocab-card';\n"
    "    card.addEventListener('click',function(){openItem(l)});\n"
    "    var tag=_pastTab==='learned'?'mast':'lern';\n"
    "    var dt=new Date(l.d+'T12:00:00');\n"
    "    card.innerHTML='<div class=\"vw\">'+l.i+'</div>'+\n"
    "      '<div class=\"vi\"><div class=\"vt\">'+l.t+'</div><div class=\"vm\">'+l.d+' · '+dayNames[dt.getDay()]+' · '+(l.g==='word'?'Word':'Lesson')+'</div></div>'+\n"
    "      '<div class=\"vs '+tag+'\">'+(_pastTab==='learned'?'✅ Learned':'🔴 Not Learned')+'</div>';\n"
    "    list.appendChild(card);\n"
    "  });\n"
    "}"
)
html = html.replace(old_past_render, new_past_render)

# 17. Remove past button click listener from document
html = html.replace(
    "document.getElementById('pastBtn').addEventListener('click',showPastView);\n",
    ""
)

# 18. Remove pastListenerRemoved for phraseBtn
html = html.replace(
    "document.getElementById('phraseBtn').addEventListener('click',showPhraseBook);\n",
    ""
)

# 19. Remove toggleHistory from filter
html = html.replace(
    "  if(!showHistory && currentWeek===_realWeek){\n"
    "    items=items.filter(function(l){return l.d>=todayStr||l.d===currentWeek});\n"
    "  }",
    "  if(currentWeek===_realWeek){\n"
    "    items=items.filter(function(l){return l.d>=todayStr||l.d===currentWeek});\n"
    "  }"
)

# 20. Restore session tab state after init
html = html.replace(
    "  buildWeeks();\n"
    "  restoreState();\n"
    "  syncActiveTabs();\n"
    "  render();\n"
    "  // ...",
    "  buildWeeks();\n"
    "  restoreState();\n"
    "  syncActiveTabs();\n"
    "  render();\n"
)

# At the end of init(), check if saved tab isn't home and switch
html = html.replace(
    "  buildWeeks();\n"
    "  restoreState();\n"
    "  syncActiveTabs();\n"
    "  render();\n"
    "}",
    "  buildWeeks();\n"
    "  restoreState();\n"
    "  syncActiveTabs();\n"
    "  render();\n"
    "  // Restore saved tab\n"
    "  try{var st=sessionStorage.getItem('et');if(st&&st!='home')switchTab(st)}catch(e){}\n"
    "}"
)

# 21. Add section-label CSS for dark mode in past view (reuse existing)
# Already has: body.dark .section-label{color:#999} - good

# ===== WRITE =====
p.write_text(html, encoding='utf-8')

# ===== VALIDATE =====
sc = re.findall(r'<script>(.*?)</script>', html, flags=re.S)
Path('.tmp_check.js').write_text(sc[0], encoding='utf-8')
r = subprocess.run(['node', '--check', '.tmp_check.js'], capture_output=True, text=True, cwd='.')
print('node check exit', r.returncode)
if r.returncode:
    print(r.stderr)
else:
    Path('.tmp_check.js').unlink()
    # Check no remaining old references
    bad = ['backFloatBtn', '_fromVocab', '_fromPhrase', '_fromPast', 'toggleHistory', 'history-btn', 'updateBackBtn', 'float-actions', 'floatActions']
    for b in bad:
        if b in html:
            print('WARN: still has', b)
    print('All clear' if all(b not in html for b in bad) else '')
    print('new CSS:', 'btm-bar' in html, 'new JS:', 'switchTab' in html, 'date labels:', 'currentDate' in html)
PY
