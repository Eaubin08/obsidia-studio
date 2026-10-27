"""Offline repair regression: no producer imports, model calls or startup hooks."""
import ast
import copy
import json
import os
import re
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator
import studio_ai
from editorial_intent import explanatory_editorial_request
from editorial_cleanup import clean_editorial_draft


def native(text='<POST>Un brouillon original à évaluer.</POST>'):
    return dict(response=text, source='REAL_BRODY_RUNTIME_NO_GRAPHITI',
                readonly=True, decision_authority='KX108_ONLY',
                emits_act=False, kernel_mutation=False, memory_write=False)


@pytest.mark.parametrize('key', ['', ' ', 'value\rheader', 'value\nheader'])
def test_native_requires_key_before_network(monkeypatch,key):
    monkeypatch.setenv('OBSIDIA_STUDIO_API_KEY',key)
    with patch.object(studio_ai.urllib.request,'build_opener') as build:
        with pytest.raises(studio_ai.InferenceError,match='AUTH_REQUIRED'):
            studio_ai._call({'message':'test'},3)
        build.assert_not_called()


def test_pr_native_uses_existing_brody_api_key(monkeypatch):
    monkeypatch.setenv('OBSIDIA_STUDIO_API_KEY','synthetic-test-value')
    monkeypatch.setenv('OBSIDIA_STUDIO_BRODY_URL','http://127.0.0.1:8000')
    response=Mock(); response.__enter__=Mock(return_value=response); response.__exit__=Mock(return_value=False)
    response.read.return_value=b'{"response":"ok"}'
    with patch.object(studio_ai.urllib.request,'build_opener') as build:
        build.return_value.open.return_value=response
        assert studio_ai._call({'message':'test'},3)=={'response':'ok'}
        req=build.return_value.open.call_args.args[0]
        assert req.get_header('X-api-key')=='synthetic-test-value'
        assert req.full_url=='http://127.0.0.1:8000/api/brody/chat'
        assert any(isinstance(h,studio_ai.E11NoRedirect) for h in build.call_args.args)
        assert any(isinstance(h,studio_ai.urllib.request.ProxyHandler) and not h.proxies for h in build.call_args.args)
        build.return_value.open.assert_called_once()


@pytest.mark.parametrize('kind',['http403','http503','network','invalid_json','oversize'])
def test_transport_errors_do_not_expose_secrets_or_retry(monkeypatch,kind):
    monkeypatch.setenv('OBSIDIA_STUDIO_API_KEY','PRIVATE_KEY_VALUE')
    with patch.object(studio_ai.urllib.request,'build_opener') as build:
        if kind.startswith('http'):
            build.return_value.open.side_effect=studio_ai.urllib.error.HTTPError('http://localhost',int(kind[4:]),'PRIVATE_KEY_VALUE',{},None)
        elif kind=='network':
            build.return_value.open.side_effect=OSError('PRIVATE_KEY_VALUE')
        else:
            response=Mock(); response.__enter__=Mock(return_value=response); response.__exit__=Mock(return_value=False)
            response.read.return_value=b'PRIVATE_KEY_VALUE' if kind=='invalid_json' else b'x'*5_000_001
            build.return_value.open.return_value=response
        with pytest.raises(studio_ai.InferenceError) as error:
            studio_ai._call({'message':'synthetic'},3)
        assert 'PRIVATE_KEY_VALUE' not in str(error.value)
        assert build.return_value.open.call_count==1


@pytest.mark.parametrize('ingress',[False,True])
def test_editorial_intent_reaches_selected_transport_without_router_entitlement(ingress):
    subject='Comment une petite entreprise peut-elle gagner du temps ?'
    prompt=explanatory_editorial_request(subject,'LinkedIn','Contexte public synthétique.')
    assert prompt.endswith('Contexte public synthétique.') and subject in prompt
    assert 'Rédige une publication LinkedIn expliquant' in prompt
    assert not any(x in prompt for x in ('ROUTER_OK','BRODY_SUFFICIENT','ALLOW','LOCAL_MODEL_GATE'))
    target='_ingress_call' if ingress else '_call'
    with patch.object(studio_ai,target,return_value={'status':'HOLD'}) as call:
        with pytest.raises(studio_ai.InferenceError):
            studio_ai.generate(prompt,use_ingress=ingress)
    sent=call.call_args.args[0]
    assert prompt in (sent if ingress else sent['message'])


@pytest.mark.parametrize('changes',[
    {'status':'HOLD'},{'status':'BLOCK'},{'readonly':False},
    {'decision_authority':'OTHER'},{'memory_write':True},{'allowed_to_act':True},
    {'pre_reasoning_snapshot':{'reasoning_directive':{'resolution_required':True}}},
    {'pre_reasoning_snapshot':{'unknown_qualification':{'unresolved_unknowns':['x']}}},
    {'source':'GOVERNED_MODEL_PROJECTION'},{'source':'TERMINAL_DIALOGUE_IDENTITY'},
])
def test_native_draft_never_overrides_refusal_or_unproven_author(changes):
    with patch.object(studio_ai,'_call',return_value={**native(),**changes}):
        with pytest.raises(studio_ai.InferenceError):
            studio_ai.generate('Sujet',use_ingress=False)


