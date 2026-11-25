#!/bin/sh
# Launcher on the device. Set LLAMA_RUNNER/LLAMA_PTE/LLAMA_TOKENIZER first (docs/ON_DEVICE_SETUP.md).
cd "$(dirname "$0")" && exec python3 -m scamguard.cli "$@"
