"""Local technical checkpoint guard. No human approval, expiry or PID binding.

This verifies the deployed files, not a remote cryptographic attestation. The
service's process origin and authentication must also be checked operationally.
"""
import hashlib
import json
from pathlib import Path

from studio_e11_contract import CHECKPOINT

ROOT = Path(__file__).resolve().parent
DEPLOYMENT = ROOT / 'data/experiments/e11_lot1/passe10e2'
MANIFEST_SHA256 = 'e017a794b73c57688841ab4b2bc168d3765f0585e9d5ebb853602a9d442d4ddc'
BASE_URL = 'http://127.0.0.1:8000'


def _file_sha256(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def verify_checkpoint(base_url):
    """Fail closed on a changed endpoint, checkpoint, manifest or deployed file."""
    if base_url != BASE_URL:
        return None
    try:
        deployment = DEPLOYMENT.resolve()
        source = deployment / 'producer_cbad0125/source'
        if not deployment.is_relative_to(ROOT.resolve()) or source.resolve() != source:
            return None
        raw = (deployment / 'EXPORT_MANIFEST.json').read_bytes()
        if len(raw) > 1_000_000 or hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        if manifest['source_commit'] != CHECKPOINT or not manifest['files']:
            return None
        for entry in manifest['files']:
            path = source / entry['path']
            resolved = path.resolve()
            if (not resolved.is_relative_to(source) or resolved != path
                    or _file_sha256(path) != entry['sha256']):
                return None
        return {'status': 'TECHNICAL_SNAPSHOT_VERIFIED', 'checkpoint': CHECKPOINT,
                'verification_method': 'PINNED_MANIFEST_SHA256',
                'manifest_sha256': MANIFEST_SHA256, 'files_verified': len(manifest['files']),
                'base_file_count': manifest.get('base_file_count', len(manifest['files'])),
                'deployment_profile': manifest.get('deployment_profile'),
                'overlay_producer_head': manifest.get('overlay', {}).get('producer_head')}
    except (OSError, ValueError, TypeError, KeyError, RuntimeError):
        return None
