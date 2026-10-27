"""Admission of pinned local software observations. No network or writer.

The selector is not evidence. Only a code-pinned, server-owned evidence catalog
can supply references; producer JSON cannot register or approve itself.
"""
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'data/experiments/internal_observation_integration_20261024'
CATALOG_SHA256 = 'fcff60ec40f029a463b09fa767caf32106aa43b0fc405f6c817aff41e942f81e'


def reference_for(identifier, brief, reference_type):
    from studio_native_editorial import need
    need(type(identifier) is str and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,127}', identifier))
    path = EVIDENCE / 'TRUSTED_OBSERVATIONS.json'
    raw = path.read_bytes()
    need(len(raw) < 16000 and hashlib.sha256(raw).hexdigest() == CATALOG_SHA256)
    catalog = json.loads(raw)
    need(catalog.get('schema') == 'STUDIO_INTERNAL_OBSERVATION_CATALOG_V1')
    entry = catalog['observations'].get(identifier)
    need(isinstance(entry, dict))
    need(entry['brief_sha256'] == hashlib.sha256(json.dumps(brief, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
    args = dict(entry)
    for key in ('observation_path', 'trace_path', 'test_path', 'test_result_path'):
        relative = Path(args[key])
        need(not relative.is_absolute() and '..' not in relative.parts)
        resolved = (ROOT / relative).resolve()
        need(resolved.is_relative_to(ROOT) and resolved.is_file())
        args[key] = resolved
    return reference_type(**args)


def validate_observation_artifact(body, brief, version, identifier, proof):
    from studio_native_editorial import need, _pure_modules
    from studio_e11_contract import _control, consume_envelope
    import studio_e11_deployment as deployment
    native_schema = 'BRODY_NATIVE_EDITORIAL_' + version
    need(body.get('final_answer_source') == 'BRODY_NATIVE_INTERNAL_OBSERVATION_' + version)
    need(body.get('editorial_route_status') == 'CONSULTATIVE_DRAFT_AVAILABLE')
    need(body.get('internal_observation_status') == 'OBSERVED_DEPENDENCY_VERIFIED')
    need(not body.get('editorial_refusal_reasons'))
    snapshot = body.get('editorial_composition_snapshot'); artifact = body.get('editorial_artifact')
    need(isinstance(snapshot, dict) and isinstance(artifact, dict))
    for obj in (body, snapshot, artifact):
        _control(obj, ('readonly', 'advisory_only', 'decision_authority', 'memory_write'))
        need(not obj.get('contradictions'))
        need('validated_causal_proof' not in obj or obj['validated_causal_proof'] is False)
        need('publication_permitted' not in obj or obj['publication_permitted'] is False)
        need('human_review_required' not in obj or obj['human_review_required'] is True)
        for key in ('editorial_version', 'editorial_version_requested', 'editorial_version_selected'):
            need(key not in obj or obj[key] == version)
    need(snapshot.get('schema') == native_schema and snapshot.get('status') == 'DRAFT_AVAILABLE')
    need(artifact.get('schema') == 'BRODY_PUBLIC_INTERNAL_OBSERVATION_ARTIFACT_' + version)
    need(artifact.get('kind') == 'INTERNAL_OBSERVATION_EXPLANATION')
    need(artifact.get('internal_observation_id') == identifier)
    need(artifact.get('editorial_version') == version and artifact.get('native_composition_schema') == native_schema)
    if version == 'V2':
        need(body.get('editorial_version_requested') == 'V2' and snapshot.get('editorial_version') == 'V2')
        need(artifact.get('selection_provenance') == {'kind':'EXPLICIT_REQUEST_FIELD','field':'editorial_version','requested':'V2','selected':'V2'})
    for obj in (snapshot, artifact):
        need(obj.get('human_review_required') is True and obj.get('publication_permitted') is False)
        need(obj.get('memory_status') == 'MEMORY_WRITE_HOLD')
    need(artifact.get('validated_causal_proof') is False)
    need(snapshot.get('internal_observation_projection') == 'PUBLIC_VIEW_NOT_ORIGINAL_RECEIPT')
    need(snapshot.get('hold_reasons') == [] and snapshot.get('essential_unresolved_symbols') == [])
    need(snapshot.get('router', {}).get('gate_verdict') == 'ALLOW' and snapshot['router'].get('fail_closed_hold') is False)
    e11 = consume_envelope(body, experiment_id='editorial-observation-boundary', provenance={})
    need(e11['consumer_status'] in {'CONTEXT_AVAILABLE', 'CONTEXT_LIMITED'})
    need(not e11['original_receipt']['cognition_shadow_memory']['context_packet'].get('contradictions'))
    pre = snapshot.get('pre_reasoning')
    need(isinstance(pre, dict) and pre == body.get('pre_reasoning_snapshot') == body.get('pipeline_pre_reasoning_snapshot'))
    need(pre.get('schema') == 'BRODY_PRE_REASONING_SNAPSHOT_V1' and pre.get('user_message') == brief)
    _control(pre, ('readonly', 'decision_authority'))
    need(pre.get('pre_reasoning_calibration', {}).get('lexical_source_status') == 'CALIBRATED')
    need(not pre.get('reasoning_directive', {}).get('contradictions'))
    modules = {}; connections = []
    try:
        modules, connections, grammar, composer, voice, calibration = _pure_modules(
            deployment.DEPLOYMENT / 'producer_cbad0125/source', modules, connections, observation=True)
        adapter = modules['apps.obsidia_api.brody_internal_observation_adapter']
        reference = reference_for(identifier, brief, adapter.InternalObservationReference)
        observation = adapter.load_internal_observation(reference)
        verified = adapter.verify_internal_observation(observation, reference, brief=brief)
        need(verified.get('status') == 'VERIFIED_INTERNAL_OBSERVATION')
        need(verified.get('validated_causal_proof') is False and verified.get('independent_attestation') is False)
        view = adapter.project_public_internal_observation
        need(snapshot.get('internal_observation') == view(observation))
        need(snapshot.get('internal_observation_verification') == view(verified))
        need(artifact.get('internal_observation') == {'schema':'BRODY_PUBLIC_INTERNAL_OBSERVATION_VIEW_V1',
            'original_observation_sha256':reference.observation_sha256, 'observation':view(observation), 'verification':view(verified)})
        frame = grammar.parse_utterance(brief); interpretation = grammar.project_editorial_brief(frame)
        need(composer.digest(snapshot.get('grammar')) == composer.digest(asdict(frame)) and not frame.contradictions)
        need(interpretation.get('supported') is True and snapshot.get('interpretation') == interpretation)
        subject = interpretation.get('subject') or {}
        need(subject.get('actor') == 'seuil' and subject.get('predicate') == 'modifier')
        need(any(a.get('head') == 'résultat' for r in subject.get('relations', []) for a in r['objects']))
        need(not any(str(m).startswith('unanalyzed_predicative_content:') for m in frame.missing))
        for key in ('editorial_intent','subject','audience','platform','constraints'):
            need(snapshot.get(key) == interpretation.get(key))
        dependency = ' '.join(a['text'] for r in subject['relations'] for a in r['objects']) + ' ' + ' '.join(r['subject'] or '' for r in subject['relations'])
        from unicodedata import normalize, combining
        def fold(value):return ''.join(c for c in normalize('NFKD', value.lower()) if not combining(c))
        need(not any(re.search(r'(?<![\w])'+re.escape(fold(x))+r'(?![\w])', fold(dependency)) for x in pre.get('unknowns', [])))
        uncertainties = [{'kind':'UNRESOLVED_SYMBOL','symbol':x} for x in pre.get('unknowns', [])]
        uncertainties += [{'kind':'EDITORIAL_CONTEXT_UNKNOWN','code':x} for x in interpretation.get('unknowns', []) if x == 'AUDIENCE_NOT_SPECIFIED']
        need(snapshot.get('uncertainties') == artifact.get('uncertainties') == uncertainties)
        need(snapshot.get('explanatory_context') == view(composer._explanatory_context(frame)))
        candidates = composer._internal_observation_operations(verified)
        selected, plan = composer._select_internal_observation_plan(candidates)
        need(bool(selected) and bool(plan))
        for key, expected in (('candidate_propositions', candidates), ('selected_propositions', selected), ('editorial_plan', plan)):
            need(snapshot.get(key) == view(expected))
        need(artifact.get('selected_propositions') == view(selected) and artifact.get('editorial_plan') == plan)
        need(artifact.get('selected_proposition_ids') == [p['id'] for p in selected])
        refs = ['internal-observation-sha256:' + reference.observation_sha256]
        need(snapshot.get('evidence_refs') == artifact.get('evidence_refs') == refs)
        realized = voice.realize_brody_editorial_plan(selected, plan, version=version, observation_verification=verified)
        need(realized.get('status') == 'REALIZED' and snapshot.get('realization') == artifact.get('realization') == view(realized))
        draft = {'text':realized['text'], 'author':'BRODY', 'status':'CONSULTATIVE_DRAFT', 'factual_claims':[],
                 'proposition_ids':realized['proposition_ids'], 'sha256':composer.digest(realized['text']), 'kind':'INTERNAL_OBSERVATION_EXPLANATION'}
        need(snapshot.get('draft') == artifact.get('draft') == draft)
        provenance = {'author':'BRODY','source':composer.source_ref(composer.compose_native_editorial), 'brief_sha256':composer.digest(brief),
                      'model_calls':0,'composition_origin':'NATIVE_RELATION_SELECTION_AND_PLANNING', 'observation_ref':reference.observation_sha256,
                      'components':[composer.source_ref(f) for f in (grammar.parse_utterance, grammar.project_editorial_brief,
                       composer._operations, composer._select_and_plan, voice.realize_brody_editorial_plan, calibration.calibrate_pre_response,
                       composer._semantic_operations, composer._internal_observation_operations, composer._select_internal_observation_plan)]}
        if version == 'V2':provenance['components'].extend(composer.source_ref(f) for f in (composer._v2_operations, composer._v2_select_and_plan))
        need(snapshot.get('provenance') == artifact.get('provenance') == view(provenance))
        c275 = calibration.calibrate_pre_response(candidate_response=realized['text'], reasoning_directive=pre['reasoning_directive'],
                    pre_reasoning_calibration=pre['pre_reasoning_calibration'], language='fr')
        need(c275.get('calibration_required') is False and c275.get('response_readiness') in {'READY','READY_WITH_UNCERTAINTY'})
        need(snapshot.get('c275') == body.get('pre_response_calibration') == c275)
        post = '<POST>' + draft['text'] + '</POST>'
        need(all(body.get(k) == post for k in ('response','response_md','final_answer')))
        return post, {'source':'BRODY_NATIVE_INTERNAL_OBSERVATION_'+version,'editorial_version':version,'response_field':'editorial_artifact',
            'decision_authority':'KX108_ONLY','human_approval_required':True,'publication_permitted':False,'model_calls':0,
            'qwen_evidence_applied':False,'lineage_verified':True,'observation_verified':True,'validated_causal_proof':False,
            'observation_sha256':reference.observation_sha256,'observation_scope':verified['relation']['scope'],
            'base_checkpoint':proof['checkpoint'],'overlay_producer_head':proof['overlay_producer_head'],'manifest_sha256':proof['manifest_sha256'],
            'e11_consumer_status':e11['consumer_status'],'context_limit_reasons':e11['context_limit_reasons'],
            'memory_retrieval_status':e11['memory_retrieval_status'],'uncertainties_count':len(uncertainties),'draft_sha256':draft['sha256']}
    finally:
        for conn in connections:conn.close()
        for module in modules.values():sys.modules.pop(module.__name__, None)
