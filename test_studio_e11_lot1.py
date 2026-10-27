"""LOT 1 contracts, synthetic data only. No producer import or live HTTP."""
import copy
import importlib
import json
import math
import os
from pathlib import Path
import uuid
from unittest.mock import Mock

import pytest

BASELINE_CHECKPOINT = '2729000c63915dd8a7749a3d6f6aa820eaab5d91'
PREVIOUS_CHECKPOINT = 'aba5e8bbac68dfae707c6015d69e27eb948c4fed'
CHECKPOINT = 'cbad01257c027e5861a1c0610d418dfd02fc8342'

def contract():
    return importlib.import_module('studio_e11_contract')

def boundary():
    return dict(decision_authority='KX108_ONLY', readonly=True, memory_write=False,
                emits_act=False, kernel_mutation=False, allowed_to_act=False, allowed_to_decide=False)

def envelope(status='MEMORY_USABLE', completeness='COMPLETE'):
    b = boundary()
    entry = dict(state_id='private-source', state_type='NATIVE_MEMORY_ITEM', source_ref='PRIVATE_PATH',
                 payload={'excerpt':'PRIVATE_MEMORY'}, provenance=['PRIVATE_REF'], uncertainty=[],
                 status='KNOWN', visibility='LONG', tags=[], summary='PRIVATE_SUMMARY', readonly=True)
    packet = dict(schema='B6_STATE_EXPLICIT_CONTEXT_PACKET_V1', packet_id='b6ctx_0123456789abcdef',
                  query='PRIVATE_QUESTION', projection={'query_tokens':[], 'included':[], 'omitted':[]},
                  state=[copy.deepcopy(entry)], instructions=[], capabilities={}, provenance_refs=['PRIVATE_REF'],
                  unknowns=[], omitted=[], boundary=copy.deepcopy(b))
    shadow = dict(schema='COGNITION_SHADOW_MEMORY_V0', input_text='PRIVATE_QUESTION',
                  memory_snapshot_ref=dict(schema_version='OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1',status=status,
                                           query='PRIVATE_QUERY',selected_items_count=1 if status=='MEMORY_USABLE' else 0),
                  state_entries=[], memory_entries=[entry] if status=='MEMORY_USABLE' else [],
                  context_packet=packet,resolution_requests=[],boundary={k:b[k] for k in ('readonly','decision_authority','memory_write','emits_act','kernel_mutation')})
    receipt = dict(version='REAL_COGNITIVE_JOIN_C1_V1',rail_mode='SHADOW_READONLY_SUPERPOSED',
                   signal_id='private-signal',created_at='2026-10-16T12:00:00Z',status='READY_SHADOW_READONLY',
                   completeness=completeness,components={'COGNITION_SHADOW_MEMORY':'OK'},errors=[],
                   critical_action_requested=False,kx108_admission='DRY_RUN',
                   decision_ticket_dry_run={'decision':'ALLOW_CONTEXT_ONLY','x108_gate_status':'X108_EVALUATED_DRY_RUN'},
                   real_execution=False,response_governance_applied=False,advisory_only=True,
                   **b,cognition_shadow_memory=shadow)
    return dict(**b,advisory_only=True,x108_mutation=False,real_action=False,emits_verdict=False,
                source='REAL_BRODY_RUNTIME',cognitive_runtime_receipt=receipt)

def consume(body):
    return contract().consume_envelope(body,experiment_id=str(uuid.uuid4()),provenance={})

def at(body, path):
    parts=path.split('.')
    for p in parts[:-1]: body=body[p]
    return body,parts[-1]

def test_valid_preserves_receipt_unknowns_omissions_and_no_truth_claim():
    body=envelope()
    packet=body['cognitive_runtime_receipt']['cognition_shadow_memory']['context_packet']
    packet['unknowns']=[{'state_id':'unknown','status':'UNKNOWN','uncertainty':['PRIVATE_UNKNOWN']}]
    packet['omitted']=[{'state_id':'omitted','reason':'PRIVATE_OMISSION'}]
    original=copy.deepcopy(body); result=consume(body)
    assert result['consumer_status']=='CONTEXT_LIMITED'
    assert body==original
    assert result['original_receipt']==original['cognitive_runtime_receipt']
    assert result['e11_context']['context_packet']['unknowns']==original['cognitive_runtime_receipt']['cognition_shadow_memory']['context_packet']['unknowns']
    assert result['e11_context']['context_packet']['omitted']==original['cognitive_runtime_receipt']['cognition_shadow_memory']['context_packet']['omitted']
    result['original_receipt']['errors'].append('local modification')
    assert body==original
    assert result['documentary_status']=='MEMORY_USABLE'
    assert result['publication_permitted'] is False and result['human_review_required'] is False

