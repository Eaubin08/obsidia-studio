"""Offline admission of real local Oracle test evidence; no HTTP or models."""
import copy
import json
from pathlib import Path
from unittest.mock import patch
import pytest
import studio_ai
import studio_native_editorial as native
import studio_internal_observation as observation
from test_brody_editorial_repair import server_namespace

A = Path(__file__).parent / 'data/experiments/internal_observation_integration_20261024'
ID = 'oracle-two-thresholds-v1'


@pytest.fixture(scope='module')
def proof():
    result = native.deployment.verify_checkpoint(native.deployment.BASE_URL)
    assert result and result['files_verified'] == 1537
    return result


@pytest.fixture(params=[('V1',False),('V1',True),('V2',False),('V2',True)])
def response(request, monkeypatch, proof):
    monkeypatch.setattr(native.deployment, 'verify_checkpoint', lambda _:proof)
    version, compact = request.param
    return version, json.loads((A/f'observation_{version}_{compact}.json').read_text(encoding='utf-8'))


def receive(version, body, identifier=ID, brief=None):
    brief = brief or body['pre_reasoning_snapshot']['user_message']
    with patch.object(studio_ai, '_call', return_value=body) as call, patch.object(studio_ai, '_ingress_call') as ingress:
        result = studio_ai.generate(brief, use_ingress=False, editorial_version=version,
                    internal_observation_id=identifier, return_receipt=True)
        call.assert_called_once(); ingress.assert_not_called()
        assert call.call_args.args[0]['internal_observation_id'] == ID
        assert all(call.call_args.args[0][k] is False for k in ('allow_local_model','allow_provider','allow_memory_candidate','allow_manual_apply'))
        return result


def test_actual_oracle_admitted_with_local_replay(response):
    version, body = response; before = copy.deepcopy(body)
    text, meta = receive(version, body)
    assert body == before
    assert text == '<POST>'+body['editorial_artifact']['draft']['text']+'</POST>'
    assert meta['observation_verified'] and meta['lineage_verified'] and meta['model_calls'] == 0
    assert meta['source'] == 'BRODY_NATIVE_INTERNAL_OBSERVATION_'+version
    assert meta['validated_causal_proof'] is False
    assert meta['observation_scope'] == 'oracle_freshness:fixed_clock:two_thresholds'
    assert meta['human_approval_required'] and meta['publication_permitted'] is False
    assert meta['e11_consumer_status'] == 'CONTEXT_LIMITED'
    assert meta['memory_retrieval_status'] == 'MEMORY_NOT_REQUIRED' and meta['uncertainties_count'] == 3
    assert not any(n.startswith(('apps.obsidia_api','periphery.language')) for n in __import__('sys').modules)


@pytest.mark.parametrize('mutation', [
 'hash','output','proof_absent','scope','contradiction','causal_generalization','hold','block',
 'qwen','provenance','unknown_artifact','version','type','plan','selected','realization','phrase_provenance',
 'limits','inputs','clock','test_identity','source_identity','unverified','review','publish','writer',
 'authority','unknown_erased','essential','text','b6_only','evidence_refs','id','c275','pre_mismatch',
 'root_publish','root_causal','root_no_review','artifact_contradiction'])
