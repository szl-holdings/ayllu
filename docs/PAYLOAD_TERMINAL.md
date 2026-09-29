# Terminal payload — GitHub org + HF SZLHOLDINGS

The Space has one writer: `.github/workflows/hf-space.yml` (reusable-hf-deploy,
lock `hf-write/space/SZLHOLDINGS/ayllu`). It runs on every push to `main` and
fails, never skips, when the `HF_TOKEN` repo secret is absent. Nothing in a
terminal writes the Hub.

```bash
cd $(git rev-parse --show-toplevel)
gh workflow run hf-space.yml --repo szl-holdings/ayllu --ref main   # republish main
python scripts/ayllu_occupy.py                                      # read-only verify
gh issue comment 20 --repo szl-holdings/ayllu --body "occupy exit + smoke map"
```

The `hf-space-receipt` artifact of that run records `hub_oid == created_oid`,
the RUNNING stage and `/healthz` HTTP 200. LIVE only after smoke 200.
Λ = Conjecture 1.
