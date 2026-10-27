# Studio — Essai réel service client V1 / V2

27 octobre 2026 — RUNTIME CONTROLLED TEST — NON_FREEZE.
KX108_ONLY — BRODY_NATIVE_AUTHOR — MEMORY_WRITE_HOLD — HUMAN_REVIEW_REQUIRED.

## Résultats réels

| Champ | V1 | V2 |
|---|---|---|
| SERVICE_CLIENT_HTTP | PASS | PASS |
| BRODY_HTTP_STATUS | 200 | 200 |
| STUDIO_HTTP_STATUS | 200 | 200 |
| LATENCY, aller-retour HTTP Studio | 5.349 s | 5.109 s |
| Sélection | Champ version absent : défaut V1 exercé | `editorial_version=V2` explicite |
| NATIVE_PROVENANCE | BRODY_NATIVE_EDITORIAL_V1, lineage_verified=true | BRODY_NATIVE_EDITORIAL_V2, lineage_verified=true |
| HUMAN_REVIEW_REQUIRED | true, politique Studio obligatoire | true, également explicite dans le contrat producteur V2 |
| PUBLICATION_PERMITTED | false | false |
| Qwen rédacteur / model_calls | aucun / 0 | aucun / 0 |
| Texte identique à la composition hors réseau | oui | oui |
| Retry / fallback | 0 / 0 | 0 / 0 |

**Deux POST Studio → deux POST Brody**, séquentiels, un par version, confirmés dans les journaux d’accès et résumés amont. Aucun autre essai cognitif ni appel direct supplémentaire à Brody. Aucun résultat n’a été retouché après génération.

Brief exact réutilisé depuis la preuve d’admission hors réseau : « Rédige une publication LinkedIn expliquant Comment une petite entreprise peut utiliser l'IA pour améliorer son service client sans perdre le contact humain ? ».

## V1 — texte intégral reçu

Une petite entreprise utiliserait l'IA pour améliorer son service client.

Une petite entreprise viserait à ne pas perdre le contact humain, examinerait son service client et vérifierait les limites de cet essai.

Un premier essai porterait sur son service client.

Une petite entreprise comparerait les résultats de cet essai avec l’objectif retenu.

## V2 — texte intégral reçu

Est-ce qu'une petite entreprise peut aider à améliorer son service client ?

Une petite entreprise utiliserait l'IA pour améliorer son service client. Une petite entreprise viserait à ne pas perdre le contact humain, examinerait son service client et vérifierait les limites de cet essai.

Par exemple, un premier essai porterait sur son service client.

Avant de poursuivre, une petite entreprise comparerait les résultats de cet essai avec l’objectif retenu.

Les textes sont des propositions consultatives natives : ils ne deviennent pas des faits établis ou une publication approuvée. Le conditionnel, les limites de formulation et le possesseur non résolu restent conservés ; leur acceptation n’est pas une résolution factuelle de ces incertitudes. Évaluation rédactionnelle finale humaine.

## Services et chargement effectif

- Brody existant **PID 47432**, `127.0.0.1:8000`, conservé sans redémarrage. Commande/cwd/Python et création concordent avec le lancement identifié du 26 octobre. Aucun changement du bootstrap, du compositeur ou des contrats producteurs.
- Studio antérieur PID 32060 rechargé une seule fois, nouveau **PID 7092**, `127.0.0.1:8108`. Pas de processus enfant de travail ni connexion active Studio observés au précontrôle.
- Validation chargée depuis la source actuelle, avec un préfixe de cache neuf et `-B`. La trace d’import contient `# code object from .../studio_native_editorial.py` ; aucun cache n’a été créé. L’empreinte du validateur est celle de la livraison ayant passé les tests hors réseau.
- Authentification Brody conservée : OpenAPI sans clé 401, avec la clé existante 200. Les POST réels acceptés démontrent le lien sortant Studio → Brody authentifié. Clé DPAPI transmise uniquement en environnement, jamais affichée ou passée en argument.
- Studio reste l’interface loopback existante, sans garde globale de clé entrante ; aucune authentification utilisateur nouvelle n’est revendiquée.
- LOT1=0 observé dans l’environnement du nouveau processus ; autopilot.enabled=false, configuration inchangée. V1 demeure le défaut OpenAPI avant et après préparation ; V2 est un opt-in.
- Contrôles finaux : deux services opérationnels, mêmes identités après les essais, laissés en fonctionnement.

## Contrats, provenance et reçus

La validation Studio exige et recompute le sujet IR, les propositions, le plan, la réalisation grammaticale/True Voice, les composants de provenance et les inconnues. Les deux réponses ont été admises par ce validateur actuel sans transformation d’une réponse B6 en POST.

V1 : schéma public `BRODY_PUBLIC_EDITORIAL_ARTIFACT_V1`. Le contrat n’y répète pas les propositions complètes ni le flag producteur de revue humaine de V2 ; leur disponibilité dans le snapshot et la revue imposée par Studio ne sont pas remplacées par une valeur productrice inventée. V2 : schéma `BRODY_PUBLIC_EDITORIAL_ARTIFACT_V2`, sélection explicite et champs de réalisation/propositions/revue requis.

Le compteur résumé de propositions dans l’artefact amont V1 ne doit pas être assimilé à une absence de sélection : V1 expose des identifiants et le snapshot vérifié, V2 répète la liste complète. Les exigences du validateur ont effectivement été exécutées dans les deux versions.

