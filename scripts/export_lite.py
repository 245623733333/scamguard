"""Export models/clf.joblib -> models/clf_lite.json (pure-Python model) and verify equality vs sklearn."""
import json, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import joblib, pandas as pd
from scamguard.lite import LiteModel

m = joblib.load("models/clf.joblib"); meta = json.load(open("models/clf.joblib.json"))
fu = m.named_steps["tfidf"]; w = fu.transformer_list[0][1]; c = fu.transformer_list[1][1]; lr = m.named_steps["lr"]
def pack(v):
    return {"ngram": list(v.ngram_range), "vocab": {k: int(i) for k, i in v.vocabulary_.items()}, "idf": [float(x) for x in v.idf_]}
d = {"word": pack(w), "char": pack(c), "coef": [float(x) for x in lr.coef_[0]], "intercept": float(lr.intercept_[0]), "ml_threshold": meta["ml_threshold"]}
json.dump(d, open("models/clf_lite.json", "w")); lite = LiteModel(d)
texts = pd.read_csv("data/indian_test_set.csv").text.tolist() + pd.read_csv("data/splits/test.csv").text.tolist()[:300]
err = max(abs(lite.prob(t) - float(m.predict_proba([t])[0, 1])) for t in texts)
print(f"max |lite - sklearn| over {len(texts)} messages = {err:.2e}"); assert err < 1e-6, "MISMATCH: do not use lite model"
print("wrote models/clf_lite.json", round(os.path.getsize("models/clf_lite.json") / 1e6, 2), "MB")
