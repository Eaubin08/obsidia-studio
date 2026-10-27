"""10K: metadata privacy, field provenance and unchanged decisions; no real HTTP."""
import copy
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from studio_e11_receipt_diagnostics import (
    MAX_COUNT, SURFACES, extract_receipt_diagnostics, sanitize_receipt_diagnostics)
from studio_e11_contract import diagnostic_summary
from studio_e11_diagnostic_client import summarize_result
from test_studio_e11_lot1 import envelope, consume, runtime, endpoint_app, http_request


def observed_envelope():
    body=envelope('MEMORY_NOT_REQUIRED','DEGRADED')
    receipt=body['cognitive_runtime_receipt']
    shadow=receipt['cognition_shadow_memory']
    entry=copy.deepcopy(envelope()['cognitive_runtime_receipt']['cognition_shadow_memory']['memory_entries'][0])
    entry.update(state_type='SENS_FRAME',status='OPEN',payload={'semantic_closure':{
        'closed':False,'reasons':['no_predicate_unit','frame:missing:PRIVATE_DETAIL',
                                 'event_reference:AMBIGUOUS:PRIVATE_DETAIL','PRIVATE_UNKNOWN_REASON']}})
    shadow['state_entries']=[entry]
    shadow['context_packet']['omitted']=[{'state_id':'PRIVATE_ID','reason':'irrelevant_to_query'},
                                        {'state_id':'PRIVATE_ID_2','reason':'PRIVATE_REASON'}]
    shadow['resolution_requests']=[{'unresolved_kind':'COREFERENCE','problem_refs':['PRIVATE_REF']},
                                   {'why_resolution_needed':'PRIVATE_QUESTION'}]
    receipt['components'].update(NPL='SKIPPED_NOT_AVAILABLE:PRIVATE_PATH',LYAPUNOV='READY:PRIVATE_PATH',
                                  SIGMA='ERROR:PRIVATE_EXCEPTION',PRIVATE_COMPONENT='PRIVATE_STATUS')
    return body


def test_explicit_receipt_fields_only_and_private_suffixes_removed():
    body=observed_envelope();receipt=body['cognitive_runtime_receipt'];before=copy.deepcopy(receipt)
    diag=extract_receipt_diagnostics(receipt)
    assert receipt==before
    assert diag['b6_omission_count']==2
    assert set(diag['b6_omission_categories'])=={'irrelevant_to_query','UNKNOWN'}
    assert diag['sens_closure_category']=='OPEN'
    assert set(diag['sens_closure_reason_categories'])=={'NO_PREDICATE_UNIT','FRAME_MISSING','EVENT_REFERENCE','UNKNOWN'}
    assert diag['b7_request_count']==2 and set(diag['b7_request_categories'])=={'COREFERENCE','UNKNOWN'}
    assert set(diag['c1_degradation_reasons'])=={'RECEIPT_DEGRADED','COMPONENT_UNAVAILABLE',
        'NPL_UNAVAILABLE','COMPONENT_ERROR','UNKNOWN_COMPONENT_STATUS'}
    assert diag['cognitive_surface_availability']==dict(SENS='PRESENT',B6='PRESENT',B7='PRESENT',
        E11='PRESENT',NPL='UNAVAILABLE',LYAPUNOV='PRESENT',M41='UNKNOWN')
    assert 'PRIVATE_' not in json.dumps(diag)


def test_absent_fields_are_unknown_not_zero_or_static_predictions():
    diag=extract_receipt_diagnostics({})
    assert diag['b6_omission_count']==diag['b7_request_count']=='UNKNOWN'
    assert diag['sens_closure_category']=='UNKNOWN'
    assert diag['b6_omission_categories']==diag['b7_request_categories']==['UNKNOWN']
    assert diag['c1_degradation_reasons']==['UNKNOWN']
    assert set(diag['cognitive_surface_availability'].values())=={'UNKNOWN'}


