"""Native service-client admission through existing Studio transport, offline."""
import copy,json,sys
from pathlib import Path
from unittest.mock import patch
import pytest
import studio_ai
import studio_native_editorial as native
from test_brody_editorial_repair import server_namespace

A=Path(__file__).parent/'data/experiments/service_client_admission_20261026'


@pytest.fixture(scope='module')
def proof():
    value=native.deployment.verify_checkpoint(native.deployment.BASE_URL)
    assert value and value['files_verified']==1537
    return value


@pytest.fixture(params=[('V1',False),('V1',True),('V2',False),('V2',True)])
def response(request,monkeypatch,proof):
    monkeypatch.setattr(native.deployment,'verify_checkpoint',lambda _:proof)
    version,compact=request.param
    return version,json.loads((A/f'public_A_{version}_{compact}.json').read_text(encoding='utf-8'))


def receive(version,body,brief=None):
    brief=brief or body['pre_reasoning_snapshot']['user_message']
    with patch.object(studio_ai,'_call',return_value=body) as call,patch.object(studio_ai,'_ingress_call') as ingress:
        try:
            result=studio_ai.generate(brief,use_ingress=False,editorial_version=version,return_receipt=True)
        finally:
            # Refusals must also prove one transport call and no fallback.
            call.assert_called_once();ingress.assert_not_called()
        assert call.call_args.args[0].get('editorial_version','V1')==version
        assert 'internal_observation_id' not in call.call_args.args[0]
        assert all(call.call_args.args[0][k] is False for k in ('allow_local_model','allow_provider','allow_memory_candidate','allow_manual_apply'))
    return result


def test_real_public_native_service_client_is_admitted_without_rewriting(response):
    version,body=response;before=copy.deepcopy(body)
    post,meta=receive(version,body)
    assert body==before
    historical=json.loads((A/f'historical_A_{version}.json').read_text())
    assert post=='<POST>'+historical['draft']['text']+'</POST>'
    assert meta['source']=='BRODY_NATIVE_EDITORIAL_'+version and meta['editorial_version']==version
    assert meta['lineage_verified'] and meta['model_calls']==0 and meta['qwen_evidence_applied'] is False
    assert meta['human_approval_required'] is True and meta['publication_permitted'] is False
    assert meta['e11_consumer_status']=='CONTEXT_LIMITED' and meta['memory_retrieval_status']=='MEMORY_NOT_REQUIRED'
    assert meta['uncertainties_count']==3
    assert any(u['kind']=='POSSESSOR_UNRESOLVED' for u in body['editorial_composition_snapshot']['uncertainties'])
    assert not any(name.startswith(('apps.obsidia_api','periphery.language')) for name in sys.modules)


@pytest.mark.parametrize('mutation',[
 'drop_possessor','resolve_possessor','change_span','invent_category','erase_unknowns','erase_all_pre_unknowns',
 'change_subject','change_projection','change_constraint','fake_causal_grounding','missing_explanatory_context',
 'causal_relation_invented','missing_semantic_provenance','wrong_semantic_hash','wrong_semantic_path','qwen_author',
 'copied_text','wrong_factual_status','wrong_proposition_scope','wrong_derived_relation','missing_plan','changed_plan',
 'changed_realization','deleted_sentence_provenance','post_missing','missing_artifact','artifact_unknown','b6_only',
 'hold','block','c1_hold','b6_contradiction','grammar_contradiction','authority','memory_write','factual_claim',
 'publish','root_publish','no_review','missing_provenance','different_brief','other_version','model_call',
 'missing_selected','extra_fact_evidence','essential_unknown','c275_refusal'])
