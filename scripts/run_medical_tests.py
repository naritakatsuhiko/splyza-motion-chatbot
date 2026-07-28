#!/usr/bin/env python3
"""Run Medical chatbot test cases against local API and save raw results."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CASES_PATH = BASE / "test_cases_medical.json"
OUT_DIR = BASE / "test_results"
OUT_DIR.mkdir(exist_ok=True)
RAW_PATH = OUT_DIR / "raw_responses.json"
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
    return {
        "auto_pass": len(failures) == 0,
        "auto_failures": failures,
    }


def main() -> None:
    suite = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = suite["cases"]
    results = []
    print(f"Running {len(cases)} cases against {API}")
    for i, case in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] {case['id']} ...", flush=True)
        resp = ask(case["question"])
        checks = auto_checks(case, resp.get("text") or "")
        row = {
            **case,
            **resp,
            **checks,
            "answered_at": datetime.now(timezone.utc).isoformat(),
        }
        results.append(row)
        status = "AUTO_PASS" if checks["auto_pass"] and resp["ok"] else "AUTO_FAIL"
        print(
            f"  -> {status} ({resp['elapsed_sec']}s) failures={checks['auto_failures']}",
            flush=True,
        )
        # mild pacing for API
        time.sleep(1.0)

    payload = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "api": API,
        "count": len(results),
        "auto_pass": sum(1 for r in results if r["ok"] and r["auto_pass"]),
        "auto_fail": sum(1 for r in results if not (r["ok"] and r["auto_pass"])),
        "results": results,
    }
    RAW_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {RAW_PATH}")
    print(f"AUTO_PASS={payload['auto_pass']} AUTO_FAIL={payload['auto_fail']}")


if __name__ == "__main__":
    main()
