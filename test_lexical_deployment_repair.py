"""Offline, standalone imports of pure lexical/calibration modules only."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'data/experiments/e11_lot1/passe10e2/producer_cbad0125/source'
REL = '_source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/reverse_os_interlanguage_canon_v1.json'
BLOB = '1b10476a363d1d004ec6b6a1fa5a8c685d217190'


def load_pure(relative):
    path=SOURCE/relative
    spec=importlib.util.spec_from_file_location('offline_'+path.stem,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def lexical():
    return load_pure('periphery/language/lexical_calibrator.py')


def test_real_runtime_path_and_git_blob(lexical):
    assert lexical._CANON_PATH==SOURCE/REL
    raw=lexical._CANON_PATH.read_bytes()
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==BLOB
    canon,error=lexical._load_canon()
    assert error is None and canon['authority']['decision_authority']=='KX108_ONLY'
    assert canon['authority']['readonly'] is True
    assert canon['authority']['allowed_to_decide'] is False
    result=lexical.calibrate_lexical_knownness('Explique X108','fr')
    assert result['status']=='CALIBRATED'
    assert 'LEXICAL_CALIBRATION_SOURCE_UNAVAILABLE' not in result['unknowns']
    assert result['known_concept_ids']


@pytest.mark.parametrize('mode',['missing','malformed_json','invalid_authority','permission_error'])
def test_source_unavailable_is_preserved_when_dependency_cannot_load(lexical,monkeypatch,tmp_path,mode):
    original=lexical._CANON_PATH
    path=tmp_path/'canon.json'
    if mode=='malformed_json': path.write_bytes(b'{')
    elif mode=='invalid_authority':
        canon=json.loads(original.read_text(encoding='utf-8-sig'))
        canon['authority']['decision_authority']='OTHER'
        path.write_text(json.dumps(canon),encoding='utf-8')
    elif mode=='permission_error':
        # Simulated permission-denied I/O; no ACL or real canon is modified.
        original_read=Path.read_text
        def denied(self,*args,**kwargs):
            if self==path: raise PermissionError('synthetic denied')
            return original_read(self,*args,**kwargs)
        monkeypatch.setattr(Path,'read_text',denied)
    monkeypatch.setattr(lexical,'_CANON_PATH',path)
    result=lexical.calibrate_lexical_knownness('Explique X108','fr')
    assert result['status']=='SOURCE_UNAVAILABLE'
    assert result['unknowns']==['LEXICAL_CALIBRATION_SOURCE_UNAVAILABLE']
    assert result['source_error']


def test_real_unknown_keeps_resolve_before_assert(lexical):
    result=lexical.calibrate_lexical_knownness('zzqvopaque987654','fr')
    assert result['status']=='CALIBRATED'
    assert result['unknowns']==['zzqvopaque987654']
    calibrator=load_pure('periphery/language/pre_reasoning_calibrator.py')
    directive=load_pure('periphery/language/reasoning_directive.py')
    calibration=calibrator.calibrate_pre_reasoning(user_message='zzqvopaque987654',language='fr',
        lexical_calibration=result,ir_candidate={'unknowns':result['unknowns']})
    observed=directive.build_reasoning_directive(calibration)
    assert observed['reasoning_mode']=='RESOLVE_BEFORE_ASSERT'
    assert observed['resolution_required'] is True
    assert observed['resolution_targets']==['zzqvopaque987654']
    assert observed['decision_authority']=='KX108_ONLY'
    for flag in ('allowed_to_act','allowed_to_decide','emits_act','memory_write','kernel_mutation'):
        assert observed[flag] is False


def test_present_canon_does_not_invent_debt_for_known_concept(lexical):
    result=lexical.calibrate_lexical_knownness('X108','fr')
    assert result['status']=='CALIBRATED' and result['unknowns']==[]
    calibrator=load_pure('periphery/language/pre_reasoning_calibrator.py')
    directive=load_pure('periphery/language/reasoning_directive.py')
    observed=directive.build_reasoning_directive(calibrator.calibrate_pre_reasoning(
        user_message='X108',language='fr',lexical_calibration=result,ir_candidate={}))
    assert observed['resolution_required'] is False
    assert observed['reasoning_mode']=='NORMAL_REASONING'


def test_updated_guard_and_complete_manifest():
    from studio_e11_deployment import verify_checkpoint,BASE_URL,DEPLOYMENT,MANIFEST_SHA256
    checked=verify_checkpoint(BASE_URL)
    assert checked and checked['files_verified']==1537 and checked['base_file_count']==1527
    assert checked['checkpoint']=='cbad01257c027e5861a1c0610d418dfd02fc8342'
    raw=(DEPLOYMENT/'EXPORT_MANIFEST.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==MANIFEST_SHA256
    manifest=json.loads(raw)
    assert manifest['file_count']==len(manifest['files'])==1537
    assert manifest['base_file_count']==1527 and len(manifest['overlay']['files'])==16
    assert manifest['total_bytes']==sum(e['bytes'] for e in manifest['files'])
    entry=next(e for e in manifest['files'] if e['path']==REL)
    assert entry['git_blob']==BLOB
    assert not any(e['path']==REL for e in json.loads((DEPLOYMENT/'EXCLUSIONS.json').read_bytes()))
    index=json.loads((DEPLOYMENT/'evidence_manifest.sha256.json').read_bytes())
    for name in ('EXPORT_MANIFEST.json','EXPORT_MANIFEST.json.sha256','EXCLUSIONS.json'):
        assert index['files'][name]==hashlib.sha256((DEPLOYMENT/name).read_bytes()).hexdigest()
