"""Usage: python -m scamguard.cli "message"   |   python -m scamguard.cli --interactive"""
import argparse, sys
from .pipeline import ScamGuard
ICON = {"scam": "[!! SCAM]", "suspicious": "[? SUSPICIOUS]", "safe": "[OK SAFE]"}

def show(sg, text):
    r = sg.analyze(text); v = r["verdict"]
    print(f"\n{ICON[v.label]}  risk={v.score:.2f}  (ML={v.clf_prob:.2f}, rules={v.rule_score:.2f})")
    print(r["explanation"])
    print(f"-- detect {r['detect_ms']:.1f} ms | total {r['total_ms']:.0f} ms | explainer: {r['explain_info']['source']}")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("text", nargs="?"); ap.add_argument("--interactive", action="store_true")
    ap.add_argument("--model", default="models/clf_lite.json" if __import__("os").path.exists("models/clf_lite.json") else "models/clf.joblib"); a = ap.parse_args()
    sg = ScamGuard(a.model)
    if a.text: show(sg, a.text)
    elif a.interactive:
        print("Paste an SMS and press Enter (Ctrl-C to quit).")
        for line in sys.stdin:
            if line.strip(): show(sg, line.strip())
    else: ap.print_help()
if __name__ == "__main__": main()