- Reçus Studio complets tels que retournés par son API (texte, POST natif et provenance minimale) : `STUDIO_RECEIPT_V1.json`, `STUDIO_RECEIPT_V2.json`.
- Résumés de l’artefact et du receipt cognitif effectivement envoyés par Brody : `BRODY_RECEIPT_SUMMARY_V1.json`, `BRODY_RECEIPT_SUMMARY_V2.json` ; capturés par le bootstrap ASGI existant sans modifier les réponses.
- Résultats détaillés : `RESULT_V1.json`, `RESULT_V2.json`, `results.json`, `OVERALL_RESULT.json` ; textes UTF-8 exacts : `DRAFT_V1.txt`, `DRAFT_V2.txt`.
- Aucune deuxième récupération du reçu ou de la mémoire depuis Studio. Le reçu cognitif complet et les contenus mémoire ne sont pas dupliqués dans les rapports ; le contrat Studio retourne une provenance minimale et sa validation obligatoire sert de preuve d’admission.

Les statuts E11/B6 limités et les inconnues restent visibles dans les métadonnées :

| Diagnostic | V1 | V2 |
|---|---|---|
| E11 consumer_status | CONTEXT_LIMITED | CONTEXT_LIMITED |
| Mémoire | MEMORY_NOT_REQUIRED | MEMORY_NOT_REQUIRED |
| Inconnues/incertitudes conservées | 3 | 3 |
| Ticket C1 | ALLOW_CONTEXT_ONLY | ALLOW_CONTEXT_ONLY |
| Complétude C1 | DEGRADED | DEGRADED |
| Refus amont de l’artefact | aucun | aucun |

`CONTEXT_LIMITED` et `MEMORY_NOT_REQUIRED` ne sont pas des preuves de vérité ; ils ne sont ni supprimés ni requalifiés. Cet essai ne concerne pas Oracle et ne revendique aucune preuve causale générale.

## Traces autorisées et mémoire

Le mécanisme existant Session ledger (always) a ajouté un record de session par essai, JSON/Markdown, avec actualisation du ledger JSONL et de son index. Les deux événements sont liés au brief exact, au précédent hash et aux séquences attendues ; leurs empreintes et frontières canoniques sont vérifiées en réutilisant les fonctions pures du ledger et le post-contrôle déjà corrigé.

Statuts explicites : `TRACE_ONLY_NOT_INDEXED`, `memory_intake=false`, `graphiti_index_write=false`, `auto_triage=false`, `readonly=true`, `memory_decision=false`, KX108_ONLY. Aucun champ absent `memory_write` n’est interprété comme false dans un record. La frontière de l’artefact Brody expose, elle, `memory_write=false` et `MEMORY_WRITE_HOLD`.

Les records de session peuvent contenir la réponse intermédiaire avant exposition éditoriale finale : ils accompagnent l’essai, mais leur texte ne remplace pas la preuve de composition native fournie par le snapshot/validateur et le reçu public final. Aucune promotion canonique ou mutation B8 n’est autorisée par ces traces.

## Empreintes et régression

- **1537 empreintes conformes avant/après**, manifeste `e017a794b73c57688841ab4b2bc168d3765f0585e9d5ebb853602a9d442d4ddc`, base `cbad01257c027e5861a1c0610d418dfd02fc8342` et overlay `72809eb3528e74f6a027cda50aebdb2c4b83974e` inchangés.
- Aucun fichier applicatif Studio modifié pendant les essais. Aucun transfert producteur, changement du compositeur, de KX108/C273/C274/B8 ou de contrat.
- Brouillons et images existants inchangés. Seules les quatre nouvelles traces de record JSON/Markdown sont ajoutées sous la copie source ; les fichiers d’index/ledger de session existants sont actualisés conformément à l’autorisation de trace.
- Les anciens JSON de preuve du bootstrap restent identiques. Ses journaux actifs sont appendus pour les nouveaux GET/POST ; leurs préfixes historiques ont été vérifiés inchangés, sans écraser les lignes anciennes.
- **REGRESSION_STATUS=1028 PASS + 17 sous-tests PASS, référence hors réseau réutilisée**, non réexécutée pendant cette passe sans changement applicatif. Les 197 tests ciblés, Oracle et les brouillons historiques sont couverts par cette référence ; aucun nouvel essai Oracle.
- Les dix FAIL producteurs historiques restent séparés ; aucun GREEN global annoncé.

## Anomalie de préparation conservée

Le premier précontrôle (`service_report.json`) s’est arrêté avant rechargement et avant toute requête cognitive : `Get-FileHash` ne pouvait pas ouvrir les journaux actifs de Brody avec son partage par défaut. Un script distinct (`resume_reload_studio.ps1`) emploie une lecture explicitement partagée sans fermer les journaux ou modifier Brody. `service_report_recovery.json` conserve la préparation réussie. Il ne s’agit pas d’un retry cognitif ; les compteurs HTTP sont exactement ceux autorisés.

## État final

| FAIT | PROUVÉ | INCERTAIN | RESTANT |
|---|---|---|---|
| Studio rechargé ; deux essais effectués | 200/200 V1/V2, provenance native, textes conservés, publication interdite, protections et empreintes conformes | La qualité générale et la couverture d’autres sujets ne découlent pas de ces deux succès | Évaluation humaine des textes ; aucune autre campagne automatique |

Services laissés opérationnels, LOT1 et autopilot désactivés. Aucun retry, fallback, publication, commit, push, merge ou reset.

STOP — KX108_ONLY / MEMORY_WRITE_HOLD / HUMAN_REVIEW_REQUIRED / BRODY_NATIVE_AUTHOR / NON_FREEZE.
