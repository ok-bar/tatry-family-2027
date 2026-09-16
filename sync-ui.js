// sync-ui.js — Auth UI + sync wiring for tatry-family-2027
// Add <script src="sync-ui.js"> at end of index.html, after sync.js

import {
  sendMagicLink, getSession, onAuthChange, signOut,
  createTrip, joinTrip, getJoinCode,
  initSync, syncVisit, syncCheck, syncExpense, syncBudget,
  fetchExpenses, deleteExpense
} from './sync.js';

// ─── Inject auth panel into the page ───────────────────────────────────────
function injectAuthPanel() {
  const panel = document.createElement('div');
  panel.id = 'sync-panel';
  panel.innerHTML = `
    <style>
      #sync-panel{position:fixed;bottom:1rem;left:1rem;z-index:9999;font-family:inherit}
      #sync-fab{background:#2d8c7f;color:#fff;border:none;border-radius:50px;
        padding:.55rem 1.1rem;font-size:13px;font-weight:700;cursor:pointer;
        box-shadow:0 2px 8px rgba(0,0,0,.25);display:flex;align-items:center;gap:.4rem}
      #sync-fab .dot{width:8px;height:8px;border-radius:50%;background:#e8c030;flex-shrink:0}
      #sync-fab .dot.green{background:#4ade80}
      #sync-drawer{display:none;position:fixed;bottom:4rem;left:1rem;
        background:#fff;border-radius:16px;padding:1.25rem;width:280px;
        box-shadow:0 8px 32px rgba(0,0,0,.18);font-size:14px;direction:rtl}
      #sync-drawer h4{margin:0 0 .75rem;font-size:15px}
      #sync-drawer input{width:100%;padding:.5rem .75rem;border:1.5px solid #c5d8d8;
        border-radius:8px;font-size:14px;margin:.35rem 0}
      #sync-drawer button{width:100%;padding:.55rem;border-radius:8px;border:none;
        background:#2d8c7f;color:#fff;font-size:14px;font-weight:600;cursor:pointer;margin-top:.35rem}
      #sync-drawer button.sec{background:#eef4f4;color:#2d8c7f;margin-top:.5rem}
      #sync-drawer .code-box{background:#eef4f4;border-radius:8px;padding:.5rem .75rem;
        font-size:18px;font-weight:700;letter-spacing:.12em;text-align:center;margin:.5rem 0}
      #sync-drawer .msg{font-size:12px;color:#4a6060;margin:.4rem 0;line-height:1.4}
      #sync-drawer .sep{border:none;border-top:1px solid #e8eeee;margin:.75rem 0}
    </style>
    <button id="sync-fab" onclick="SyncUI.toggle()">
      <span class="dot" id="sync-dot"></span>
      <span id="sync-fab-label">סנכרון</span>
    </button>
    <div id="sync-drawer" id="sync-drawer"></div>
  `;
  document.body.appendChild(panel);
}

// ─── Drawer states ──────────────────────────────────────────────────────────
function drawerLoggedOut() {
  document.getElementById('sync-drawer').innerHTML = `
    <h4>🔄 סנכרון בין מכשירים</h4>
    <p class="msg">הכנסו עם כתובת אימייל — ישלח לינק כניסה. לא צריך סיסמה.</p>
    <input id="sync-email" type="email" placeholder="your@email.com" dir="ltr">
    <button onclick="SyncUI.sendLink()">שלח לינק כניסה</button>
    <p class="msg" id="sync-msg"></p>
  `;
}

function drawerLoggedIn(email, joinCode, tripId) {
  document.getElementById('sync-drawer').innerHTML = `
    <h4>✅ מחובר כ-${email}</h4>
    ${joinCode ? `
      <p class="msg">קוד שיתוף — ליאת / עומרי מזינים אותו להצטרף:</p>
      <div class="code-box" id="join-code-display">${joinCode}</div>
      <button class="sec" onclick="SyncUI.copyCode('${joinCode}')">העתק קוד</button>
    ` : `
      <p class="msg">עוד לא ביחד. צרו טיול חדש או הצטרפו עם קוד:</p>
      <button onclick="SyncUI.create()">צור טיול חדש (ואני מקבל קוד)</button>
      <hr class="sep">
      <input id="join-input" type="text" placeholder="קוד 8 ספרות" dir="ltr" maxlength="8">
      <button onclick="SyncUI.join()">הצטרף לטיול</button>
    `}
    <hr class="sep">
    <p class="msg" id="sync-status">⚡ מחובר · שינויים מסונכרנים בזמן אמת</p>
    <button class="sec" onclick="SyncUI.signOut()">התנתק</button>
  `;
}

function drawerNoTrip(email) {
  drawerLoggedIn(email, null, null);
}

