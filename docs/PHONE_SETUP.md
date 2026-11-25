# Running ScamGuard on an Arm Android phone (Termux) - no sklearn needed on the phone
The detector on the phone is pure Python (`scamguard/lite.py`), verified against scikit-learn (max difference ~1e-16, see `scripts/export_lite.py`).

## On your laptop (once)
```
pip install -r requirements.txt
python scripts/get_uci.py && python scripts/train.py && python scripts/evaluate.py
python scripts/export_lite.py        # makes models/clf_lite.json; must print "max |lite - sklearn| ... e-1x"
```
Commit `models/clf_lite.json` to the repo (it is small) so the phone and reviewers can use it.

## On the phone
1. Install **Termux from F-Droid** (the Play Store version is outdated). Open it, then:
```
pkg update && pkg install python git
git clone https://github.com/<you>/scamguard.git && cd scamguard     # needs internet ONCE
python scripts/demo.py
```
(No internet for git? Copy the folder to the phone, run `termux-setup-storage`, then `cp -r ~/storage/downloads/scamguard ~/`.)
2. Prove it is Arm: run `uname -m` (should print `aarch64`) and `getprop ro.product.model`.
3. Turn on **Airplane mode** (and Wi-Fi off), then run `python scripts/demo.py` and `python scripts/benchmark.py --trials 30 --note "<phone model>, Termux, template explainer"`.
4. Screen-record with the phone's built-in screen recorder.

## Llama on the phone
ExecuTorch's Android Llama demo app can run a Llama `.pte` on the phone, but exporting the model and building/installing that app is a multi-hour job. If you do not complete it, state in the report and video: "Llama/ExecuTorch integration is implemented in code (`explainer.py`) but NOT demonstrated on-device; the demo uses the template explainer." Do not claim otherwise.
