# Example SLO for the Order Service

## Service Level Objective

**99% of requests to `/orders` respond successfully (HTTP 2xx/3xx) over a
30-day window.**

> Note: `/health` and `/metrics` are deliberately **excluded** from the SLI.
> Health checks are high-volume, almost-always-successful traffic that would
> inflate availability and hide real user pain — a classic SLO anti-pattern.

## Service Level Indicator (SLI)

```promql
sum(rate(order_requests_total{endpoint="/orders", status=~"2..|3.."}[5m]))
/
sum(rate(order_requests_total{endpoint="/orders"}[5m]))
```

## Error Budget

- A 99% SLO over 30 days allows **1% of requests to fail** — that is the
  error budget (~7.2 hours of full downtime equivalent per month).
- While budget remains, the team ships features at normal speed.
- When the budget is exhausted, feature releases pause and the team spends
  its time on reliability work until the budget recovers.

## Alerting — burn rate, not raw availability

Alerting on "availability < 95% for 5 minutes" pages too late for fast
outages and too often for slow ones. Instead, alert on **how fast the error
budget is burning**, using two windows:

| Alert | Condition | Meaning | Action |
|-------|-----------|---------|--------|
| Fast burn | error rate > 14.4 × (1 − SLO) over 1 h **and** over 5 m | budget gone in ~2 days | **Page** on-call |
| Slow burn | error rate > 3 × (1 − SLO) over 24 h **and** over 2 h | budget gone in ~10 days | Ticket, review next working day |

Example fast-burn expression for this service (SLO 99% → 1 − SLO = 0.01):

```promql
(
  sum(rate(order_requests_total{endpoint="/orders", status=~"5.."}[1h]))
  /
  sum(rate(order_requests_total{endpoint="/orders"}[1h]))
) > (14.4 * 0.01)
```

## Discussion questions (Part F)

1. Is 99% realistic for this lab service? What would 99.9% cost?
2. Who decides when the error budget pauses releases — the team or the platform?
3. Which alert above would you route to a pager, and which to a ticket queue? Why?
