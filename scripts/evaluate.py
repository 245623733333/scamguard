"""Evaluate ML-only, rules-only and fused system on UCI held-out test + Indian hand-written set. Writes results/metrics.json."""
import json, os, sys
import numpy as np, pandas as pd
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scamguard import classifier
from scamguard.fusion import fuse

model = classifier.load("models/clf.joblib")
meta = json.load(open("models/clf.joblib.json"))

def metrics(y, pred):
    p, r, f, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return dict(precision=round(float(p), 4), recall=round(float(r), 4), f1=round(float(f), 4), fpr=round(float(fp / max(fp + tn, 1)), 4),
                tp=int(tp), fp=int(fp), tn=int(tn), fn=int(fn), n=int(len(y)))

def run(df):
    probs = model.predict_proba(df.text)[:, 1]; y = df.label.values
    out = {"ml_only": metrics(y, (probs >= meta["ml_threshold"]).astype(int))}
    vs = [fuse(t, p) for t, p in zip(df.text, probs)]
    out["fused_scam_only"] = metrics(y, [int(v.label == "scam") for v in vs])
    out["fused_scam_or_suspicious"] = metrics(y, [int(v.label != "safe") for v in vs])
    out["rules_only"] = metrics(y, [int(v.rule_score >= 0.35) for v in vs])
    wrong = [(t, int(l), v.label, float(v.score)) for t, l, v in zip(df.text, y, vs) if (v.label == "scam") != bool(l)]
    return out, wrong

res = {}
for name, path in [("uci_test", "data/splits/test.csv"), ("indian_test", "data/indian_test_set.csv")]:
    res[name], wrong = run(pd.read_csv(path))
    print(f"\n== {name} =="); [print(f"  {k:26s}", v) for k, v in res[name].items()]
    print(f"  fused errors ({len(wrong)}):"); [print("   ", w) for w in wrong[:15]]
os.makedirs("results", exist_ok=True); json.dump(res, open("results/metrics.json", "w"), indent=2)
