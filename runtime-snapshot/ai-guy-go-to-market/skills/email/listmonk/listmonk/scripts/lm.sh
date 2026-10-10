#!/usr/bin/env bash
# lm.sh — listmonk API helper. Reads LISTMONK_URL, LISTMONK_USER, LISTMONK_TOKEN from env.
set -euo pipefail

: "${LISTMONK_URL:?Set LISTMONK_URL (e.g. https://your-instance.up.railway.app)}"
: "${LISTMONK_USER:?Set LISTMONK_USER (admin or API user name)}"
: "${LISTMONK_TOKEN:?Set LISTMONK_TOKEN (password or API token)}"

BASE="${LISTMONK_URL%/}"
AUTH=(-H "Authorization: token ${LISTMONK_USER}:${LISTMONK_TOKEN}")

json() { if command -v jq >/dev/null 2>&1; then jq .; else cat; fi; }

req() { # method path [json-body]
  local method="$1" path="$2" body="${3:-}"
  if [ -n "$body" ]; then
    curl -sS --fail-with-body -X "$method" "${AUTH[@]}" -H "Content-Type: application/json" \
      -d "$body" "${BASE}${path}" | json
  else
    curl -sS --fail-with-body -X "$method" "${AUTH[@]}" "${BASE}${path}" | json
  fi
}

cmd="${1:-help}"; shift || true

case "$cmd" in
  health)
    req GET /api/health ;;
  lists)
    req GET "/api/lists?per_page=100" ;;
  create-list) # name [public|private] [single|double]
    name="${1:?usage: create-list NAME [public|private] [single|double]}"
    req POST /api/lists "$(printf '{"name":"%s","type":"%s","optin":"%s"}' "$name" "${2:-private}" "${3:-single}")" ;;
  subs) # [list_id]
    if [ -n "${1:-}" ]; then req GET "/api/subscribers?list_id=$1&per_page=100"
    else req GET "/api/subscribers?per_page=100"; fi ;;
  add-sub) # email name list_ids_csv (e.g. 1,2)
    email="${1:?usage: add-sub EMAIL NAME LIST_IDS}"; name="${2:?name required}"; ids="${3:?list ids required, e.g. 1,2}"
    req POST /api/subscribers "$(printf '{"email":"%s","name":"%s","status":"enabled","lists":[%s],"preconfirm_subscriptions":true}' "$email" "$name" "$ids")" ;;
  campaigns)
    req GET "/api/campaigns?per_page=100&order=desc&order_by=created_at" ;;
  create-campaign) # name subject list_ids_csv body_file [content_type]
    name="${1:?usage: create-campaign NAME SUBJECT LIST_IDS BODY_FILE [content_type]}"
    subject="${2:?subject required}"; ids="${3:?list ids required}"; bodyfile="${4:?body file required}"
    ctype="${5:-html}"
    body=$(python3 -c 'import json,sys; print(json.dumps(open(sys.argv[1]).read()))' "$bodyfile")
    req POST /api/campaigns "$(printf '{"name":"%s","subject":"%s","lists":[%s],"type":"regular","content_type":"%s","body":%s}' "$name" "$subject" "$ids" "$ctype" "$body")" ;;
  test-campaign) # campaign_id email
    id="${1:?usage: test-campaign ID EMAIL}"; email="${2:?email required}"
    camp=$(curl -sS --fail-with-body "${AUTH[@]}" "${BASE}/api/campaigns/$id")
    printf '%s' "$camp" | python3 -c '
import json,sys
c=json.load(sys.stdin)["data"]
payload={k:c[k] for k in ("name","subject","lists","type","content_type","body") if k in c}
payload["lists"]=[l["id"] if isinstance(l,dict) else l for l in payload.get("lists",[])]
payload["subscribers"]=[sys.argv[1]]
print(json.dumps(payload))' "$email" > /tmp/lm_test_payload.json
    curl -sS --fail-with-body -X POST "${AUTH[@]}" -H "Content-Type: application/json" \
      -d @/tmp/lm_test_payload.json "${BASE}/api/campaigns/$id/test" | json ;;
  start-campaign) # campaign_id  — BEGINS REAL SENDING
    id="${1:?usage: start-campaign ID}"
    req PUT "/api/campaigns/$id/status" '{"status":"running"}' ;;
  tx) # template_id email [data_json]
    tid="${1:?usage: tx TEMPLATE_ID EMAIL [DATA_JSON]}"; email="${2:?email required}"
    req POST /api/tx "$(printf '{"template_id":%s,"subscriber_email":"%s","data":%s}' "$tid" "$email" "${3:-{\}}")" ;;
  raw) # METHOD PATH [JSON]
    req "${1:?usage: raw METHOD /api/... [JSON]}" "${2:?path required}" "${3:-}" ;;
  help|*)
    grep -E '^\s{2}[a-z-]+\)' "$0" | sed 's/).*//' | tr -d ' ' ; ;;
esac
