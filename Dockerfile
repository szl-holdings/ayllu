# Ayllu Counsel — Hugging Face Docker Space (port 7860)
# `FROM python:3.12-slim` hits Docker Hub rate-limit → factory exit 128.
# `COPY .` ships pytest caches and pyc into the image. Explicit COPY + GCR.
FROM mirror.gcr.io/library/python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=7860

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py LICENSE README.md NOTICE HONEST_DISCLOSURE.md ./
COPY ayllu ./ayllu

EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/health', timeout=4)"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
