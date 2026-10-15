"""Independent, deterministic Studio editorial contract.

No model call, no authority decision, no publishing. The source is user text,
not verified external evidence.
"""
def build_readonly_draft(idea: str, source_text: str, network: str) -> dict:
    subject = idea.strip()
    original = source_text.strip()
    if not subject and not original:
        raise ValueError("Sujet ou texte source requis.")
    if original:
        text = original
        source = "USER_SOURCE_TEXT_ONLY"
        warning = "Texte utilisateur conservé sans génération IA. Vérification humaine requise."
    else:
        # A framing worksheet, NOT invented project claims or AI synthesis.
        text = (
            f"{subject}\n\n"
            "Ce sujet mérite une explication factuelle avant publication.\n\n"
            "[Contexte vérifiable à renseigner]\n\n"
            "[Ce qui a réellement été réalisé et sa source]\n\n"
            "[Limites, éléments non démontrés ou prochaines étapes]\n\n"
            "Quelle question souhaitez-vous approfondir ?"
        )
        source = "STUDIO_DETERMINISTIC_TEMPLATE"
        warning = "Trame locale non générée par Brody ni Qwen : compléter les preuves avant publication."
    return {
        "text": text,
        "warning": warning,
        "provenance": {
            "source": source,
            "network": network,
            "brody_post_model_synthesis_proven": False,
            "qwen_evidence_applied": False,
            "human_approval_required": True,
            "publication_permitted": False,
            "cognitive_gate": "NOT_CALLED",
        },
    }
