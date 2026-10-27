# Studio — Admission des observations internes Brody

Validation finale : 26 octobre 2026. Mode RESUME / validation uniquement.

## Verdicts

| Champ | Résultat |
|---|---|
| STUDIO_OBSERVATION_CONTRACT_SUPPORTED | YES — V1/V2, normal/compact |
| VERIFIED_INTERNAL_OBSERVATION_ACCEPTED | YES — cas Oracle avec preuves locales épinglées et rejeu |
| UNVERIFIED_OBSERVATION_REJECTED | YES — preuves absentes/altérées et mutations de contrat refusées |
| V1_V2_BASELINES_PRESERVED | YES — brouillons identiques octet pour octet, rapports HTTP conservés |
| PROVENANCE_VERIFIED | YES — observation, source, test, trace, JUnit, propositions et phrases |
| REGRESSION_RESULTS | 761 PASS + 17 sous-tests PASS ; 0 FAIL / 0 ERROR |
| READY_FOR_ONE_REAL_TRIAL | HOLD_RUNTIME_PREPARATION — admission hors réseau prête, services/catalogue non chargés ni vérifiés dans cette passe |

Aucun GREEN global : les dix FAIL producteurs historiques restent une référence distincte, non réexécutée sur le nouveau HEAD producteur.

## Reprise et résultats exacts

La régression complète post-correction s’était terminée le 24 octobre à 17:55, malgré l’interruption visible du run. `studio_full.log` indique **761 passed, 17 subtests passed in 125.11s**. Le JUnit contient 761 éléments testcase et un compteur de 778 incluant les 17 sous-tests ; aucun échec, erreur ou skip. Elle comprend **212 tests d’admission des observations internes**. Aucun fichier Python racine n’a été modifié depuis ce résultat ; cette exécution terminée a été conservée, sans duplication.

La validation réellement manquante a été exécutée maintenant avec les scripts préparés :

- `prepare_actual_validation.py`, puis `actual_validation.py` ; aucun fichier moteur modifié pour cette reprise.
- Python : `C:\Users\User\.codex\visualizations\2026\10\16\01a14555-4da0-79f3-a5bc-76c3d8477dc6\passe10d\isolated_aba5e8bb\python_runtime\python.exe` ; version 3.13.3.
- **8 admissions PASS** : observations V1/V2 normales/compactes et brouillons éditoriaux ordinaires V1/V2 normaux/compacts.
- `actual_validation.log` : `ACTUAL_PYTHON_VALIDATION_8_PASS`.
- Garde : 0 tentative réseau, 0 subprocess, 0 tentative d’écriture hors artefacts ; 8 connexions SQLite en lecture seule, aucune mémoire canonique écrite.
- Acquisition Oracle antérieure conservée : **1 PASS**, `capture.xml` et ses octets épinglés inchangés ; aucune nouvelle acquisition.
- Les huit réponses publiques ont été produites précédemment par appels Python hors réseau du responder. Aucun POST HTTP, modèle externe ou publication dans cette passe.

## Corrections confrontées au contrat réel

1. **Grammaire sérialisée** : le contrat HTTP utilise JSON, donc les tuples de la représentation Python deviennent des listes. La comparaison emploie le digest JSON déterministe du compositeur existant sur l’intégralité de la grammaire ; aucun champ n’est retiré ni normalisé sémantiquement pour faire réussir le test.
2. **V2 explicite** : le responder expose `editorial_version_requested=V2`, la version V2 dans le snapshot, et `selection_provenance` dans l’artefact ; il n’expose pas systématiquement un champ racine `editorial_version_selected`. Studio exige les champs réellement présents et refuse toute version contradictoire si ce champ optionnel existe. La version demandée reste un paramètre explicite de l’appel Studio, jamais déduite de la réponse.

Les deux échecs du premier passage ciblé (`targeted_first.log` : 368 PASS / 2 FAIL) appartiennent à l’ancienne assertion V2. Le code corrigé est couvert par la régression complète post-correction et par les huit admissions du Python Brody. Les refus n’ont pas été assouplis.

