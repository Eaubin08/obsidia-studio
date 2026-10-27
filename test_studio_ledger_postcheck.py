"""Offline post-control replay, using the preserved real Oracle trace."""
from pathlib import Path, PureWindowsPath
import copy,hashlib,importlib.util,json,sys
import pytest

S=Path(__file__).parent
A=S/'data/experiments/ledger_postcheck_20261026'
T=S/'data/experiments/internal_observation_real_trial_20261026'
R=S/'data/experiments/e11_lot1/passe10e2/producer_cbad0125/source'
spec=importlib.util.spec_from_file_location('_studio_ledger_postcheck',A/'ledger_postcheck.py')
post=importlib.util.module_from_spec(spec);spec.loader.exec_module(post)


@pytest.fixture
def bundle():
    expected=json.loads((A/'EXPECTED_TRACE.json').read_text())
    record=Path(expected['record_path']);session=record.parent.parent
    return {'record':record.read_bytes(),'index':(session/'SESSION_INDEX.json').read_bytes(),
            'ledger':(session/'SESSION_LEDGER.jsonl').read_bytes(),
            'source':(R/'periphery/brody_memory_readonly/session_memory_ledger_readonly/brody_session_memory_ledger_readonly_v2.py').read_bytes(),
            'e2e':(T/'result.json').read_bytes(),'expected':expected}


def validate(b):
    return post.validate_trace(b['record'],b['index'],b['ledger'],b['source'],b['e2e'],expected=b['expected'])


def encoded(value):return json.dumps(value,ensure_ascii=False,indent=2).encode()


def repack_record(b,record):
    """Self-consistent mutants remain synthetic test inputs, never stored traces.

    Re-pin only in the fixture to exercise semantic gates independently of SHA
    rejection. The real offline runner never re-pins EXPECTED_TRACE.json.
    """
    record=copy.deepcopy(record)
    base=dict(record);base.pop('event_hash',None)
    event=post.sha((record['previous_event_hash']+json.dumps(base,sort_keys=True,ensure_ascii=False,separators=(',',':'))).encode())
    record['event_hash']=event
    index=json.loads(b['index']);lines=[json.loads(line) for line in b['ledger'].splitlines() if line.strip()]
    old_seq=b['expected']['sequence']
    for line_number,line in enumerate(lines):
        if line['sequence']==old_seq:lines[line_number]=copy.deepcopy(record)
    for entry in index['records']:
        if entry['sequence']==old_seq:
            entry['event_hash']=event
            if 'user_input_sha256' in record:entry['user_input_sha256']=record['user_input_sha256']
            if 'response_md_sha256' in record:entry['response_md_sha256']=record['response_md_sha256']
    index['latest_event_hash']=event
    b['record']=encoded(record);b['index']=encoded(index)
    b['ledger']=b'\n'.join(json.dumps(x,ensure_ascii=False).encode() for x in lines)+b'\n'
    b['expected'].update(record_sha256=post.sha(b['record']),index_sha256=post.sha(b['index']),
                          ledger_sha256=post.sha(b['ledger']),event_hash=event)


def test_real_canonical_ledger_passes_without_invented_memory_write(bundle):
    before=copy.deepcopy(bundle);record=json.loads(bundle['record'])
    assert 'memory_write' not in record
    out=validate(bundle)
    assert out['status']=='PASS' and out['schema_memory_write_field']=='NOT_DEFINED_NOT_DEFAULTED'
    assert out['memory_status']=='MEMORY_WRITE_HOLD' and out['memory_promotion_admitted'] is False
    assert bundle==before


def test_explicit_historical_false_does_not_replace_canonical_fields(bundle):
    record=json.loads(bundle['record']);record['memory_write']=False;repack_record(bundle,record)
    assert validate(bundle)['status']=='PASS'


@pytest.mark.parametrize('field',['memory_intake','graphiti_index_write','auto_triage','memory_decision','allowed_to_decide',
    'emits_act','kernel_mutation','x108_mutation','memory_write','canonical_write','memory_promotion','knowledge_promotion','auto_promote_candidate'])
def test_promotion_or_mutation_true_holds_even_when_hashes_are_consistent(bundle,field):
    record=json.loads(bundle['record']);record[field]=True;repack_record(bundle,record)
    assert validate(bundle)['status']=='HOLD'


@pytest.mark.parametrize('field',['memory_intake','graphiti_index_write','auto_triage','readonly','response_only','memory_decision','decision_authority'])
def test_required_indicator_absent_holds_even_when_hashes_are_consistent(bundle,field):
    record=json.loads(bundle['record']);record.pop(field);repack_record(bundle,record)
    out=validate(bundle)
    assert out['status']=='HOLD' and out['reason']=='CANONICAL_BOUNDARY_FIELD_MISSING'


@pytest.mark.parametrize('value',[None,0,1,'false','False'])
def test_no_boolean_coercion_for_required_or_historical_indicator(bundle,value):
    record=json.loads(bundle['record']);record['memory_write']=value;repack_record(bundle,record)
    assert validate(bundle)['status']=='HOLD'