def test_explicit_empty_lists_are_distinct_from_missing():
    diag=extract_receipt_diagnostics(envelope()['cognitive_runtime_receipt'])
    assert diag['b6_omission_count']==diag['b7_request_count']==0
    assert diag['b6_omission_categories']==diag['b7_request_categories']==[]
    assert diag['c1_degradation_reasons']==[]
    assert diag['sens_closure_category']=='UNKNOWN'
    assert diag['cognitive_surface_availability']['B7']=='PRESENT'


@pytest.mark.parametrize('closed,expected',[(True,'CLOSED'),(False,'OPEN'),(None,'UNKNOWN'),(1,'UNKNOWN'),('false','UNKNOWN')])
def test_sens_category_requires_explicit_boolean(closed,expected):
    receipt=observed_envelope()['cognitive_runtime_receipt']
    closure=receipt['cognition_shadow_memory']['state_entries'][0]['payload']['semantic_closure']
    closure['closed']=closed
    assert extract_receipt_diagnostics(receipt)['sens_closure_category']==expected


def test_open_state_does_not_invent_closure_or_b7_category():
    receipt=observed_envelope()['cognitive_runtime_receipt']
    receipt['cognition_shadow_memory']['state_entries'][0]['payload']={}
    receipt['cognition_shadow_memory']['resolution_requests']=[{'uncertainty':['PRIVATE_TEXT']}]
    diag=extract_receipt_diagnostics(receipt)
    assert diag['sens_closure_category']=='UNKNOWN'
    assert diag['sens_closure_reason_categories']==['UNKNOWN']
    assert diag['b7_request_categories']==['UNKNOWN']


@pytest.mark.parametrize('category',['COREFERENCE','SOURCE_SCOPE','CONDITIONAL_ATTACHMENT','TEMPORAL_REFERENCE',
    'DEIXIS','ENTITY_IDENTITY','CONTRADICTION','UNKNOWN_TERM_OR_PREDICATE','DOMAIN_SPECIFIC_AMBIGUITY',
    'WORLD_OR_PHYSICAL_REFERENCE','OTHER_EXPLICIT_UNRESOLVED'])
def test_b7_known_categories_are_copied_without_semantic_validation(category):
    receipt=envelope()['cognitive_runtime_receipt']
    receipt['cognition_shadow_memory']['resolution_requests']=[{'unresolved_kind':category}]
    diag=extract_receipt_diagnostics(receipt)
    assert diag['b7_request_categories']==[category]
    assert 'b7_validated' not in diag


@pytest.mark.parametrize('category',['irrelevant_to_query','visibility_hide','ENTRY_LIMIT','PACKET_SIZE_LIMIT'])
def test_omission_categories_are_read_from_reason_not_guessed(category):
    receipt=envelope()['cognitive_runtime_receipt']
    receipt['cognition_shadow_memory']['context_packet']['omitted']=[{'reason':category}]
    assert extract_receipt_diagnostics(receipt)['b6_omission_categories']==[category]
    receipt['cognition_shadow_memory']['context_packet']['omitted']=[{'state_type':'NATIVE_MEMORY_ITEM'}]
    assert extract_receipt_diagnostics(receipt)['b6_omission_categories']==['UNKNOWN']


@pytest.mark.parametrize('value,expected',[(None,'NOT_PRESENT'),({},'NOT_PRESENT'),
    ({'status':'PRIVATE_STATUS'},'PRESENT'),([], 'UNKNOWN')])
def test_m41_surface_presence_is_not_validation(value,expected):
    receipt=envelope()['cognitive_runtime_receipt'];receipt['world_hypothesis_snapshot']=value
    diag=extract_receipt_diagnostics(receipt)
    assert diag['cognitive_surface_availability']['M41']==expected
    assert 'PRIVATE_' not in json.dumps(diag)


