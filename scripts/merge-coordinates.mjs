// scripts/merge-coordinates.mjs
// One-time merge: takes the already-fetched data/coordinates.json (produced by
// an earlier run of the geocoder) and writes those points into map.js's
// MAP_POINTS object. Makes NO network requests — just merges local files.
//
// Usage: node scripts/merge-coordinates.mjs

import { readFile, writeFile } from 'node:fs/promises';

const COORDS_PATH = new URL('../data/coordinates.json', import.meta.url);
const MAP_JS_PATH  = new URL('../map.js', import.meta.url);

function extractMapPoints(mapJsSrc) {
  const match = mapJsSrc.match(/const\s+MAP_POINTS\s*=\s*(\{[\s\S]*?\});/);
  if (!match) throw new Error('Could not find MAP_POINTS object in map.js');
  // eslint-disable-next-line no-new-func
  return { points: new Function(`return ${match[1]}`)(), raw: match[0] };
}

async function main() {
  const [coordsRaw, mapJsSrc] = await Promise.all([
    readFile(COORDS_PATH, 'utf8'),
    readFile(MAP_JS_PATH, 'utf8')
  ]);

  const coords = JSON.parse(coordsRaw);
  const { points: existing, raw: existingBlock } = extractMapPoints(mapJsSrc);

  const merged = { ...existing };
  let added = 0, skippedNull = 0;

  for (const [id, v] of Object.entries(coords)) {
    if (v === null) { skippedNull++; continue; }       // failed geocodes — leave for manual entry
    if (merged[id]) continue;                          // already verified in map.js — don't overwrite
    merged[id] = {
      lat: v.lat,
      lon: v.lng ?? v.lon,                              // coordinates.json used "lng"; map.js uses "lon"
      source: v.display_name
        ? `https://nominatim.openstreetmap.org/ui/search.html?q=${encodeURIComponent(v.display_name)}`
        : 'https://www.openstreetmap.org/'
    };
    added++;
  }

  const sortedIds = Object.keys(merged).sort();
  const body = sortedIds.map(id => {
    const v = merged[id];
    return `  ${JSON.stringify(id)}:{lat:${v.lat},lon:${v.lon},source:${JSON.stringify(v.source)}}`;
  }).join(',\n');
  const newBlock = `const MAP_POINTS={\n${body}\n};`;

  const newMapJs = mapJsSrc.replace(existingBlock, newBlock);
  await writeFile(MAP_JS_PATH, newMapJs, 'utf8');

  console.log(`Merged ${added} new points into map.js (${sortedIds.length} total verified).`);
  if (skippedNull) console.log(`${skippedNull} places had no geocoding result and still need manual coordinates.`);
}

main().catch(err => { console.error(err); process.exit(1); });
