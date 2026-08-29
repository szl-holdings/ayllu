# Ayllu Counsel — Hugging Face Docker Space.
# ECR pin avoids Docker Hub exit 128. Explicit COPY — no pytest cache.
FROM public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=7860
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./app.py
COPY ayllu ./ayllu
COPY data ./data
COPY NOTICE ./NOTICE
COPY HONEST_DISCLOSURE.md ./HONEST_DISCLOSURE.md
EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
