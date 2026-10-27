"""Admission of the pinned public Brody artifact, without cognitive execution.

Only pure linguistic/planning/realization functions are loaded from the verified
deployment. No Router, SENS, model, memory retrieval or application startup is
imported. This verifies local lineage, not factual truth or publication rights.
"""
import ast
import builtins
from dataclasses import asdict
import json
from pathlib import Path
import sqlite3
import sys
import threading
import types

import studio_e11_deployment as deployment
from studio_e11_contract import _control, consume_envelope

_LOCK = threading.RLock()


class NativeArtifactError(ValueError):
    pass


def need(ok):
    if not ok:
        raise NativeArtifactError('BRODY_NATIVE_ARTIFACT_INVALID')


def _pure_modules(root, modules, connections, *, observation=False, semantic=False):
    """Private module names; canonical application imports never execute."""
    original_import = builtins.__import__

    def importer(name, globals=None, locals=None, fromlist=(), level=0):
        if name in modules:
            return modules[name]
        need(not name.startswith(('app.', 'apps.', 'periphery.', 'scripts.')))
        return original_import(name, globals, locals, fromlist, level)

    def load(name, relative, functions=None):
        path = root / relative
        private = '_studio_native_' + name.replace('.', '_')
        module = types.ModuleType(private)
        module.__file__ = str(path)
        module.__dict__['__builtins__'] = dict(vars(builtins), __import__=importer)
        sys.modules[private] = module  # dataclasses/inspect need their defining module
        modules[name] = module
        source = path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(path))
        if functions is not None:
            tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in functions]
            need({n.name for n in tree.body} == set(functions))
        exec(compile(tree, str(path), 'exec'), module.__dict__)
        return module

    corpus = load('app.semantic.lattice.lexical_corpus', 'app/semantic/lattice/lexical_corpus.py')

    def readonly_connection():
        if not connections:
            conn = sqlite3.connect((root / 'data/linguistic_corpus/lexicon.db').as_uri() + '?mode=ro',
                                   uri=True, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA query_only=ON')
            connections.append(conn)
        return connections[0]

    corpus._get_connection = readonly_connection
    load('app.semantic.lattice.primitives', 'app/semantic/lattice/primitives.py')
    load('app.semantic.lattice.complement_commitment', 'app/semantic/lattice/complement_commitment.py')
    load('app.semantic.lattice.occurrence_derivation', 'app/semantic/lattice/occurrence_derivation.py')
    load('app.semantic.lattice.occurrence_projection', 'app/semantic/lattice/occurrence_projection.py')
    load('app.semantic.lattice.lexicon', 'app/semantic/lattice/lexicon.py')
    grammar = load('app.semantic.lattice.french_grammar', 'app/semantic/lattice/french_grammar.py')
    load('app.semantic.lattice.native_realization', 'app/semantic/lattice/native_realization.py')
    composer = load('apps.obsidia_api.brody_editorial_composition', 'apps/obsidia_api/brody_editorial_composition.py')
    voice = load('apps.obsidia_api.brody_true_voice_adapter', 'apps/obsidia_api/brody_true_voice_adapter.py',
                 ['realize_brody_editorial_plan', '_realize_brody_editorial_v2', '_realize_internal_observation'])
    calibration = load('periphery.language.pre_response_calibrator', 'periphery/language/pre_response_calibrator.py')
    if observation or semantic:
        load('app.semantic.lattice.flow_validators', 'app/semantic/lattice/flow_validators.py')
        load('app.semantic.lattice.ordered_meaning_flow', 'app/semantic/lattice/ordered_meaning_flow.py')
        load('app.semantic.lattice.language_flow_projection', 'app/semantic/lattice/language_flow_projection.py')
    if observation:
        load('periphery.agents.brody_documentation_architecture_reports', 'periphery/agents/brody_documentation_architecture_reports.py')
        load('apps.obsidia_api.brody_internal_observation_adapter', 'apps/obsidia_api/brody_internal_observation_adapter.py')
    return modules, connections, grammar, composer, voice, calibration


def validate_native_artifact(body, brief, *, base_url=deployment.BASE_URL, editorial_version="V1", internal_observation_id=None):
    """Return a detached draft/provenance. Fail closed; never change producer data."""
    with _LOCK:
        return _validate(body, brief, base_url, editorial_version, internal_observation_id)


def _validate(body, brief, base_url, editorial_version, internal_observation_id=None):
    need(type(editorial_version) is str and editorial_version in {"V1", "V2"})
    native_schema = "BRODY_NATIVE_EDITORIAL_" + editorial_version
    need(base_url == deployment.BASE_URL)
    proof = deployment.verify_checkpoint(base_url)
    need(proof is not None and proof.get('deployment_profile') == 'BRODY_NATIVE_EDITORIAL_WIP_OVERLAY_V1')
    need(isinstance(body, dict) and isinstance(brief, str))
    if internal_observation_id is not None:
        from studio_internal_observation import validate_observation_artifact
        try:
            return validate_observation_artifact(body, brief, editorial_version, internal_observation_id, proof)
        except (KeyError, TypeError, OSError, AttributeError, ImportError, ValueError):
            raise NativeArtifactError('BRODY_NATIVE_ARTIFACT_INVALID') from None
    need(body.get('editorial_route_status') == 'CONSULTATIVE_DRAFT_AVAILABLE')
    need(body.get('final_answer_source') == native_schema)
    for obj in (body, body.get('editorial_composition_snapshot', {}), body.get('editorial_artifact', {})):
        need(isinstance(obj, dict))
        for key in ('editorial_version', 'editorial_version_requested', 'editorial_version_selected'):
            need(key not in obj or obj[key] == editorial_version)
    need(not body.get('editorial_refusal_reasons'))
    # LOT 1 remains the sole C1/E11/B6 contract validator, unmodified.
    e11 = consume_envelope(body, experiment_id='editorial-boundary', provenance={})
    need(e11['consumer_status'] in {'CONTEXT_AVAILABLE', 'CONTEXT_LIMITED'})
    snapshot = body.get('editorial_composition_snapshot')
    artifact = body.get('editorial_artifact')
    need(isinstance(snapshot, dict) and isinstance(artifact, dict))
    need(snapshot.get('schema') == native_schema and snapshot.get('status') == 'DRAFT_AVAILABLE')
    need(artifact.get('schema') == 'BRODY_PUBLIC_EDITORIAL_ARTIFACT_' + editorial_version)
    if editorial_version == 'V2':
        need(body.get('editorial_version_requested') == 'V2')
        need(snapshot.get('editorial_version') == artifact.get('editorial_version') == 'V2')
        need(snapshot.get('human_review_required') is True and artifact.get('human_review_required') is True)
        need(snapshot.get('publication_permitted') is False)
        need(artifact.get('native_composition_schema') == native_schema)
        need(artifact.get('selection_provenance') == {'kind':'EXPLICIT_REQUEST_FIELD', 'field':'editorial_version', 'requested':'V2', 'selected':'V2'})
        for key in ('selected_propositions', 'realization', 'evidence_refs'):
            need(key in artifact and artifact[key] == snapshot.get(key))
    for obj in (body, snapshot, artifact):
        _control(obj, ('readonly', 'advisory_only', 'decision_authority', 'memory_write'))
        need(obj.get('memory_write') is False)
        # V1 has no mandatory producer review flag: Studio always requires review.
        # A contradictory explicit flag is refused, never overwritten by policy.
        need('human_review_required' not in obj or obj['human_review_required'] is True)
        need('publication_permitted' not in obj or obj['publication_permitted'] is False)
    need(artifact.get('publication_permitted') is False)
    need(snapshot.get('memory_status') == artifact.get('memory_status') == 'MEMORY_WRITE_HOLD')
    need(snapshot.get('hold_reasons') == [] and snapshot.get('essential_unresolved_symbols') == [])
    need(snapshot.get('evidence_refs') == [])  # this bounded contract contains advisory operations only
    pre = snapshot.get('pre_reasoning')
    need(isinstance(pre, dict) and pre == body.get('pre_reasoning_snapshot') == body.get('pipeline_pre_reasoning_snapshot'))
    need(pre.get('schema') == 'BRODY_PRE_REASONING_SNAPSHOT_V1')
    need(pre.get('user_message') == brief)
    _control(pre, ('readonly', 'decision_authority'))
    need(pre.get('pre_reasoning_calibration', {}).get('lexical_source_status') == 'CALIBRATED')
    need(not pre.get('reasoning_directive', {}).get('contradictions'))
    route = snapshot.get('router', {})
    need(route.get('gate_verdict') == 'ALLOW' and route.get('fail_closed_hold') is False)
    need(not snapshot.get('grammar', {}).get('contradictions'))
    need(not e11['original_receipt']['cognition_shadow_memory']['context_packet'].get('contradictions'))
    root = deployment.DEPLOYMENT / 'producer_cbad0125/source'
    modules = {}; connections = []
    try:
        modules, connections, grammar, composer, voice, calibration = _pure_modules(root, modules, connections, semantic=True)
        # Bind subject/constraints to the actual sent brief with the existing IR.
        frame = grammar.parse_utterance(brief)
        interpretation = grammar.project_editorial_brief(frame)
        need(composer.digest(snapshot.get('grammar')) == composer.digest(asdict(frame)))
        need(interpretation.get('supported') is True and snapshot.get('interpretation') == interpretation)
        need(not frame.contradictions and not any(str(m).startswith('unanalyzed_predicative_content:') for m in frame.missing))
        for key in ('editorial_intent', 'subject', 'audience', 'platform', 'constraints'):
            need(snapshot.get(key) == interpretation.get(key))
        semantic = interpretation.get('topic_kind') == 'SEMANTIC_RELATIONS'
        uncertainties = [{'kind':'UNRESOLVED_SYMBOL', 'symbol':x} for x in pre.get('unknowns', [])]
        if semantic:
            qualification = pre.get('unknown_qualification', {})
            need(qualification.get('schema') == 'BRODY_UNKNOWN_QUALIFICATION_V1'
                 and qualification.get('user_message') == brief
                 and qualification.get('unresolved_unknowns') == pre.get('unknowns'))
            # Mirror the pinned composer's IR-derived records exactly. Do not
            # accept arbitrary categories or delete an unresolved possessor.
            for relation in interpretation['subject'].get('relations', []):
                for argument in relation['objects']:
                    words = argument['text'].split()
                    if words and words[0].casefold() in {'son','sa','ses','leur','leurs'}:
                        uncertainties.append({'kind':'POSSESSOR_UNRESOLVED', 'unit_id':relation['unit_id'],
                            'source_span':argument.get('source_span'), 'resolution':'SOURCE_PERSPECTIVE_PRESERVED'})
            uncertainties.extend({'kind':'EDITORIAL_CONTEXT_UNKNOWN','code':x}
                for x in interpretation.get('unknowns', []) if x == 'AUDIENCE_NOT_SPECIFIED')
            need(composer.digest(snapshot.get('explanatory_context')) == composer.digest(composer._explanatory_context(frame)))
        need(composer.digest(snapshot.get('uncertainties')) == composer.digest(uncertainties))
        # Unknowns in essential predicates must not be erased by a forged snapshot.
        import re, unicodedata
        def fold(text):
            return ''.join(c for c in unicodedata.normalize('NFKD',text.lower()) if not unicodedata.combining(c))
        dependency = ' '.join(a.text for u in frame.units if u.lemma in {'utiliser','gagner'} for a in u.objects)
        if semantic:
            relations = interpretation['subject'].get('relations', [])
            dependency = ' '.join(a['text'] for relation in relations for a in relation['objects'])
            dependency += ' ' + ' '.join(relation['subject'] or '' for relation in relations)
        need(not any(re.search(r'(?<![\w])'+re.escape(fold(x))+r'(?![\w])',fold(dependency)) for x in pre.get('unknowns', [])))
        if editorial_version == 'V2':
            candidates = composer._v2_operations(interpretation, composer._operations(interpretation))
            selected, plan = composer._v2_select_and_plan(candidates, interpretation['constraints'])
        else:
            candidates = composer._operations(interpretation)
            selected, plan = composer._select_and_plan(candidates, interpretation['constraints'])
        need(snapshot.get('candidate_propositions') == candidates and snapshot.get('selected_propositions') == selected)
        need(snapshot.get('editorial_plan') == plan and bool(plan))
        realized = (voice.realize_brody_editorial_plan(selected, plan, version='V2')
                    if editorial_version == 'V2' else voice.realize_brody_editorial_plan(selected, plan))
        need(realized.get('status') == 'REALIZED' and snapshot.get('realization') == realized)
        draft = {'text':realized['text'], 'author':'BRODY', 'status':'CONSULTATIVE_DRAFT',
                 'factual_claims':[], 'proposition_ids':realized['proposition_ids'], 'sha256':composer.digest(realized['text'])}
        need(snapshot.get('draft') == draft and artifact.get('draft') == draft)
        provenance = {'author':'BRODY', 'source':composer.source_ref(composer.compose_native_editorial),
            'brief_sha256':composer.digest(brief), 'model_calls':0,
            'composition_origin':'NATIVE_RELATION_SELECTION_AND_PLANNING',
            'components':[composer.source_ref(f) for f in (grammar.parse_utterance,grammar.project_editorial_brief,
                composer._operations,composer._select_and_plan,voice.realize_brody_editorial_plan,calibration.calibrate_pre_response)]}
        if semantic:
            provenance['components'].append(composer.source_ref(composer._semantic_operations))
        if editorial_version == 'V2':
            provenance['components'].extend(composer.source_ref(f) for f in (composer._v2_operations, composer._v2_select_and_plan))
        need(composer.digest(snapshot.get('provenance')) == composer.digest(artifact.get('provenance')) == composer.digest(provenance))
        need(artifact.get('uncertainties') == snapshot['uncertainties'])
        need(artifact.get('editorial_plan') == plan and artifact.get('selected_proposition_ids') == [p['id'] for p in selected])
        c275 = calibration.calibrate_pre_response(candidate_response=realized['text'],
            reasoning_directive=pre['reasoning_directive'],pre_reasoning_calibration=pre['pre_reasoning_calibration'],language='fr')
        need(c275.get('calibration_required') is False and c275.get('response_readiness') in {'READY','READY_WITH_UNCERTAINTY'})
        need(snapshot.get('c275') == body.get('pre_response_calibration') == c275)
        post = '<POST>' + realized['text'] + '</POST>'
        need(all(body.get(k) == post for k in ('response','response_md','final_answer')))
        return post, {'source':native_schema, 'editorial_version':editorial_version, 'response_field':'editorial_artifact',
            'decision_authority':'KX108_ONLY', 'human_approval_required':True, 'publication_permitted':False,
            'qwen_evidence_applied':False, 'model_calls':0, 'lineage_verified':True,
            'base_checkpoint':proof['checkpoint'], 'overlay_producer_head':proof['overlay_producer_head'],
            'manifest_sha256':proof['manifest_sha256'], 'e11_consumer_status':e11['consumer_status'],
            'context_limit_reasons':e11['context_limit_reasons'], 'memory_retrieval_status':e11['memory_retrieval_status'],
            'uncertainties_count':len(snapshot['uncertainties']), 'draft_sha256':draft['sha256']}
    except (KeyError, TypeError, OSError, AttributeError, ImportError, ValueError):
        raise NativeArtifactError('BRODY_NATIVE_ARTIFACT_INVALID') from None
    finally:
        for conn in connections:
            conn.close()
        for module in modules.values():
            sys.modules.pop(module.__name__, None)