@pytest.mark.parametrize('path',[
    'decision_authority','readonly','memory_write','allowed_to_act','allowed_to_decide','emits_act','kernel_mutation',
    'cognitive_runtime_receipt','cognitive_runtime_receipt.version','cognitive_runtime_receipt.rail_mode',
    'cognitive_runtime_receipt.status','cognitive_runtime_receipt.errors','cognitive_runtime_receipt.components',
    'cognitive_runtime_receipt.critical_action_requested','cognitive_runtime_receipt.decision_ticket_dry_run',
    'cognitive_runtime_receipt.cognition_shadow_memory','cognitive_runtime_receipt.cognition_shadow_memory.boundary',
    'cognitive_runtime_receipt.cognition_shadow_memory.memory_snapshot_ref.schema_version',
    'cognitive_runtime_receipt.cognition_shadow_memory.context_packet.unknowns',
    'cognitive_runtime_receipt.cognition_shadow_memory.context_packet.omitted',
    'cognitive_runtime_receipt.cognition_shadow_memory.context_packet.provenance_refs',
])
def test_required_fields_absent_fail_closed(path):
    body=envelope(); obj,key=at(body,path); del obj[key]
    result=consume(body)
    assert result['consumer_status']=='REFUSED' and result['e11_context'] is None

@pytest.mark.parametrize('path,value',[
    ('cognitive_runtime_receipt.version','NEXT'),('cognitive_runtime_receipt.rail_mode','NEXT'),
    ('cognitive_runtime_receipt.cognition_shadow_memory.schema','NEXT'),
    ('cognitive_runtime_receipt.cognition_shadow_memory.context_packet.schema','NEXT'),
    ('cognitive_runtime_receipt.cognition_shadow_memory.memory_snapshot_ref.schema_version','NEXT'),
    ('readonly',1),('memory_write',0),('allowed_to_act','false'),('decision_authority',None),
    ('cognitive_runtime_receipt.errors',{}),('cognitive_runtime_receipt.completeness','UNKNOWN'),
    ('cognitive_runtime_receipt.cognition_shadow_memory.memory_snapshot_ref.selected_items_count',True),
    ('cognitive_runtime_receipt.cognition_shadow_memory.memory_snapshot_ref.status','FUTURE'),
    ('cognitive_runtime_receipt.cognition_shadow_memory.state_entries',{}),
])
def test_versions_and_types(path,value):
    body=envelope(); obj,key=at(body,path); obj[key]=value
    assert consume(body)['consumer_status']=='REFUSED'

@pytest.mark.parametrize('path,value',[
    ('status','HOLD'),('gate_verdict','BLOCK'),('decision_authority','OTHER'),('memory_write',True),
    ('allowed_to_act',True),('allowed_to_decide',True),('emits_act',True),('kernel_mutation',True),
    ('cognitive_runtime_receipt.decision_ticket_dry_run.decision','HOLD'),
    ('cognitive_runtime_receipt.decision_ticket_dry_run.decision','BLOCK'),
    ('cognitive_runtime_receipt.decision_authority','OTHER'),
    ('cognitive_runtime_receipt.critical_action_requested',True),
    ('cognitive_runtime_receipt.cognition_shadow_memory.boundary.memory_write',True),
    ('cognitive_runtime_receipt.cognition_shadow_memory.context_packet.boundary.allowed_to_act',True),
])
def test_governance_refusals(path,value):
    body=envelope(); obj,key=at(body,path); obj[key]=value
    result=consume(body)
    assert result['consumer_status']=='REFUSED' and result['original_receipt'] is None

def test_action_block_and_documentary_quotes_do_not_authorize_or_refuse_context():
    body=envelope(); body['action_gateway_sandbox_verdict']='BLOCK'
    body['cognitive_runtime_receipt']['cognition_shadow_memory']['memory_entries'][0]['payload']['excerpt']='HOLD BLOCK decision_authority OTHER'
    assert consume(body)['consumer_status']=='CONTEXT_AVAILABLE'

@pytest.mark.parametrize('status,complete', [('MEMORY_REQUIRED_EMPTY','COMPLETE'),
    ('MEMORY_REQUIRED_NO_NATIVE_SOURCE','COMPLETE'),('MEMORY_REQUIRED_INVALID_NATIVE_SOURCE','COMPLETE'),
    ('MEMORY_REQUIRED_EMPTY_QUERY','COMPLETE'),('MEMORY_USABLE','DEGRADED')])
def test_empty_and_degraded_remain_limited(status,complete):
    assert consume(envelope(status,complete))['consumer_status']=='CONTEXT_LIMITED'

@pytest.mark.parametrize('raw',[b'{',b'[]',b'{"a":1,"a":2}',b'{"a":{"b":1,"b":2}}',
    b'{"a":NaN}',b'{"a":Infinity}',b'{"a":1e999}',b'\xff'])
def test_strict_json(raw):
    with pytest.raises(contract().ContractError): contract().parse_envelope(raw)

def test_json_roundtrip():
    assert contract().parse_envelope(json.dumps(envelope()).encode())==envelope()

@pytest.fixture
def runtime(monkeypatch,tmp_path):
    import studio_ai
    journal=importlib.import_module('studio_experiment_journal')
    monkeypatch.setenv('OBSIDIA_STUDIO_ENABLE_E11_LOT1','1')
    monkeypatch.setenv('OBSIDIA_STUDIO_API_KEY','DUMMY_PRIVATE_KEY')
    monkeypatch.setenv('OBSIDIA_STUDIO_BRODY_URL','http://127.0.0.1:8000')
    monkeypatch.setattr(journal,'JOURNAL_PATH',tmp_path/'events.jsonl')
    monkeypatch.setattr(studio_ai,'verify_e11_service',lambda base:{'status':'TECHNICAL_SNAPSHOT_VERIFIED',
        'checkpoint':CHECKPOINT,'evidence_id':str(uuid.uuid4())})
    calls=[]
    class Reply:
        status=200
        def __enter__(self): return self
        def __exit__(self,*a): return False
        def getcode(self): return self.status
        def read(self,n): return json.dumps(envelope()).encode()[:n]
    opener=Mock()
    def open_(req,timeout): calls.append((req,timeout)); return Reply()
    opener.open.side_effect=open_
    factory=Mock(return_value=opener)
    monkeypatch.setattr(studio_ai.urllib.request,'build_opener',factory)
    return studio_ai,journal,calls,opener,factory

