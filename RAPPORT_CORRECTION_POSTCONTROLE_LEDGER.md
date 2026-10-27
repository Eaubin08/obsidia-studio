# Correction ciblée — Post-contrôle du ledger Oracle

Date : 26 octobre 2026. Mode APPLY, STUDIO / VALIDATION / TRACE, risque LOW.

## Verdicts

| Champ | Résultat |
|---|---|
| LEDGER_SCHEMA_IDENTIFIED | YES — BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_RECORD |
| FALSE_HOLD_CAUSE | Exigence erronée de `memory_write=false` dans le record ; ce champ n’y est pas défini |
| RUNNER_CORRECTED | YES — post-contrôle versionné, autonome et strictement hors réseau |
| CANONICAL_TRACE_VERIFIED | YES — trace réelle, index, JSONL, session, empreintes et preuve E2E concordants |
| MEMORY_PROMOTION_REJECTED | YES — indicateurs vrais, manquants ou non booléens refusés |
| NEGATIVE_GATES_PASS | YES — 70 tests ciblés PASS |
| REGRESSION_RESULTS | 831 PASS + 17 sous-tests PASS ; 0 FAIL / 0 ERROR |
| E2E_EVIDENCE_UNCHANGED | YES — 65 fichiers originaux surveillés inchangés, empreintes et rapports conservés |

Aucun nouveau résultat cognitif, aucun changement d’autorité, aucune approbation humaine créée. Aucun GREEN global de la stack déduit de ces tests Studio ; les FAIL producteurs historiques ne sont pas réexécutés.

## Cause et schéma réellement inspectés

Dans `apps/obsidia_api/brody_automation_orchestrator.py`, `run_brody_automation_layer()` appelle toujours `_run_session_ledger()` (« Session ledger (always) »). Le résumé retourné par l’orchestrateur contient `memory_write=false`. Le record construit par `periphery/brody_memory_readonly/session_memory_ledger_readonly/brody_session_memory_ledger_readonly_v2.py::build_record()` possède un contrat distinct, sans ce champ.

Ses preuves explicites sont : `readonly=true`, `response_only=true`, `memory_decision=false`, `memory_intake=false`, `graphiti_index_write=false`, `auto_triage=false`, `memory_intake_status=TRACE_ONLY_NOT_INDEXED`, `triage_status=NOT_APPLIED_NEXT_PALIER`, ainsi que les frontières kernel/action/autorité de `BOUNDARY`.

L’ancien runner appliquait `record.get('memory_write') is False`. Un champ absent donnait None et déclenchait le faux `SESSION_TRACE_MEMORY_BOUNDARY`, alors que le record canonique était complet. Le nouveau validateur n’invente pas une valeur pour ce champ : il le classe **NOT_DEFINED_NOT_DEFAULTED**, et exige tous les indicateurs canoniques explicites. S’il est néanmoins présent, `memory_write` doit être exactement false ; aucune conversion de 0, chaîne ou null n’est admise.

Le schéma BOUNDARY et les fonctions pures `canonical_json()` / `sha256_text()` sont lus depuis le source déployé épinglé et réutilisés par sélection AST, sans exécuter le module ledger ni ses fonctions d’écriture. Aucun changement du format producteur.

## Correction et fichiers

- `data/experiments/ledger_postcheck_20261026/ledger_postcheck.py` : validateur pur PASS/HOLD ; intégrité, identité de session, séquence, lien précédent, référence de fichier, index, JSONL et provenance E2E. Aucun réseau, processus, mémoire ou écriture.
- `data/experiments/ledger_postcheck_20261026/replay_postcheck.py` : **point d’entrée corrigé** du post-contrôle, qui relit uniquement les traces existantes. Il ne peut pas envoyer de POST, importer l’ancien runner HTTP, démarrer un service ou réécrire un résultat cognitif.
- `test_studio_ledger_postcheck.py` : 70 tests nouveaux ; mutations conservées exclusivement en mémoire.
- `EXPECTED_TRACE.json`, scripts de validation, snapshots et rapports sont ajoutés dans le même dossier Studio. Le SHA de la référence est épinglé dans le runner ; aucune référence transmise par client n’est admise.

