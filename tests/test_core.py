import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scamguard.features import extract
from scamguard.fusion import fuse
from scamguard.explainer import template_explanation, build_prompt

def test_scam_rules():
    s, r, _ = extract("Your SBI account will be blocked. Update KYC immediately at http://sbi-kyc.xyz")
    assert s >= 0.6 and r

def test_otp_warning_not_flagged():
    s, _, fired = extract("123456 is your OTP. Do not share this OTP with anyone.")
    assert "asks_secret" not in fired and s < 0.2

def test_otp_request_flagged():
    _, _, fired = extract("Please share the OTP you received to cancel your order")
    assert "asks_secret" in fired

def test_fusion_and_fallback():
    v = fuse("Share your OTP and UPI PIN, urgent, you won a lottery! http://bit.ly/x", 0.9)
    assert v.label == "scam" and "scam" in template_explanation(v).lower()
    assert "<<<" in build_prompt("hello", v)

def test_llm_skipped_for_safe():
    from scamguard.explainer import explain
    class Boom:
        def generate(self, p): raise AssertionError("LLM must not run for safe messages")
    v = fuse("Hi running late will reach by 7.", 0.02)
    _, info = explain("Hi running late will reach by 7.", v, Boom())
    assert v.label == "safe" and info["source"] == "template-skipped-safe"
