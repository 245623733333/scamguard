"""On-device benchmark. RUN ON THE REAL ARM DEVICE. Writes results/benchmark.json."""
import argparse, glob, json, os, platform, resource, statistics as st, sys
import csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scamguard.pipeline import ScamGuard

def pct(x, q): x = sorted(x); return x[min(len(x) - 1, int(round(q * (len(x) - 1))))]
ap = argparse.ArgumentParser(); ap.add_argument("--trials", type=int, default=30)
ap.add_argument("--note", default="", help="e.g. 'Llama-3.2-1B 8da4w, 4 threads'"); a = ap.parse_args()
def temp_c():
    for f in glob.glob("/sys/class/thermal/thermal_zone*/temp"):
        try: return int(open(f).read()) / 1000
        except Exception: pass
    return None
t_start = temp_c(); temps = []
sg = ScamGuard("models/clf_lite.json" if os.path.exists("models/clf_lite.json") else "models/clf.joblib"); msgs = [r["text"] for r in csv.DictReader(open("data/indian_test_set.csv", encoding="utf-8"))]
rows = []
for i in range(a.trials):
    r = sg.analyze(msgs[i % len(msgs)]); info = r["explain_info"]; temps.append(temp_c())
    rows.append(dict(detect_ms=r["detect_ms"], total_ms=r["total_ms"], source=info["source"],
                     first_token_ms=info.get("first_token_ms"), prompt_tokens=info.get("prompt_tokens"),
                     generated_tokens=info.get("generated_tokens")))
det = [r["detect_ms"] for r in rows]; tot = [r["total_ms"] for r in rows]
llm_used = sum(r["source"] == "llama-executorch" for r in rows)
llm_attempted = sum(r["source"] in ("llama-executorch", "template-fallback") for r in rows)
tv = [t for t in temps if t is not None]
size = lambda p: round(os.path.getsize(p) / 1e6, 1) if p and os.path.exists(p) else None
out = dict(note=a.note, device=platform.platform(), machine=platform.machine(), python=platform.python_version(),
           trials=a.trials, llm_invoked=llm_attempted, llm_invocation_rate=llm_attempted / a.trials, llama_calls_ok=llm_used,
           fallback_after_llm_error=llm_attempted - llm_used, temp_c_start=t_start, temp_c_max=max(tv) if tv else None,
           loadavg=os.getloadavg(),
           detect_ms=dict(median=st.median(det), p95=pct(det, .95)), total_ms=dict(median=st.median(tot), p95=pct(tot, .95), first_call=tot[0]),
           peak_rss_mb_self=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
           peak_rss_mb_children=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024,
           sizes_mb=dict(classifier=size("models/clf_lite.json") or size("models/clf.joblib"), llama_pte=size(os.environ.get("LLAMA_PTE"))), raw=rows)
if platform.machine() not in ("aarch64", "arm64", "armv8l"): out["WARNING"] = "NOT an Arm device: results are not valid for the challenge"
os.makedirs("results", exist_ok=True); json.dump(out, open("results/benchmark.json", "w"), indent=2)
print(json.dumps({k: v for k, v in out.items() if k != "raw"}, indent=2))
