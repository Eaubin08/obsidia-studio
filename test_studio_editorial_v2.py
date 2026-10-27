"""Explicit V2 admission against actual deployed public offline responses."""
import copy
import json
from pathlib import Path
from unittest.mock import patch
import pytest
import studio_ai
import studio_native_editorial as native
from test_brody_editorial_repair import server_namespace

A = Path(__file__).parent / 'data/experiments/internal_observation_integration_20261024'

@pytest.fixture(scope='module')
def proof():
    p = native.deployment.verify_checkpoint(native.deployment.BASE_URL)
    assert p and p['files_verified'] == 1537
    return p

@pytest.fixture(params=[False, True], ids=['normal','compact'])
def response(request, monkeypatch, proof):
    monkeypatch.setattr(native.deployment,'verify_checkpoint',lambda _:proof)
    return json.loads((A / ('public_fixture_V2_'+str(request.param)+'.json')).read_text(encoding='utf-8'))

def receive(body, version='V2'):
    brief=body['pre_reasoning_snapshot']['user_message']
    with patch.object(studio_ai,'_call',return_value=body) as call, patch.object(studio_ai,'_ingress_call') as ingress:
        result=studio_ai.generate(brief,use_ingress=False,editorial_version=version,return_receipt=True)
        call.assert_called_once();ingress.assert_not_called()
        assert call.call_args.args[0].get('editorial_version','V1')==version
        assert all(call.call_args.args[0][key] is False for key in ('allow_local_model','allow_provider','allow_memory_candidate','allow_manual_apply'))
    return result

def test_v2_admits_native_response_preserving_limits(response):
    before=copy.deepcopy(response)
    text,meta=receive(response)
    assert response==before
    assert text=='<POST>'+response['editorial_artifact']['draft']['text']+'</POST>'
    assert meta['source']=='BRODY_NATIVE_EDITORIAL_V2' and meta['editorial_version']=='V2'
    assert meta['lineage_verified'] and meta['model_calls']==0
    assert meta['e11_consumer_status']=='CONTEXT_LIMITED'
    assert meta['memory_retrieval_status']=='MEMORY_NOT_REQUIRED'
    assert meta['uncertainties_count']>0
    assert meta['human_approval_required'] and meta['publication_permitted'] is False

@pytest.mark.parametrize('mutation',[
 'wrong_selected_version','wrong_requested_version','snapshot_version','artifact_version',
 'missing_selection','selection_not_explicit','native_schema','missing_plan','changed_plan',
 'selected_missing','selected_changed','realization_missing','realization_changed','evidence_changed',
 'human_review_missing','publication','qwen_source','qwen_component','wrong_hash','model_calls',
 'factual_claim','contradiction','essential_unknown','unknown_erased','c275','hold','block',
 'authority','memory_write','b6_only','missing_provenance','wrong_schema','missing_receipt'])
def test_v2_fail_closed(response,mutation):
    body=copy.deepcopy(response);a=body['editorial_artifact'];s=body['editorial_composition_snapshot']
    if mutation=='wrong_selected_version':body['editorial_version_selected']='V1'
    elif mutation=='wrong_requested_version':body['editorial_version_requested']='V1'
    elif mutation=='snapshot_version':s['editorial_version']='V1'
    elif mutation=='artifact_version':a['editorial_version']='V1'
    elif mutation=='missing_selection':a.pop('selection_provenance')
    elif mutation=='selection_not_explicit':a['selection_provenance']['kind']='INFERRED'
    elif mutation=='native_schema':a['native_composition_schema']='BRODY_NATIVE_EDITORIAL_V1'
    elif mutation=='missing_plan':a.pop('editorial_plan')
    elif mutation=='changed_plan':s['editorial_plan'][0]['role']='conclusion';a['editorial_plan']=copy.deepcopy(s['editorial_plan'])
    elif mutation=='selected_missing':a.pop('selected_propositions')
    elif mutation=='selected_changed':a['selected_propositions'][0]['factual_status']='VERIFIED'
    elif mutation=='realization_missing':a.pop('realization')
    elif mutation=='realization_changed':a['realization']['text']='Qwen text'
    elif mutation=='evidence_changed':a['evidence_refs']=['invented']
    elif mutation=='human_review_missing':a.pop('human_review_required')
    elif mutation=='publication':a['publication_permitted']=True
    elif mutation=='qwen_source':body['final_answer_source']='QWEN'
    elif mutation=='qwen_component':s['provenance']['author']='QWEN';a['provenance']=copy.deepcopy(s['provenance'])
    elif mutation=='wrong_hash':s['provenance']['components'][0]['sha256']='0'*64;a['provenance']=copy.deepcopy(s['provenance'])
    elif mutation=='model_calls':s['provenance']['model_calls']=1;a['provenance']=copy.deepcopy(s['provenance'])
    elif mutation=='factual_claim':s['draft']['factual_claims']=['invented'];a['draft']=copy.deepcopy(s['draft'])
    elif mutation=='contradiction':s['grammar']['contradictions']=['conflict']
    elif mutation=='essential_unknown':s['essential_unresolved_symbols']=['unknown']
    elif mutation=='unknown_erased':s['uncertainties']=[];a['uncertainties']=[]
    elif mutation=='c275':body['pre_response_calibration']['calibration_required']=True
    elif mutation in ('hold','block'):body['status']=mutation.upper()
    elif mutation=='authority':body['decision_authority']='QWEN'
    elif mutation=='memory_write':a['memory_write']=True
    elif mutation=='b6_only':body.pop('editorial_artifact');body['final_answer_source']='B6_ADVISORY_CONTEXT'
    elif mutation=='missing_provenance':a.pop('provenance')
    elif mutation=='wrong_schema':a['schema']='BRODY_PUBLIC_EDITORIAL_ARTIFACT_V1'
    elif mutation=='missing_receipt':body.pop('cognitive_runtime_receipt')
    with pytest.raises(studio_ai.InferenceError):receive(body)