// ─── SyncUI public API ──────────────────────────────────────────────────────
let _drawerOpen = false;

window.SyncUI = {
  toggle() {
    _drawerOpen = !_drawerOpen;
    document.getElementById('sync-drawer').style.display = _drawerOpen ? 'block' : 'none';
  },

  async sendLink() {
    const email = document.getElementById('sync-email')?.value?.trim();
    if (!email) return;
    const msg = document.getElementById('sync-msg');
    try {
      await sendMagicLink(email);
      msg.textContent = '✉️ נשלח! בדקו את האימייל וחזרו לאפליקציה.';
    } catch(e) {
      msg.textContent = 'שגיאה: ' + e.message;
    }
  },

  async create() {
    try {
      const { join_code } = await createTrip('הטיול של עומרי וליאת');
      location.reload();
    } catch(e) {
      alert('שגיאה: ' + e.message);
    }
  },

  async join() {
    const code = document.getElementById('join-input')?.value?.trim();
    if (!code) return;
    try {
      await joinTrip(code);
      location.reload();
    } catch(e) {
      alert('קוד לא נמצא. בדקו שהקוד נכון.');
    }
  },

  async signOut() {
    await signOut();
    location.reload();
  },

  copyCode(code) {
    navigator.clipboard.writeText(code).then(() => {
      const el = document.getElementById('join-code-display');
      if (el) { el.textContent = 'הועתק ✓'; setTimeout(() => el.textContent = code, 2000); }
    });
  }
};

// ─── Remote change handler — updates app.js state ──────────────────────────
function onRemoteChange(change) {
  if (change.type === 'full') {
    // Reload visited and checked from localStorage (already written by sync.js)
    if (window.visited !== undefined) {
      try { window.visited = JSON.parse(localStorage.getItem('tatry-visited-v1') || '{}'); } catch {}
    }
    if (window.checked !== undefined) {
      try { window.checked = JSON.parse(localStorage.getItem('tatry-checklist-v1') || '{}'); } catch {}
    }
    // Re-render current view
    if (typeof render === 'function') render();
    return;
  }

  if (change.type === 'visit') {
    if (window.visited !== undefined) window.visited[change.activityId] = change.done;
    // Update all matching checkboxes in DOM
    document.querySelectorAll(`[data-visit="${change.activityId}"]`).forEach(el => {
      el.checked = change.done;
      el.closest('label')?.classList.toggle('done', change.done);
    });
    if (typeof visitsView === 'function' && document.getElementById('main')?.querySelector('.visitchecks')) {
      visitsView();
    }
    return;
  }

  if (change.type === 'check') {
    if (window.checked !== undefined) window.checked[change.key] = change.done;
    document.querySelectorAll(`[data-check="${change.key}"]`).forEach(el => {
      el.checked = change.done;
    });
    return;
  }

  if (change.type === 'budget' || change.type === 'expense') {
    // Re-render budget view if active
    if (typeof TripTools !== 'undefined' && TripTools.budgetView && 
        document.querySelector('.budgetview')) {
      TripTools.budgetView();
    }
  }
}

// ─── Wire into app.js events ────────────────────────────────────────────────
function wireAppEvents() {
  // Intercept visit checkbox changes
  document.addEventListener('change', e => {
    if (e.target.matches('[data-visit]')) {
      syncVisit(e.target.dataset.visit, e.target.checked);
    }
    if (e.target.matches('[data-check]')) {
      syncCheck(String(e.target.dataset.check), e.target.checked);
    }
  }, true); // capture phase — runs before app.js handler
}

// ─── Bootstrap ──────────────────────────────────────────────────────────────
async function boot() {
  injectAuthPanel();
  wireAppEvents();

  const session = await getSession();

  if (!session) {
    setDot('yellow');
    setLabel('כניסה');
    drawerLoggedOut();
    // Listen for magic link redirect
    onAuthChange(async s => { if (s) location.reload(); });
    return;
  }

  const { user } = session;
  _userId = user.id;
  setDot('green');
  setLabel('מסונכרן');

  const tripId = await initSync(user.id, onRemoteChange);

  if (!tripId) {
    drawerNoTrip(user.email);
    return;
  }

  const joinCode = getJoinCode();
  drawerLoggedIn(user.email, joinCode, tripId);

  // Expose syncExpense and syncBudget for trip-tools.js
  window._syncExpense = syncExpense;
  window._syncBudget  = syncBudget;
  window._fetchExpenses = fetchExpenses;
  window._deleteExpense = deleteExpense;
}

function setDot(color) {
  const d = document.getElementById('sync-dot');
  if (d) { d.className = 'dot' + (color === 'green' ? ' green' : ''); }
}
function setLabel(label) {
  const l = document.getElementById('sync-fab-label');
  if (l) l.textContent = label;
}

boot();