def test_enabled_transport_one_call_auth_and_private_journal(runtime):
    s,j,calls,opener,factory=runtime
    result=s.run_e11_experiment('PRIVATE_QUESTION')
    assert result['consumer_status']=='CONTEXT_AVAILABLE'
    assert len(calls)==1 and calls[0][1]==30
    req=calls[0][0]; body=json.loads(req.data)
    assert req.get_header('X-api-key')=='DUMMY_PRIVATE_KEY'
    assert body['message']=='PRIVATE_QUESTION'
    assert all(body[k] is False for k in ('allow_provider','allow_local_model','allow_memory_candidate','allow_manual_apply','compact','debug','debug_full'))
    log=j.JOURNAL_PATH.read_text()
    for forbidden in ('PRIVATE_', 'DUMMY_PRIVATE_KEY','original_receipt','payload','X-API-Key'):
        assert forbidden not in log
    event=json.loads(log)
    assert event['status']=='CONTEXT_AVAILABLE' and event['checkpoint_configured']==CHECKPOINT

def test_disabled_and_rollback_no_http_no_journal(runtime,monkeypatch):
    s,j,calls,*_=runtime
    monkeypatch.delenv('OBSIDIA_STUDIO_ENABLE_E11_LOT1',raising=False)
    assert s.run_e11_experiment('Sujet')['error_code']=='DISABLED'
    assert not calls and not j.JOURNAL_PATH.exists()
    monkeypatch.setenv('OBSIDIA_STUDIO_ENABLE_E11_LOT1','0')
    assert s.run_e11_experiment('Sujet')['error_code']=='DISABLED'
    assert not calls and not j.JOURNAL_PATH.exists()

@pytest.mark.parametrize('value',['','   ','x'*4097,42])
def test_input_rejected_before_network(runtime,value):
    s,j,calls,*_=runtime
    assert s.run_e11_experiment(value)['consumer_status']=='REFUSED'
    assert not calls

def test_key_missing_no_anonymous_attempt(runtime,monkeypatch):
    s,j,calls,*_=runtime; monkeypatch.delenv('OBSIDIA_STUDIO_API_KEY',raising=False)
    assert s.run_e11_experiment('Sujet')['error_code']=='AUTH_REQUIRED'
    assert not calls

def test_unverified_service_holds_activation(runtime,monkeypatch):
    s,j,calls,*_=runtime
    monkeypatch.setattr(s,'verify_e11_service',lambda base:None)
    assert s.run_e11_experiment('Sujet')['error_code']=='HOLD_ACTIVATION'
    assert not calls

@pytest.mark.parametrize('url',['http://example.org','https://localhost:8000','http://user:pass@localhost:8000',
    'http://localhost:8000/path','http://127.0.0.1:8000/?private=1'])
def test_loopback_only_new_transport(runtime,monkeypatch,url):
    s,j,calls,*_=runtime; monkeypatch.setenv('OBSIDIA_STUDIO_BRODY_URL',url)
    assert s.run_e11_experiment('Sujet')['consumer_status']=='REFUSED'
    assert not calls

@pytest.mark.parametrize('kind',['timeout','401','503','redirect','oversize','malformed'])
def test_transport_failures_no_retry_or_fallback(runtime,monkeypatch,kind):
    import urllib.error
    s,j,calls,opener,_=runtime
    fallback=Mock(side_effect=AssertionError('no fallback'))
    monkeypatch.setattr(s,'generate',fallback)
    if kind=='timeout': opener.open.side_effect=TimeoutError('PRIVATE_EXCEPTION')
    elif kind in ('401','503','redirect'):
        opener.open.side_effect=urllib.error.HTTPError('PRIVATE_URL',302 if kind=='redirect' else int(kind),'PRIVATE_ERROR',{},None)
    else:
        reply=Mock(); reply.__enter__=Mock(return_value=reply); reply.__exit__=Mock(return_value=False)
        reply.getcode.return_value=200
        reply.read.return_value=b'x'*5_000_001 if kind=='oversize' else b'{'
        opener.open.side_effect=None; opener.open.return_value=reply
    result=s.run_e11_experiment('Sujet')
    assert result['consumer_status'] in ('REFUSED','UNAVAILABLE')
    assert result['e11_context'] is None
    assert opener.open.call_count==1
    fallback.assert_not_called()
    assert 'PRIVATE_' not in j.JOURNAL_PATH.read_text()

def test_journal_failure_withholds_context(runtime,monkeypatch):
    s,j,*_=runtime
    monkeypatch.setattr(j,'record_experiment',Mock(side_effect=OSError('PRIVATE_PATH')))
    result=s.run_e11_experiment('Sujet')
    assert result['consumer_status']=='REFUSED' and result['error_code']=='JOURNAL_UNAVAILABLE'
    assert result['e11_context'] is None and result['original_receipt'] is None