Le runner HTTP original `internal_observation_real_trial_20261026/one_trial.py` reste archivé **octet pour octet**, car il appartient au paquet de preuve E2E. Il n’est ni rejoué ni corrigé sur place. Son post-contrôle est remplacé, pour cette validation, par le point d’entrée versionné ci-dessus. Le fichier `result.json` conserve `HOLD_POST_CHECK` et le rapport historique reste inchangé. Le résultat corrigé est écrit uniquement dans **POSTCHECK_CORRECTED.json : PASS / CANONICAL_TRACE_ONLY_VERIFIED**.

## Tests réellement exécutés

- Relecture hors réseau du record réel : PASS ; aucun nouveau record ni appel Brody.
- Suite ciblée : **70 PASS**, `targeted.log` / `targeted.xml`.
- Régression Studio/E11 complète : **831 PASS + 17 sous-tests PASS**, `regression.log` / `studio_regression.xml`.
- Garde de test : 0 tentative réseau, 0 subprocess, 0 tentative d’écriture hors des nouveaux artefacts. Les tests n’importent pas le ledger applicatif et n’appellent aucun writer.

Cas couverts :

- record canonique sans le champ historique : PASS ; variante synthétique avec champ explicitement false et frontière complète : PASS ;
- promotion mémoire ou mutation activée : HOLD, même avec empreintes et index synthétiques cohérents ;
- indicateur canonique requis absent : HOLD ; aucune valeur absente n’est interprétée comme false ;
- champs mal typés, record incomplet, statut inconnu, session/séquence discordantes : HOLD ;
- altération ou absence de record/index/JSONL/source/E2E, provenance invalide, duplication JSON et liens incohérents : HOLD ;
- publication autorisée, validation humaine fausse ou absente, Qwen attribué auteur, preuve causale générale, ticket HOLD/BLOCK : HOLD ;
- conservation des fichiers et rapports originaux : PASS.

Pour isoler les gardes sémantiques, certains mutants sont ré-empreintés **uniquement dans les fixtures en mémoire** : cela démontre que des hashes cohérents ne suffisent pas à autoriser une promotion. Le runner réel ne ré-épingle jamais les preuves modifiées et ne fabrique aucune attestation.

## Contrôles inspectés et préservation

Les appels de l’orchestrateur et le format du ledger ont été inspectés statiquement. Aucun nouveau test runtime producteur ni test HTTP n’a été exécuté. La trace réelle est celle de l’essai précédent : HTTP 200/200, 14,031 secondes, artefact natif vérifié, `validated_causal_proof=false`, validation humaine requise et publication interdite. Ces résultats ne sont pas recalculés ou réécrits.

Les 65 empreintes protégées incluent les artefacts originaux de l’essai, le runner HTTP et ses contrôles historiques, le ledger de session existant, les rapports antérieurs et les manifestes. Zéro écart ; zéro modification des fichiers Python racine préexistants. **1537 fichiers de déploiement revérifiés**, manifeste `e017a794b73c57688841ab4b2bc168d3765f0585e9d5ebb853602a9d442d4ddc` inchangé.

Autopilot : configuration inchangée, `enabled=false`. LOT1 : valeur 0 observée dans l’environnement du processus Studio par lecture de métadonnées non sensibles, sans HTTP ou injection. Services non redémarrés et non reconfigurés. Aucun changement producteur, KX108, C273/C274, B8 ou mémoire canonique. MEMORY_WRITE_HOLD maintenu.

Le PASS signifie uniquement que cette trace correspond au contrat de journalisation de session et aux preuves E2E conservées. Il n’autorise aucune promotion mémoire, publication, action ou conclusion causale générale. Le ledger peut conserver une réponse intermédiaire antérieure à l’exposition finale : son texte n’est pas assimilé au brouillon natif final ; le lien de cette validation repose sur l’identité de session, la demande, les références épinglées et le résultat E2E observé.

## Bilan

| État | Constat |
|---|---|
| FAIT | Post-contrôle versionné corrigé et tests ajoutés, sans modifier les preuves historiques. |
| PROUVÉ | Trace canonique admise ; promotions et preuves insuffisantes refusées ; 70 tests ciblés et 831 tests + 17 sous-tests de régression PASS. |
| INCERTAIN | Aucune propriété nouvelle du moteur cognitif ou de stockages externes n’est certifiée par ce post-contrôle. |
| RESTANT | Utiliser ce validateur dans tout futur runner autorisé, au lieu de l’exigence historique erronée ; aucun nouvel essai à lancer automatiquement. |

STOP — KX108_ONLY / SESSION_LEDGER_ALLOWED / MEMORY_WRITE_HOLD / NO_PUBLICATION.
