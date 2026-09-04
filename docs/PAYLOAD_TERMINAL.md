# Terminal payload — GitHub org + HF SZLHOLDINGS

```bash
cd $(git rev-parse --show-toplevel)
python -m pip install huggingface_hub==1.19.0
python scripts/ayllu_occupy.py
gh secret set HF_TOKEN --repo szl-holdings/ayllu   # if token in env
gh workflow run hf-space.yml --repo szl-holdings/ayllu
gh issue comment 20 --repo szl-holdings/ayllu --body "occupy exit + smoke map"
```

LIVE only after smoke 200. Λ = Conjecture 1.
