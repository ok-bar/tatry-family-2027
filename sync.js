// sync.js — Supabase real-time sync for tatry-family-2027
// Syncs: visited, checked, expenses, budget between all devices in the same trip
// Files stay in IndexedDB locally — never uploaded

const SUPA_URL = 'https://zszmhanowbfwbtjmdwmz.supabase.co';
const SUPA_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpzem1oYW5vd2Jmd2J0am1kd216Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0Mzc1OTQsImV4cCI6MjA5MzAxMzU5NH0.A5fh3r6Tfl0yFub_xfBIkqXDzQBYs8zJ7rdmea0oaBs';

// ─── Supabase client (loaded from CDN in index.html) ───────────────────────
let _supa = null;
function supa() {
  if (!_supa) _supa = window.supabase.createClient(SUPA_URL, SUPA_KEY);
  return _supa;
}

// ─── State ─────────────────────────────────────────────────────────────────
let _tripId   = null;
let _userId   = null;
let _channel  = null;
let _online   = navigator.onLine;

window.addEventListener('online',  () => { _online = true;  _flushQueue(); });
window.addEventListener('offline', () => { _online = false; });

// Offline write queue — flushed when connection returns
const QUEUE_KEY = 'tatry-sync-queue-v1';
function _loadQueue()       { try { return JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]'); } catch { return []; } }
function _saveQueue(q)      { try { localStorage.setItem(QUEUE_KEY, JSON.stringify(q)); } catch {} }
function _enqueue(op)       { const q = _loadQueue(); q.push(op); _saveQueue(q); }

async function _flushQueue() {
  if (!_tripId || !_online) return;
  const q = _loadQueue();
  if (!q.length) return;
  _saveQueue([]);
  for (const op of q) {
    try { await _execOp(op); } catch { _enqueue(op); } // re-queue on failure
  }
}

async function _execOp(op) {
  if (op.type === 'visit')   return _pushVisit(op.activityId, op.done);
  if (op.type === 'check')   return _pushCheck(op.checkKey,   op.done);
  if (op.type === 'expense') return _pushExpense(op.expense);
  if (op.type === 'budget')  return _pushBudget(op.cents);
}

// ─── Auth — magic link ─────────────────────────────────────────────────────
export async function sendMagicLink(email) {
  const { error } = await supa().auth.signInWithOtp({
    email,
    options: { emailRedirectTo: location.origin }
  });
  if (error) throw error;
}

export async function getSession() {
  const { data } = await supa().auth.getSession();
  return data.session;
}

export function onAuthChange(cb) {
  supa().auth.onAuthStateChange((_event, session) => cb(session));
}

export async function signOut() {
  await supa().auth.signOut();
  _tripId = null; _userId = null;
  if (_channel) { supa().removeChannel(_channel); _channel = null; }
}

// ─── Trip create / join ────────────────────────────────────────────────────
export async function createTrip(name = 'הטיול שלנו') {
  const { data, error } = await supa().rpc('tatry_create_trip', { p_name: name });
  if (error) throw error;
  const row = data[0];
  localStorage.setItem('tatry-trip-id-v1',   row.trip_id);
  localStorage.setItem('tatry-join-code-v1',  row.join_code);
  return row;
}

export async function joinTrip(code) {
  const { data, error } = await supa().rpc('tatry_join_trip', { p_join_code: code });
  if (error) throw error;
  const row = data[0];
  localStorage.setItem('tatry-trip-id-v1', row.trip_id);
  return row;
}

export function getJoinCode() {
  return localStorage.getItem('tatry-join-code-v1') || null;
}

// ─── Init — call after auth is confirmed ───────────────────────────────────
export async function initSync(userId, onRemoteChange) {
  _userId = userId;
  _tripId = localStorage.getItem('tatry-trip-id-v1');
  if (!_tripId) return null; // not yet in a trip

  // Load all remote state and merge into local
  await _pullAll(onRemoteChange);

  // Subscribe to realtime changes
  _channel = supa()
    .channel('trip:' + _tripId)
    .on('postgres_changes', {
      event: '*', schema: 'public', table: 'tatry_trip_visits',
      filter: 'trip_id=eq.' + _tripId
    }, payload => _handleVisitChange(payload, onRemoteChange))
    .on('postgres_changes', {
      event: '*', schema: 'public', table: 'tatry_trip_expenses',
      filter: 'trip_id=eq.' + _tripId
    }, payload => _handleExpenseChange(payload, onRemoteChange))
    .on('postgres_changes', {
      event: '*', schema: 'public', table: 'tatry_trip_settings',
      filter: 'trip_id=eq.' + _tripId
    }, payload => _handleSettingsChange(payload, onRemoteChange))
    .subscribe();

  await _flushQueue();
  return _tripId;
}

// ─── Pull all remote state on connect ──────────────────────────────────────
async function _pullAll(cb) {
  const [visits, expenses, settings] = await Promise.all([
    supa().from('tatry_trip_visits').select('*').eq('trip_id', _tripId),
    supa().from('tatry_trip_expenses').select('*').eq('trip_id', _tripId),
    supa().from('tatry_trip_settings').select('*').eq('trip_id', _tripId).maybeSingle()
  ]);

  // Merge visits → local visited + checked
  const visited = {};
  const checked = {};
  (visits.data || []).forEach(r => {
    if (r.activity_id.startsWith('check:')) {
      checked[r.activity_id.slice(6)] = r.done;
    } else {
      visited[r.activity_id] = r.done;
    }
  });

  // Write to localStorage (app.js reads these)
  try {
    localStorage.setItem('tatry-visited-v1',   JSON.stringify(visited));
    localStorage.setItem('tatry-checklist-v1', JSON.stringify(checked));
    if (settings.data) {
      localStorage.setItem('tatry-budget-v1', String(settings.data.budget_cents));
    }
  } catch {}

  cb({ type: 'full', visited, checked,
       expenses: expenses.data || [],
       budgetCents: settings.data?.budget_cents ?? 0 });
}

// ─── Realtime handlers ─────────────────────────────────────────────────────
function _handleVisitChange({ new: r }, cb) {
  if (!r || r.updated_by === _userId) return; // ignore own writes
  if (r.activity_id.startsWith('check:')) {
    const checked = _localChecked();
    checked[r.activity_id.slice(6)] = r.done;
    try { localStorage.setItem('tatry-checklist-v1', JSON.stringify(checked)); } catch {}
    cb({ type: 'check', key: r.activity_id.slice(6), done: r.done });
  } else {
    const visited = _localVisited();
    visited[r.activity_id] = r.done;
    try { localStorage.setItem('tatry-visited-v1', JSON.stringify(visited)); } catch {}
    cb({ type: 'visit', activityId: r.activity_id, done: r.done });
  }
}

function _handleExpenseChange({ eventType, new: r, old: o }, cb) {
  if (r?.updated_by === _userId) return;
  cb({ type: 'expense', eventType, expense: r, oldId: o?.expense_id });
}

function _handleSettingsChange({ new: r }, cb) {
  if (!r || r.updated_by === _userId) return;
  try { localStorage.setItem('tatry-budget-v1', String(r.budget_cents)); } catch {}
  cb({ type: 'budget', budgetCents: r.budget_cents });
}

// ─── Writes — called from app.js ───────────────────────────────────────────
export async function syncVisit(activityId, done) {
  // Update local immediately
  const v = _localVisited();
  v[activityId] = done;
  try { localStorage.setItem('tatry-visited-v1', JSON.stringify(v)); } catch {}

  const op = { type: 'visit', activityId, done };
  if (!_tripId || !_online) { _enqueue(op); return; }
  try { await _pushVisit(activityId, done); }
  catch { _enqueue(op); }
}

export async function syncCheck(checkKey, done) {
  const c = _localChecked();
  c[checkKey] = done;
  try { localStorage.setItem('tatry-checklist-v1', JSON.stringify(c)); } catch {}

  const op = { type: 'check', checkKey, done };
  if (!_tripId || !_online) { _enqueue(op); return; }
  try { await _pushCheck(checkKey, done); }
  catch { _enqueue(op); }
}

export async function syncExpense(expense) {
  const op = { type: 'expense', expense };
  if (!_tripId || !_online) { _enqueue(op); return; }
  try { await _pushExpense(expense); }
  catch { _enqueue(op); }
}

export async function syncBudget(cents) {
  try { localStorage.setItem('tatry-budget-v1', String(cents)); } catch {}
  const op = { type: 'budget', cents };
  if (!_tripId || !_online) { _enqueue(op); return; }
  try { await _pushBudget(cents); }
  catch { _enqueue(op); }
}

// ─── Remote pushes ─────────────────────────────────────────────────────────
async function _pushVisit(activityId, done) {
  const { error } = await supa().from('tatry_trip_visits').upsert({
    trip_id: _tripId, activity_id: activityId,
    done, updated_at: new Date().toISOString(), updated_by: _userId
  }, { onConflict: 'trip_id,activity_id' });
  if (error) throw error;
}

async function _pushCheck(checkKey, done) {
  return _pushVisit('check:' + checkKey, done);
}

async function _pushExpense(expense) {
  const { error } = await supa().from('tatry_trip_expenses').upsert({
    trip_id: _tripId,
    expense_id:   expense.id,
    title:        expense.title,
    place:        expense.place || 'general',
    category:     expense.category || 'אטרקציות',
    currency:     expense.currency,
    amount_cents: expense.amountCents,
    eur_cents:    expense.eurCents,
    expense_date: expense.date,
    rate:         expense.rate ?? null,
    updated_at:   new Date().toISOString(),
    updated_by:   _userId
  }, { onConflict: 'trip_id,expense_id' });
  if (error) throw error;
}

async function _pushBudget(cents) {
  const { error } = await supa().from('tatry_trip_settings').upsert({
    trip_id: _tripId, budget_cents: cents,
    updated_at: new Date().toISOString(), updated_by: _userId
  }, { onConflict: 'trip_id' });
  if (error) throw error;
}

// ─── Helpers ───────────────────────────────────────────────────────────────
function _localVisited() { try { return JSON.parse(localStorage.getItem('tatry-visited-v1') || '{}'); } catch { return {}; } }
function _localChecked() { try { return JSON.parse(localStorage.getItem('tatry-checklist-v1') || '{}'); } catch { return {}; } }

// ─── Fetch all expenses (for budget view) ──────────────────────────────────
export async function fetchExpenses() {
  if (!_tripId) return [];
  const { data, error } = await supa().from('tatry_trip_expenses').select('*').eq('trip_id', _tripId).order('expense_date');
  if (error) throw error;
  return data;
}

export async function deleteExpense(expenseId) {
  if (!_tripId) return;
  const { error } = await supa().from('tatry_trip_expenses').delete()
    .eq('trip_id', _tripId).eq('expense_id', expenseId);
  if (error) throw error;
}
