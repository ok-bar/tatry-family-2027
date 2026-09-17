// scripts/geocode-places.mjs
// One-time geocoding script — run manually, NOT part of the live site.
// Respects Nominatim usage policy: max 1 req/sec, identified User-Agent.
// Usage: node scripts/geocode-places.mjs
// Output: data/coordinates.json — { "<place-id>": { "lat": ..., "lng": ..., "display_name": "..." } }

import { writeFile, readFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';

const DATA_JS_PATH = new URL('../data.js', import.meta.url);
const OUT_PATH = new URL('../data/coordinates.json', import.meta.url);
const OUT_DIR = new URL('../data/', import.meta.url);

// Nominatim requires a real identifying User-Agent — replace with your contact if you like
const USER_AGENT = 'tatry-family-2027-tripplanner/1.0 (personal use, one-time geocode)';
const DELAY_MS = 1100; // stay under Nominatim's 1 req/sec limit, with margin

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function loadPlaces() {
  const src = await readFile(DATA_JS_PATH, 'utf8');
  // Extract the PLACES = [...] array via a safe sandboxed eval of just that slice.
  const match = src.match(/const\s+PLACES\s*=\s*(\[[\s\S]*?\n\]);/);
  if (!match) throw new Error('Could not find PLACES array in data.js — check the file structure.');
  // eslint-disable-next-line no-new-func
  const PLACES = new Function(`return ${match[1]}`)();
  return PLACES;
}

async function geocodeOne(query) {
  const url = 'https://nominatim.openstreetmap.org/search?' + new URLSearchParams({
    q: query,
    format: 'json',
    limit: '1',
    addressdetails: '0'
  });
  const res = await fetch(url, { headers: { 'User-Agent': USER_AGENT } });
  if (!res.ok) throw new Error(`Nominatim HTTP ${res.status} for "${query}"`);
  const rows = await res.json();
  if (!rows.length) return null;
  const r = rows[0];
  return { lat: parseFloat(r.lat), lng: parseFloat(r.lon), display_name: r.display_name };
}

async function main() {
  const places = await loadPlaces();
  console.log(`Loaded ${places.length} places from data.js`);

  let existing = {};
  if (existsSync(OUT_PATH)) {
    existing = JSON.parse(await readFile(OUT_PATH, 'utf8'));
    console.log(`Found existing coordinates.json with ${Object.keys(existing).length} entries — will only fill in missing ones.`);
  }

  const results = { ...existing };
  const toGeocode = places.filter(p => p.map && !results[p.id]);
  console.log(`${toGeocode.length} places need geocoding (${places.length - toGeocode.length} already cached).`);

  for (const [i, p] of toGeocode.entries()) {
    process.stdout.write(`[${i + 1}/${toGeocode.length}] ${p.id} — "${p.map}" ... `);
    try {
      const geo = await geocodeOne(p.map);
      if (geo) {
        results[p.id] = geo;
        console.log(`✓ ${geo.lat.toFixed(5)}, ${geo.lng.toFixed(5)}`);
      } else {
        console.log('✗ no result — needs manual coordinates');
        results[p.id] = null;
      }
    } catch (err) {
      console.log(`✗ error: ${err.message}`);
      results[p.id] = null;
    }
    await sleep(DELAY_MS); // rate limit — do not remove
  }

  if (!existsSync(OUT_DIR)) await mkdir(OUT_DIR, { recursive: true });
  await writeFile(OUT_PATH, JSON.stringify(results, null, 2), 'utf8');

  const missing = Object.entries(results).filter(([, v]) => v === null).map(([k]) => k);
  console.log(`\nDone. Wrote ${Object.keys(results).length} entries to data/coordinates.json`);
  if (missing.length) {
    console.log(`\n⚠️  ${missing.length} places need MANUAL coordinates (Nominatim found nothing):`);
    missing.forEach(id => console.log('   - ' + id));
    console.log('Edit data/coordinates.json directly for these — search the place on openstreetmap.org and copy lat/lng.');
  }
}

main().catch(err => { console.error(err); process.exit(1); });
