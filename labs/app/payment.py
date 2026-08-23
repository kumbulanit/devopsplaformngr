"""Payment service — the second sample microservice for the course.

Endpoints:
    GET  /health    Liveness/readiness information.
    POST /payments  Approve a payment for an order.
    GET  /payments  List payments processed since startup (in-memory).
    GET  /metrics   Prometheus exposition format metrics.
"""
import os
import time
import uuid

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

APP_ENV = os.getenv("APP_ENV", "development")
BUILD_ID = os.getenv("BUILD_ID", "local")

app = FastAPI(title="Payment Service", version="1.0.0")

REQUEST_COUNT = Counter(
    "payment_requests_total",
    "Total HTTP requests handled by the payment service",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "payment_request_duration_seconds",
    "HTTP request duration in seconds for the payment service",
    ["method", "endpoint"],
)

PAYMENTS: list[dict] = []


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    endpoint = request.url.path
    REQUEST_COUNT.labels(request.method, endpoint, str(response.status_code)).inc()
    REQUEST_DURATION.labels(request.method, endpoint).observe(duration)
    return response


class HealthResponse(BaseModel):
    status: str
    env: str
    build_id: str


class PaymentRequest(BaseModel):
    order_id: str
    amount: float


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", env=APP_ENV, build_id=BUILD_ID)


@app.post("/payments", status_code=201)
def create_payment(payment: PaymentRequest):
    record = {
        "payment_id": str(uuid.uuid4())[:8],
        "order_id": payment.order_id,
        "amount": payment.amount,
        "status": "approved",
    }
    PAYMENTS.append(record)
    return record


@app.get("/payments")
def list_payments():
    return {"payments": PAYMENTS, "count": len(PAYMENTS)}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