def test_metadata_bounds_reject_bool_and_overflow_without_saturation_claims():
    diag=sanitize_receipt_diagnostics({'b6_omission_count':True,'b7_request_count':MAX_COUNT+1,
        'b6_omission_categories':['irrelevant_to_query']*(MAX_COUNT+1),
        'cognitive_surface_availability':{'PRIVATE_SOURCE':'PRIVATE_TEXT','SENS':{'private':'text'}}})
    assert diag['b6_omission_count']==diag['b7_request_count']=='UNKNOWN'
    assert diag['b6_omission_categories']==['UNKNOWN']
    assert set(diag['cognitive_surface_availability'])==set(SURFACES)
    assert 'PRIVATE_' not in json.dumps(diag)


def test_real_c1_stage_error_format_is_normalized_without_exception_text():
    receipt=envelope()['cognitive_runtime_receipt']
    receipt['components']['SIGMA']='SIGMA:DEGRADED:ValueError:PRIVATE_EXCEPTION'
    diag=extract_receipt_diagnostics(receipt)
    assert diag['c1_degradation_reasons']==['COMPONENT_ERROR']
    assert 'PRIVATE_' not in json.dumps(diag) and 'ValueError' not in json.dumps(diag)


def test_output_size_is_bounded_even_with_all_categories_and_private_values():
    import studio_e11_receipt_diagnostics as d
    malicious={'b6_omission_count':d.MAX_COUNT,'b7_request_count':d.MAX_COUNT,
        'b6_omission_categories':list(d.OMISSION_CATEGORIES)*20,
        'b7_request_categories':list(d.B7_CATEGORIES)*20,
        'sens_closure_reason_categories':list(d.CLOSURE_REASON_CATEGORIES)*20,
        'c1_degradation_reasons':list(d.DEGRADATION_CATEGORIES)*20,
        'cognitive_surface_availability':{name:'PRIVATE_'+'x'*10000 for name in d.SURFACES}}
    encoded=json.dumps(d.sanitize_receipt_diagnostics(malicious))
    assert len(encoded.encode())<4096 and 'PRIVATE_' not in encoded


def test_api_client_and_journal_share_all_fields_and_do_not_mutate_receipt(runtime):
    s,j,calls,opener,*_=runtime
    body=observed_envelope();before=copy.deepcopy(body)
    reply=Mock();reply.__enter__=Mock(return_value=reply);reply.__exit__=Mock(return_value=False)
    reply.getcode.return_value=200;reply.read.return_value=json.dumps(body).encode()
    opener.open.side_effect=None;opener.open.return_value=reply
    response=http_request(endpoint_app())
    assert response.status_code==200 and opener.open.call_count==1
    result=response.json();client=summarize_result(result);event=json.loads(j.JOURNAL_PATH.read_text())
    for key,value in diagnostic_summary(result).items():
        assert result[key]==client[key]==event[key]==value
    assert result['original_receipt']==before['cognitive_runtime_receipt'] and body==before
    assert 'PRIVATE_' not in json.dumps(client) and 'PRIVATE_' not in j.JOURNAL_PATH.read_text()


def test_journal_sanitizes_injected_new_metadata(runtime):
    s,j,*_=runtime;result=consume(envelope())
    for key in sanitize_receipt_diagnostics({}):result[key]='PRIVATE_TEXT'
    result['cognitive_surface_availability']={'NPL':'UNAVAILABLE','PRIVATE_COMPONENT':'PRIVATE_TEXT'}
    j.record_experiment(result,elapsed_ms=1,response_bytes=2)
    event=json.loads(j.JOURNAL_PATH.read_text())
    assert 'PRIVATE_' not in json.dumps(event)
    assert event['cognitive_surface_availability']['NPL']=='UNAVAILABLE'


@pytest.mark.parametrize('decision',['HOLD','BLOCK'])
def test_unaccepted_receipt_is_not_mined_for_diagnostics(decision):
    body=observed_envelope();body['cognitive_runtime_receipt']['decision_ticket_dry_run']['decision']=decision
    result=consume(body)
    assert result['consumer_status']=='REFUSED' and result['governance_status']==decision
    assert result['original_receipt'] is None
    assert sanitize_receipt_diagnostics(result)==sanitize_receipt_diagnostics({})


