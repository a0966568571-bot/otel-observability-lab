"""Shared OpenTelemetry setup for the Task 3 services (frontend / backend)."""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracing(service_name: str):
    # service.name is what Jaeger uses to tell the two services apart
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
