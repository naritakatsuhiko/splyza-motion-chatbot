#!/usr/bin/env python3
from __future__ import annotations
import json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW_PATH = BASE / "test_results" / "raw_responses.json"
API = "http://localhost:3001/api/query"
SLEEP_SEC = 20

def ask(message: str, timeout: int = 120) -> dict:
    body = json.dumps({"message": message}).encode("utf-8")
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"}, method="POST")
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            data = json.loads(res.read().decode("utf-8"))
            return {"ok": True, "status": res.status, "elapsed_sec": round(time.time()-started,2), "text": data.get("text") or "", "error": data.get("error")}
    except Exception as e:
        return {"ok": False, "status": None, "elapsed_sec": round(time.time()-started,2), "text": "", "error": str(e)}

def auto_checks(case, text):
    t = text or ""
    failures = []
    for s in case.get("must_include_all") or []:
        if s and s not in t: failures.append(f"missing_all:{s}")
    any_list = case.get("must_include_any") or []
    if any_list and not any(s in t for s in any_list if s): failures.append(f"missing_any:{any_list}")
    url_part = case.get("must_url_contains")
    if url_part and url_part not in t: failures.append(f"missing_url:{url_part}")
    for s in case.get("must_not_include") or []:
        if s and s in t: failures.append(f"forbidden:{s}")
    return {"auto_pass": len(failures)==0, "auto_failures": failures}

def main():
    payload = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    failed = [r for r in payload["results"] if not (r.get("ok") and r.get("text"))]
    print(f"Retrying {len(failed)} failed cases with {SLEEP_SEC}s pacing", flush=True)
    by_id = {r["id"]: r for r in payload["results"]}
    for i, case in enumerate(failed, 1):
        print(f"[{i}/{len(failed)}] wait {SLEEP_SEC}s then {case['id']} ...", flush=True)
        time.sleep(SLEEP_SEC)
        resp = ask(case["question"])
        if not resp["ok"] and ("429" in (resp.get("error") or "") or "500" in (resp.get("error") or "")):
            print("  rate limited/error, wait 65s and retry once", flush=True)
            time.sleep(70)
            resp = ask(case["question"])
        checks = auto_checks(case, resp.get("text") or "")
        by_id[case["id"]] = {**case, **resp, **checks, "retried_at": datetime.now(timezone.utc).isoformat()}
        print(f"  -> {'AUTO_PASS' if checks['auto_pass'] and resp['ok'] else 'AUTO_FAIL'} ({resp['elapsed_sec']}s) {checks['auto_failures']}", flush=True)
    results = [by_id[r["id"]] for r in payload["results"]]
    out = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "api": API,
        "count": len(results),
        "auto_pass": sum(1 for r in results if r.get("ok") and r.get("auto_pass")),
        "auto_fail": sum(1 for r in results if not (r.get("ok") and r.get("auto_pass"))),
        "note": "Includes rate-limit retries with pacing",
        "results": results,
    }
    RAW_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {RAW_PATH}", flush=True)
    print(f"AUTO_PASS={out['auto_pass']} AUTO_FAIL={out['auto_fail']}", flush=True)

if __name__ == "__main__":
    main()
