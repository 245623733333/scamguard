"""Train TF-IDF+LR on deduplicated UCI + Indian seed. Threshold tuned on VALIDATION only."""
import argparse, json, os, sys
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scamguard import classifier

def load_uci(path):
    df = pd.read_csv(path, sep="\t", header=None, names=["label", "text"], quoting=3, encoding="utf-8")
    df["label"] = (df["label"] == "spam").astype(int)
    return df

ap = argparse.ArgumentParser()
ap.add_argument("--uci", default="data/SMSSpamCollection"); ap.add_argument("--seed_in", default="data/indian_train_seed.csv")
ap.add_argument("--out", default="models/clf.joblib"); ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--max_fpr", type=float, default=0.01); a = ap.parse_args()

df = load_uci(a.uci)
n0 = len(df); df["key"] = df.text.str.lower().str.replace(r"\W+", " ", regex=True).str.strip()
df = df.drop_duplicates("key").drop(columns="key"); print(f"dedup: {n0} -> {len(df)}")
tr, tmp = train_test_split(df, test_size=0.30, stratify=df.label, random_state=a.seed)
va, te = train_test_split(tmp, test_size=0.50, stratify=tmp.label, random_state=a.seed)
seed = pd.read_csv(a.seed_in)
tr_aug = pd.concat([tr, pd.concat([seed] * 5)], ignore_index=True)
model = classifier.build().fit(tr_aug.text, tr_aug.label)

os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
p = model.predict_proba(va.text)[:, 1]
neg = p[va.label.values == 0]; pos = p[va.label.values == 1]
cands = np.linspace(0.05, 0.95, 91)
best = max((t for t in cands if (neg >= t).mean() <= a.max_fpr), key=lambda t: (pos >= t).mean(), default=0.5)
print(f"ML threshold on validation (FPR<={a.max_fpr}): {best:.2f}")
os.makedirs("data/splits", exist_ok=True)
tr.to_csv("data/splits/train.csv", index=False); va.to_csv("data/splits/val.csv", index=False); te.to_csv("data/splits/test.csv", index=False)
classifier.save(model, a.out, {"ml_threshold": float(best), "n_train": len(tr_aug), "n_val": len(va), "n_test": len(te), "seed": a.seed})
