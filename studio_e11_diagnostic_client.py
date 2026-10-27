"""Metadata-only E11 client summary. No HTTP, retrieval, persistence or classification."""
from studio_e11_contract import CHECKPOINT, ERROR_CODES, MEMORY_STATUSES, STATUSES, diagnostic_summary


def _object(value):
    return value if type(value) is dict else {}


def _known(value, allowed, default=None):
    return value if type(value) is str and value in allowed else default


def _count(value):
    return len(value) if type(value) is list else 0


def summarize_result(result):
    """Reuse the consumer's enums/diagnostics; never reinterpret a memory status."""
    result = _object(result)
    context = _object(result.get('e11_context'))
    receipt = _object(result.get('original_receipt'))
    packet = _object(context.get('context_packet'))
    memory = _object(context.get('memory_snapshot_ref'))
    provenance = _object(result.get('provenance'))
    verification = _object(provenance.get('service_verification'))
    return {
        'consumer_status': _known(result.get('consumer_status'), STATUSES, 'UNKNOWN'),
        'error_code': _known(result.get('error_code'), ERROR_CODES, 'UNKNOWN'),
        'documentary_status': _known(result.get('documentary_status'), MEMORY_STATUSES),
        'receipt_version': _known(receipt.get('version'), {'REAL_COGNITIVE_JOIN_C1_V1'}),
        'e11_schema': _known(context.get('schema'), {'COGNITION_SHADOW_MEMORY_V0'}),
        'b6_schema': _known(packet.get('schema'), {'B6_STATE_EXPLICIT_CONTEXT_PACKET_V1'}),
        'memory_schema': _known(memory.get('schema_version'), {'OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1'}),
        'counts': {'memory_entries': _count(context.get('memory_entries')),
                   'unknowns': _count(packet.get('unknowns')), 'omitted': _count(packet.get('omitted'))},
        'receipt_preserved': bool(receipt),
        'publication_permitted': result.get('publication_permitted') is True,
        'checkpoint_verified': verification.get('checkpoint') == CHECKPOINT,
        **diagnostic_summary(result),
    }