@pytest.fixture(scope='module')
def baseline_10h():
    root=Path(__file__).parent
    data=(root/'data/experiments/e11_lot1/passe10k/consumer_10h.snapshot').read_bytes()
    recorded=json.loads((root/'data/experiments/e11_lot1/passe10i/run_report.json').read_text(encoding='utf-8-sig'))
    assert hashlib.sha256(data).hexdigest()==recorded['source_sha256']['studio_e11_contract.py']
    namespace={};exec(compile(data,'verified_10h_baseline','exec'),namespace)
    return namespace['consume_envelope']


@pytest.mark.parametrize('mode',['not_required','usable','empty','no_source','invalid_source','unavailable',
    'unknown_memory','degraded','unknowns','omissions','open_sens','closure_only','b7','npl','lyapunov',
    'm41','hold','block','authority','bad_e11','bad_b6','malformed_optional'])
def test_decisions_and_original_content_equal_verified_10h_baseline(baseline_10h,mode):
    memory={'not_required':'MEMORY_NOT_REQUIRED','empty':'MEMORY_REQUIRED_EMPTY',
        'no_source':'MEMORY_REQUIRED_NO_NATIVE_SOURCE','invalid_source':'MEMORY_REQUIRED_INVALID_NATIVE_SOURCE',
        'unavailable':'MEMORY_UNAVAILABLE','unknown_memory':'FUTURE_PRIVATE_STATUS'}.get(mode,'MEMORY_USABLE')
    body=envelope(memory,'DEGRADED' if mode=='degraded' else 'COMPLETE')
    receipt=body['cognitive_runtime_receipt'];shadow=receipt['cognition_shadow_memory'];packet=shadow['context_packet']
    if mode=='unknowns':packet['unknowns']=[{'status':'OPEN','uncertainty':['PRIVATE_TEXT']}]
    elif mode=='omissions':packet['omitted']=[{'reason':'ENTRY_LIMIT','state_id':'PRIVATE_ID'}]
    elif mode in ('open_sens','closure_only'):
        entry=copy.deepcopy(observed_envelope()['cognitive_runtime_receipt']['cognition_shadow_memory']['state_entries'][0])
        entry['status']='OPEN' if mode=='open_sens' else 'KNOWN'
        shadow['state_entries']=[entry]
    elif mode=='b7':shadow['resolution_requests']=[{'unresolved_kind':'CONTRADICTION'}]
    elif mode in ('npl','lyapunov'):receipt['components'][mode.upper()]='SKIPPED_NOT_AVAILABLE:PRIVATE_REASON'
    elif mode=='m41':receipt['world_hypothesis_snapshot']={'members':[{'unknowns':['PRIVATE_HYPOTHESIS']}]}
    elif mode in ('hold','block'):receipt['decision_ticket_dry_run']['decision']=mode.upper()
    elif mode=='authority':body['decision_authority']='OTHER'
    elif mode=='bad_e11':shadow['schema']='FUTURE'
    elif mode=='bad_b6':packet['schema']='FUTURE'
    elif mode=='malformed_optional':receipt.update(world_hypothesis_snapshot=['PRIVATE_DATA'],components={'COGNITION_SHADOW_MEMORY':'OK','NPL':{'status':'PRIVATE_DATA'}})
    before=copy.deepcopy(body)
    old=baseline_10h(body,experiment_id='synthetic',provenance={'test':'unchanged'})
    new=__import__('studio_e11_contract').consume_envelope(body,experiment_id='synthetic',provenance={'test':'unchanged'})
    assert {key:new[key] for key in old if key!='diagnostics_version'}=={key:value for key,value in old.items() if key!='diagnostics_version'}
    assert body==before
