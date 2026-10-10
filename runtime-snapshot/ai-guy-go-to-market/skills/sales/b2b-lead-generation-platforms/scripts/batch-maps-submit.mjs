// Submit Google Maps scrapes for multiple cities in sequence
// Usage: node submit_batch.mjs
// Edit CITIES array and SEARCH_QUERY before running

import { maps, wallet } from './lib/client.mjs';
import { writeFileSync } from 'fs';

// CONFIGURE THESE:
const SEARCH_QUERY = 'real estate agent';
const LIMIT = 10;  // places per city ($0.01 each)
const DELAY_MS = 200;  // between calls

const CITIES = [
  "Miami, FL", "Fort Lauderdale, FL", "Tampa, FL", "Orlando, FL"
  // ... add all cities
];

// Check wallet
try {
  const w = await wallet();
  console.log(`Balance: $${w.balanceUsd || '?'} — est. max cost: $${(CITIES.length * LIMIT * 0.01).toFixed(2)}`);
} catch(e) {
  console.log(`Wallet check failed: ${e.message}`);
}

const results = [];
let submitted = 0;
let failed = 0;

for (let i = 0; i < CITIES.length; i++) {
  const city = CITIES[i];
  try {
    const r = await maps(SEARCH_QUERY, city, LIMIT);
    results.push({ city, ok: true, runId: r.runId, datasetId: r.datasetId });
    submitted++;
    console.log(`${i+1}/${CITIES.length} ✓ ${city} ${r.runId}`);
  } catch(e) {
    results.push({ city, ok: false, error: e.message, status: e.status });
    failed++;
    console.log(`${i+1}/${CITIES.length} ✗ ${city} ${e.message}`);
  }
  
  if (i < CITIES.length - 1) {
    await new Promise(r => setTimeout(r, DELAY_MS));
  }
}

const ok = results.filter(r => r.ok);
const runIds = ok.map(r => r.runId);

writeFileSync('/tmp/fl_maps_all_ids.json', JSON.stringify({
  search_query: SEARCH_QUERY,
  limit: LIMIT,
  total: CITIES.length,
  submitted,
  failed,
  run_ids: runIds,
  est_max_cost: (CITIES.length * LIMIT * 0.01).toFixed(2),
  timestamp: Date.now()
}, null, 2));

console.log(`\nDone: ${submitted}/${CITIES.length} submitted, ${failed} failed`);
console.log(`Run IDs saved to /tmp/fl_maps_all_ids.json`);
console.log(`Next: run scripts/batch-maps-poll-merge.mjs to collect results`);
