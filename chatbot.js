(function () {
  'use strict';

  /* ── Google Fonts (only if not already loaded) ─────────────────────────── */
  if (!document.querySelector('link[href*="Poppins"]')) {
    const fl = document.createElement('link');
    fl.rel = 'stylesheet';
    fl.href = 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap';
    document.head.appendChild(fl);
  }

  /* ── Inject CSS (scoped to #cb-* / .cb-* only) ─────────────────────────── */
  const _s = document.createElement('style');
  _s.textContent = `
:root {
  --cb-accent:   #5B2D9B;
  --cb-accent2:  #7c45c8;
  --cb-light:    #9B72E0;
  --cb-yellow:   #F9BF3F;
  --cb-bg:       #0e0b1a;
  --cb-surface:  #1a1530;
  --cb-surface2: #231d3a;
  --cb-border:   rgba(155,114,224,0.18);
  --cb-text:     #e8e3ff;
  --cb-muted:    rgba(232,227,255,0.5);
  --cb-radius:   20px;
  --cb-font:     'Poppins', sans-serif;
  --cb-right:    28px;
  --cb-shadow:   0 24px 64px rgba(0,0,0,0.6);
}
#cb-launcher {
  position:fixed; bottom:28px; right:var(--cb-right); z-index:9500;
  width:58px; height:58px; border-radius:50%;
  background:linear-gradient(135deg,var(--cb-accent),var(--cb-light));
  border:none; cursor:pointer; box-shadow:0 8px 28px rgba(91,45,155,.55);
  display:flex; align-items:center; justify-content:center;
  transition:transform .35s cubic-bezier(.34,1.56,.64,1),box-shadow .3s; outline:none;
}
#cb-launcher:hover{transform:scale(1.1);box-shadow:0 12px 36px rgba(91,45,155,.7);}
#cb-launcher.open{transform:scale(.88) rotate(45deg);}
#cb-launcher svg{width:26px;height:26px;fill:#fff;transition:opacity .2s;}
#cb-launcher.open .ico-chat{opacity:0;position:absolute;}
#cb-launcher.open .ico-close{opacity:1;}
#cb-launcher .ico-close{opacity:0;position:absolute;}
#cb-launcher:not(.open)::before{
  content:''; position:absolute; inset:-7px; border-radius:50%;
  border:2px solid rgba(91,45,155,.4);
  animation:cb-pulse 2.8s ease-out infinite;
}
@keyframes cb-pulse{0%{transform:scale(1);opacity:.8;}70%,100%{transform:scale(1.6);opacity:0;}}
#cb-window{
  position:fixed; bottom:100px; right:var(--cb-right); z-index:9400;
  width:380px; max-width:calc(100vw - 48px);
  height:560px; max-height:calc(100vh - 130px);
  background:var(--cb-surface); border:1px solid var(--cb-border);
  border-radius:var(--cb-radius); box-shadow:var(--cb-shadow);
  display:flex; flex-direction:column; overflow:hidden;
  transform:translateY(22px) scale(.96); opacity:0; pointer-events:none;
  transition:transform .38s cubic-bezier(.34,1.26,.64,1),opacity .28s ease;
  font-family:var(--cb-font);
}
#cb-window.open{transform:translateY(0) scale(1);opacity:1;pointer-events:all;}
.cb-header{
  background:linear-gradient(135deg,var(--cb-accent) 0%,var(--cb-accent2) 100%);
  padding:13px 14px 12px; display:flex; align-items:center; gap:10px; flex-shrink:0;
}
.cb-avatar{
  width:42px;height:42px;border-radius:50%;border:2px solid rgba(255,255,255,.45);
  background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center;
  font-size:.85rem;font-weight:700;color:#fff;flex-shrink:0;overflow:hidden;
}
.cb-avatar img{width:100%;height:100%;object-fit:cover;border-radius:50%;}
.cb-hinfo{flex:1;}
.cb-hname{font-size:.88rem;font-weight:700;color:#fff;line-height:1.2;}
.cb-hstatus{font-size:.67rem;color:rgba(255,255,255,.75);display:flex;align-items:center;gap:4px;margin-top:2px;}
.cb-dot{width:6px;height:6px;border-radius:50%;background:#4ade80;animation:cb-blink 2s ease-in-out infinite;}
@keyframes cb-blink{0%,100%{opacity:1}50%{opacity:.3}}
.cb-hbtns{display:flex;gap:5px;}
.cb-hbtn{
  width:28px;height:28px;border-radius:50%;border:none;
  background:rgba(255,255,255,.15);color:#fff;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  font-size:.72rem;transition:background .2s;
}
.cb-hbtn:hover{background:rgba(255,255,255,.3);}
.cb-msgs{
  flex:1;overflow-y:auto;padding:14px 12px 6px;
  display:flex;flex-direction:column;gap:10px;scroll-behavior:smooth;
}
.cb-msgs::-webkit-scrollbar{width:3px;}
.cb-msgs::-webkit-scrollbar-thumb{background:rgba(155,114,224,.25);border-radius:4px;}
.cb-msg{display:flex;gap:7px;align-items:flex-end;max-width:100%;}
.cb-msg.bot{flex-direction:row;}
.cb-msg.usr{flex-direction:row-reverse;}
.cb-mavatar{
  width:27px;height:27px;border-radius:50%;flex-shrink:0;
  font-size:.67rem;font-weight:700;display:flex;align-items:center;justify-content:center;
  margin-bottom:2px;overflow:hidden;
}
.bot .cb-mavatar{background:linear-gradient(135deg,var(--cb-accent),var(--cb-light));color:#fff;border:1.5px solid rgba(155,114,224,.3);}
.bot .cb-mavatar img{width:100%;height:100%;object-fit:cover;border-radius:50%;}
.usr .cb-mavatar{background:var(--cb-yellow);color:#1c1c2e;}
.cb-bbl{padding:9px 13px;border-radius:18px;font-size:.81rem;line-height:1.65;max-width:82%;word-break:break-word;}
.bot .cb-bbl{background:var(--cb-surface2);border:1px solid var(--cb-border);border-bottom-left-radius:4px;color:var(--cb-text);}
.usr .cb-bbl{background:linear-gradient(135deg,var(--cb-accent),var(--cb-accent2));color:#fff;border-bottom-right-radius:4px;}
.cb-typing .cb-bbl{display:flex;align-items:center;gap:4px;padding:12px 15px;}
.cb-td{width:6px;height:6px;border-radius:50%;background:var(--cb-light);opacity:.6;animation:cb-typing 1.3s ease-in-out infinite;}
.cb-td:nth-child(2){animation-delay:.18s}
.cb-td:nth-child(3){animation-delay:.36s}
@keyframes cb-typing{0%,60%,100%{transform:translateY(0);opacity:.6}30%{transform:translateY(-5px);opacity:1}}
.cb-speak-btn{
  display:inline-flex;align-items:center;gap:4px;margin-top:5px;padding:3px 8px;border-radius:12px;
  border:1px solid rgba(155,114,224,.3);background:transparent;color:var(--cb-light);
  font-size:.67rem;font-family:var(--cb-font);cursor:pointer;transition:all .2s;
}
.cb-speak-btn:hover{background:rgba(155,114,224,.15);}
.cb-speak-btn.playing{color:var(--cb-yellow);border-color:var(--cb-yellow);}
.cb-bbl img.preview{max-width:100%;border-radius:10px;margin-top:6px;display:block;}
.cb-sugg{padding:5px 12px 2px;display:flex;gap:5px;flex-wrap:wrap;flex-shrink:0;}
.cb-chip{
  padding:4px 11px;border-radius:20px;border:1.5px solid rgba(155,114,224,.3);
  background:rgba(155,114,224,.07);color:var(--cb-light);
  font-size:.7rem;font-weight:600;cursor:pointer;transition:all .2s;font-family:var(--cb-font);white-space:nowrap;
}
.cb-chip:hover{background:var(--cb-accent);color:#fff;border-color:var(--cb-accent);}
.cb-bar{padding:9px 11px 12px;border-top:1px solid var(--cb-border);display:flex;align-items:flex-end;gap:7px;flex-shrink:0;}
#cb-input{
  flex:1;border:1.5px solid var(--cb-border);border-radius:18px;padding:8px 13px;
  font-size:.8rem;font-family:var(--cb-font);background:rgba(155,114,224,.06);color:var(--cb-text);
  outline:none;resize:none;min-height:36px;max-height:100px;line-height:1.5;transition:border-color .2s;
}
#cb-input:focus{border-color:var(--cb-accent);}
#cb-input::placeholder{color:var(--cb-muted);}
.cb-btn{width:36px;height:36px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:.88rem;transition:all .22s;flex-shrink:0;}
#cb-send{background:linear-gradient(135deg,var(--cb-accent),var(--cb-light));color:#fff;box-shadow:0 4px 14px rgba(91,45,155,.45);}
#cb-send:hover{transform:scale(1.1);}
#cb-mic{background:rgba(155,114,224,.1);border:1.5px solid var(--cb-border);color:var(--cb-light);}
#cb-mic:hover{background:rgba(155,114,224,.2);}
#cb-mic.listening{background:#ef4444;border-color:#ef4444;color:#fff;animation:cb-micpulse 1s ease-in-out infinite;}
@keyframes cb-micpulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.4)}50%{box-shadow:0 0 0 9px rgba(239,68,68,0)}}
#cb-attach-btn{background:rgba(155,114,224,.1);border:1.5px solid var(--cb-border);color:var(--cb-light);}
#cb-attach-btn:hover{background:rgba(155,114,224,.2);}
#cb-file{display:none;}
#cb-img-preview{padding:6px 12px 0;display:none;flex-shrink:0;}
#cb-img-preview img{height:52px;border-radius:8px;border:1.5px solid var(--cb-border);cursor:pointer;opacity:.85;}
#cb-img-preview span{font-size:.65rem;color:var(--cb-muted);display:block;margin-top:3px;}
@media(max-width:480px){
  #cb-window{bottom:0;right:0;left:0;width:100%;max-width:100%;height:78vh;border-radius:20px 20px 0 0;}
  #cb-launcher{right:16px;bottom:16px;}
}
`;
  document.head.appendChild(_s);

  /* ── Inject HTML ────────────────────────────────────────────────────────── */
  const _wrap = document.createElement('div');
  _wrap.innerHTML = '<button id="cb-launcher" aria-label="Open chat" title="Chat with Niveditha\'s AI"><svg class="ico-chat" viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.477 2 12c0 1.89.525 3.66 1.438 5.168L2.047 21.34a.75.75 0 0 0 .955.955l4.172-1.391A9.96 9.96 0 0 0 12 22c5.523 0 10-4.477 10-10S17.523 2 12 2Z"/></svg><svg class="ico-close" viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12" stroke="#fff" stroke-width="2.5" stroke-linecap="round" fill="none"/></svg></button><div id="cb-window" role="dialog" aria-label="Chat with Niveditha"><div class="cb-header"><div class="cb-avatar" id="cb-av">N</div><div class="cb-hinfo"><div class="cb-hname">Niveditha Srikanth</div><div class="cb-hstatus"><span class="cb-dot"></span> Talking directly to Nivi</div></div><div class="cb-hbtns"><button class="cb-hbtn" id="cb-refresh-btn" title="Refresh knowledge base">&#8634;</button><button class="cb-hbtn" id="cb-clear-btn" title="Clear chat">&#10005;</button></div></div><div class="cb-msgs" id="cb-msgs"></div><div class="cb-sugg" id="cb-sugg"></div><div id="cb-img-preview"><img id="cb-img-thumb" src="" alt="Attached image"><span>Click to remove</span></div><div class="cb-bar"><button class="cb-btn" id="cb-attach-btn" title="Attach image"><svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor"><path d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2ZM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5Z"/></svg></button><input type="file" id="cb-file" accept="image/*" style="display:none"><textarea id="cb-input" rows="1" placeholder="Ask Niveditha anything…"></textarea><button class="cb-btn" id="cb-mic" title="Voice input"><svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor"><path d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4Zm-2 14.93V18H8v2h8v-2h-2v-2.07A8 8 0 0 0 20 11h-2a6 6 0 0 1-12 0H4a8 8 0 0 0 6 7.93Z"/></svg></button><button class="cb-btn" id="cb-send" title="Send"><svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor"><path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405Z"/></svg></button></div></div>';
  document.body.appendChild(_wrap);

  /* ── CONFIG ─────────────────────────────────────────────────────────────── */
  const API      = 'https://niveditha-04-github-io.onrender.com';
  const GREETING = "Hi! I'm Niveditha Srikanth. Ask me about my work, projects, research, or anything else — I'll give you a straight answer.";
  const CHIPS_0  = ['Tell me about yourself', "What's your current role?", 'What projects have you built?', 'What research have you done?'];

  /* ── STATE ──────────────────────────────────────────────────────────────── */
  let history      = [];
  let pendingImage = null;
  let currentAudio = null;

  /* ── ELEMENTS ───────────────────────────────────────────────────────────── */
  const launcher   = document.getElementById('cb-launcher');
  const win        = document.getElementById('cb-window');
  const msgs       = document.getElementById('cb-msgs');
  const sugg       = document.getElementById('cb-sugg');
  const input      = document.getElementById('cb-input');
  const sendBtn    = document.getElementById('cb-send');
  const micBtn     = document.getElementById('cb-mic');
  const attachBtn  = document.getElementById('cb-attach-btn');
  const fileEl     = document.getElementById('cb-file');
  const preview    = document.getElementById('cb-img-preview');
  const imgThumb   = document.getElementById('cb-img-thumb');
  const clearBtn   = document.getElementById('cb-clear-btn');
  const refreshBtn = document.getElementById('cb-refresh-btn');

  /* ── OPEN / CLOSE ───────────────────────────────────────────────────────── */
  let isOpen = false;
  function toggle() {
    isOpen = !isOpen;
    launcher.classList.toggle('open', isOpen);
    win.classList.toggle('open', isOpen);
    if (isOpen && msgs.children.length === 0) addBot(GREETING, CHIPS_0);
    if (isOpen) setTimeout(function(){ input.focus(); }, 380);
  }
  launcher.addEventListener('click', toggle);

  /* ── MESSAGES ───────────────────────────────────────────────────────────── */
  function addBot(text, chips) {
    chips = chips || [];
    var row = document.createElement('div');
    row.className = 'cb-msg bot';
    var av = document.createElement('div');
    av.className = 'cb-mavatar';
    av.textContent = 'N';
    var right = document.createElement('div');
    var bbl = document.createElement('div');
    bbl.className = 'cb-bbl';
    bbl.innerHTML = text;
    var spk = document.createElement('button');
    spk.className = 'cb-speak-btn';
    spk.innerHTML = '&#9654; Listen';
    spk.dataset.text = text.replace(/<[^>]+>/g, '');
    spk.addEventListener('click', function(){ speak(spk); });
    right.appendChild(bbl);
    right.appendChild(spk);
    row.appendChild(av);
    row.appendChild(right);
    msgs.appendChild(row);
    setChips(chips);
    scrollBottom();
    return bbl;
  }

  function addUser(text, imgDataUrl) {
    var row = document.createElement('div');
    row.className = 'cb-msg usr';
    var av = document.createElement('div');
    av.className = 'cb-mavatar';
    av.textContent = 'Y';
    var bbl = document.createElement('div');
    bbl.className = 'cb-bbl';
    bbl.textContent = text || '';
    if (imgDataUrl) {
      var img = document.createElement('img');
      img.className = 'preview';
      img.src = imgDataUrl;
      bbl.appendChild(img);
    }
    row.appendChild(bbl);
    row.appendChild(av);
    msgs.appendChild(row);
    setChips([]);
    scrollBottom();
  }

  function addTyping() {
    var row = document.createElement('div');
    row.className = 'cb-msg bot cb-typing';
    row.innerHTML = '<div class="cb-mavatar">N</div><div class="cb-bbl"><span class="cb-td"></span><span class="cb-td"></span><span class="cb-td"></span></div>';
    msgs.appendChild(row);
    scrollBottom();
    return row;
  }

  function setChips(chips) {
    sugg.innerHTML = '';
    chips.forEach(function(c) {
      var btn = document.createElement('button');
      btn.className = 'cb-chip';
      btn.textContent = c;
      btn.addEventListener('click', function(){ input.value = c; send(); });
      sugg.appendChild(btn);
    });
  }

  function scrollBottom() { msgs.scrollTop = msgs.scrollHeight; }

  /* ── SEND ───────────────────────────────────────────────────────────────── */
  async function send() {
    var text = input.value.trim();
    if (!text && !pendingImage) return;
    var imgSnap = pendingImage;
    input.value = '';
    input.style.height = 'auto';
    clearImage();
    addUser(text, imgSnap ? imgSnap.dataUrl : null);
    var typing = addTyping();
    sendBtn.disabled = true;
    try {
      var body = { message: text || 'What is in this image?', history: history };
      if (imgSnap) body.image = imgSnap.b64;
      var res  = await fetch(API + '/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      var data = await res.json();
      typing.remove();
      var answer = data.answer || 'Sorry, something went wrong on my end.';
      addBot(answer, guessChips(text));
      history.push({ role: 'user', content: text });
      history.push({ role: 'assistant', content: answer });
      if (history.length > 20) history = history.slice(-20);
    } catch (e) {
      typing.remove();
      addBot('Hmm, something went wrong on my end. Give it another try!');
    }
    sendBtn.disabled = false;
    input.focus();
  }

  function guessChips(q) {
    if (!q) return [];
    var l = q.toLowerCase();
    if (l.indexOf('project') !== -1)  return ['Tell me more about a project', 'What tech do you use?', 'Any GitHub links?'];
    if (l.indexOf('work') !== -1 || l.indexOf('role') !== -1) return ['What was your biggest achievement?', 'Tell me about your research', 'Your tech stack?'];
    if (l.indexOf('research') !== -1) return ['Any publications?', 'What is your current focus?', 'Tell me more'];
    return ['Tell me more', 'What else should I know?', 'Any other projects?'];
  }

  sendBtn.addEventListener('click', send);
  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
  input.addEventListener('input', function() {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 100) + 'px';
  });

  /* ── VOICE INPUT ────────────────────────────────────────────────────────── */
  var recognition = null, listening = false;
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.onresult = function(e) { input.value = e.results[0][0].transcript; stopListening(); send(); };
    recognition.onerror  = function() { stopListening(); };
    recognition.onend    = function() { stopListening(); };
    micBtn.addEventListener('click', function() {
      if (listening) { recognition.stop(); stopListening(); }
      else { recognition.start(); startListening(); }
    });
  } else {
    micBtn.title = 'Voice input not supported in this browser';
    micBtn.style.opacity = '.4';
  }
  function startListening() { listening = true; micBtn.classList.add('listening'); micBtn.title = 'Tap to stop'; }
  function stopListening()  { listening = false; micBtn.classList.remove('listening'); micBtn.title = 'Voice input'; }

  /* ── VOICE OUTPUT ───────────────────────────────────────────────────────── */
  async function speak(btn) {
    var text = btn.dataset.text;
    if (!text) return;
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
    if (btn.classList.contains('playing')) {
      btn.classList.remove('playing');
      btn.innerHTML = '&#9654; Listen';
      return;
    }
    document.querySelectorAll('.cb-speak-btn.playing').forEach(function(b) {
      b.classList.remove('playing'); b.innerHTML = '&#9654; Listen';
    });
    btn.innerHTML = '&#8987; Generating…';
    btn.disabled = true;
    try {
      var res = await fetch(API + '/speak', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text }),
      });
      if (!res.ok) throw new Error('TTS error');
      var blob = await res.blob();
      var url  = URL.createObjectURL(blob);
      var audio = new Audio(url);
      currentAudio = audio;
      btn.classList.add('playing');
      btn.innerHTML = '&#9646;&#9646; Playing…';
      btn.disabled = false;
      audio.play();
      audio.onended = function() {
        btn.classList.remove('playing');
        btn.innerHTML = '&#9654; Listen';
        URL.revokeObjectURL(url);
        currentAudio = null;
      };
    } catch (e) {
      btn.innerHTML = '&#9654; Listen';
      btn.disabled = false;
    }
  }

  /* ── IMAGE UPLOAD ───────────────────────────────────────────────────────── */
  attachBtn.addEventListener('click', function() { fileEl.click(); });
  fileEl.addEventListener('change', function() {
    var file = fileEl.files[0];
    if (!file) return;
    fileEl.value = '';
    var reader = new FileReader();
    reader.onload = function(e) {
      var dataUrl = e.target.result;
      pendingImage  = { b64: dataUrl.split(',')[1], dataUrl: dataUrl };
      imgThumb.src  = dataUrl;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  });
  imgThumb.addEventListener('click', clearImage);
  function clearImage() { pendingImage = null; preview.style.display = 'none'; imgThumb.src = ''; }

  /* ── CLEAR & REFRESH ────────────────────────────────────────────────────── */
  clearBtn.addEventListener('click', function() {
    msgs.innerHTML = ''; sugg.innerHTML = ''; history = []; clearImage();
    addBot(GREETING, CHIPS_0);
  });
  refreshBtn.addEventListener('click', async function() {
    refreshBtn.textContent = '…';
    try { await fetch(API + '/refresh', { method: 'POST' }); refreshBtn.textContent = '✓'; }
    catch (e) { refreshBtn.textContent = '✕'; }
    setTimeout(function() { refreshBtn.textContent = '↺'; }, 2000);
  });

})();