@pytest.mark.parametrize('status,code',[(401,'AUTH_REJECTED'),(403,'AUTH_REJECTED'),
                                      (503,'SERVICE_UNAVAILABLE')])
def test_http_error_classification_without_reading_sensitive_body(runtime,status,code):
    import io
    import urllib.error
    s,j,calls,opener,_=runtime
    body=io.BytesIO(b'PRIVATE_SERVER_DETAILS')
    opener.open.side_effect=urllib.error.HTTPError('PRIVATE_URL',status,'PRIVATE_ERROR',{},body)
    result=s.run_e11_experiment('PRIVATE_QUESTION')
    assert result['error_code']==code and result['consumer_status']=='UNAVAILABLE'
    assert result['e11_context'] is None and result['original_receipt'] is None
    assert opener.open.call_count==1 and body.closed
    assert 'PRIVATE_' not in j.JOURNAL_PATH.read_text()


def test_connection_refused_no_retry_or_fallback(runtime,monkeypatch):
    import urllib.error
    s,j,calls,opener,_=runtime
    fallback=Mock(side_effect=AssertionError('no fallback'))
    monkeypatch.setattr(s,'generate',fallback)
    opener.open.side_effect=urllib.error.URLError(ConnectionRefusedError('PRIVATE_ADDRESS'))
    result=s.run_e11_experiment('PRIVATE_QUESTION')
    assert result['error_code']=='SERVICE_UNAVAILABLE'
    assert result['e11_context'] is None and opener.open.call_count==1
    fallback.assert_not_called()
    assert 'PRIVATE_' not in j.JOURNAL_PATH.read_text()

def test_redirect_handler_never_follows(runtime):
    s,*_=runtime
    handler=s.E11NoRedirect()
    assert handler.redirect_request(None,None,302,'private',{},'http://example.org') is None


def required_paths():
    body=envelope()
    paths=[]
    objects=['','cognitive_runtime_receipt','cognitive_runtime_receipt.cognition_shadow_memory',
             'cognitive_runtime_receipt.cognition_shadow_memory.memory_snapshot_ref',
             'cognitive_runtime_receipt.cognition_shadow_memory.boundary',
             'cognitive_runtime_receipt.cognition_shadow_memory.context_packet',
             'cognitive_runtime_receipt.cognition_shadow_memory.context_packet.boundary',
             'cognitive_runtime_receipt.decision_ticket_dry_run']
    for prefix in objects:
        obj=body
        for part in prefix.split('.') if prefix else []: obj=obj[part]
        for key in obj:
            if key in ('source',): continue
            paths.append((prefix+'.' if prefix else '')+key)
    return paths

@pytest.mark.parametrize('path',required_paths())
def test_every_required_field_null_rejected(path):
    body=envelope(); obj,key=at(body,path); obj[key]=None
    assert consume(body)['consumer_status']=='REFUSED'

def test_explicit_hold_block_classification():
    for decision,code in [('HOLD','UPSTREAM_HOLD'),('BLOCK','UPSTREAM_BLOCK')]:
        body=envelope(); body['cognitive_runtime_receipt']['decision_ticket_dry_run']['decision']=decision
        assert consume(body)['error_code']==code

def test_contradictory_memory_count_rejected():
    body=envelope('MEMORY_NOT_REQUIRED')
    body['cognitive_runtime_receipt']['cognition_shadow_memory']['memory_entries']=envelope()['cognitive_runtime_receipt']['cognition_shadow_memory']['memory_entries']
    assert consume(body)['consumer_status']=='REFUSED'

def test_journal_does_not_merge_attacker_metadata(runtime):
    s,j,*_=runtime
    result=consume(envelope())
    result['experiment_id']=str(uuid.uuid4())
    result['question']='PRIVATE_QUESTION'; result['exception']='PRIVATE_ERROR'
    result['provenance']={'service_verification':{'status':'PRIVATE_FAKE','checkpoint':'PRIVATE_PATH'}}
    j.record_experiment(result,elapsed_ms=1,response_bytes=2)
    assert 'PRIVATE_' not in j.JOURNAL_PATH.read_text()

def test_journal_rejects_outside_studio(runtime,monkeypatch):
    s,j,*_=runtime
    monkeypatch.setattr(j,'JOURNAL_PATH',Path(__file__).resolve().parent.parent/'should-never-be-written.jsonl')
    result=consume(envelope())
    with pytest.raises(ValueError): j.record_experiment(result,elapsed_ms=1,response_bytes=1)

@pytest.mark.parametrize('mode', ['missing','wrong_sha','initial_sha','previous_sha',
    'wrong_url','tampered_manifest','tampered_source','outside','valid','expired_legacy','new_pid'])
