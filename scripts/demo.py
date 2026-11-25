"""Scripted demo for screen recording ON THE ARM DEVICE: shows device info, proves network is off,
then runs scam + legitimate messages. Usage: python scripts/demo.py  (press Enter between messages)"""
import os, platform, socket, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scamguard.pipeline import ScamGuard
from scamguard.cli import ICON

MSGS = [
 ("SCAM: KYC threat", "Dear customer your SBI account will be blocked today. Update KYC immediately at http://sbi-kyc-update.xyz"),
 ("SCAM: UPI collect refund", "UPI collect request of Rs 9999 from refund-dept. Accept to receive your refund in your account"),
 ("SCAM: courier fee", "Your parcel is held at customs. Pay Rs 49 redelivery fee at http://indiapost-track.cc to release"),
 ("LEGIT: bank OTP", "123456 is your OTP for login to Flipkart. Do not share this OTP with anyone."),
 ("LEGIT: debit alert", "Rs 1250.00 debited from A/c XX4521 on 28-10-26 at SWIGGY. Avl bal Rs 10432.55. Not you? Call 18001234567"),
 ("LEGIT: personal", "Hi running late will reach by 7. Start dinner without me."),
]
def online():
    try: socket.create_connection(("1.1.1.1", 53), timeout=2).close(); return True
    except OSError: return False
def sh(c):
    try: return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception: return "n/a"

print("=" * 70); print("ScamGuard - on-device SMS scam detection (offline)"); print("=" * 70)
print("Device :", sh("cat /proc/device-tree/model | tr -d '\\0'") or platform.node())
print("CPU    :", platform.machine(), sh("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2"))
print("RAM    :", sh("free -h | awk '/Mem/{print $2}'"))
print("Network:", "ONLINE  <-- turn Wi-Fi/Ethernet off before recording!" if online() else "OFFLINE (no internet reachable)")
sg = ScamGuard("models/clf_lite.json" if os.path.exists("models/clf_lite.json") else "models/clf.joblib"); print("Explainer:", "Llama via ExecuTorch" if sg.llm else "template fallback (Llama not configured)")
for title, text in MSGS:
    input(f"\n[Enter] next: {title} "); print("SMS:", text)
    r = sg.analyze(text); v = r["verdict"]
    print(f"\n{ICON[v.label]}  risk={v.score:.2f} (ML={v.clf_prob:.2f}, rules={v.rule_score:.2f})\n{r['explanation']}")
    print(f"-- detect {r['detect_ms']:.1f} ms | total {r['total_ms']:.0f} ms | explainer: {r['explain_info']['source']}")
print("\nDemo complete.")