## Frontière d’admission

`server.GenIn.internal_observation_id` et `studio_ai.generate(..., internal_observation_id=...)` ne transmettent qu’un identifiant opaque. Les champs de preuve/référence/vérification/catalogue fournis par le client sont refusés. L’absence de sélection explicite ne permet pas l’admission implicite d’une observation.

Le catalogue local `TRUSTED_OBSERVATIONS.json` est épinglé par SHA dans `studio_internal_observation.py`. Ses références sont limitées à des fichiers sous Studio, liées à l’empreinte exacte du brief. Studio recharge le reçu conservé, vérifie code, test, JUnit, trace et empreintes, puis réexécute le mécanisme Oracle pur à horloge fixe via le vérificateur interne existant. Les données et la vérification reçues de Brody doivent correspondre à cette reconstruction et à sa projection publique.

Les propositions, le plan, la réalisation, les phrases, leurs opérations et leur provenance sont recomputés depuis les composants déployés, en modules privés. Aucun Router, SENS, récupération mémoire, modèle ou démarrage applicatif n’est exécuté par le validateur Studio. La vue publique est distinguée des octets originaux : le SHA du reçu identifie le reçu conservé, pas le dictionnaire projeté.

Les variantes V1/V2 exigent `validated_causal_proof=false`, validation humaine obligatoire, publication interdite, `MEMORY_WRITE_HOLD` et KX108_ONLY. Le HOLD produit par l’Oracle constitue un résultat logiciel cité, et ne remplace jamais une décision de gouvernance HOLD/BLOCK.

Refus vérifiés : empreinte altérée, sortie falsifiée, preuves absentes/altérées, portée ou brief incompatibles, contradiction, généralisation causale abusive, HOLD/BLOCK, substitution Qwen, provenance manquante, artefact/version inconnus, plan ou réalisation modifiés, retrait des inconnues, publication autorisée, absence de validation humaine et mémoire écrivable.

Les limites E11 restent visibles : `CONTEXT_LIMITED`, `MEMORY_NOT_REQUIRED`, inconnues, demandes non résolues et reçu dégradé ne sont pas transformés en succès factuel.

## Déploiement et préservation

- Checkpoint d’origine conservé : `cbad01257c027e5861a1c0610d418dfd02fc8342`.
- Overlay déployé : `72809eb3528e74f6a027cda50aebdb2c4b83974e` et huit empreintes WIP épinglées ; ce n’est pas une revendication de checkout propre ou de commit de livraison.
- Manifeste : `e017a794b73c57688841ab4b2bc168d3765f0585e9d5ebb853602a9d442d4ddc`.
- **1 537 fichiers vérifiés**, zéro écart ; tailles, unicité des chemins, SHA du manifeste, sidecar et index de preuves contrôlés.
- Les huit fichiers transférés lors de l’intégration restent exactement conformes à `transfer.json`. Aucun nouveau transfert lors de cette reprise.
- Baselines V1/V2 et configuration autopilot inchangées ; autopilot désactivé. Aucun changement de configuration LOT1 ni de service.
- HEAD producteur observé maintenant : `5ae7f49021e2180d51a8285d280c5876a34bc57f` ; auparavant `72809eb3528e74f6a027cda50aebdb2c4b83974e`. HEAD/WIP ont évolué concurremment, mais aucune des huit empreintes productrices surveillées n’a changé. Ce delta global n’est pas audité ici. Aucun fichier producteur n’a été écrit par cette passe.
- Aucun changement moteur Studio pendant la reprise : seulement scripts, résultats et rapport de validation.

Fichiers de l’intégration précédente conservés : `studio_internal_observation.py` ajouté ; `studio_native_editorial.py`, `studio_ai.py`, `server.py`, `studio_e11_deployment.py` adaptés ; tests d’admission et fixtures mis à jour ; copie servie et manifestes actualisés exclusivement sous Studio. Le détail des huit chemins déployés et de leurs empreintes est dans `transfer.json`, et les originaux dans `before/`.

