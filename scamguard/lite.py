"""Pure-Python (no numpy/sklearn) inference for the TF-IDF + LogisticRegression model, so the detector
runs on phones (Termux) and minimal Linux images. Exported from the sklearn model by scripts/export_lite.py
and verified against it. Mirrors sklearn: lowercase, \\b\\w\\w+\\b word 1-2grams, char_wb 2-5grams,
sublinear tf (1+ln tf), idf, L2 norm per vectorizer, concatenation, logistic regression."""
import json, math, re

_TOKEN = re.compile(r"(?u)\b\w\w+\b")
_WS = re.compile(r"\s\s+")

def _word_ngrams(text, lo, hi):
    toks = _TOKEN.findall(text)
    out = []
    for n in range(lo, hi + 1):
        for i in range(len(toks) - n + 1):
            out.append(" ".join(toks[i:i + n]))
    return out

def _char_wb_ngrams(text, lo, hi):
    text = _WS.sub(" ", text)
    out = []
    for w in text.split():
        w = " " + w + " "
        L = len(w)
        for n in range(lo, hi + 1):
            off = 0
            out.append(w[off:off + n])
            while off + n < L:
                off += 1
                out.append(w[off:off + n])
            if off == 0:
                break
    return out

def _vec(grams, vocab, idf):
    tf = {}
    for g in grams:
        j = vocab.get(g)
        if j is not None:
            tf[j] = tf.get(j, 0) + 1
    x = {j: (1.0 + math.log(c)) * idf[j] for j, c in tf.items()}
    norm = math.sqrt(sum(v * v for v in x.values()))
    return {j: v / norm for j, v in x.items()} if norm > 0 else x

class LiteModel:
    def __init__(self, d):
        self.d = d
    @classmethod
    def load(cls, path):
        return cls(json.load(open(path)))
    def prob(self, text):
        d = self.d; text = text.lower(); z = d["intercept"]
        w, c = d["word"], d["char"]
        for j, v in _vec(_word_ngrams(text, *w["ngram"]), w["vocab"], w["idf"]).items():
            z += d["coef"][j] * v
        off = len(w["idf"])
        for j, v in _vec(_char_wb_ngrams(text, *c["ngram"]), c["vocab"], c["idf"]).items():
            z += d["coef"][off + j] * v
        return 1.0 / (1.0 + math.exp(-z))