@pytest.mark.parametrize('field,value',[('readonly',1),('decision_authority','QWEN'),('memory_intake_status','PROMOTED'),
    ('triage_status','APPLIED'),('session_id','other-session'),('sequence',999),('response_md_sha256','0'*64),
    ('user_input','Other request'),('status','UNRECOGNIZED_LEDGER')])
def test_incomplete_conflicting_or_mismatched_record_holds(bundle,field,value):
    record=json.loads(bundle['record']);record[field]=value;repack_record(bundle,record)
    assert validate(bundle)['status']=='HOLD'


@pytest.mark.parametrize('part',['record','index','ledger','source','e2e'])
def test_raw_evidence_tampering_or_absence_holds(bundle,part):
    bundle[part]+=b' '
    assert validate(bundle)['status']=='HOLD'
    bundle[part]=b''
    assert validate(bundle)['status']=='HOLD'


@pytest.mark.parametrize('kind',['session','path','event','count','required_indicator','duplicate'])
def test_index_provenance_must_match_record(bundle,kind):
    index=json.loads(bundle['index']);entry=index['records'][-1]
    if kind=='session':index['session_id']='other'
    elif kind=='path':entry['record_json']='C:\\unrelated\\record.json'
    elif kind=='event':entry['event_hash']='0'*64
    elif kind=='count':index['record_count']+=1
    elif kind=='required_indicator':index.pop('memory_intake')
    elif kind=='duplicate':index['records'].append(copy.deepcopy(entry));index['record_count']+=1
    bundle['index']=encoded(index);bundle['expected']['index_sha256']=post.sha(bundle['index'])
    assert validate(bundle)['status']=='HOLD'


@pytest.mark.parametrize('kind',['session','record','missing','previous','duplicate'])
def test_ledger_jsonl_must_match_record_and_index(bundle,kind):
    lines=[json.loads(line) for line in bundle['ledger'].splitlines() if line.strip()]
    if kind=='session':lines[-1]['session_id']='other'
    elif kind=='record':lines[-1]['memory_intake_status']='PROMOTED'
    elif kind=='missing':lines.pop()
    elif kind=='previous':lines[-2]['event_hash']='0'*64
    elif kind=='duplicate':lines.append(copy.deepcopy(lines[-1]))
    bundle['ledger']=b'\n'.join(json.dumps(x).encode() for x in lines)
    bundle['expected']['ledger_sha256']=post.sha(bundle['ledger'])
    assert validate(bundle)['status']=='HOLD'


@pytest.mark.parametrize('kind',['publish','no_review','missing_review','provenance_publish','provenance_review','upstream_publish',
    'upstream_review','causal_proof','provenance_absent','qwen','writer','gate_hold','gate_block','wrong_observation','unknown_hold'])
def test_e2e_publication_review_and_governance_gates_remain_closed(bundle,kind):
    e=json.loads(bundle['e2e'])
    if kind=='publish':e['PUBLICATION_PERMITTED']=True
    elif kind=='no_review':e['HUMAN_REVIEW_REQUIRED']=False
    elif kind=='missing_review':e.pop('HUMAN_REVIEW_REQUIRED')
    elif kind=='provenance_publish':e['provenance']['publication_permitted']=True
    elif kind=='provenance_review':e['provenance'].pop('human_approval_required')
    elif kind=='upstream_publish':e['upstream']['publication_permitted']=True
    elif kind=='upstream_review':e['upstream'].pop('human_review_required')
    elif kind=='causal_proof':e['validated_causal_proof']=True
    elif kind=='provenance_absent':e.pop('provenance')
    elif kind=='qwen':e['provenance']['source']='QWEN'
    elif kind=='writer':e['upstream']['memory_write']=True
    elif kind in ('gate_hold','gate_block'):e['upstream']['governance_ticket']=kind.removeprefix('gate_').upper()
    elif kind=='wrong_observation':e['provenance']['observation_sha256']='0'*64
    elif kind=='unknown_hold':e['result']='HOLD';e['BLOCK_REASON']='COGNITIVE_REFUSAL'
    bundle['e2e']=encoded(e);bundle['expected']['e2e_sha256']=post.sha(bundle['e2e'])
    assert validate(bundle)['status']=='HOLD'


def test_duplicate_json_key_is_not_admitted(bundle):
    bundle['record']=bundle['record'].replace(b'"readonly": true',b'"readonly": true, "readonly": true')
    bundle['expected']['record_sha256']=post.sha(bundle['record'])
    assert validate(bundle)['status']=='HOLD'


def test_original_e2e_files_reports_and_ledgers_unchanged():
    before=json.loads((A/'before.json').read_text())
    assert all(post.sha((S/path).read_bytes())==pin for path,pin in before['originals'].items())


def test_corrected_runner_has_no_network_or_trial_execution():
    source=(A/'replay_postcheck.py').read_text(encoding='utf-8-sig')
    import ast
    tree=ast.parse(source)
    imports=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
    assert not any(n.startswith(('urllib','http','requests','socket','subprocess','one_trial')) for n in imports)
    assert 'validate_trace' in source and 'POSTCHECK_CORRECTED.json' in source
