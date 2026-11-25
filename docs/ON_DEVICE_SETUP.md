# On-device setup (Raspberry Pi 5, 64-bit Raspberry Pi OS)
ExecuTorch changes quickly. **Verify every command against the current official docs** (pytorch.org/executorch, examples/models/llama) and record the exact versions used.

## 1. Export the model (on a bigger machine)
Accept the Llama 3.2 license and download `Llama-3.2-1B-Instruct`. Then, in an ExecuTorch checkout (pin a release tag):
```
python -m examples.models.llama.export_llama \
  --checkpoint <path>/consolidated.00.pth --params <path>/params.json \
  -kv --use_sdpa_with_kv_cache -X --xnnpack-extended-ops \
  -qmode 8da4w --group_size 128 -d fp32 --max_seq_length 1024 --max_context_length 1024 \
  --metadata '{"get_bos_id":128000,"get_eos_ids":[128009,128001]}' --output_name llama3_2_1b_8da4w.pte
```
Make a second export (different quantization/context) for the comparison table.
## 2. Build `llama_main` for aarch64 (natively on the Pi or cross-compile), following the ExecuTorch Llama README. Test:
```
./cmake-out/examples/models/llama/llama_main --model_path=llama3_2_1b_8da4w.pte --tokenizer_path=tokenizer.model --prompt="Hello" --seq_len=64 --temperature=0
```
## 3. Connect ScamGuard
```
export LLAMA_RUNNER=$PWD/cmake-out/examples/models/llama/llama_main
export LLAMA_PTE=$PWD/llama3_2_1b_8da4w.pte
export LLAMA_TOKENIZER=$PWD/tokenizer.model
```
Flag names (`--cpu_threads`, `--seq_len`), BOS handling and the stats line differ between releases; adjust `LlamaExecuTorch.generate` if needed. The CLI prints `explainer: llama-executorch` when Llama is really used.
## Limits
Each call reloads the model (slow); a persistent runner would fix this. Android would need the detector ported to Kotlin.