def test_technical_checkpoint_guard(monkeypatch,tmp_path,mode):
    import hashlib
    import studio_ai
    import studio_e11_deployment as deployment
    monkeypatch.setattr(deployment,'ROOT',tmp_path)
    monkeypatch.setattr(deployment,'DEPLOYMENT',tmp_path/'deployment')
    folder=deployment.DEPLOYMENT
    source=folder/'producer_cbad0125/source'
    source.mkdir(parents=True)
    (source/'module.py').write_bytes(b'# fixed source')
    manifest={'source_commit':CHECKPOINT,'files':[{'path':'module.py',
        'sha256':hashlib.sha256(b'# fixed source').hexdigest()}]}
    if mode=='wrong_sha': manifest['source_commit']='0'*40
    elif mode=='initial_sha': manifest['source_commit']=BASELINE_CHECKPOINT
    elif mode=='previous_sha': manifest['source_commit']=PREVIOUS_CHECKPOINT
    elif mode=='outside': manifest['files'][0]['path']='../../outside.py'
    raw=json.dumps(manifest).encode()
    monkeypatch.setattr(deployment,'MANIFEST_SHA256',hashlib.sha256(raw).hexdigest())
    (folder/'EXPORT_MANIFEST.json').write_bytes(raw)
    if mode=='missing': (folder/'EXPORT_MANIFEST.json').unlink()
    elif mode=='tampered_manifest': (folder/'EXPORT_MANIFEST.json').write_bytes(b'{}')
    elif mode=='tampered_source': (source/'module.py').write_bytes(b'# changed')
    # Old human evidence is deliberately irrelevant, including expiry and PID.
    if mode in ('expired_legacy','new_pid'):
        (tmp_path/'service_verification.json').write_text(json.dumps({
            'expires_at':'2000-01-01T00:00:00Z','status':'PENDING_HUMAN_REVIEW','pid':99999}))
    base='http://localhost:9000' if mode=='wrong_url' else deployment.BASE_URL
    observed=studio_ai.verify_e11_service(base)
    assert (observed is not None)==(mode in ('valid','expired_legacy','new_pid'))
    if observed:
        assert observed['status']=='TECHNICAL_SNAPSHOT_VERIFIED'
        assert 'expires_at' not in observed and 'pid' not in observed


def test_checkpoint_alignment_keeps_historical_identity():
    assert contract().BASELINE_CHECKPOINT == BASELINE_CHECKPOINT
    assert contract().PREVIOUS_CHECKPOINT == PREVIOUS_CHECKPOINT
    assert contract().CHECKPOINT == CHECKPOINT


def test_alignment_preserves_m41_as_unvalidated_receipt_data():
    body=envelope()
    original_e11=copy.deepcopy(body['cognitive_runtime_receipt']['cognition_shadow_memory'])
    snapshot={'status':'HYPOTHESIS_SET_ATTACHED','set_id':'synthetic-set',
              'members':[{'unknowns':['synthetic-a']},{'unknowns':['synthetic-b']}],
              'readonly':True,'decision_authority':'KX108_ONLY'}
    body['cognitive_runtime_receipt']['world_hypothesis_snapshot']=snapshot
    result=consume(body)
    assert result['consumer_status']=='CONTEXT_AVAILABLE'
    assert result['original_receipt']==body['cognitive_runtime_receipt']
    assert result['e11_context']==original_e11
    result['original_receipt']['world_hypothesis_snapshot']['members'].clear()
    assert len(snapshot['members'])==2


def test_alignment_provenance_and_journal_keep_both_checkpoints(runtime):
    s,j,calls,*_=runtime
    result=s.run_e11_experiment('PRIVATE_QUESTION')
    assert result['consumer_status']=='CONTEXT_AVAILABLE'
    assert result['provenance']['baseline_checkpoint']==BASELINE_CHECKPOINT
    assert result['provenance']['previous_configured_checkpoint']==PREVIOUS_CHECKPOINT
    assert result['provenance']['configured_checkpoint']==CHECKPOINT
    event=json.loads(j.JOURNAL_PATH.read_text())
    assert event['checkpoint_initial']==BASELINE_CHECKPOINT
    assert event['checkpoint_previous']==PREVIOUS_CHECKPOINT
    assert event['checkpoint_configured']==CHECKPOINT
    assert event['checkpoint_verified']==CHECKPOINT
    assert len(calls)==1


@pytest.mark.parametrize('decision,code',[('HOLD','UPSTREAM_HOLD'),('BLOCK','UPSTREAM_BLOCK')])
def test_m41_does_not_override_context_refusal(decision,code):
    body=envelope()
    body['cognitive_runtime_receipt']['world_hypothesis_snapshot']={'status':'HYPOTHESIS_SET_ATTACHED'}
    body['cognitive_runtime_receipt']['decision_ticket_dry_run']['decision']=decision
    result=consume(body)
    assert result['error_code']==code
    assert result['original_receipt'] is None and result['e11_context'] is None


def endpoint_app():
    """Compile the exact added server declarations, without seed/scheduler/autopilot side effects."""
    import ast
    import studio_ai
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    tree=ast.parse((Path(__file__).parent/'server.py').read_text(encoding='utf-8'))
    nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef))
           and n.name in ('E11ExperimentInput','experiment_e11_context')]
    assert len(nodes)==2
    namespace=dict(app=FastAPI(),os=os,studio_ai=studio_ai,HTTPException=HTTPException,
                   Request=Request,JSONResponse=JSONResponse,BaseModel=BaseModel)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'server.py','exec'),namespace)
    return namespace['app']