def test_nonconforming_service_client_output_refused(response,mutation):
    version,original=response;body=copy.deepcopy(original)
    s=body['editorial_composition_snapshot'];a=body['editorial_artifact'];brief=original['pre_reasoning_snapshot']['user_message']
    if mutation=='drop_possessor':
        s['uncertainties']=[u for u in s['uncertainties'] if u['kind']!='POSSESSOR_UNRESOLVED'];a['uncertainties']=copy.deepcopy(s['uncertainties'])
    elif mutation=='resolve_possessor':
        for u in s['uncertainties']:
            if u['kind']=='POSSESSOR_UNRESOLVED':u['resolution']='RESOLVED'
        a['uncertainties']=copy.deepcopy(s['uncertainties'])
    elif mutation=='change_span':
        next(u for u in s['uncertainties'] if u['kind']=='POSSESSOR_UNRESOLVED')['source_span']=[0,1]
        a['uncertainties']=copy.deepcopy(s['uncertainties'])
    elif mutation=='invent_category':s['uncertainties'].append({'kind':'VALIDATED_FACT'});a['uncertainties']=copy.deepcopy(s['uncertainties'])
    elif mutation=='erase_unknowns':s['uncertainties']=a['uncertainties']=[]
    elif mutation=='erase_all_pre_unknowns':
        for p in (s['pre_reasoning'],body['pre_reasoning_snapshot'],body['pipeline_pre_reasoning_snapshot']):p['unknowns']=[]
        s['uncertainties']=[u for u in s['uncertainties'] if u['kind']!='UNRESOLVED_SYMBOL'];a['uncertainties']=copy.deepcopy(s['uncertainties'])
    elif mutation=='change_subject':s['subject']['actor']='other'
    elif mutation=='change_projection':s['interpretation']['topic_kind']='IA_TIME_SAVING'
    elif mutation=='change_constraint':s['constraints']['requires_explanation']=True
    elif mutation=='fake_causal_grounding':s['explanatory_context']['causal_relations_grounded']=True
    elif mutation=='missing_explanatory_context':s.pop('explanatory_context')
    elif mutation=='causal_relation_invented':s['explanatory_context']['relations'].append({'relation_type':'VALIDATED_CAUSAL_PROOF'})
    elif mutation in ('missing_semantic_provenance','wrong_semantic_hash','wrong_semantic_path'):
        components=s['provenance']['components'];item=next(x for x in components if x['function']=='_semantic_operations')
        if mutation=='missing_semantic_provenance':components.remove(item)
        elif mutation=='wrong_semantic_hash':item['sha256']='0'*64
        else:item['path']='C:/Users/User/Downloads/untrusted.py'
        a['provenance']=copy.deepcopy(s['provenance'])
    elif mutation=='qwen_author':s['provenance']['author']='QWEN';a['provenance']=copy.deepcopy(s['provenance'])
    elif mutation=='copied_text':s['draft']['text']=a['draft']['text']='A prewritten post from Qwen.'
    elif mutation=='wrong_factual_status':s['selected_propositions'][0]['factual_status']='VERIFIED_FACT'
    elif mutation=='wrong_proposition_scope':s['selected_propositions'][0]['scope']={'actor':'other'}
    elif mutation=='wrong_derived_relation':s['selected_propositions'][0]['derived_from']['subject_unit_ids']=[]
    elif mutation=='missing_plan':s['editorial_plan']=a['editorial_plan']=[]
    elif mutation=='changed_plan':s['editorial_plan'].reverse();a['editorial_plan']=copy.deepcopy(s['editorial_plan'])
    elif mutation=='changed_realization':s['realization']['realizations']=[]
    elif mutation=='deleted_sentence_provenance':s['realization']['sentences'][0].pop('proposition_ids')
    elif mutation=='post_missing':body['response']='Plain B6 context'
    elif mutation=='missing_artifact':body.pop('editorial_artifact')
    elif mutation=='artifact_unknown':a['schema']='BRODY_EDITORIAL_UNVERIFIED'
    elif mutation=='b6_only':body.pop('editorial_artifact');body['final_answer_source']='B6_ADVISORY_CONTEXT'
    elif mutation in ('hold','block'):body['status']=mutation.upper()
    elif mutation=='c1_hold':body['cognitive_runtime_receipt']['decision_ticket_dry_run']['decision']='HOLD'
    elif mutation=='b6_contradiction':body['cognitive_runtime_receipt']['cognition_shadow_memory']['context_packet']['contradictions']=['conflict']
    elif mutation=='grammar_contradiction':s['grammar']['contradictions']=['conflict']
    elif mutation=='authority':a['decision_authority']='BRODY'
    elif mutation=='memory_write':a['memory_write']=True
    elif mutation=='factual_claim':a['draft']['factual_claims']=['unverified']
    elif mutation=='publish':a['publication_permitted']=True
    elif mutation=='root_publish':body['publication_permitted']=True
    elif mutation=='no_review':a['human_review_required']=False
    elif mutation=='missing_provenance':a.pop('provenance')
    elif mutation=='different_brief':brief=brief.replace('service client','stock')
    elif mutation=='other_version':a['editorial_version']='V2' if version=='V1' else 'V1'
    elif mutation=='model_call':s['provenance']['model_calls']=1;a['provenance']=copy.deepcopy(s['provenance'])
    elif mutation=='missing_selected':s['selected_propositions']=[]
    elif mutation=='extra_fact_evidence':s['evidence_refs']=['unqualified-fact']
    elif mutation=='essential_unknown':
        for p in (s['pre_reasoning'],body['pre_reasoning_snapshot'],body['pipeline_pre_reasoning_snapshot']):
            p['unknowns'].append('contact');p['unknown_qualification']['unresolved_unknowns']=copy.deepcopy(p['unknowns'])
        s['uncertainties'].insert(2,{'kind':'UNRESOLVED_SYMBOL','symbol':'contact'});a['uncertainties']=copy.deepcopy(s['uncertainties'])
        s['essential_unresolved_symbols']=[]
    elif mutation=='c275_refusal':body['pre_response_calibration']['calibration_required']=True
    with pytest.raises(studio_ai.InferenceError):receive(version,body,brief)