def test_observation_mutants_refused(response, mutation):
    version, original = response; body = copy.deepcopy(original)
    a = body['editorial_artifact']; s = body['editorial_composition_snapshot']; view = a['internal_observation']
    if mutation == 'hash':view['original_observation_sha256'] = '0'*64
    elif mutation == 'output':
        s['internal_observation']['runs'][1]['output']['gate'] = 'ALLOW'
        view['observation'] = copy.deepcopy(s['internal_observation'])
    elif mutation == 'proof_absent':a.pop('internal_observation')
    elif mutation == 'scope':
        s['internal_observation']['scope'] = 'general';view['observation'] = copy.deepcopy(s['internal_observation'])
    elif mutation == 'contradiction':body['cognitive_runtime_receipt']['cognition_shadow_memory']['context_packet']['contradictions'] = ['conflict']
    elif mutation == 'causal_generalization':
        a['validated_causal_proof'] = True;s['internal_observation_verification']['relation']['relation_type'] = 'VALIDATED_CAUSAL_PROOF'
    elif mutation in ('hold','block'):body['status'] = mutation.upper()
    elif mutation == 'qwen':a['draft']['author'] = s['draft']['author'] = 'QWEN'
    elif mutation == 'provenance':a.pop('provenance')
    elif mutation == 'unknown_artifact':a['schema'] = 'ARBITRARY_OBSERVATION_V1'
    elif mutation == 'version':a['editorial_version'] = 'V3'
    elif mutation == 'type':a['kind'] = 'VALIDATED_CAUSAL_PROOF'
    elif mutation == 'plan':s['editorial_plan'] = a['editorial_plan'] = []
    elif mutation == 'selected':s['selected_propositions'] = a['selected_propositions'] = []
    elif mutation == 'realization':s['realization'] = a['realization'] = {}
    elif mutation == 'phrase_provenance':a['realization']['sentences'][0].pop('provenance')
    elif mutation == 'limits':s['internal_observation_verification']['relation']['scope'] = 'all_software'
    elif mutation == 'inputs':view['observation']['runs'][0]['inputs']['threshold_seconds'] = 999
    elif mutation == 'clock':view['observation']['clock']['fixed'] = False
    elif mutation == 'test_identity':view['observation']['test_identity'] = 'invented'
    elif mutation == 'source_identity':view['verification']['provenance']['source']['sha256'] = '0'*64
    elif mutation == 'unverified':s['internal_observation_verification']['status'] = 'HOLD'
    elif mutation == 'review':a['human_review_required'] = False
    elif mutation == 'publish':a['publication_permitted'] = True
    elif mutation == 'writer':a['memory_write'] = True
    elif mutation == 'authority':a['decision_authority'] = 'QWEN'
    elif mutation == 'unknown_erased':a['uncertainties'] = s['uncertainties'] = []
    elif mutation == 'essential':s['essential_unresolved_symbols'] = ['seuil']
    elif mutation == 'text':a['draft']['text'] = s['draft']['text'] = 'Qwen says that all thresholds cause HOLD.'
    elif mutation == 'b6_only':body.pop('editorial_artifact');body['final_answer_source'] = 'B6_ADVISORY_CONTEXT'
    elif mutation == 'evidence_refs':a['evidence_refs'] = s['evidence_refs'] = []
    elif mutation == 'id':a['internal_observation_id'] = 'other'
    elif mutation == 'c275':body['pre_response_calibration']['calibration_required'] = True
    elif mutation == 'pre_mismatch':body['pre_reasoning_snapshot']['user_message'] = 'Other brief'
    elif mutation == 'root_publish':body['publication_permitted'] = True
    elif mutation == 'root_causal':body['validated_causal_proof'] = True
    elif mutation == 'root_no_review':body['human_review_required'] = False
    elif mutation == 'artifact_contradiction':a['contradictions'] = ['conflict']
    with pytest.raises(studio_ai.InferenceError):receive(version, body, brief=original['pre_reasoning_snapshot']['user_message'])


def test_no_implicit_observation_admission(response):
    version, body = response
    with pytest.raises(native.NativeArtifactError):
        native.validate_native_artifact(body, body['pre_reasoning_snapshot']['user_message'], editorial_version=version)


@pytest.mark.parametrize('identifier',['missing','../escape','',True,{},'x'*129])
def test_bad_selection_never_calls_transport(identifier):
    with patch.object(studio_ai, '_call') as call, patch.object(studio_ai, '_ingress_call') as ingress:
        with pytest.raises(studio_ai.InferenceError):
            studio_ai.generate('Rédige une publication LinkedIn expliquant comment le seuil peut modifier le résultat.',
                               use_ingress=False, internal_observation_id=identifier)
        call.assert_not_called();ingress.assert_not_called()


