# ScamGuard: On-Device SMS Scam Detection on an Arm Phone
**Bharat AI-SoC Challenge 2026-27 · Problem Statement 3 · Use case A (SMS scam detection)**

**Team:** Sri Amsha · **College:** Gokaraju Lailavathi Engineering College · **Faculty mentor:** "none"
**Repository:** https://github.com/245623733333/scamguard · **Demo video:** https://drive.google.com/file/d/11_OtkN5_b_bgZPR7BoN4eT04a__iUZQf/view

## Summary
ScamGuard classifies an SMS as *safe*, *suspicious* or *scam*, lists the reasons in plain language and recommends a safe next step. It runs entirely offline on an Arm Android phone (Vivo V21e 5G, `aarch64`) with no cloud calls. Detection takes about 1.2 ms (median) and about 28 MB of memory.

**Important scope statement.** The Llama-family explainer through ExecuTorch is implemented in code (`scamguard/explainer.py`) but was **not demonstrated on a device**. All results and the demo video use the deterministic template explainer. This report states clearly what was and was not measured.

## 1. Problem and goals
Scam SMS messages in India commonly imitate banks, UPI, KYC updates, courier fees and OTP requests. Cloud-based filters send message content off the phone and fail without internet. Goals:
1. Detect scam SMS locally, with few false alarms on legitimate bank OTPs and transaction alerts.
2. Explain why a message was flagged in simple language and recommend one safe action.
3. Keep data on the device, work offline, and use little memory and time.

**Scope.** The system analyses one SMS text at a time. It does not read the inbox automatically, click links, delete messages or store message content. It handles English text only. Other use cases (phishing URL, network traffic) are not covered; the code is modular so detectors can be added.

## 2. System architecture
```
SMS text -> rules + URL checks ------+
SMS text -> TF-IDF + Logistic Reg. --+--> risk fusion --> verdict (safe/suspicious/scam) + reasons
                                                              |
                         explainer: Llama via ExecuTorch (implemented, NOT demonstrated)
                                    or template explanation (used in all results)
```
- **Detector (traceable):** a rule layer (OTP/PIN requests, KYC and account-block threats, urgency, prize and refund lures, UPI collect requests, authority threats, shortened or unusual links) plus a TF-IDF (word 1-2 grams and character 2-5 grams) + logistic regression classifier. Every verdict carries the list of reasons that fired. Phrases such as "never share your OTP" are not treated as requests.
- **Risk fusion:** score = 0.5 x classifier probability + 0.5 x rule score. Scam if score >= 0.60, suspicious if >= 0.35, otherwise safe. Strong rule evidence is not diluted.
- **Explainer:** the language model is advisory only. It receives structured evidence (verdict and reasons) and cannot change the verdict. It is invoked only for scam or suspicious messages. If it is missing, slow or contradicts the verdict, a template explanation is used and the output states which source produced it.
- **Hardware path:** everything demonstrated runs on the Arm CPU. No NPU or accelerator is used.
- **Deployment form:** the trained model is exported to JSON (`models/clf_lite.json`, 1.7 MB) and run by a pure-Python predictor (`scamguard/lite.py`), so the phone needs only Python and no scikit-learn or numpy. The export is checked against scikit-learn on 293 messages (maximum difference about 3e-16).

## 3. Hardware and software setup
| Item | Value |
|---|---|
| Device | Vivo V21e 5G (model V2055) |
| SoC / architecture | Arm, `aarch64` (confirmed with `uname -m`) |
| RAM | 4GB |
| OS | Android 13 |
| Runtime environment | Termux, Python 3.14.8 |
| Detector runtime | Pure-Python inference of TF-IDF + logistic regression (no sklearn on device) |
| Training environment | Laptop (Windows), Python 3.12, scikit-learn |
| ExecuTorch version | Not run on device |
| Llama model | Llama 3.2 1B Instruct planned; **not run** (would be subject to the Meta Llama license) |
| Quantization / threads | Not applicable to the demonstrated build (planned: 4-bit weights, XNNPACK) |

