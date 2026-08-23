# Example SLO for the Order Service

## Service Level Objective

**99% of requests to `/health` and `/orders` respond successfully (HTTP 2xx/3xx) over a 30-day window.**

## Service Level Indicator (SLI)

```promql
rate(order_requests_total{status=~"2..|3.."}[5m])
/
rate(order_requests_total[5m])
```

## Error Budget

- If availability drops below 99%, the error budget is exhausted for the month.
- When the budget is exhausted, feature releases are paused until reliability improves.

## Alerting

Page the on-call engineer if the 5-minute availability drops below 95%.
