"""Assignment 8 - Task 2 (E level)
Same spans as Task 1, but exported over OTLP/gRPC to the Dockerized collector:
app -> collector (localhost:4317) -> debug log + out/telemetry.json
"""
import time

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource.create({"service.name": "a8-shop"})
provider = TracerProvider(resource=resource)

# Only the exporter changes: Console -> OTLP. The span code below is identical to Task 1.
exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("a8.demo")

with tracer.start_as_current_span("checkout") as parent:
    parent.set_attribute("order.id", "A8-1001")
    with tracer.start_as_current_span("charge-card") as child:
        child.set_attribute("payment.amount", 299)
        time.sleep(0.05)
        print("paid")

# BatchSpanProcessor sends in the background; shutdown() flushes the last batch
# before the program exits, otherwise the spans could be lost.
provider.shutdown()

p, c = parent.get_span_context(), child.get_span_context()
print("sent to collector at localhost:4317")
print(f"checkout    trace_id={p.trace_id:032x} span_id={p.span_id:016x}")
print(f"charge-card trace_id={c.trace_id:032x} span_id={c.span_id:016x} "
      f"parent_id={child.parent.span_id:016x}")