def test_native_original_draft_preserves_provenance_and_response():
    from test_studio_ai import public_native
    result=public_native(); before=copy.deepcopy(result)
    brief=result['pre_reasoning_snapshot']['user_message']
    with patch.object(studio_ai,'_call',return_value=result) as call:
        text,receipt=studio_ai.generate(brief,use_ingress=False,return_receipt=True)
    assert text==result['response'] and result==before
    assert receipt['source']=='BRODY_NATIVE_EDITORIAL_V1' and receipt['response_field']=='editorial_artifact'
    assert receipt['lineage_verified'] is True
    assert receipt['publication_permitted'] is False
    assert call.call_args.args[0]['allow_local_model'] is False



def test_prompt_echo_is_not_original_writing():
    text=studio_ai._native_editorial_request('Sujet')
    with patch.object(studio_ai,'_call',return_value=native('<POST>'+text+'</POST>')):
        with pytest.raises(studio_ai.InferenceError):
            studio_ai.generate('Sujet',use_ingress=False)


@pytest.mark.parametrize('verdict',['HOLD','BLOCK'])
def test_existing_receipt_validator_preserves_cognitive_refusals(verdict):
    from test_studio_e11_lot1 import envelope
    result=envelope()
    result.update(native())
    result['status']=verdict
    with patch.object(studio_ai,'_call',return_value=result):
        with pytest.raises(studio_ai.InferenceError):
            studio_ai.generate('Sujet',use_ingress=False)


def server_namespace():
    tree=ast.parse(Path('server.py').read_text(encoding='utf-8'))
    nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('GenIn','generate')]
    namespace=dict(app=FastAPI(),BaseModel=BaseModel,HTTPException=HTTPException,
                   Literal=__import__("typing").Literal, Field=Field, model_validator=model_validator,
                   os=os,re=re,studio_ai=studio_ai,templates=lambda:[],
                   NETWORKS={'linkedin':{'label':'LinkedIn','hint':'court','limit':3000}},
                   clean_editorial_draft=clean_editorial_draft)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'server.py','exec'),namespace)
    return namespace


@pytest.mark.parametrize('mode',['studio_llamacpp','studio_local_model','studio_template','unknown'])
def test_server_requires_brody_author(monkeypatch,mode):
    monkeypatch.setenv('OBSIDIA_STUDIO_EDITORIAL_MODE',mode)
    ns=server_namespace()
    with patch.object(studio_ai,'generate') as generate:
        with pytest.raises(HTTPException) as error: ns['generate'](ns['GenIn'](idea='Sujet'))
    assert error.value.status_code==503 and 'BRODY_AUTHOR_REQUIRED' in error.value.detail
    generate.assert_not_called()


def test_governed_ingress_disabled_never_falls_back(monkeypatch):
    monkeypatch.setenv('OBSIDIA_STUDIO_EDITORIAL_MODE','governed_ingress')
    monkeypatch.setenv('OBSIDIA_STUDIO_USE_INGRESS','0')
    ns=server_namespace()
    with patch.object(studio_ai,'generate') as generate:
        with pytest.raises(HTTPException): ns['generate'](ns['GenIn'](idea='Sujet'))
    generate.assert_not_called()


def test_server_refusal_does_not_return_user_text_or_call_twice(monkeypatch):
    monkeypatch.setenv('OBSIDIA_STUDIO_EDITORIAL_MODE','brody_native')
    monkeypatch.setenv('OBSIDIA_STUDIO_ALLOW_BRODY_NATIVE','1')
    ns=server_namespace()
    with patch.object(studio_ai,'generate',side_effect=studio_ai.InferenceError('GOVERNANCE_BOUNDARY')) as generate:
        with pytest.raises(HTTPException) as error:
            ns['generate'](ns['GenIn'](idea='Sujet',source_text='Texte utilisateur'))
    assert error.value.status_code==409
    generate.assert_called_once()


def test_server_selected_native_preserves_subject_and_receipt(monkeypatch):
    monkeypatch.setenv('OBSIDIA_STUDIO_EDITORIAL_MODE','brody_native')
    monkeypatch.setenv('OBSIDIA_STUDIO_ALLOW_BRODY_NATIVE','1')
    ns=server_namespace(); receipt={'source':'BRODY_NATIVE','publication_permitted':False}
    with patch.object(studio_ai,'generate',return_value=('<POST>Texte original.</POST>',receipt)) as generate:
        result=ns['generate'](ns['GenIn'](idea='Question intacte ?'))
    assert result['provenance']==receipt
    assert 'Question intacte ?' in generate.call_args.args[0]
    assert 'Rédige une publication LinkedIn expliquant' in generate.call_args.args[0]
    assert generate.call_args.kwargs=={'return_receipt':True,'use_ingress':False}
