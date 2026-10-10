// Poll all Maps scrape runs, download completed ones, merge CSVs with phone dedup
// Usage: node poll_and_merge.mjs
// Requires: ALL_IDS_FILE at /tmp/fl_maps_all_ids.json with {run_ids: [...]}

import { status, download } from './lib/client.mjs';
import { readFileSync, writeFileSync, mkdirSync, existsSync, appendFileSync } from 'fs';

const data = JSON.parse(readFileSync('/tmp/fl_maps_all_ids.json', 'utf-8'));
const runIds = data.run_ids;
const OUT_DIR = '/tmp/fl_maps_results';
const MERGED = '/tmp/fl_real_estate_agents_all.csv';

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

// Load previous progress
const PROGRESS_FILE = '/tmp/fl_maps_progress.json';
let progress = {};
if (existsSync(PROGRESS_FILE)) {
  progress = JSON.parse(readFileSync(PROGRESS_FILE, 'utf-8'));
}

let done = 0;
let running = 0;
let failed = 0;
const doneFiles = [];

for (let i = 0; i < runIds.length; i++) {
  const rid = runIds[i];
  
  if (progress[rid] === 'downloaded') {
    done++;
    doneFiles.push(`${OUT_DIR}/${rid}.csv`);
    continue;
  }
  if (progress[rid] === 'failed') {
    failed++;
    continue;
  }
  
  try {
    const s = await status(rid);
    
    if (s.status === 'SUCCEEDED') {
      try {
        const outPath = `${OUT_DIR}/${rid}.csv`;
        const result = await download(rid, outPath);
        progress[rid] = 'downloaded';
        done++;
        doneFiles.push(outPath);
        console.log(`✓ [${done}/${runIds.length}] ${rid} (${result.bytes} bytes)`);
      } catch(e) {
        console.log(`✗ [${rid}] Download failed: ${e.message}`);
        progress[rid] = 'download_failed';
        failed++;
      }
    } else if (s.status === 'FAILED' || s.status === 'CANCELLED') {
      progress[rid] = 'failed';
      failed++;
      console.log(`✗ [${rid}] ${s.status}`);
    } else {
      progress[rid] = 'running';
      running++;
    }
  } catch(e) {
    console.log(`? [${rid}] Status error: ${e.message}`);
  }
  
  writeFileSync(PROGRESS_FILE, JSON.stringify(progress));
  if (i < runIds.length - 1) await new Promise(r => setTimeout(r, 50));
}

console.log(`\nStatus: ${done} done, ${running} running, ${failed} failed`);

// Merge when all done
if (done > 0 && done >= (runIds.length - failed)) {
  console.log(`\nMerging ${done} CSVs...`);
  
  const firstCSV = readFileSync(doneFiles[0], 'utf-8');
  const header = firstCSV.split('\n')[0];
  writeFileSync(MERGED, header + '\n');
  
  const seenPhones = new Set();
  let totalRows = 0;
  let rowsWithPhone = 0;
  
  for (const f of doneFiles) {
    const csv = readFileSync(f, 'utf-8');
    const rows = csv.split('\n').slice(1).filter(r => r.trim());
    
    for (const row of rows) {
      const phoneMatch = row.match(/(\+?1[-\s.]?)?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}/);
      const phone = phoneMatch ? phoneMatch[0].replace(/[^\d]/g, '') : null;
      
      if (phone && seenPhones.has(phone)) continue;
      if (phone) { seenPhones.add(phone); rowsWithPhone++; }
      
      appendFileSync(MERGED, row + '\n');
      totalRows++;
    }
  }
  
  console.log(`Merged: ${totalRows} rows, ${rowsWithPhone} with phone numbers → ${MERGED}`);
} else {
  console.log(`Still waiting: ${running} runs in progress`);
}
