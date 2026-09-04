# Free Hugging Face path (no paid key)

Hub list API is free and needs no token.
Hub *inference* needs a free HF token (no credit card). Measured 2026-09-04: router.huggingface.co returns 401 with no Authorization.

Do not use xAI. Do not use paid Inference Endpoints.

Preferred free-tier models (under ~10B):
- Qwen/Qwen3-8B
- Qwen/Qwen2.5-7B-Instruct
- Qwen/Qwen2.5-3B-Instruct
- Qwen/Qwen2.5-1.5B-Instruct
- Qwen/Qwen3-0.6B

Set Space secret HF_TOKEN (same write token used to publish) then:

```bash
python scripts/ayllu_hf_free.py
```

Label LIVE-HF only if chat completions returns text. Else SOFTWARE.
