"""Offline public-response integration; fixtures contain only the public brief.

Fixtures came from the deployed public Python function, not an HTTP request.
All mutation cases must retain fail-closed behavior, normal and compact.
"""
import copy
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import studio_ai
import studio_native_editorial as native

ARTIFACTS = Path(__file__).parent / 'data/experiments/internal_observation_integration_20261024'


@pytest.fixture(scope='module')
def verified_deployment():
    proof = native.deployment.verify_checkpoint(native.deployment.BASE_URL)
    assert proof and proof['files_verified'] == 1537
    return proof


@pytest.fixture(params=[False, True], ids=['normal', 'compact'])
def public(request, monkeypatch, verified_deployment):
    # Lineage mutants do not change deployment files. Verify that independent
    # boundary once, then isolate these tests from repeated 556 MB hashing.
    monkeypatch.setattr(native.deployment, 'verify_checkpoint', lambda _: verified_deployment)
    return json.loads((ARTIFACTS / ('public_fixture_' + str(request.param) + '.json')).read_text(encoding='utf-8'))


def test_public_native_admitted_without_retrieval_or_model(public):
    before = copy.deepcopy(public)
    brief = public['pre_reasoning_snapshot']['user_message']
    with patch.object(studio_ai, '_call', return_value=public) as call, patch.object(studio_ai, '_ingress_call') as ingress:
        post, receipt = studio_ai.generate(brief, use_ingress=False, return_receipt=True)
    call.assert_called_once(); ingress.assert_not_called()
    assert public == before
    assert post == '<POST>' + public['editorial_artifact']['draft']['text'] + '</POST>'
    assert receipt['lineage_verified'] is True and receipt['model_calls'] == 0
    assert receipt['human_approval_required'] is True and receipt['publication_permitted'] is False
    assert receipt['e11_consumer_status'] == 'CONTEXT_LIMITED'
    assert receipt['memory_retrieval_status'] == 'MEMORY_NOT_REQUIRED'
    assert public['pre_reasoning_snapshot']['reasoning_directive']['resolution_required'] is True
    assert receipt['uncertainties_count'] == len(public['editorial_composition_snapshot']['uncertainties']) > 0
    assert not call.call_args.args[0]['allow_local_model']
    assert not any(name.startswith(('apps.obsidia_api', 'periphery.language')) for name in __import__('sys').modules)


