"""Risk fusion: combine ML probability and rule score into a verdict with reasons."""
from dataclasses import dataclass, field
from .features import extract

@dataclass
class Verdict:
    label: str            # "scam" | "suspicious" | "safe"
    score: float
    clf_prob: float
    rule_score: float
    reasons: list = field(default_factory=list)
    fired: list = field(default_factory=list)

def fuse(text, clf_prob, w_clf=0.5, t_scam=0.60, t_susp=0.35):
    rule_score, reasons, fired = extract(text)
    score = w_clf * clf_prob + (1 - w_clf) * rule_score
    if rule_score >= 0.7:                       # strong rule evidence should not be diluted
        score = max(score, 0.5 * rule_score + 0.3)
    if clf_prob >= 0.5:
        reasons = reasons + ["its wording closely matches known scam messages"]
    label = "scam" if score >= t_scam else "suspicious" if score >= t_susp else "safe"
    return Verdict(label, round(score, 3), round(clf_prob, 3), round(rule_score, 3), reasons, fired)
