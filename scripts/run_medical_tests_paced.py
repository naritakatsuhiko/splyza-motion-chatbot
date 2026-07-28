#!/usr/bin/env python3
"""Run selected Medical test cases slowly (free-tier friendly).

Examples:
  python3 scripts/run_medical_tests_paced.py --ids F01
  python3 scripts/run_medical_tests_paced.py --ids F01,F02,F03 --sleep 90
  python3 scripts/run_medical_tests_paced.py --category F_EXTRA --sleep 120
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CASES_PATH = BASE / "test_cases_medical.json"
OUT_DIR = BASE / "test_results"
RAW_EXTRA = OUT_DIR / "raw_responses_extra.json"
API = "http://localhost:3001/api/query"


def ask(message: str, timeout: int = 120) -> dict:
    body = json.dumps({"message": message}).encode("utf-8")
    req = urllib.request.Request(
        API,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            data = json.loads(res.read().decode("utf-8"))
            return {
                "ok": True,
                "status": res.status,
                "elapsed_sec": round(time.time() - started, 2),
                "text": data.get("text") or "",
                "error": data.get("error"),
            }
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "status": None,
            "elapsed_sec": round(time.time() - started, 2),
            "text": "",
            "error": str(e),
        }


def auto_checks(case: dict, text: str) -> dict:
    t = text or ""
    failures = []
    for s in case.get("must_include_all") or []:
        if s and s not in t:
            failures.append(f"missing_all:{s}")
    any_list = case.get("must_include_any") or []
    if any_list and not any(s in t for s in any_list if s):
        failures.append(f"missing_any:{any_list}")
    url_part = case.get("must_url_contains")
    if url_part and url_part not in t:
        failures.append(f"missing_url:{url_part}")
    for s in case.get("must_not_include") or []:
        if s and s in t:
            failures.append(f"forbidden:{s}")
    return {"auto_pass": len(failures) == 0, "auto_failures": failures}


def load_existing() -> dict:
    if RAW_EXTRA.exists():
        return json.loads(RAW_EXTRA.read_text(encoding="utf-8"))
    return {"results": [], "by_id": {}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", default="", help="Comma-separated IDs, e.g. F01,F02")
    parser.add_argument("--category", default="", help="e.g. F_EXTRA")
    parser.add_argument("--sleep", type=int, default=90, help="Seconds between requests")
    parser.add_argument("--model-note", default="gemini-3.5-flash via local API")
    args = parser.parse_args()

    suite = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = suite["cases"]
    if args.ids:
        want = {x.strip() for x in args.ids.split(",") if x.strip()}
        cases = [c for c in cases if c["id"] in want]
    elif args.category:
        cases = [c for c in cases if c.get("category") == args.category]
    else:
        raise SystemExit("Specify --ids or --category")

    if not cases:
        raise SystemExit("No matching cases")

    existing = load_existing()
    by_id = {r["id"]: r for r in existing.get("results", [])}

    print(
        f"Running {len(cases)} case(s) against {API} with {args.sleep}s pacing",
        flush=True,
    )
    for i, case in enumerate(cases, 1):
        if i > 1:
            print(f"sleep {args.sleep}s ...", flush=True)
            time.sleep(args.sleep)
        print(f"[{i}/{len(cases)}] {case['id']} ...", flush=True)
        resp = ask(case["question"])
        err = resp.get("error") or ""
        if (not resp["ok"]) or ("429" in err) or ("503" in err) or ("RESOURCE_EXHAUSTED" in err):
            print("  transient error, wait 70s and retry once", flush=True)
            time.sleep(70)
            resp = ask(case["question"])
        checks = auto_checks(case, resp.get("text") or "")
        row = {
            **case,
            **resp,
            **checks,
            "test_model": args.model_note,
            "answered_at": datetime.now(timezone.utc).isoformat(),
        }
        by_id[case["id"]] = row
        status = "AUTO_PASS" if checks["auto_pass"] and resp["ok"] else "AUTO_FAIL"
        preview = (resp.get("text") or resp.get("error") or "").replace("\n", " ")[:120]
        print(f"  -> {status} ({resp['elapsed_sec']}s) {checks['auto_failures']}", flush=True)
        print(f"  preview: {preview}", flush=True)

    # Keep previous extra results + newly run ones
    ordered_ids = [c["id"] for c in json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]]
    results = [by_id[i] for i in ordered_ids if i in by_id]
    # Also keep any orphan IDs
    for i, row in by_id.items():
        if i not in {r["id"] for r in results}:
            results.append(row)

    out = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "api": API,
        "model_note": args.model_note,
        "count": len(results),
        "auto_pass": sum(1 for r in results if r.get("ok") and r.get("auto_pass")),
        "auto_fail": sum(1 for r in results if not (r.get("ok") and r.get("auto_pass"))),
        "results": results,
    }
    OUT_DIR.mkdir(exist_ok=True)
    RAW_EXTRA.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {RAW_EXTRA}", flush=True)
    print(f"EXTRA AUTO_PASS={out['auto_pass']} AUTO_FAIL={out['auto_fail']}", flush=True)


if __name__ == "__main__":
    main()
