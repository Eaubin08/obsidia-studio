"""Tests hors réseau du raccord Studio → Brody / routeur Obsidia."""
import os
import unittest
from unittest.mock import patch
import studio_ai
import json
from pathlib import Path

def public_native():
    path=Path(__file__).parent/'data/experiments/internal_observation_integration_20261024/public_fixture_False.json'
    return json.loads(path.read_text(encoding='utf-8'))


def native_result(**fields):
    return {"readonly": True, "decision_authority": "KX108_ONLY",
            "source": "REAL_BRODY_RUNTIME_NO_GRAPHITI", **fields}


class LocalAIContractTests(unittest.TestCase):
    def setUp(self):
        # Every test starts offline in Brody-only mode regardless of shell flags.
        self._mode = patch.dict(os.environ, {"OBSIDIA_STUDIO_USE_INGRESS": "0"})
        self._mode.start()
        self.addCleanup(self._mode.stop)

    def test_loopback_only(self):
        self.assertEqual(studio_ai._endpoint({"base_url": "http://127.0.0.1:8000"}),
                         "http://127.0.0.1:8000/api/brody/chat")
        for url in ("https://example.org", "http://example.org",
                    "http://127.0.0.1:8000/v1", "http://user:pass@localhost:8000"):
            with self.subTest(url=url), self.assertRaises(studio_ai.InferenceError):
                studio_ai._endpoint({"base_url": url})

    def test_brody_first(self):
        payload = public_native()
        brief = payload['pre_reasoning_snapshot']['user_message']
        with patch.object(studio_ai, '_call', return_value=payload) as call:
            self.assertEqual(studio_ai.generate(brief), payload['response'])
        data = call.call_args.args[0]
        self.assertEqual(data['message'], brief)
        self.assertFalse(data['allow_provider'])
        self.assertFalse(data['allow_local_model'])
        self.assertEqual(data['language'], 'fr')

    def test_native_request_preserves_topic_and_no_fabrication(self):
        subject = "Pourquoi comprendre avant d'agir ?"
        message = studio_ai._native_editorial_request(subject)
        self.assertIn(subject, message)
        self.assertTrue(message.startswith("Rédige une publication LinkedIn expliquant "))
        self.assertNotIn("ALLOW", message)
        with self.assertRaises(studio_ai.InferenceError):
            studio_ai._native_editorial_request(" ")

    def test_ingress_receives_unmodified_subject(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_USE_INGRESS": "1",
                                      "OBSIDIA_STUDIO_ENABLE_INGRESS": "1"}):
            with patch.object(studio_ai, "_ingress_call", return_value={
                "status": "HOLD", "emits_act": False
            }) as ingress:
                with self.assertRaises(studio_ai.InferenceError):
                    studio_ai.generate("Sujet intact")
                self.assertEqual(ingress.call_args.args[0], "Sujet intact")

    def test_reject_act(self):
        with patch.object(studio_ai, "_call", return_value={"response": "texte", "emits_act": True}):
            with self.assertRaises(studio_ai.InferenceError):
                studio_ai.generate("Rédige")

    def test_identity_fallback_rejected(self):
        payload = {
            "response": "Je suis Brody, interface structurée readonly.",
            "final_answer": "Je suis Brody.",
            "response_md": "Ce symbole reste non résolu avant raisonnement.",
            "final_answer_source": "TERMINAL_DIALOGUE_IDENTITY",
        }
        payload = native_result(**payload)
        with patch.object(studio_ai, "_call", return_value=payload):
            with self.assertRaisesRegex(studio_ai.InferenceError, "TERMINAL_DIALOGUE_IDENTITY"):
                studio_ai.generate("Rédige un post")

    def test_echoed_post_instruction_is_not_a_generated_draft(self):
        diagnostic = (
            "Synthese readonly depuis source-pack.\\n"
            "- Requete : Reponds sous la forme <POST>texte redige</POST>.\\n"
            "- Familles consultees : READINESS, GAP_MATRIX"
        )
        with patch.object(studio_ai, "_call", return_value={"response": diagnostic}):
            with self.assertRaises(studio_ai.InferenceError):
                studio_ai.generate("Pourquoi comprendre avant d'agir ?")

    def test_structured_post_preferred_over_identity(self):
        # A POST in only one response field no longer proves native lineage.
        payload = native_result(response='Je suis Brody.', final_answer='Je suis Brody.',
                                response_md='<POST>Brouillon non attesté.</POST>')
        with patch.object(studio_ai, '_call', return_value=payload):
            with self.assertRaises(studio_ai.InferenceError):
                studio_ai.generate('Rédige')

    def test_non_empty_post_only(self):
        with patch.object(studio_ai, "_call", return_value={"response": "<POST></POST>"}):
            with self.assertRaises(studio_ai.InferenceError):
                studio_ai.generate("Rédige")

    def test_explicit_native_mode_never_calls_ingress(self):
        payload = public_native()
        with patch.dict(os.environ, {'OBSIDIA_STUDIO_USE_INGRESS':'1'}):
            with patch.object(studio_ai, '_ingress_call') as ingress:
                with patch.object(studio_ai, '_call', return_value=payload) as call:
                    self.assertEqual(studio_ai.generate(payload['pre_reasoning_snapshot']['user_message'], use_ingress=False), payload['response'])
                    call.assert_called_once(); ingress.assert_not_called()

    def test_ingress_opt_in_off_by_default(self):
        payload = public_native()
        with patch.dict(os.environ, {'OBSIDIA_STUDIO_USE_INGRESS':'0'}):
            with patch.object(studio_ai, '_call', return_value=payload) as call:
                self.assertEqual(studio_ai.generate(payload['pre_reasoning_snapshot']['user_message']), payload['response'])
                call.assert_called_once()

    def test_ingress_requires_explicit_enable(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_USE_INGRESS": "1",
                                      "OBSIDIA_STUDIO_ENABLE_INGRESS": "0"}):
            with self.assertRaises(studio_ai.InferenceError):
                studio_ai.generate("Rédige")

    def test_ingress_output_must_be_editorial(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_USE_INGRESS": "1",
                                      "OBSIDIA_STUDIO_ENABLE_INGRESS": "1"}):
            with patch.object(studio_ai, "_ingress_call", return_value={
                "status": "HOLD", "response": "no draft", "emits_act": False
            }):
                with self.assertRaisesRegex(studio_ai.InferenceError, "GOVERNANCE_REFUSED"):
                    studio_ai.generate("Rédige")

    def test_verified_qwen_ingress_is_not_a_brody_draft(self):
        payload = {
            "status": "READY_READONLY", "readonly": True, "advisory_only": True,
            "decision_authority": "KX108_ONLY", "allowed_to_act": False,
            "memory_write": False, "emits_act": False, "kernel_mutation": False,
            "route_decision": {
                "router_status": "ROUTER_OK", "fail_closed_hold": False,
                "gate_verdict": "ALLOW",
            },
            "brody_sufficiency": {"status": "BRODY_INSUFFICIENT", "next_stage": "LOCAL_MODEL_GATE"},
            "local_model_stage": {
                "status": "EVIDENCE_READY", "eligible": True,
                "attempted": True, "model_call_used": True,
                "evidence_applied": True, "tokens_remote": 0,
            },
            "final_response": "Proposition sur comprendre, proposer, décider.",
        }
        env = {"OBSIDIA_STUDIO_USE_INGRESS": "1", "OBSIDIA_STUDIO_ENABLE_INGRESS": "1"}
        with patch.dict(os.environ, env), patch.object(studio_ai, "_ingress_call", return_value=payload):
            with self.assertRaises(studio_ai.InferenceError):
                studio_ai.generate("Rédige")
        for change in (
            {"local_model_stage": {**payload["local_model_stage"], "evidence_applied": False}},
            {"route_decision": {**payload["route_decision"], "fail_closed_hold": True}},
            {"advisory_only": False},
            {"local_model_stage": {**payload["local_model_stage"], "tokens_remote": 42}},
        ):
            with self.subTest(change=change), patch.dict(os.environ, env):
                with patch.object(studio_ai, "_ingress_call", return_value={**payload, **change}):
                    with self.assertRaises(studio_ai.InferenceError):
                        studio_ai.generate("Rédige")

    def test_verified_brody_sufficient_skips_qwen(self):
        payload = {
            "status": "READY_READONLY", "readonly": True, "advisory_only": True,
            "decision_authority": "KX108_ONLY", "allowed_to_act": False,
            "memory_write": False, "emits_act": False, "kernel_mutation": False,
            "route_decision": {"router_status": "ROUTER_OK", "fail_closed_hold": False,
                               "gate_verdict": "ALLOW"},
            "brody_sufficiency": {
                "status": "BRODY_SUFFICIENT", "sufficient": True,
                "next_stage": "LOCAL_STACK_RESULT", "brody_boundary_ok": True,
                "output_contract_ok": True, "contradictions": [], "risk_flags": [],
            },
            "local_model_stage": {"status": "SKIPPED", "model_call_used": False},
            "final_response": "Texte de Brody seul à vérifier humainement.",
        }
        env = {"OBSIDIA_STUDIO_USE_INGRESS": "1", "OBSIDIA_STUDIO_ENABLE_INGRESS": "1"}
        with patch.dict(os.environ, env), patch.object(studio_ai, "_ingress_call", return_value=payload):
            with self.assertRaises(studio_ai.InferenceError):
                studio_ai.generate("Rédige")
        for bad in ({"brody_sufficiency": {**payload["brody_sufficiency"], "sufficient": False}},
                    {"brody_sufficiency": {**payload["brody_sufficiency"], "contradictions": ["ACTION"]}},
                    {"local_model_stage": {"model_call_used": True}},
                    {"route_decision": {**payload["route_decision"], "gate_verdict": "HOLD"}}):
            with patch.dict(os.environ, env), patch.object(studio_ai, "_ingress_call",
                return_value={**payload, **bad}):
                with self.assertRaises(studio_ai.InferenceError):
                    studio_ai.generate("Rédige")

    def test_provenance_receipt_brody_and_qwen(self):
        base = {
            "status": "READY_READONLY", "readonly": True, "advisory_only": True,
            "decision_authority": "KX108_ONLY", "allowed_to_act": False,
            "emits_act": False, "kernel_mutation": False,
            "route_decision": {"router_status": "ROUTER_OK", "fail_closed_hold": False,
                               "gate_verdict": "ALLOW"},
            "final_response": "Texte éditorial consultatif.",
        }
        suff = {"status": "BRODY_SUFFICIENT", "sufficient": True,
                "next_stage": "LOCAL_STACK_RESULT", "brody_boundary_ok": True,
                "output_contract_ok": True, "contradictions": [], "risk_flags": []}
        qwen_suff = {"status": "BRODY_INSUFFICIENT", "next_stage": "LOCAL_MODEL_GATE"}
        qwen_stage = {"status": "EVIDENCE_READY", "eligible": True, "attempted": True,
                      "model_call_used": True, "evidence_applied": True, "tokens_remote": 0}
        env = {"OBSIDIA_STUDIO_USE_INGRESS": "1", "OBSIDIA_STUDIO_ENABLE_INGRESS": "1"}
        brody = {**base, "brody_sufficiency": suff,
                 "local_model_stage": {"status": "SKIPPED", "model_call_used": False}}
        qwen = {**base, "brody_sufficiency": qwen_suff,
                "local_model_stage": qwen_stage,
                "final_answer_snapshot": {"governed_model_projection_selected": True}}
        for payload, expected in ((brody, "BRODY_NATIVE"), (qwen, "GOVERNED_MODEL_PROJECTION")):
            with self.subTest(expected=expected), patch.dict(os.environ, env):
                with patch.object(studio_ai, "_ingress_call", return_value=payload):
                    # Neither a source label nor sufficient plain text proves a
                    # public editorial plan/realization. Both stay rejected.
                    with self.assertRaises(studio_ai.InferenceError):
                        studio_ai.generate("Question", return_receipt=True)

    def test_real_post_wrapper_uses_newlines(self):
        payload = public_native()
        with patch.object(studio_ai, '_call', return_value=payload):
            output = studio_ai.generate(payload['pre_reasoning_snapshot']['user_message'], use_ingress=False)
        self.assertEqual(output, payload['response'])
        self.assertIn('\n\n', output)
        self.assertNotIn(r'\n', output)

    def test_true_governance_boundary_is_never_promoted_to_a_draft(self):
        result = {
            "status": "READY_READONLY", "readonly": True,
            "decision_authority": "KX108_ONLY",
            "route_decision": {"router_status": "ROUTER_OK", "fail_closed_hold": False,
                               "gate_verdict": "ALLOW"},
            "brody_sufficiency": {
                "status": "GOVERNANCE_BOUNDARY",
                "next_stage": "KX108_GOVERNANCE",
                "contradictions": ["REQUEST_REQUIRES_ACTION_OR_WRITE_BUT_ROUTE_IS_READONLY"],
                "risk_flags": ["BOUNDARY_REQUEST"],
            },
            "local_model_stage": {"status": "SKIPPED", "evidence_applied": False},
            "final_response": "Texte non autorisé.",
        }
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_USE_INGRESS": "1"}):
            with patch.object(studio_ai, "_ingress_call", return_value=result):
                with self.assertRaisesRegex(studio_ai.InferenceError, "GOVERNANCE_BOUNDARY"):
                    studio_ai.generate("Sujet")

    def test_default_status_is_configuration_only(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_BRODY_URL": "http://127.0.0.1:8000"}):
            st = studio_ai.status()
            self.assertFalse(st["ready"])
            self.assertEqual(st["provider"], "obsidia_brody")


if __name__ == "__main__":
    unittest.main()
