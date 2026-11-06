# Ayllu Counsel — Hugging Face Docker Space.
# GCR pin — ECR Public is factory exit 128; Anatomy Space already runs this FROM exit 128. Explicit COPY — no pytest cache.
# Digest-pinned: the tag names the line Dependabot tracks; the digest is the exact
# multi-arch OCI index Dependabot last resolved for that tag. The CPython release behind
# a digest is its org.opencontainers.image.version annotation (read the index from
# mirror.gcr.io). CI's space-python job tests the same minor (.github/workflows/ci.yml).
FROM mirror.gcr.io/library/python:3.15-slim@sha256:8c13a3f37a6a5b71498228e902c4b9f51c1f7900d49fabf71f9a650c6120e0d0

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=7860
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./app.py
COPY ayllu ./ayllu
COPY data ./data
COPY LICENSE ./LICENSE
COPY NOTICE ./NOTICE
COPY HONEST_DISCLOSURE.md ./HONEST_DISCLOSURE.md
EXPOSE 7860
# /healthz is served by ayllu/space.py. The slim image has no curl, so probe with
# the interpreter that runs the app. Any non-200 or connection error is unhealthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD ["python", "-c", "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:7860/healthz', timeout=4).status == 200 else 1)"]
CMD ["uvicorn", "ayllu.space:app", "--host", "0.0.0.0", "--port", "7860"]
