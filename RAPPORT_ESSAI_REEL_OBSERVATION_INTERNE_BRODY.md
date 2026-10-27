# Essai réel — Observation interne Oracle via Studio → Brody

Date : 26 octobre 2026. Essai cognitif unique autorisé ; aucune publication.

## Résultat

**REAL_OBSERVATION_TRIAL=PASS** pour le parcours natif et son admission Studio. Pas de GREEN global de la stack.

| Contrôle | Observation réelle |
|---|---|
| BRODY_HTTP_STATUS | 200 |
| STUDIO_HTTP_STATUS | 200 |
| LATENCE_HTTP_STUDIO | 14.031 secondes |
| LATENCE_HTTP_BRODY | 7.572 secondes, mesure ASGI côté serveur |
| EDITORIAL_VERSION | V1, choix explicite conforme au défaut préservé |
| NATIVE_AUTHORSHIP_VERIFIED | YES — BRODY_NATIVE_INTERNAL_OBSERVATION_V1 |
| POST_ARTIFACT_PRESENT | YES — BRODY_PUBLIC_INTERNAL_OBSERVATION_ARTIFACT_V1 |
| OBSERVED_DEPENDENCY_VERIFIED | YES — VERIFIED_INTERNAL_OBSERVATION |
| PROVENANCE_VERIFIED | YES — revalidation locale par Studio |
| VALIDATED_CAUSAL_PROOF | false |
| HUMAN_REVIEW_REQUIRED | true ; aucune approbation humaine fabriquée |
| PUBLICATION_PERMITTED | false |
| MEMORY_STATUS | MEMORY_WRITE_HOLD |
| MODEL_CALLS | 0 ; Qwen non utilisé |
| POST_STUDIO / POST_BRODY | exactement 1 / 1, confirmés par access logs |
| RETRY / FALLBACK | 0 / 0 |

## Texte intégral reçu, sans réécriture

Dans cet essai à horloge fixe, les données ont un âge de 301 secondes.

Le composant avec un seuil de 302 secondes retourne ALLOW, tandis que le composant avec un seuil de 300 secondes retourne HOLD.

Cette observation porte uniquement sur ces deux exécutions de la version vérifiée.

`DRAFT.txt` contient les octets UTF-8 reçus dans l’artefact. Le texte présenté par Studio est identique au texte natif (`studio_text_equals_native_draft=true`). Il reste un brouillon consultatif soumis à examen humain, pas une publication autorisée.

## Provenance et portée

- Identifiant serveur : `oracle-two-thresholds-v1`.
- Observation : `297e4e5691d4b5f98962b143635b7a7995d38aa92cf11089e3b677736ad91afd`.
- Code de base : `cbad01257c027e5861a1c0610d418dfd02fc8342` ; overlay de développement épinglé `72809eb3528e74f6a027cda50aebdb2c4b83974e`.
- Manifeste : `e017a794b73c57688841ab4b2bc168d3765f0585e9d5ebb853602a9d442d4ddc` ; **1537 fichiers conformes avant et après l’essai**.
- Catalogue lu depuis les preuves Oracle réellement acquises et leurs pins, vérifié avant l’ouverture du port. Source, test, trace, résultat JUnit, entrées, horloge fixe et sorties ont été contrôlés par l’adaptateur interne existant.
- Relation : `OBSERVED_DEPENDENCY`, portée `oracle_freshness:fixed_clock:two_thresholds`, âge 301 secondes, seuils 302/300, résultats logiciels ALLOW/HOLD.
- Quatre propositions sélectionnées, trois étapes de plan et trois phrases avec réalisation/provenance natives. Studio a recomputé le plan, les propositions, les réalisations et les preuves ; l’audit amont conserve le digest de l’artefact, pas un reçu complet.
- Empreinte de l’artefact public : `43591c76c3f0608871a83f31fc219d11f2b2ba48fc1d4ce13712176d3b61522a`.
- Aucune preuve causale générale ni attestation B8 indépendante revendiquée.

Le ticket C1 observé reste `ALLOW_CONTEXT_ONLY`, reçu `REAL_COGNITIVE_JOIN_C1_V1`, complétude `DEGRADED`. E11 reste `CONTEXT_LIMITED`, mémoire `MEMORY_NOT_REQUIRED`, inconnues conservées : 3. Les limites B6/E11 et les surfaces indisponibles ne sont pas effacées. Le HOLD cité dans l’explication est la sortie du mécanisme Oracle ; il n’est pas une autorisation ni un refus de gouvernance à contourner.

Les raisons de refus de l’artefact réel sont vides. Les scénarios négatifs ne sont pas rejoués en HTTP : leur couverture reste celle des 212 tests d’admission inclus dans la régression hors réseau précédente (761 PASS + 17 sous-tests PASS). Les dix FAIL producteurs historiques restent séparés et n’ont pas été réexécutés.

## Lancement autonome et authentification