def test_cross_scope_brief_refused_before_transport():
    with patch.object(studio_ai,'_call') as call:
        with pytest.raises(studio_ai.InferenceError):studio_ai.generate('Autre sujet',use_ingress=False,internal_observation_id=ID)
        call.assert_not_called()


def test_ingress_has_no_observation_port():
    with patch.object(studio_ai,'_call') as call, patch.object(studio_ai,'_ingress_call') as ingress:
        with pytest.raises(studio_ai.InferenceError,match='OBSERVATION_NATIVE_ENDPOINT_REQUIRED'):
            studio_ai.generate('subject',use_ingress=True,internal_observation_id=ID)
        call.assert_not_called();ingress.assert_not_called()


@pytest.mark.parametrize('missing',['ACQUIRED_OBSERVATION.json','ACQUIRED_TRACE.json','capture.xml','TRUSTED_OBSERVATIONS.json'])
def test_local_proof_missing_refuses(response,monkeypatch,missing):
    version, body = response; original = Path.read_bytes
    def read(path):
        if path == A/missing:raise FileNotFoundError('fixture missing')
        return original(path)
    monkeypatch.setattr(Path,'read_bytes',read)
    with pytest.raises(studio_ai.InferenceError):receive(version,body)


@pytest.mark.parametrize('file',['ACQUIRED_OBSERVATION.json','ACQUIRED_TRACE.json','capture.xml','TRUSTED_OBSERVATIONS.json'])
def test_local_proof_changed_refuses(response,monkeypatch,file):
    version, body = response; original = Path.read_bytes
    def read(path):
        raw = original(path)
        return raw+b' ' if path == A/file else raw
    monkeypatch.setattr(Path,'read_bytes',read)
    with pytest.raises(studio_ai.InferenceError):receive(version,body)


@pytest.mark.parametrize('key',['internal_observation','internal_observation_reference','internal_observation_verification','internal_observation_catalog'])
def test_client_proof_cannot_register_itself(key):
    ns = server_namespace()
    with pytest.raises(ValueError):ns['GenIn'](idea='brief',**{key:{'verified':True}})


@pytest.mark.parametrize('version',['V1','V2'])
def test_server_explicit_selection_reaches_existing_client(monkeypatch,version):
    monkeypatch.setenv('OBSIDIA_STUDIO_EDITORIAL_MODE','brody_native');monkeypatch.setenv('OBSIDIA_STUDIO_ALLOW_BRODY_NATIVE','1')
    ns=server_namespace()
    with patch.object(studio_ai,'generate',return_value=('<POST>Une explication.</POST>',{'publication_permitted':False})) as call:
        ns['generate'](ns['GenIn'](idea='Rédige une publication LinkedIn expliquant comment le seuil peut modifier le résultat.',
                        internal_observation_id=ID,editorial_version=version))
    assert call.call_args.kwargs['internal_observation_id'] == ID
    assert call.call_args.kwargs.get('editorial_version','V1') == version


def test_existing_v1_v2_draft_bytes_preserved():
    old=A.parent/'native_editorial_v2_integration_20261024'
    for version in ('V1','V2'):
        name='public_fixture_'+('V2_' if version=='V2' else '')+'False.json'
        assert json.loads((A/name).read_text())['editorial_artifact']['draft'] == json.loads((old/name).read_text())['editorial_artifact']['draft']


def test_trusted_catalog_paths_remain_inside_studio():
    from dataclasses import dataclass
    reference=observation.reference_for(ID, json.loads((A/'observation_V1_False.json').read_text())['pre_reasoning_snapshot']['user_message'], lambda **kw:kw)
    assert all(reference[k].is_relative_to(observation.ROOT) for k in ('observation_path','trace_path','test_path','test_result_path'))
