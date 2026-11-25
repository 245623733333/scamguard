# ScamGuard — On-device SMS scam detection with a Llama explainer
Bharat AI-SoC Challenge 2026-27 · Problem Statement 3 · Use case A (SMS scam detection)

Runs **offline on an Arm device** (target: Raspberry Pi 5). No cloud calls; no data leaves the device.

## Pipeline
```
SMS -> rules + URL checks ----+
SMS -> TF-IDF + LogReg (ML) --+--> risk fusion --> verdict + reasons
                                        |
            Llama 3.2 Instruct via ExecuTorch (Arm CPU, XNNPACK) -> plain-language explanation + one action
            (deterministic template fallback if the LLM is unavailable; the output states which was used)
```
The detector decides; Llama only explains. Classifier/rules run in Python on the CPU; Llama runs in a separate ExecuTorch process. No NPU/Hailo is used unless stated in the report.

## Quick start
```
pip install -r requirements.txt
python scripts/get_uci.py      # one-time download (UCI SMS Spam Collection)
python scripts/train.py        # dedup, split, train, tune threshold on validation
python scripts/evaluate.py     # -> results/metrics.json
python -m scamguard.cli "Your SBI account will be blocked. Update KYC at http://sbi-kyc.xyz"
```
## On a phone (Termux, no sklearn): see docs/PHONE_SETUP.md
`python scripts/export_lite.py` creates `models/clf_lite.json`; the CLI/demo/benchmark use it automatically.

## On the Arm device (see docs/ON_DEVICE_SETUP.md)
```
export LLAMA_RUNNER=... LLAMA_PTE=... LLAMA_TOKENIZER=...
python scripts/demo.py                                   # scripted demo for the video
python scripts/benchmark.py --trials 30 --note "Llama-3.2-1B 8da4w, 4 threads"
python scripts/make_report.py                            # fills docs/REPORT_filled.md from results/*.json
```
Without the LLAMA_* variables the app uses the template explainer and says so.

## Data and honesty notes
- `data/indian_test_set.csv` (30) and `indian_train_seed.csv` (24) were hand-written by the authors to mimic Indian SMS styles; they are small and not real captured SMS.
- Rules were designed while looking at the test examples, so rules-only scores on that set are optimistic.
- Llama use is subject to the Meta Llama license ("Built with Llama" attribution).

## Design notes (aligned with challenge session guidance)
- LLM is advisory only: it receives structured evidence and cannot change the verdict. It is invoked only for scam/suspicious messages (set `LLAMA_ALWAYS=1` to force); the benchmark reports the invocation rate.
- Known limitation: the current runner starts `llama_main` per explanation (model reloaded each time). A persistent service that loads the model once is the planned improvement.
- No message content is stored; the app does not click links or delete messages.
- Detector updates (rules/model) can be installed locally when connected; detection works fully offline.
- Not yet covered: Hindi/regional/code-mixed messages, real collected data, near-duplicate/campaign-aware splits.
