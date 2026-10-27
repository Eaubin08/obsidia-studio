# Intégration contrôlée Brody V2 — validation hors réseau

Mode: APPLY | Layer: CONNECTORS | Risk: MEDIUM  
Périmètre : Studio et sa copie productrice seulement. KX108_ONLY, V1_DEFAULT, V2_OPT_IN, MEMORY_WRITE_HOLD, DRAFT_ONLY.

## Verdicts

- STUDIO_V1_DEFAULT_PRESERVED=YES
- STUDIO_V2_OPT_IN_AVAILABLE=YES (API `editorial_version="V2"` / client Python ; pas de nouveau sélecteur graphique)
- V2_PRODUCER_DEPLOYED=YES (copie sur disque, non rechargée dans les services)
- V2_PROVENANCE_VERIFIED=OFFLINE_LOCAL_LINEAGE
- V1_V2_REGRESSION_RESULTS=549 PASS / 0 FAIL / 0 ERROR + 17 sous-tests PASS
- READY_FOR_ONE_REAL_V2_TRIAL=YES_OFFLINE ; précontrôles et rechargement contrôlé requis avant HTTP

Aucun POST HTTP, redémarrage, publication, commit ou push. Aucune activation de V2 par défaut ni changement de configuration autopilot/LOT1.

## Fichiers et provenance du transfert

Quatre fichiers seulement, copiés depuis le WIP producteur :

- `apps/obsidia_api/brody_editorial_composition.py`
- `apps/obsidia_api/brody_true_voice_adapter.py`
- `apps/obsidia_api/brody_real_response_pipeline.py`
- `apps/obsidia_api/routes/brody.py`

Destination : `data/experiments/e11_lot1/passe10e2/producer_cbad0125/source`.
Base conservée : `cbad01257c027e5861a1c0610d418dfd02fc8342`. Origine du nouvel overlay : HEAD `b8c06be7d7f0e4b7ce3b60092377ccc5ea07da4c`, fichiers WIP, **non présentés comme code commité à ce SHA**. Le manifeste conserve le profil historique de la famille `BRODY_NATIVE_EDITORIAL_WIP_OVERLAY_V1` et inscrit séparément la réparation `BRODY_NATIVE_EDITORIAL_V2_OPT_IN` dans son historique. Les douze autres dépendances de l’overlay sont identiques au producteur.

1 535 fichiers vérifiés ; base 1 527 ; total 592 081 954 octets. Manifeste SHA-256 : `f9fffba9a94efeb30d7a7190a6dbc488aaa65d84b6edec52cd9a5a4eeb8265a5`. Index des empreintes et compteurs vérifiés. Les sauvegardes initiales et le détail des empreintes sont dans le dossier d’expérience.

Le HEAD, l’état Git et les empreintes des quatre fichiers producteurs sont identiques entre début et fin du contrôle. Aucun changement du dépôt producteur.

## Consommateur Studio

- `server.py` : champ Literal V1/V2, V1 par défaut ; V2 transmis uniquement si explicitement choisi ; V2 + Ingress refusé avant transport.
- `studio_ai.py` : sélection fermée avant appel, conservation X-API-Key, une seule requête, aucun fallback ; version demandée transmise au validateur.
- `studio_native_editorial.py` : liaison stricte demande/réponse, schémas publics/natifs, sélection explicite, provenance, empreintes, brief, plan, propositions, réalisation, C275 et frontières factuelles. Les fonctions pures V2 sont réutilisées ; ni compose_native_editorial, ni cognition, Router, modèle ou récupération mémoire ne sont relancés par Studio pour l’admission.
- `studio_e11_deployment.py` : pin du manifeste actualisé, checkpoint de base inchangé, aucune expiration/PID/approbation ajoutée.
- `test_studio_editorial_v2.py` : 99 cas V2 et croisés V1/V2.
- `test_studio_native_editorial.py`, `test_studio_ai.py` : nouveaux artefacts de test V1 correspondant aux nouvelles empreintes, anciens reçus préservés.
- `test_brody_editorial_repair.py` : le chargeur AST du schéma utilise désormais Literal.

