# Order service image — multi-stage build.
# Stage 1 ("builder") installs dependencies; the final stage copies only what
# is needed to run, keeping the image small (Lab 02 inspects these layers).

FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

ARG BUILD_ID=local
ENV APP_ENV=production \
    BUILD_ID=${BUILD_ID} \
    PYTHONUNBUFFERED=1

# Run as a non-root user (Lab 02 and Lab 07 discuss why).
RUN useradd --create-home --uid 1001 appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY main.py .

# Numeric UID, not the name: with runAsNonRoot Kubernetes must be able to
# verify the user is not root, and it cannot resolve names from the image.
USER 1001
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