def http_request(app,*,body=None,origin=None,peer='127.0.0.1',raw=None):
    import asyncio
    import httpx
    async def request():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,client=(peer,123)),base_url='http://localhost') as client:
            headers={'Origin':origin} if origin is not None else {}
            if raw is not None:
                return await client.post('/api/experiments/e11/context',content=raw,headers=headers)
            return await client.post('/api/experiments/e11/context',json=body or {'text':'PRIVATE_QUESTION'},headers=headers)
    return asyncio.run(request())

def test_endpoint_enabled_simulated_http_no_publication(runtime):
    s,j,calls,*_=runtime
    response=http_request(endpoint_app())
    assert response.status_code==200
    assert response.headers['cache-control']=='no-store'
    assert response.json()['publication_permitted'] is False
    assert len(calls)==1

@pytest.mark.parametrize('mode',['disabled','foreign_origin','remote_peer','extra_field','wrong_type'])
def test_endpoint_rejects_without_http(runtime,monkeypatch,mode):
    s,j,calls,*_=runtime; args={}
    if mode=='disabled': monkeypatch.setenv('OBSIDIA_STUDIO_ENABLE_E11_LOT1','0')
    elif mode=='foreign_origin': args['origin']='https://example.org'
    elif mode=='remote_peer': args['peer']='192.0.2.1'
    elif mode=='extra_field': args['body']={'text':'Sujet','allow_provider':True}
    elif mode=='wrong_type': args['body']={'text':123}
    response=http_request(endpoint_app(),**args)
    assert response.status_code in (403,404,422)
    assert not calls and not j.JOURNAL_PATH.exists()

def test_deadline_closes_detached_response_socket():
    import studio_ai
    deadline=studio_ai.E11Deadline()
    sock=Mock()
    deadline.sockets.append(sock)
    deadline.expire()
    assert deadline.expired.is_set()
    sock.shutdown.assert_called_once()

def test_truncated_http_response_is_bounded_failure(runtime):
    import http.client
    s,j,calls,opener,*_=runtime
    opener.open.side_effect=http.client.IncompleteRead(b'PRIVATE_MEMORY',123)
    result=s.run_e11_experiment('Sujet')
    assert result['consumer_status']=='UNAVAILABLE'
    assert result['original_receipt'] is None
    assert opener.open.call_count==1
    assert 'PRIVATE_' not in j.JOURNAL_PATH.read_text()

def test_wrapped_network_timeout_keeps_bounded_error(runtime):
    import urllib.error
    s,j,calls,opener,*_=runtime
    opener.open.side_effect=urllib.error.URLError(TimeoutError('PRIVATE_ERROR'))
    result=s.run_e11_experiment('Sujet')
    assert result['error_code']=='TIMEOUT'
    assert opener.open.call_count==1 and 'PRIVATE_' not in j.JOURNAL_PATH.read_text()

def test_huge_integer_decoder_failure_is_contract_error():
    with pytest.raises(contract().ContractError):
        contract().parse_envelope(b'{"number":'+b'1'*5000+b'}')

def test_expired_deadline_never_delivers_context(runtime,monkeypatch):
    s,j,calls,opener,*_=runtime
    original=s.E11Deadline
    def expired():
        deadline=original(); deadline.expire(); return deadline
    monkeypatch.setattr(s,'E11Deadline',expired)
    result=s.run_e11_experiment('Sujet')
    assert result['error_code']=='TIMEOUT' and result['e11_context'] is None