## 4. Data
- **UCI SMS Spam Collection**, deduplicated (case and punctuation normalized): Deduplicated: 5,574 messages reduced to 5,130. Stratified split 70 / 15 / 15 (seed 42). The held-out test set has 770 messages.
- **Indian-context seed set (24 messages: 12 scam, 12 legitimate)**, written by the authors, added to training five times so it influences the model.
- **Indian-context test set (30 messages: 15 scam, 15 legitimate)**, written by the authors. It covers KYC, lottery, utility, courier, OTP, UPI, refund and loan scams, and legitimate OTPs, debit and credit alerts, bills, deliveries and personal messages.
- **Privacy:** no real user messages were collected. All Indian-context messages are fictional and contain no real numbers or accounts. The app stores nothing.
- **Limits:** the Indian sets are small, synthetic and English. They were written by the same people who wrote the rules, so results on them are optimistic. The UCI split is random and is not protected against near-duplicate campaigns.

## 5. Detection results
Threshold for the classifier alone was tuned on the validation set for a false-positive rate of at most 1%. Test sets were not used for tuning. Fusion weights and thresholds were set by hand beforehand, not tuned on the test sets.

| Dataset | System | n | Precision | Recall | F1 | FPR | TP/FP/TN/FN |
|---|---|---|---|---|---|---|---|
| UCI test | Classifier only | 770 | 0.910 | 0.958 | 0.933 | 0.0133 | 91/9/666/4 |
| UCI test | Fused, "scam" only | 770 | 1.000 | 0.168 | 0.288 | 0.0000 | 16/0/675/79 |
| UCI test | Fused, "scam or suspicious" | 770 | 0.988 | 0.874 | 0.927 | 0.0015 | 83/1/674/12 |
| UCI test | Rules only | 770 | 1.000 | 0.084 | 0.155 | 0.0000 | 8/0/675/87 |
| Indian test | Classifier only | 30 | 0.714 | 1.000 | 0.833 | 0.400 | 15/6/9/0 |
| Indian test | Fused, "scam" only | 30 | 1.000 | 0.867 | 0.929 | 0.000 | 13/0/15/2 |
| Indian test | Fused, "scam or suspicious" | 30 | 0.938 | 1.000 | 0.968 | 0.067 | 15/1/14/0 |
| Indian test | Rules only | 30 | 1.000 | 0.867 | 0.929 | 0.000 | 13/0/15/2 |

**Findings**
1. **The classifier alone transfers poorly to Indian messages.** Trained mostly on UCI (UK-style spam), it flags 6 of 15 legitimate Indian messages (FPR 0.40), mainly bank and transaction-style texts. Combining it with rules reduces false alarms to 0 of 15 at the "scam" level and 1 of 15 at the "scam or suspicious" level.
2. **Practical alert setting.** Counting "scam or suspicious" as an alert gives, on UCI, precision 0.988, recall 0.874 and FPR 0.15% (1 false alarm in 675 legitimate messages), and on the Indian set recall 1.0 with 1 false alarm in 15.
3. **Weakness: low "scam"-level recall on UCI (0.168).** Most UCI spam is UK-style promotion (prizes, premium-rate numbers) that the India-focused rules rarely match. Without rule evidence, the fused score is capped at 0.5 x classifier probability (at most 0.5), which is below the 0.60 scam threshold, so these messages become "suspicious" instead of "scam". The alert is still raised, but the label is weaker than it should be. Calibrating fusion weights and thresholds on validation data is the clear next step.
4. **Classifier-only FPR on UCI was 1.33% on test** (9 of 675), slightly above the 1% validation target, which is normal sampling variation.
5. Error analysis. On the Indian test set, no scam was missed at alert level. Two scams were labelled "suspicious" instead of "scam": an Amazon-impersonation message asking the user to share an OTP (fused score 0.359) and a Jio SIM-deactivation message with a call-back number (0.574, just below the 0.60 threshold). In both cases the rules fired but their weights were too small to cross the scam threshold, which shows the hand-set weights need calibration. The one false alarm at alert level was a legitimate UPI credit notification ("Rs 5000 credited to your A/c ... via UPI from ..."), labelled "suspicious" with a score of 0.431; real transaction alerts remain the hardest legitimate class. On the UCI test set, 79 of 95 spam messages did not reach the "scam" level; most were labelled "suspicious" (alert raised), and 12 were missed entirely. The fully missed messages are typically UK-style call-back or subscription messages that contain no phrases covered by the India-focused rules and had low classifier scores. Detecting call-back and premium-rate number patterns, and calibrating the fusion thresholds on validation data, are the planned fixes.5. Error analysis. On the Indian test set, no scam was missed at alert level. Two scams were labelled "suspicious" instead of "scam": an Amazon-impersonation message asking the user to share an OTP (fused score 0.359) and a Jio SIM-deactivation message with a call-back number (0.574, just below the 0.60 threshold). In both cases the rules fired but their weights were too small to cross the scam threshold, which shows the hand-set weights need calibration. The one false alarm at alert level was a legitimate UPI credit notification ("Rs 5000 credited to your A/c ... via UPI from ..."), labelled "suspicious" with a score of 0.431; real transaction alerts remain the hardest legitimate class. On the UCI test set, 79 of 95 spam messages did not reach the "scam" level; most were labelled "suspicious" (alert raised), and 12 were missed entirely. The fully missed messages are typically UK-style call-back or subscription messages that contain no phrases covered by the India-focused rules and had low classifier scores. Detecting call-back and premium-rate number patterns, and calibrating the fusion thresholds on validation data, are the planned fixes.

