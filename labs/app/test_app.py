"""Tests for the order service.

The payment service is not required: creating an order while the payment
service is down records payment status "unavailable", and the tests accept
either outcome so they pass in every lab environment.
"""
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "env" in body
    assert "build_id" in body


def test_create_order():
    response = client.post(
        "/orders",
        json={"item": "coffee", "quantity": 2, "price": 3.5},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["item"] == "coffee"
    assert body["quantity"] == 2
    assert body["total"] == 7.0
    assert body["payment"]["status"] in ("approved", "unavailable")


def test_create_order_rejects_invalid_quantity():
    response = client.post(
        "/orders",
        json={"item": "coffee", "quantity": 0, "price": 3.5},
    )
    assert response.status_code == 422


def test_list_orders():
    before = client.get("/orders").json()["count"]
    client.post("/orders", json={"item": "tea", "quantity": 1, "price": 2.0})
    after = client.get("/orders").json()
    assert after["count"] == before + 1


def test_metrics_endpoint():
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "order_requests_total" in response.text
    assert "order_request_duration_seconds" in response.text
