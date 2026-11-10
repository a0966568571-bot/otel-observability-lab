"""Task 3 - backend service (payment). Port 5002."""
import time

from flask import Flask, request
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from otel_setup import init_tracing

tracer = init_tracing("payment-backend")
app = Flask(__name__)
# Server side: read the incoming `traceparent` header and continue that trace.
FlaskInstrumentor().instrument_app(app)


@app.get("/charge")
def charge():
    # Show what actually arrived over the wire.
    print(f"[backend] traceparent header = {request.headers.get('traceparent')}", flush=True)
    with tracer.start_as_current_span("charge-card") as span:
        span.set_attribute("payment.amount", 299)
        time.sleep(0.05)  # pretend the bank call takes 50 ms
        ctx = span.get_span_context()
        print(f"[backend] trace_id={ctx.trace_id:032x}", flush=True)
    return {"status": "paid"}


if __name__ == "__main__":
    app.run(port=5002)
