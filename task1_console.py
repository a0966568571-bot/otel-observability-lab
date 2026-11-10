"""Assignment 8 - Task 1 (A level)
Minimal OpenTelemetry demo: a parent span and a child span,
printed to the console by ConsoleSpanExporter.
"""
import time

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# 1. Tracer provider: the factory that creates tracers and holds the pipeline.
resource = Resource.create({"service.name": "a8-shop"})
provider = TracerProvider(resource=resource)

# 2. Span processor + exporter: every finished span is printed to stdout.
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("a8.demo")

# 3. Parent span "checkout" with a child span "charge-card".
with tracer.start_as_current_span("checkout") as parent:
    parent.set_attribute("order.id", "A8-1001")
    with tracer.start_as_current_span("charge-card") as child:
        child.set_attribute("payment.amount", 299)
        time.sleep(0.05)  # pretend the card charge takes 50 ms
        print("paid")

# 4. Short summary so the IDs are easy to compare in the screenshot.
p, c = parent.get_span_context(), child.get_span_context()
print("\n===== ID check =====")
print(f"checkout    trace_id={p.trace_id:032x} span_id={p.span_id:016x}")
print(f"charge-card trace_id={c.trace_id:032x} span_id={c.span_id:016x} "
      f"parent_id={child.parent.span_id:016x}")
print("same trace:", p.trace_id == c.trace_id,
      "| child.parent == parent.span_id:", child.parent.span_id == p.span_id)