@pytest.mark.parametrize('version',['V1',None,True,'v2','V3',' V2'])
def test_response_does_not_select_requested_version(response,version):
    with pytest.raises(studio_ai.InferenceError):receive(response,version)

@pytest.mark.parametrize('version',[None,True,'V3','v2',' V2'])
def test_bad_version_never_calls_transport(version):
    with patch.object(studio_ai,'_call') as call,patch.object(studio_ai,'_ingress_call') as ingress:
        with pytest.raises(studio_ai.InferenceError):studio_ai.generate('brief',use_ingress=False,editorial_version=version)
        call.assert_not_called();ingress.assert_not_called()

def test_v2_ingress_refused_before_any_call():
    with patch.object(studio_ai,'_call') as call,patch.object(studio_ai,'_ingress_call') as ingress:
        with pytest.raises(studio_ai.InferenceError,match='V2_NATIVE_ENDPOINT_REQUIRED'):
            studio_ai.generate('brief',use_ingress=True,editorial_version='V2')
        call.assert_not_called();ingress.assert_not_called()

def test_old_fixture_not_reinterpreted_after_overlay(proof,monkeypatch):
    monkeypatch.setattr(native.deployment,'verify_checkpoint',lambda _:proof)
    old=A.parent/'native_editorial_integration_20261023/public_fixture_False.json'
    body=json.loads(old.read_text(encoding='utf-8'))
    with pytest.raises(studio_ai.InferenceError):receive(body,'V1')

def test_v1_native_draft_byte_identical_to_baseline():
    old=A.parent/'native_editorial_integration_20261023/public_fixture_False.json'
    before=json.loads(old.read_text(encoding='utf-8'))
    after=json.loads((A/'public_fixture_False.json').read_text(encoding='utf-8'))
    assert before['editorial_artifact']['draft']==after['editorial_artifact']['draft']
    assert 'editorial_version_requested' not in after

@pytest.mark.parametrize('version',['V1','V2'])
def test_server_forwards_explicit_v2_only(monkeypatch,version):
    monkeypatch.setenv('OBSIDIA_STUDIO_EDITORIAL_MODE','brody_native')
    monkeypatch.setenv('OBSIDIA_STUDIO_ALLOW_BRODY_NATIVE','1')
    ns=server_namespace()
    with patch.object(studio_ai,'generate',return_value=('<POST>Un brouillon.</POST>',{'publication_permitted':False})) as call:
        result=ns['generate'](ns['GenIn'](idea='Un sujet',editorial_version=version))
    assert call.call_args.kwargs.get('editorial_version','V1')==version
    if version=='V1':assert 'editorial_version' not in call.call_args.kwargs
    assert result['provenance']['publication_permitted'] is False

@pytest.mark.parametrize('version',[None,True,'v2','V3',' V2'])
def test_request_schema_rejects_invalid_versions(version):
    with pytest.raises(ValueError):server_namespace()['GenIn'](idea='Sujet',editorial_version=version)

def test_request_schema_default_v1():
    assert server_namespace()['GenIn'](idea='Sujet').editorial_version=='V1'

@pytest.mark.parametrize('compact',[False,True])
def test_v1_response_cannot_satisfy_explicit_v2(compact,monkeypatch,proof):
    monkeypatch.setattr(native.deployment,'verify_checkpoint',lambda _:proof)
    body=json.loads((A/('public_fixture_'+str(compact)+'.json')).read_text(encoding='utf-8'))
    with pytest.raises(studio_ai.InferenceError):receive(body,'V2')

def test_server_v2_ingress_refused_without_transport(monkeypatch):
    monkeypatch.setenv('OBSIDIA_STUDIO_EDITORIAL_MODE','governed_ingress')
    ns=server_namespace()
    with patch.object(studio_ai,'generate') as call:
        with pytest.raises(Exception) as error:ns['generate'](ns['GenIn'](idea='Sujet',editorial_version='V2'))
        assert error.value.status_code==409
        call.assert_not_called()
