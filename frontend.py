"""Task 3 - frontend service (shop). Port 5001.

GET /checkout -> calls backend GET /charge over HTTP.
Context propagation is ON by default (W3C traceparent header).
Failure demo: start with PROPAGATION=off, and the header is no longer sent.
(OTEL_PROPAGATORS=none and an empty CompositePropagator both crashed the Flask
instrumentation in 0.66b2: their extract() returns None instead of a Context.
So the demo keeps extract() and only turns inject() into a no-op.)
"""
import os

import requests
from flask import Flask
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from otel_setup import init_tracing

tracer = init_tracing("shop-frontend")

if os.environ.get("PROPAGATION", "on") == "off":
    class NoInject(TraceContextTextMapPropagator):
        def inject(self, carrier, context=None, setter=None):
            pass  # outgoing calls carry no traceparent header

    set_global_textmap(NoInject())
    print("[frontend] context propagation OFF", flush=True)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)   # span for every incoming request
RequestsInstrumentor().instrument()       # span for every outgoing call + inject traceparent

BACKEND = "http://localhost:5002/charge"


@app.get("/checkout")
def checkout():
    with tracer.start_as_current_span("checkout") as span:
        span.set_attribute("order.id", "A8-1001")
        ctx = span.get_span_context()
        print(f"[frontend] trace_id={ctx.trace_id:032x}", flush=True)
        result = requests.get(BACKEND, timeout=5).json()
    return {"order": "A8-1001", "payment": result["status"],
            "trace_id": f"{ctx.trace_id:032x}"}


if __name__ == "__main__":
    app.run(port=5001)
