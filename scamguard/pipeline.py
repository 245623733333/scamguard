import time, os
from . import classifier
from .fusion import fuse
from .explainer import explain, get_llm_from_env

class ScamGuard:
    def __init__(self, model_path="models/clf.joblib", llm="env", t_scam=0.60, t_susp=0.35, w_clf=0.5):
        self.model = classifier.load(model_path)
        self.llm = get_llm_from_env() if llm == "env" else llm
        self.kw = dict(t_scam=t_scam, t_susp=t_susp, w_clf=w_clf)

    def detect(self, text):
        return fuse(text, classifier.prob(self.model, text), **self.kw)

    def analyze(self, text, explain_it=True):
        t0 = time.perf_counter(); v = self.detect(text); t1 = time.perf_counter()
        res = {"verdict": v, "detect_ms": (t1 - t0) * 1e3}
        if explain_it:
            e, info = explain(text, v, self.llm)
            res.update(explanation=e, explain_info=info, total_ms=(time.perf_counter() - t0) * 1e3)
        return res
