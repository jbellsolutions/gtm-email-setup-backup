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
  create-campaign) # name subject list_ids_csv body_file [content_type] [from_email] [template_id] [reply_to]
    name="${1:?usage: create-campaign NAME SUBJECT LIST_IDS BODY_FILE [content_type] [from_email] [template_id] [reply_to]}"
    subject="${2:?subject required}"; ids="${3:?list ids required}"; bodyfile="${4:?body file required}"
    ctype="${5:-html}"; from_email="${6:-}"; template_id="${7:-}"; reply_to="${8:-}"
    body=$(python3 -c 'import json,sys; print(json.dumps(open(sys.argv[1]).read()))' "$bodyfile")
    # Build JSON with optional fields
    python3 -c "
import json,sys
payload = {
    'name': sys.argv[1],
    'subject': sys.argv[2],
    'lists': [int(x) for x in sys.argv[3].split(',')],
    'type': 'regular',
    'content_type': sys.argv[4],
    'body': open(sys.argv[5]).read(),
    'messenger': 'email',
}
if sys.argv[6]: payload['from_email'] = sys.argv[6]
if sys.argv[7]: payload['template_id'] = int(sys.argv[7])
if sys.argv[8]: payload['headers'] = [{'key': 'Reply-To', 'value': sys.argv[8]}]
print(json.dumps(payload))
" "$name" "$subject" "$ids" "$ctype" "$bodyfile" "$from_email" "$template_id" "$reply_to" > /tmp/lm_create_payload.json
    req POST /api/campaigns "$(cat /tmp/lm_create_payload.json)" ;;
  test-campaign) # campaign_id email [email2 email3 ...]
    id="${1:?usage: test-campaign ID EMAIL [EMAIL2 ...]}"; shift
    emails="$*"
    [ -n "$emails" ] || { echo "usage: test-campaign ID EMAIL [EMAIL2 ...]"; exit 1; }
    camp=$(curl -sS --fail-with-body "${AUTH[@]}" "${BASE}/api/campaigns/$id")
    printf '%s' "$camp" | python3 -c '
import json,sys
c=json.load(sys.stdin)["data"]
# Include ALL fields the test endpoint needs — missing messenger/from_email/headers cause failures
payload={k:c[k] for k in ("name","subject","type","content_type","body","messenger","from_email","template_id","headers") if k in c and c[k] is not None}
payload["lists"]=[l["id"] if isinstance(l,dict) else l for l in c.get("lists",[])]
if "template_id" not in payload: payload["template_id"]=1
emails=sys.argv[1].split()
payload["subscribers"]=emails
print(json.dumps(payload))' "$emails" > /tmp/lm_test_payload.json
    curl -sS --fail-with-body -X POST "${AUTH[@]}" -H "Content-Type: application/json" \
      -d @/tmp/lm_test_payload.json "${BASE}/api/campaigns/$id/test" | json ;;
  update-campaign) # campaign_id  — updates a draft campaign (args: key=value pairs passed as JSON via stdin)
    id="${1:?usage: update-campaign ID  (pipe JSON body via stdin)}"
    body=$(cat)
    req PUT "/api/campaigns/$id" "$body" ;;
  start-campaign) # campaign_id  — BEGINS REAL SENDING
    id="${1:?usage: start-campaign ID}"
    req PUT "/api/campaigns/$id/status" '{"status":"running"}' ;;
  upload-media) # file_path  — uploads an image/file, returns hosted URL
    filepath="${1:?usage: upload-media FILE_PATH}"
    curl -sS --fail-with-body "${AUTH[@]}" -F "file=@${filepath}" "${BASE}/api/media" | json ;;
  tx) # template_id email [data_json]
    tid="${1:?usage: tx TEMPLATE_ID EMAIL [DATA_JSON]}"; email="${2:?email required}"
    req POST /api/tx "$(printf '{"template_id":%s,"subscriber_email":"%s","data":%s}' "$tid" "$email" "${3:-{}}")" ;;
  logs)
    req GET /api/logs ;;
  raw) # METHOD PATH [JSON]
    req "${1:?usage: raw METHOD /api/... [JSON]}" "${2:?path required}" "${3:-}" ;;
  help|*)
    grep -E '^\s{2}[a-z-]+\)' "$0" | sed 's/).*//' | tr -d ' ' ; ;;
esac