def test_no_producer_imports_in_new_modules():
    import ast
    for name in ('studio_e11_contract.py','studio_experiment_journal.py',
                 'studio_e11_diagnostic_client.py','studio_e11_receipt_diagnostics.py'):
        tree=ast.parse((Path(__file__).parent/name).read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                assert all(not a.name.startswith(('app.','apps.','periphery.','runtime_wiring')) for a in node.names)
            elif isinstance(node,ast.ImportFrom):
                assert not (node.module or '').startswith(('app.','apps.','periphery.','runtime_wiring'))

@pytest.mark.parametrize('raw',[b'{"text":"one","text":"two"}',b'{',b'{"text":NaN}',b'x'*65_537],
                         ids=['duplicate','malformed','nonfinite','oversize'])
def test_endpoint_raw_json_strict_without_http(runtime,raw):
    s,j,calls,*_=runtime
    response=http_request(endpoint_app(),raw=raw)
    assert response.status_code in (400,413)
    assert not calls and not j.JOURNAL_PATH.exists()


@pytest.mark.parametrize('memory',sorted(contract().MEMORY_STATUSES))
def test_10h_memory_statuses_share_consumer_client_and_journal(runtime,memory):
    from studio_e11_diagnostic_client import summarize_result
    s,j,*_=runtime
    body=envelope(memory)
    original=copy.deepcopy(body)
    result=consume(body)
    expected='CONTEXT_AVAILABLE' if memory in {'MEMORY_USABLE','MEMORY_NOT_REQUIRED'} else 'CONTEXT_LIMITED'
    assert result['consumer_status']==expected
    assert result['memory_retrieval_status']==memory
    assert result['e11_contract_status']=='VALID'
    assert result['b6_context_status']=='VALID'
    assert result['governance_status']=='CONTEXT_ALLOWED'
    assert result['receipt_availability']=='VALIDATED'
    assert result['context_limit_reasons']==([] if expected=='CONTEXT_AVAILABLE' else [memory])
    assert result['original_receipt']==original['cognitive_runtime_receipt'] and body==original
    summary=summarize_result(result)
    assert summary['documentary_status']==memory
    j.record_experiment(result,elapsed_ms=1,response_bytes=2)
    event=json.loads(j.JOURNAL_PATH.read_text())
    for key in contract().diagnostic_summary(result):
        assert event[key]==summary[key]==result[key]


@pytest.mark.parametrize('kind,reason',[
    ('degraded','RECEIPT_DEGRADED'),('surface','RECEIPT_SURFACES_UNAVAILABLE'),
    ('unknowns','B6_UNKNOWNS'),('omitted','B6_OMISSIONS'),('projection_omitted','B6_OMISSIONS'),
    ('state_error','B6_STATE_ERROR'),('state_open','B6_UNKNOWNS'),('reduced','B6_REDUCED_VISIBILITY')])
def test_10h_memory_not_required_never_erases_other_limits(kind,reason):
    body=envelope('MEMORY_NOT_REQUIRED')
    receipt=body['cognitive_runtime_receipt']
    packet=receipt['cognition_shadow_memory']['context_packet']
    if kind=='degraded': receipt['completeness']='DEGRADED'
    elif kind=='surface': receipt['components']['NPL']='SKIPPED_NOT_AVAILABLE:NPL_RUNTIME_NOT_MATERIALIZED'
    elif kind=='unknowns': packet['unknowns']=[{'state_id':'synthetic','status':'OPEN','uncertainty':['PRIVATE_UNKNOWN']}]
    elif kind=='omitted': packet['omitted']=[{'state_id':'synthetic','reason':'PRIVATE_OMISSION'}]
    elif kind=='projection_omitted': packet['projection']['omitted']=[{'state_id':'synthetic','reason':'ENTRY_LIMIT'}]
    elif kind=='reduced': packet['projection']['included']=[{'state_id':'synthetic','reason':'PACKET_SIZE_LIMIT:reduced_to_SHORT'}]
    else: packet['state'][0]['status']='ERROR' if kind=='state_error' else 'OPEN'
    result=consume(body)
    assert result['consumer_status']=='CONTEXT_LIMITED'
    assert result['memory_retrieval_status']=='MEMORY_NOT_REQUIRED'
    assert result['context_limit_reasons']==[reason]
    assert result['b6_context_status']==('LIMITED' if reason.startswith('B6_') else 'VALID')


def test_10h_accumulates_independent_reasons_without_modifying_receipt():
    body=envelope('MEMORY_NOT_REQUIRED','DEGRADED'); receipt=body['cognitive_runtime_receipt']
    receipt['components']['NPL']='UNAVAILABLE'
    packet=receipt['cognition_shadow_memory']['context_packet']
    packet['unknowns']=[{'status':'OPEN'}];packet['omitted']=[{'reason':'ENTRY_LIMIT'}]
    before=copy.deepcopy(body)
    result=consume(body)
    assert set(result['context_limit_reasons'])=={'RECEIPT_DEGRADED','RECEIPT_SURFACES_UNAVAILABLE','B6_UNKNOWNS','B6_OMISSIONS'}
    assert result['original_receipt']==before['cognitive_runtime_receipt'] and body==before


def test_10h_e11_requests_stay_limited_without_claiming_b7_validation():
    body=envelope('MEMORY_NOT_REQUIRED')
    body['cognitive_runtime_receipt']['cognition_shadow_memory']['resolution_requests']=[
        {'unresolved_kind':'COREFERENCE','why_resolution_needed':'PRIVATE_UNRESOLVED'}]
    result=consume(body)
    assert result['consumer_status']=='CONTEXT_LIMITED'
    assert result['context_limit_reasons']==['E11_UNRESOLVED_REQUESTS']
    assert result['e11_contract_status']=='VALID' and result['b6_context_status']=='VALID'
    assert 'b7_validated' not in result and 'm41_validated' not in result


@pytest.mark.parametrize('field',['decision_authority','memory_write'])
def test_10h_memory_not_required_cannot_clear_contradictory_authority(field):
    body=envelope('MEMORY_NOT_REQUIRED')
    body[field]='OTHER' if field=='decision_authority' else True
    result=consume(body)
    assert result['consumer_status']=='REFUSED'
    assert result['governance_status']=='REFUSED'
    assert result['context_limit_reasons']==['GOVERNANCE_REFUSED']


@pytest.mark.parametrize('memory',['MEMORY_REQUIRED_FUTURE','PRIVATE_STATUS','UNKNOWN','MEMORY_EMPTY'])
def test_10h_unknown_memory_never_becomes_success_or_leaks(runtime,memory):
    from studio_e11_diagnostic_client import summarize_result
    s,j,*_=runtime
    result=consume(envelope(memory))
    assert result['consumer_status']=='REFUSED' and result['error_code']=='SCHEMA_MISMATCH'
    assert result['memory_retrieval_status']=='UNKNOWN'
    assert result['e11_contract_status']=='INVALID'
    assert result['receipt_availability']=='PRESENT_UNVALIDATED'
    assert result['original_receipt'] is None and result['e11_context'] is None
    assert 'MEMORY_STATUS_UNKNOWN' in result['context_limit_reasons']
    j.record_experiment(result,elapsed_ms=1,response_bytes=2)
    assert 'PRIVATE_' not in j.JOURNAL_PATH.read_text()
    assert summarize_result(result)['documentary_status'] is None


@pytest.mark.parametrize('decision',['HOLD','BLOCK'])
def test_10h_refusal_diagnostics_do_not_expose_receipt(decision):
    body=envelope('MEMORY_NOT_REQUIRED')
    body['cognitive_runtime_receipt']['decision_ticket_dry_run']['decision']=decision
    result=consume(body)
    assert result['consumer_status']=='REFUSED'
    assert result['governance_status']==decision
    assert result['context_limit_reasons']==['GOVERNANCE_'+decision]
    assert result['receipt_availability']=='PRESENT_UNVALIDATED'
    assert result['original_receipt'] is None


@pytest.mark.parametrize('path,status_field,reason',[
    ('cognitive_runtime_receipt.cognition_shadow_memory.schema','e11_contract_status','E11_INVALID'),
    ('cognitive_runtime_receipt.cognition_shadow_memory.context_packet.schema','b6_context_status','B6_INVALID')])
def test_10h_contract_failure_stays_refused(path,status_field,reason):
    body=envelope('MEMORY_NOT_REQUIRED'); obj,key=at(body,path);obj[key]='UNKNOWN_SCHEMA'
    result=consume(body)
    assert result['consumer_status']=='REFUSED' and result[status_field]=='INVALID'
    assert reason in result['context_limit_reasons'] and result['original_receipt'] is None


def test_10h_memory_required_error_state_is_preserved():
    body=envelope('MEMORY_REQUIRED_INVALID_NATIVE_SOURCE')
    shadow=body['cognitive_runtime_receipt']['cognition_shadow_memory']
    entry=copy.deepcopy(envelope()['cognitive_runtime_receipt']['cognition_shadow_memory']['memory_entries'][0])
    entry.update(state_type='NATIVE_MEMORY_STATUS',status='UNKNOWN',payload={'status':'MEMORY_REQUIRED_INVALID_NATIVE_SOURCE'})
    shadow['memory_entries']=[entry]
    result=consume(body)
    assert result['consumer_status']=='CONTEXT_LIMITED'
    assert set(result['context_limit_reasons'])=={'MEMORY_REQUIRED_INVALID_NATIVE_SOURCE','B6_UNKNOWNS'}
    assert result['e11_context']['memory_entries']==[entry]


def test_10h_diagnostic_allowlist_resists_private_and_malformed_values(runtime):
    from studio_e11_diagnostic_client import summarize_result
    s,j,*_=runtime
    result=consume(envelope())
    for key in contract().DIAGNOSTIC_ENUMS: result[key]='PRIVATE_SECRET'
    result['context_limit_reasons']=['PRIVATE_QUESTION',{'excerpt':'PRIVATE_MEMORY'},'B6_UNKNOWNS','B6_UNKNOWNS']
    j.record_experiment(result,elapsed_ms=1,response_bytes=2)
    summary=summarize_result(result)
    assert summary['context_limit_reasons']==['B6_UNKNOWNS']
    assert 'PRIVATE_' not in json.dumps(summary) and 'PRIVATE_' not in j.JOURNAL_PATH.read_text()
    assert set(json.loads(j.JOURNAL_PATH.read_text()))==j.JOURNAL_FIELDS
    assert summarize_result({'documentary_status':['PRIVATE_MEMORY']})['documentary_status'] is None


def test_10h_unavailable_transport_has_no_invented_cognitive_diagnostics(runtime):
    s,j,calls,opener,*_=runtime
    opener.open.side_effect=TimeoutError('PRIVATE_ERROR')
    result=s.run_e11_experiment('PRIVATE_QUESTION')
    assert opener.open.call_count==1
    assert result['consumer_status']=='UNAVAILABLE'
    assert result['memory_retrieval_status']=='NOT_OBSERVED'
    assert result['receipt_availability']=='NOT_OBSERVED'
    assert result['e11_contract_status']==result['b6_context_status']==result['governance_status']=='NOT_CHECKED'


def test_10h_diagnostic_script_timeout_still_writes_safe_report(monkeypatch,tmp_path):
    import runpy
    import sys
    import urllib.request
    source=Path(__file__).parent/'data/experiments/e11_lot1/passe10e7/single_trial.py'
    target=tmp_path/'isolated_studio/data/experiments/e11_lot1/passe10e7/single_trial.py'
    target.parent.mkdir(parents=True)
    target.write_bytes(source.read_bytes())
    opener=Mock();opener.open.side_effect=TimeoutError('PRIVATE_EXCEPTION')
    monkeypatch.setattr(urllib.request,'build_opener',Mock(return_value=opener))
    monkeypatch.setattr(sys,'path',list(sys.path))
    runpy.run_path(str(target),run_name='__main__')
    result=json.loads(target.with_name('trial_result.json').read_text())
    assert opener.open.call_count==1
    assert result['transport_or_parse_error'] is True and result['http_status'] is None
    assert result['journal_events_added']==0 and 'PRIVATE_' not in json.dumps(result)
    assert target.with_name('POST_ATTEMPTED').exists()
