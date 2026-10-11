# AYLLU native presentation source

The actual served fronts are `ayllu/static/chamber.html`, `ayllu/static/counsel.html` and `ayllu/static/psyche.html`, returned by the existing `app.py` handlers. Docker starts `ayllu.space`; importing that entry performs an occupancy beat, so the presentation browser verifier deliberately does not import or start the application.

All three files now contain the exact native small Orbit suite artwork from accepted `szl-brand@27d12e77fc0f9f1a0e5fae8b34adf2380d51d070`, SHA-256 `6e2b7d72a3af3d9602b79de41df0194ede6496a9661f057108ec224c0efc92e6`. Each has visible source and CC BY 4.0 artwork attribution. Apache-2.0 code remains unchanged. The graphite/silver/teal roles are a scoped native KANCHAY projection, not a claim that a full new stylesheet is served. All presentation stays inside the existing Docker COPY closure; no asset route, CDN, publisher or workflow is added.

## Interface changes

Opaque reading panels and restrained foil edges, responsive minimum-width grids, native focus/skip destinations, real textarea labels, 44px controls and high-contrast/reduced-motion behavior give the three workspaces a consistent identity. The chamber's decorative animation stops for reduced motion and hidden tabs. Its roster selection exposes the current seat and retains native Space/Enter behavior. The Psyche page groups secondary measurement/model indicators in a native disclosure while preserving their IDs, labels and calculation sources.

Response text is correctly escaped, including quotes, in all three renderers. Response links admit only HTTP(S), reject credential-bearing/unsupported URLs and display unavailable text for missing links. This repairs the prior no-op escaping in Counsel/Psyche and unsafe HTML-attribute interpolation in Counsel/Chamber. Organs retain their supplied source URL when valid.

GET discovery has a ten-second abort deadline; POST methods, paths, payloads, Human Lock, server admission and timeout contracts remain intact. Initial unread counts use a dash. Unavailable discovery clears current memory/graph labels. Failed action responses cannot paint sealed/grafted outcomes. A locally engaged Human Lock is described as still subject to server attestation/admission. No scientific label, mathematical implementation, receipt authority or autonomous capability is promoted.

## Verification and network boundary

The final source browser verifier passed the three fronts at 320, 390, 768, 1280 and 1920px. It records exact source hashes and blocks external requests and every non-GET request. Discovery uses clearly labeled local UNAVAILABLE data; failed operational response paints use an in-memory `j` stub without sending an action. Checks cover actual keyboard skip focus, control sizes, layout containment, labels, exact SVG identity, malicious markup and URL strings remaining inert, GET deadlines, eight failed-action paints, roster selection, reduced motion and the metrics disclosure. Final qualification recorded zero page errors, attempted writes or external requests.

```sh
CHROME_PATH=/path/to/chromium python tools/verify_ayllu_browser.py --output /new/evidence-directory
python -m ayllu.selftest
```

A broad local test invocation was initially stopped by automatic approval review because the live HF request path was not yet qualified. Source inspection traced it to `tests/test_api.py::test_organism_routes`: its local Hatun status route called the standalone service's public health/readiness probes. This shape test now injects an explicit local 503 probe and asserts both paths, both UNAVAILABLE labels and NOT_PROBED tools. Production probes and publisher behavior are unchanged. The isolated test passed.

The final full suite then passed all 410 tests with production urllib transport denied before test-module import and **zero unmocked transport attempts**. Existing provider tests retain their explicit in-memory recorder. This is separate evidence from the earlier stopped invocation. Offline selftest and 15 pure publisher tests also passed. Browser success is presentation evidence, not a deployed-runtime or scientific-validation receipt.

Eight protected hashes were recorded before edits: app, Space entry, Dockerfile, workflow, Space contract, card README, Psyche engine and Counsel backend. All remain identical. Existing POST request expressions/payloads are preserved. `git diff --check` passes.

The sole publication path remains `hf-space.yml`: configured existing credential, exact accepted main, Docker-derived closure, `.hf-space.json` contract and immutable Hub/runtime/health receipt. Review and normal merge precede publisher observation and live readback; no new live delivery is claimed by these local results.