@pytest.mark.parametrize('mutation', [
    'post_absent','qwen','source','provenance','component_hash','selected','plan','realization',
    'text','factual_claim','contradiction','essential_unknown','unknown_erased','c275',
    'hold','block','authority','writer','memory_unknown','e11_schema','b6_schema','snapshot_mismatch',
    'ticket','admission','missing_receipt','unknown_status','unknown_memory','wrong_brief','cross_brief','hidden_dependency',
    'missing_essential','missing_hold','missing_evidence',
])
def test_public_mutants_refused(public, mutation):
    d=copy.deepcopy(public);s=d['editorial_composition_snapshot'];a=d['editorial_artifact']
    receipt=d['cognitive_runtime_receipt'];e11=receipt['cognition_shadow_memory']
    brief=d['pre_reasoning_snapshot']['user_message']
    if mutation=='post_absent':d['response']='context only'
    elif mutation=='qwen':a['draft']['author']='QWEN'
    elif mutation=='source':d['final_answer_source']='B6_ADVISORY_CONTEXT'
    elif mutation=='provenance':a.pop('provenance')
    elif mutation=='component_hash':s['provenance']['components'][0]['sha256']='0'*64
    elif mutation=='selected':s['selected_propositions'].reverse()
    elif mutation=='plan':s['editorial_plan']=[]
    elif mutation=='realization':s['realization']['realizations']=[]
    elif mutation=='text':a['draft']['text']='Texte utilisateur ou Qwen à recopier.'
    elif mutation=='factual_claim':a['draft']['factual_claims']=['UNVERIFIED']
    elif mutation=='contradiction':e11['context_packet']['contradictions']=['CONFLICT']
    elif mutation=='essential_unknown':s['essential_unresolved_symbols']=['IA']
    elif mutation=='unknown_erased':a['uncertainties']=[]
    elif mutation=='c275':d['pre_response_calibration']['calibration_required']=True
    elif mutation=='hold':d['status']='HOLD'
    elif mutation=='block':d['status']='BLOCK'
    elif mutation=='authority':a['decision_authority']='OTHER'
    elif mutation=='writer':a['memory_write']=True
    elif mutation=='memory_unknown':e11['memory_snapshot_ref']['status']='NEW_SUCCESS'
    elif mutation=='e11_schema':e11['schema']='UNSUPPORTED'
    elif mutation=='b6_schema':e11['context_packet']['schema']='UNSUPPORTED'
    elif mutation=='snapshot_mismatch':d['pre_reasoning_snapshot']['unknowns']=[]
    elif mutation=='ticket':receipt['decision_ticket_dry_run']['decision']='HOLD'
    elif mutation=='admission':receipt['kx108_admission']='BLOCK'
    elif mutation=='missing_receipt':d.pop('cognitive_runtime_receipt')
    elif mutation=='unknown_status':d['status']='NEW_SUCCESS'
    elif mutation=='unknown_memory':e11['memory_snapshot_ref']['selected_items_count']=1
    elif mutation=='cross_brief':
        for p in (s['pre_reasoning'],d['pre_reasoning_snapshot'],d['pipeline_pre_reasoning_snapshot']):
            p['user_message']='Autre demande sans lien avec le brief courant.'
    elif mutation=='hidden_dependency':
        for p in (s['pre_reasoning'],d['pre_reasoning_snapshot'],d['pipeline_pre_reasoning_snapshot']):
            p['unknowns']=['IA']
        s['uncertainties']=a['uncertainties']=[{'kind':'UNRESOLVED_SYMBOL','symbol':'IA'}]
        s['essential_unresolved_symbols']=[]  # self-declared closure is not sufficient
    elif mutation=='missing_essential':s.pop('essential_unresolved_symbols')
    elif mutation=='missing_hold':s.pop('hold_reasons')
    elif mutation=='missing_evidence':s.pop('evidence_refs')
    else:brief=brief.replace('temps','argent')
    with patch.object(studio_ai,'_call',return_value=d):
        with pytest.raises(studio_ai.InferenceError):
            studio_ai.generate(brief,use_ingress=False)


def test_deployment_mismatch_fails_closed(public):
    with patch.object(native.deployment,'verify_checkpoint',return_value=None):
        with pytest.raises(native.NativeArtifactError):
            native.validate_native_artifact(public,public['pre_reasoning_snapshot']['user_message'])


def test_no_arbitrary_payload_path_is_opened(public):
    public['editorial_artifact']['provenance']['source']['path']='C:/Users/User/Downloads/private'
    with pytest.raises(native.NativeArtifactError):
        native.validate_native_artifact(public,public['pre_reasoning_snapshot']['user_message'])


def test_changed_endpoint_cannot_reuse_local_proof(public, monkeypatch):
    monkeypatch.setenv('OBSIDIA_STUDIO_BRODY_URL','http://127.0.0.1:8111')
    with patch.object(studio_ai,'_call',return_value=public):
        with pytest.raises(studio_ai.InferenceError):
            studio_ai.generate(public['pre_reasoning_snapshot']['user_message'],use_ingress=False)


def test_explicit_brief_preserved_and_bare_subject_has_no_governance_injection():
    brief='Rédige une publication LinkedIn expliquant un sujet inconnu.'
    assert studio_ai._native_editorial_request(brief)==brief
    subject='Comment gagner du temps ?'
    assert studio_ai._native_editorial_request(subject).endswith(subject)
    assert not any(s in studio_ai._native_editorial_request(subject) for s in ('ALLOW','BRODY_SUFFICIENT','<POST>'))