Les anciens reçus ne sont pas réécrits ni approuvés implicitement. Un test confirme qu’un ancien artefact aux empreintes périmées est refusé. Le texte natif V1 recalculé est identique octet pour octet au brouillon V1 de référence ; son origine reste V1. Aucun contenu Qwen/B6 n’est promu en publication.

## Exécution et résultats

Quatre appels directs de fonctions publiques Python, sans HTTP : V1 normal/compact et V2 normal/compact. Aucun appel Qwen. Le garde a bloqué quatre sondes Graphiti et quatre tentatives de ledger hors du dossier expérimental ; ces effets ne sont pas décrits comme inexistants. Le réseau applicatif et les écritures correspondantes ont été empêchés. Les SQLite du corpus sont ouverts en lecture seule.

Importation vérifiée avec le Python autonome 3.13.3 utilisé par Brody : 88 origines de modules contrôlées, toutes dans le déploiement Studio. Aucun serveur démarré.

Commandes :

```powershell
python -X utf8 -B data/experiments/native_editorial_v2_integration_20261024/probe_deployment.py
python -X utf8 -B data/experiments/native_editorial_v2_integration_20261024/run_studio_tests.py
```

Les runners bloquent le réseau et limitent les écritures aux artefacts. Résultat final : **549 PASS, 17 sous-tests PASS, 0 FAIL**, 67,20 s. Le garde de la suite Studio enregistre zéro tentative réseau, sous-processus ou écriture externe. La première suite a relevé un compteur d’octets de manifeste obsolète (545 PASS / 1 FAIL / 17 sous-tests PASS) ; compteur et empreintes corrigés, assertion préservée, puis suite complète rejouée. Le mauvais appel initial de signature `_v2_operations` a également été corrigé avant validation V2.

Tests couvrant les versions inconnues/croisées, normal/compact, preuve altérée, plan ou réalisation manquants, fait non vérifié, inconnue essentielle, contradiction, C275, HOLD/BLOCK, substitution Qwen, réponse B6 seule, mémoire et E11. `CONTEXT_LIMITED`, `MEMORY_NOT_REQUIRED`, inconnues et publication interdite restent observés dans les artefacts admis. Revue statique finale indépendante : aucun défaut concret restant identifié ; ce contrôle n’est pas une observation HTTP.

Les **8 FAIL historiques du producteur** restent une référence séparée de la passe publique V2 précédente (39 PASS / 8 FAIL sur son sous-ensemble historique). Ils ne sont pas rejoués ni corrigés ici. Aucun GREEN global de la stack n’est annoncé.

## FAIT / PROUVÉ / INCERTAIN / RESTANT

| État | Résultat |
|---|---|
| FAIT | Transfert ciblé, sauvegardes, opt-in Studio, manifestes, tests hors réseau et documentation. |
| PROUVÉ | 1 535 empreintes ; V1 inchangée par défaut et texte identique ; admission V2 normale/compacte ; refus stricts ; 549 PASS + 17 sous-tests ; producteur et autopilot inchangés. |
| INCERTAIN | Comportement HTTP V2 et identité du code actuellement en mémoire : aucun service contrôlé ou redémarré dans cette passe. La validation de lignée locale ne prouve pas à elle seule l’origine du service distant. |
| RESTANT | Un futur rechargement contrôlé, précontrôles d’authentification/origines/LOT1/autopilot, puis un seul essai réel V2 explicitement demandé. Aucune publication automatique. |

Procédure et rollback : `BRODY_STUDIO_V2_OPT_IN.md`. Omettre la version ou choisir V1 pour revenir au comportement fonctionnel par défaut ; pour restaurer l’ancien déploiement, restaurer ensemble les quatre fichiers, manifestes et pin depuis les sauvegardes, en préservant les WIP ultérieurs. Aucune restauration exécutée.

STOP après validation hors réseau.
