"""Fill docs/REPORT.md with REAL numbers from results/*.json -> docs/REPORT_filled.md (+PDF if pandoc exists)."""
import json, os, shutil, subprocess
m = json.load(open("results/metrics.json")); b = json.load(open("results/benchmark.json")) if os.path.exists("results/benchmark.json") else None
L = ["\n## Auto-generated results (from results/*.json)\n", "### Detection\n", "| Dataset | System | n | Precision | Recall | F1 | FPR | TP/FP/TN/FN |", "|---|---|---|---|---|---|---|---|"]
for ds, sy in m.items():
    for name, r in sy.items():
        L.append(f"| {ds} | {name} | {r['n']} | {r['precision']} | {r['recall']} | {r['f1']} | {r['fpr']} | {r['tp']}/{r['fp']}/{r['tn']}/{r['fn']} |")
if b:
    L += ["\n### On-device performance\n", f"- Device: {b['device']} ({b['machine']}), Python {b['python']}", f"- Note: {b['note']}",
          f"- Trials: {b['trials']} (LLM invoked: {b['llm_invoked']} = {b['llm_invocation_rate']:.0%}; Llama OK: {b['llama_calls_ok']}; fallback after LLM error: {b['fallback_after_llm_error']})",
          f"- Detector latency ms: median {b['detect_ms']['median']:.1f}, p95 {b['detect_ms']['p95']:.1f}",
          f"- End-to-end ms: median {b['total_ms']['median']:.0f}, p95 {b['total_ms']['p95']:.0f}, first call {b['total_ms']['first_call']:.0f}",
          f"- Peak RSS MB: self {b['peak_rss_mb_self']:.0f}, child (Llama runner) {b['peak_rss_mb_children']:.0f}",
          f"- Model sizes MB: {b['sizes_mb']}", f"- Temperature C: start {b['temp_c_start']}, max {b['temp_c_max']}; load average {b['loadavg']}"]
    if "WARNING" in b: L.append(f"- **WARNING: {b['WARNING']}**")
out = open("docs/REPORT.md").read() + "\n".join(L) + "\n"
open("docs/REPORT_filled.md", "w").write(out); print("wrote docs/REPORT_filled.md")
ok = False
if shutil.which("pandoc"):
    ok = subprocess.run(["pandoc", "docs/REPORT_filled.md", "-o", "docs/REPORT.pdf"], capture_output=True).returncode == 0
if ok: print("wrote docs/REPORT.pdf")
else:
    if os.path.exists("docs/REPORT.pdf"): os.remove("docs/REPORT.pdf")
    print("No PDF made. Open docs/REPORT_filled.md in Google Docs/Word, finish the <fill> parts, then File > Download > PDF.")
