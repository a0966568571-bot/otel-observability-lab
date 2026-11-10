# Assignment 8: Observability with OpenTelemetry

Code for my OpenTelemetry lab (DevOps course, Assignment 8). CHANGYENJUNG.

| Task | Level | What it does |
|---|---|---|
| 1 | A | Parent + child span printed to the console |
| 2 | E | Same spans sent over OTLP to a Dockerized collector, exported to its log and a JSON file |
| 3 | O | Context propagation across two Flask services, viewed in Jaeger, plus a "propagation off" failure demo |

## Files

| File | Used in | Purpose |
|---|---|---|
| `task1_console.py` | Task 1 | `checkout` (parent) and `charge-card` (child), `ConsoleSpanExporter` |
| `task2_otlp.py` | Task 2 | Same spans, `OTLPSpanExporter` + `BatchSpanProcessor` to `localhost:4317` |
| `otel-collector-config.yaml` | Task 2 | OTLP receiver → batch → debug + file exporters |
| `otel-collector-config-o.yaml` | Task 3 | Same pipeline plus an exporter to Jaeger |
| `otel_setup.py` | Task 3 | Shared tracer setup, sets `service.name` |
| `frontend.py` | Task 3 | `shop-frontend` on :5001, `/checkout` calls the backend |
| `backend.py` | Task 3 | `payment-backend` on :5002, prints the `traceparent` header it receives |
| `evidence/` | all | Sample output from my own runs |

Tested with Python 3.15, opentelemetry-sdk 1.45.2, collector 0.164.0, Jaeger 2.10.0, Docker 29.8 on macOS.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.10 or newer is needed (opentelemetry-sdk 1.45.2). My Anaconda Python was 3.8, so I used the Homebrew Python instead.

## Task 1 (A): console output

```bash
python task1_console.py
```

Both spans share one `trace_id`, and the child's `parent_id` equals the parent's `span_id`.
The child is printed first because a span is exported when it ends, and the child ends first.

## Task 2 (E): Dockerized collector

```bash
mkdir -p out && chmod 777 out
docker run -d --rm --name otel-collector -p 4317:4317 \
  -v "$PWD/otel-collector-config.yaml:/etc/otelcol/config.yaml" \
  -v "$PWD/out:/out" \
  otel/opentelemetry-collector:0.164.0

python task2_otlp.py
docker logs otel-collector     # debug exporter output
cat out/telemetry.json         # file exporter output
```

The same trace ID and span IDs show up in the program output, the collector log and `out/telemetry.json`.

## Task 3 (O): context propagation across services

```bash
docker stop otel-collector
docker network create otel-net
docker run -d --rm --name jaeger --network otel-net -p 16686:16686 jaegertracing/jaeger:2.10.0
docker run -d --rm --name otel-collector --network otel-net -p 4317:4317 \
  -v "$PWD/otel-collector-config-o.yaml:/etc/otelcol/config.yaml" \
  -v "$PWD/out:/out" \
  otel/opentelemetry-collector:0.164.0
```

Then in three terminals:

```bash
python backend.py                    # terminal 1
python frontend.py                   # terminal 2
curl -s localhost:5001/checkout      # terminal 3
```

Open http://localhost:16686 and search for `shop-frontend`: one trace, 5 spans, 2 services.

Failure demo: stop the frontend and start it with propagation off.

```bash
PROPAGATION=off python frontend.py
curl -s localhost:5001/checkout
```

The backend now prints `traceparent header = None`, and Jaeger shows two separate traces
(frontend 3 spans, backend 2 spans) instead of one.

Note: I first tried `OTEL_PROPAGATORS=none`, but with instrumentation 0.66b2 it made the Flask app
return 500 (`extract()` returned `None`). So `PROPAGATION=off` only disables `inject()`.

## Clean up

```bash
docker stop otel-collector jaeger
docker network rm otel-net
```
