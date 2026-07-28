# SPLYZA Motion Medical チャットボット検証用テストケース

Medical版のテストケースは以下を正とします。

- ケース定義: [`test_cases_medical.json`](./test_cases_medical.json)（40問）
- 最新結果: [`test_results/TEST_RESULTS_MEDICAL.md`](./test_results/TEST_RESULTS_MEDICAL.md)
- 生回答: [`test_results/raw_responses.json`](./test_results/raw_responses.json)

実行:

```bash
npm run dev   # http://localhost:3001
python3 scripts/run_medical_tests.py
# 失敗分の再実行（無料枠に注意。20秒間隔）
python3 scripts/retry_failed_tests.py
```

旧スポーツ版Motion用の設問は本ファイルでは扱いません（`pending_knowledge/legacy_motion_help/` 参照）。
