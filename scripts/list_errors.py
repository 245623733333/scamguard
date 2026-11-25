import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scamguard.pipeline import ScamGuard
sg = ScamGuard("models/clf_lite.json")
for r in csv.DictReader(open("data/indian_test_set.csv", encoding="utf-8")):
    v = sg.detect(r["text"])
    if r["label"] == "0" and v.label != "safe":
        print(v.label, v.score, "|", r["text"])