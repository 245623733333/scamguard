"""Rule-based feature extraction. Each rule returns a weight and a plain-language reason."""
import re
from urllib.parse import urlparse

URL_RE = re.compile(r"(https?://[^\s]+|www\.[^\s]+|\b(?:bit\.ly|tinyurl\.com|t\.co|cutt\.ly|rb\.gy|is\.gd|t\.me)/[^\s]+|\b[a-z0-9-]+\.(?:xyz|top|club|info|link|cc|tk|ml|icu)\b[^\s]*)", re.I)
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "cutt.ly", "rb.gy", "is.gd", "goo.gl", "shorturl.at", "t.me"}
BAD_TLDS = (".xyz", ".top", ".club", ".info", ".link", ".cc", ".tk", ".ml", ".icu")
# "never share your OTP" is a warning, not a request: remove such phrases first
NEGATION_RE = re.compile(r"\b(never|do not|don't|dont|not to|should not|shouldn't)\s+(share|disclose|give|tell|reveal|send)\b[^.!?]*", re.I)

RULES = [
    ("asks_secret", re.compile(r"\b(share|send|tell|enter|provide|confirm|give|reply with)\b.{0,40}\b(otp|upi pin|pin|cvv|password|mpin)\b", re.I), 0.40,
     "it asks you to hand over a secret code or PIN"),
    ("kyc_threat", re.compile(r"\b(kyc|pan|aadhaar|aadhar|sim)\b.{0,50}\b(update|expire[sd]?|verify|block(ed)?|suspend(ed)?|deactivat\w*|not linked)\b", re.I), 0.30,
     "it threatens to block your account, SIM or KYC unless you act"),
    ("urgency", re.compile(r"\b(urgent(ly)?|immediately|within \d+ ?(hours?|hrs?|mins?|minutes?)|today only|last chance|expires? (today|tonight)|disconnected tonight|avoid arrest)\b", re.I), 0.15,
     "it pressures you to act very fast"),
    ("prize", re.compile(r"\b(you have won|you won|winner|lottery|lucky draw|congratulations|prize|selected for)\b", re.I), 0.25,
     "it claims you won or were selected for something"),
    ("fee_for_reward", re.compile(r"\b(processing fee|redelivery fee|registration fee|claim fee|pay (rs|inr|₹))\b|\b(refund|cashback|reward)\b.{0,40}\b(claim|accept|receive|redeem)\b", re.I), 0.20,
     "it asks for a payment or action to receive money or a reward"),
    ("upi_collect", re.compile(r"\bupi\b.{0,20}\bcollect\b|\bcollect request\b", re.I), 0.20,
     "it sends a UPI collect request, which takes money from you"),
    ("authority_threat", re.compile(r"\b(cbi|police|customs|income tax|arrest|illegal activity|narcotics)\b.{0,60}\b(contact|call|whatsapp|pay|avoid)\b", re.I), 0.30,
     "it pretends to be an official authority and threatens you"),
    ("easy_money", re.compile(r"\b(earn rs ?[\d,]+ (daily|per day)|work from home|0 interest|no documents)\b", re.I), 0.20,
     "it promises easy money"),
]
LEGIT = [
    ("otp_warning", re.compile(r"\b(do not|don't|never)\s+share\b", re.I), -0.25),
    ("txn_alert", re.compile(r"\b(debited|credited)\b.{0,60}\b(a/c|account|acct)\b|\b(a/c|account|acct)\b.{0,60}\b(debited|credited)\b", re.I), -0.15),
]

def find_urls(text):
    return [m.group(0).rstrip(".,)") for m in URL_RE.finditer(text)]

def url_flags(url):
    u = url if "://" in url else "http://" + url
    host = (urlparse(u).hostname or "").lower()
    flags = []
    if host in SHORTENERS or any(host.endswith("." + s) for s in SHORTENERS):
        flags.append(("shortened_link", 0.20, "it contains a shortened link that hides the real website"))
    if host.endswith(BAD_TLDS):
        flags.append(("odd_domain", 0.20, "the link uses an unusual website ending often used for scams"))
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
        flags.append(("ip_link", 0.30, "the link points to a raw IP address"))
    if re.search(r"(bank|sbi|hdfc|icici|axis|paytm|kyc|upi|refund|incometax).*-.*|-.*(bank|sbi|hdfc|kyc|refund|verify)", host) and host.endswith(BAD_TLDS + (".com", ".in")):
        flags.append(("lookalike", 0.15, "the website name imitates a bank or official service"))
    return flags

def extract(text):
    """Return (rule_score in [0,1], reasons list, fired rule names)."""
    clean = NEGATION_RE.sub(" ", text)
    score, reasons, fired = 0.0, [], []
    for name, rx, w, reason in RULES:
        if rx.search(clean):
            score += w; reasons.append(reason); fired.append(name)
    urls = find_urls(text)
    if urls:
        score += 0.10; fired.append("has_link")
        reasons.append("it contains a link you did not ask for")
        seen = set()
        for u in urls:
            for name, w, reason in url_flags(u):
                if name not in seen:
                    seen.add(name); score += w; reasons.append(reason); fired.append(name)
    for name, rx, w in LEGIT:
        if rx.search(text) and not urls:
            score += w; fired.append(name)
    return max(0.0, min(1.0, score)), reasons, fired