def test_service_client_normal_compact_payloads_have_identical_artifact_and_text():
    for version in ('V1','V2'):
        a=json.loads((A/f'public_A_{version}_False.json').read_text());b=json.loads((A/f'public_A_{version}_True.json').read_text())
        assert a['editorial_artifact']==b['editorial_artifact'] and a['response']==b['response']


@pytest.mark.parametrize('version',['V1','V2'])
def test_missing_human_review_flag_v2_refused_but_v1_keeps_existing_contract(monkeypatch,proof,version):
    monkeypatch.setattr(native.deployment,'verify_checkpoint',lambda _:proof)
    body=json.loads((A/f'public_A_{version}_False.json').read_text())
    if version=='V2':
        body['editorial_artifact'].pop('human_review_required')
        with pytest.raises(studio_ai.InferenceError):receive(version,body)
    else:
        assert 'human_review_required' not in body['editorial_artifact']
        assert receive(version,body)[1]['human_approval_required'] is True


@pytest.mark.parametrize('version',['V1','V2'])
def test_service_client_server_preserves_brief_and_explicit_version(monkeypatch,proof,version):
    monkeypatch.setattr(native.deployment,'verify_checkpoint',lambda _:proof)
    monkeypatch.setenv('OBSIDIA_STUDIO_EDITORIAL_MODE','brody_native');monkeypatch.setenv('OBSIDIA_STUDIO_ALLOW_BRODY_NATIVE','1')
    body=json.loads((A/f'public_A_{version}_False.json').read_text());ns=server_namespace()
    subject="Comment une petite entreprise peut utiliser l'IA pour améliorer son service client sans perdre le contact humain ?"
    with patch.object(studio_ai,'_call',return_value=body) as call,patch.object(studio_ai,'_ingress_call') as ingress:
        out=ns['generate'](ns['GenIn'](idea=subject,editorial_version=version))
    call.assert_called_once();ingress.assert_not_called()
    assert call.call_args.args[0]['message']==body['pre_reasoning_snapshot']['user_message']
    assert call.call_args.args[0].get('editorial_version','V1')==version
    assert out['provenance']['human_approval_required'] is True and out['provenance']['publication_permitted'] is False
