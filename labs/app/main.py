"""Order service — the primary sample microservice for the course.

Endpoints:
    GET  /health   Liveness/readiness information.
    POST /orders   Create an order; calls the payment service.
    GET  /orders   List orders created since startup (in-memory).
    GET  /metrics  Prometheus exposition format metrics.

Configuration (environment variables):
    APP_ENV              Environment name shown in /health (default: development).
    BUILD_ID             Build identifier shown in /health (default: local).
    PAYMENT_SERVICE_URL  Base URL of the payment service
                         (default: http://localhost:8001).
"""
import os
import time
import uuid

import httpx
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel, Field
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

APP_ENV = os.getenv("APP_ENV", "development")
BUILD_ID = os.getenv("BUILD_ID", "local")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8001")

app = FastAPI(title="Order Service", version="1.0.0")

REQUEST_COUNT = Counter(
    "order_requests_total",
    "Total HTTP requests handled by the order service",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "order_request_duration_seconds",
    "HTTP request duration in seconds for the order service",
    ["method", "endpoint"],
)

# In-memory store: intentionally simple. Restarting the container clears it,
# which the labs use to discuss statelessness and horizontal scaling.
ORDERS: list[dict] = []


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


class OrderRequest(BaseModel):
    item: str
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        env=APP_ENV,
        build_id=BUILD_ID,
    )


@app.post("/orders", status_code=201)
def create_order(order: OrderRequest):
    order_id = str(uuid.uuid4())[:8]
    total = round(order.quantity * order.price, 2)

    # Call the payment service. If it is unreachable the order is still
    # accepted with payment status "unavailable" — a deliberately simple
    # resilience pattern the labs build on.
    try:
        response = httpx.post(
            f"{PAYMENT_SERVICE_URL}/payments",
            json={"order_id": order_id, "amount": total},
            timeout=2.0,
        )
        response.raise_for_status()
        payment = response.json()
    except httpx.HTTPError:
        payment = {"order_id": order_id, "amount": total, "status": "unavailable"}

    record = {
        "id": order_id,
        "item": order.item,
        "quantity": order.quantity,
        "price": order.price,
        "total": total,
        "payment": payment,
    }
    ORDERS.append(record)
    return record


@app.get("/orders")
def list_orders():
    return {"orders": ORDERS, "count": len(ORDERS)}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
