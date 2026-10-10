# Batch State Tracker

Python state tracker for multi-keyword Meta Ad Library batch extraction campaigns. Tracks completed keywords, cumulative advertisers, batch counts, and total scrolls.

## Usage

Initialize the campaign in execute_code:
```python
import json, os

ALL_KEYWORDS = [
    {"kw": "TRT clinic", "vertical": "Men's Health & Hormone"},
    {"kw": "medspa", "vertical": "Med Spas & Aesthetics"},
    # ...
]

OUTPUT_DIR = "/tmp/meta_ad_spray"
os.makedirs(OUTPUT_DIR, exist_ok=True)

state_file = f"{OUTPUT_DIR}/spray_state.json"
state = {
    "completed_keywords": [],
    "current_keyword_idx": 0,
    "cumulative_advertisers": {},
    "batch_num": 0,
    "total_scrolled": 0,
    "last_batch_count": 0,
    "no_growth_streak": 0,  # consecutive batches with 0 new advertisers
}

with open(state_file, "w") as f:
    json.dump(state, f)
```

After each batch (in execute_code), update and check exhaustion:
```python
with open(state_file) as f:
    state = json.load(f)

state["batch_num"] += 1
state["total_scrolled"] += 3

# Check for exhaustion
new_count = 73  # from browser_console result
delta = new_count - state.get("last_batch_count", 0)
state["last_batch_count"] = new_count

if delta == 0:
    state["no_growth_streak"] += 1
else:
    state["no_growth_streak"] = 0

if state["no_growth_streak"] >= 2:
    print(f"KEYWORD EXHAUSTED at batch {state['batch_num']}, {new_count} advertisers")
    state["completed_keywords"].append(state["current_keyword_idx"])
    state["current_keyword_idx"] += 1
    state["batch_num"] = 0
    state["total_scrolled"] = 0
    state["no_growth_streak"] = 0
    # Trigger next keyword navigation

with open(state_file, "w") as f:
    json.dump(state, f)
```