Les ports 8000 et 8108 étaient libres ; aucun processus préexistant n’a été arrêté. Deux services seulement ont été lancés, sans reload ni nouveau modèle :

- Brody : PID **47432**, `127.0.0.1:8000`, Python autonome existant 3.13.3, cwd copie `producer_cbad0125/source` sous Studio. Le bootstrap local `serve_brody.py` vérifie puis injecte uniquement la référence Oracle typée dans le catalogue existant avant de charger l’app publique.
- Studio : PID **32060**, `127.0.0.1:8108`, Python 3.13 existant, `uvicorn server:app`, cwd Studio.

Les commandes, heures de création, répertoires, chemins Python et origines des modules sont enregistrés dans `service_start_report.json` et `brody_startup.json`. Les modules producteurs contrôlés proviennent de la copie épinglée ; aucun dépôt producteur n’est modifié.

La clé existante DPAPI a été réutilisée sans affichage, argument de commande ou journalisation. Brody refuse `/openapi.json` sans clé (401), l’autorise avec la clé (200), et renvoie 405 sur GET authentifié `/api/brody/chat` ; aucun POST de contrôle direct n’a été envoyé à Brody. Le vrai POST Studio a réutilisé `X-API-Key` et obtenu 200. Studio est le service local loopback existant, sans garde globale de clé entrante ; cette limite n’est pas présentée comme une authentification utilisateur. Aucun contrôle d’accès n’a été désactivé.

## Ledger : anomalie du runner et vérification conservée

Le résultat brut `result.json` reste **HOLD_POST_CHECK / SESSION_TRACE_MEMORY_BOUNDARY**. Ce HOLD appartient au contrôle du runner, pas à KX108 ou au producteur. Il a exigé `memory_write=false` directement dans un record de ledger alors que ce champ ne fait pas partie de son schéma canonique. Son absence n’a pas été remplacée par false.

La relecture ciblée du schéma et du record existants a vérifié les vrais champs : `readonly=true`, `memory_decision=false`, `memory_intake=false`, `graphiti_index_write=false`, `auto_triage=false`, `memory_intake_status=TRACE_ONLY_NOT_INDEXED`, `emits_act=false`, `kernel_mutation=false`, `decision_authority=KX108_ONLY`. Le hash de l’événement, la ligne JSONL et l’index de session concordent. Ces preuves sont dans `POSTCHECK_RECONCILIATION.json`, qui référence le SHA du résultat brut sans le modifier.

Un seul nouveau record de session est observé (JSON et Markdown), dans le ledger existant de la copie Studio ; l’index et le JSONL de cette session ont été actualisés par le mécanisme existant. Ce sont les traces explicitement autorisées, sans promotion canonique ou B8. Aucun deuxième appel ni changement de décision cognitive n’a été utilisé pour lever le diagnostic.

Deux détails des scripts de diagnostic ont également été corrigés sans action sur les services : prise en charge du BOM UTF-8 du source ledger et du `ensure_ascii=false` de sa sérialisation canonique ; comparaison des créations de processus en ticks UTC, car PowerShell désérialise les chaînes ISO en objets datetime. Ils ne modifient ni les contrats ni le résultat HTTP original.

## État final et limites

- Deux services opérationnels, mêmes PID et commandes au contrôle final ; laissés en fonctionnement à la demande de l’utilisateur.
- LOT1=0 réellement observé dans l’environnement Studio ; autopilot désactivé, configuration inchangée.
- KX108_ONLY et MEMORY_WRITE_HOLD conservés ; mémoire Native canonique non promue par ce parcours.
- Code Studio et 1537 fichiers déployés inchangés après l’essai ; brouillons et images existants inchangés.
- Aucune publication, aucun commit/push, aucun transfert ou changement producteur, aucune modification kernel/C273/C274/B8.
- Le bootstrap d’audit ASGI résume la réponse réelle sans la modifier. Aucun reçu intégral, extrait mémoire ou clé n’est ajouté aux rapports ; le ledger de session conserve ses propres traces conformément à l’autorisation utilisateur.
- La vérification de non-promotion repose sur les frontières du parcours audité, les reçus, les champs du ledger et les fichiers observés ; elle n’est pas présentée comme un audit système exhaustif de tous les stockages externes.

| État | Constat |
|---|---|
| FAIT | Deux services lancés, catalogue Oracle configuré, exactement un POST Studio et un POST Brody. |
| PROUVÉ | HTTP 200/200, artefact natif admis, provenance recomputée, validation humaine requise, publication interdite, trace canonique conforme. |
| INCERTAIN | Aucune causalité générale ni correction factuelle externe déduite de cet essai logiciel borné. |
| RESTANT | Évaluation humaine du brouillon ; anomalie du post-check conservée pour une correction ultérieure du runner, aucun nouvel essai automatique. |

STOP — KX108_ONLY / OBSERVED_DEPENDENCY / MEMORY_WRITE_HOLD / HUMAN_REVIEW_REQUIRED / NO_PUBLICATION.