## Référence productrice distincte

Dernière régression productrice conservée au 24 octobre : **514 PASS / 10 FAIL / 0 ERROR**, 524 tests. Elle ne décrit pas automatiquement le nouveau HEAD du 26 octobre. Aucun test producteur n’a été relancé durant cette reprise.

- `tests.test_language_flow_projection::test_same_object_can_participate_in_temporal_epistemic_and_governance_flows`
- `tests.integration_cognition.test_brody_public_editorial_v2_opt_in::test_current_studio_still_accepts_its_pinned_v1_and_rejects_new_producer_identity`
- `tests.test_semantic_grammar_regressions::test_passive_under_modal`
- `tests.test_semantic_grammar_regressions::test_infinitive_under_unrecognized_governor_is_embedded`
- `tests.test_semantic_grammar_regressions::test_substring_is_not_a_verb`
- `tests.test_semantic_grammar_regressions::test_negated_belief_keeps_embedded_event_positive`
- `tests.test_semantic_grammar_regressions::test_requests_in_disguise_hold[essaie de lancer le script]`
- `tests.test_semantic_lattice_primitives::test_connection_kinds_from_language`
- `tests.integration_cognition.test_brody_native_linguistic_ownership_red::test_r8_b6_and_b7_advisory_context_retains_priority`
- `tests.integration_cognition.test_native_editorial_capacity_required::test_level_c_original_brody_draft_and_studio_artifact`

## Explication native admise

Dans cet essai à horloge fixe, les données ont un âge de 301 secondes.

Le composant avec un seuil de 302 secondes retourne ALLOW, tandis que le composant avec un seuil de 300 secondes retourne HOLD.

Cette observation porte uniquement sur ces deux exécutions de la version vérifiée.

Cette explication décrit seulement deux exécutions locales de la version épinglée : âge 301 secondes, seuils 302/300, horloge fixe, sorties ALLOW/HOLD. Elle ne prouve ni causalité générale, ni pertinence universelle des seuils, ni qualité de données externes ; aucune attestation indépendante B8 n’est revendiquée.

## Condition du prochain essai réel

L’admission hors réseau est prête. Le runtime Brody conserve un catalogue d’observations **vide par défaut** ; le test hors réseau l’avait injecté temporairement puis retiré. Les services n’ont été ni démarrés, ni redémarrés, ni sondés dans cette validation.

Avant tout essai réel, une prochaine passe devra charger de manière contrôlée la copie épinglée et le catalogue serveur de confiance, vérifier authentification, origines de code et empreintes des services, tout en gardant LOT1/autopilot désactivés et la mémoire en HOLD. La simple présence d’un catalogue côté consommateur ne configure pas le serveur.

L’essai futur utilisera uniquement l’identifiant `oracle-two-thresholds-v1`, la version explicitement choisie et le brief exact déjà lié aux preuves : « Rédige une publication LinkedIn expliquant comment le seuil peut modifier le résultat. ». Une reformulation ne doit pas être reliée silencieusement à la preuve existante. Aucun POST n’est exécuté ni implicitement autorisé par ce rapport.

| État | Constat |
|---|---|
| FAIT | Reprise sans transfert ni changement moteur ; contrôle Python Brody manquant exécuté et rapport produit. |
| PROUVÉ | Régression 761 PASS + 17 sous-tests, 212 tests observation inclus, huit admissions Python, 1537 empreintes et baselines conformes. |
| INCERTAIN | Identité/code effectivement chargés et catalogue des services non contrôlés ; aucune preuve causale générale. |
| RESTANT | Chargement runtime contrôlé et vérifications techniques avant un éventuel essai HTTP unique ; dix FAIL producteurs historiques distincts. |

STOP — KX108_ONLY / OBSERVED_DEPENDENCY / BRODY_NATIVE_AUTHOR / HUMAN_REVIEW_REQUIRED / MEMORY_WRITE_HOLD.