**Caution.** The Indian test set has 15 messages per class, so one message moves recall or FPR by 6.7 points. The rules were written while looking at these examples, so these numbers overstate real-world performance. Independent, anonymised real messages are needed for a fair estimate.

## 6. On-device performance (Vivo V21e 5G, Termux, Airplane mode)
Measured with `scripts/benchmark.py`, 30 trials over the Indian test messages, template explainer.

| Metric | Result |
|---|---|
| Detector latency (median / p95) | 1.17 ms / 2.37 ms |
| First call latency | 3.74 ms |
| End-to-end latency (median / p95) | 1.17 ms / 2.38 ms (identical in practice, because the LLM was never called) |
| Peak memory (RSS) | about 27.8 MB |
| Classifier file size | 1.7 MB (JSON) |
| LLM invocation rate | 0% in this run (no LLM configured) |
| Time to first token, tokens/s | Not measured (no LLM run) |
| Temperature, CPU load | Not available on non-rooted Android; not measured |
| Sustained behaviour | Not tested beyond 30 trials |

Offline operation: the demo was recorded with Airplane mode on, and the demo banner reports `Network: OFFLINE`. Detection and explanations work without any connection.

## 7. User effectiveness
"A user study with non-technical participants was not conducted in Phase 1."

## 8. Limitations
- The Llama / ExecuTorch explainer is implemented but **not demonstrated or measured on any device**.
- The runner design starts the model for every explanation, reloading it each time. A persistent service that loads the model once is not built.
- Small, synthetic, English-only Indian-context data; no Hindi, regional or code-mixed messages.
- Rules were written while viewing the test examples; the random UCI split is not protected against campaign leakage.
- Fusion weights and thresholds were not calibrated on validation data (see finding 3).
- Adversarial messages, obfuscated links and new scam styles can evade the rules.
- No Android app or APK; the demo runs in a terminal (Termux). Reading SMS directly would need permissions and user consent.
- Temperature, CPU utilisation and long-run behaviour were not measured.

## 9. Optimization and engineering choices
- A lightweight detector (rules + linear model) answers in about 1 ms, so most messages need no language model.
- The model is exported to a 1.7 MB JSON file and run by dependency-free Python, which made deployment on a phone possible without scikit-learn, and it was verified numerically against the original model.
- The LLM is gated (scam or suspicious only), constrained to short evidence-based output, and backed by a template fallback so the application never fails.
- *Planned, not demonstrated:* 4-bit weight quantization, KV cache and the XNNPACK backend for Llama 3.2 1B through ExecuTorch, and a persistent runner.

## 10. Reproduction, licenses and development notes
```
pip install -r requirements.txt
python scripts/get_uci.py && python scripts/train.py && python scripts/evaluate.py
python scripts/export_lite.py
# on the phone (Termux): pkg install python git; clone the repo; python scripts/demo.py
python scripts/benchmark.py --trials 30 --note "Vivo V21e 5G, Termux, template explainer"
```
- Data: UCI SMS Spam Collection (check the dataset page for its license and citation). scikit-learn is BSD licensed. Llama models, if used, fall under the Meta Llama license.
- Development note: parts of the code and documentation were developed with the help of an AI assistant (Claude). All reported results were produced by running the code on the stated devices.