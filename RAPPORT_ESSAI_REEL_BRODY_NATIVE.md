# Essai réel unique Studio → Brody natif

**STUDIO_BRODY_E2E=PASS** — 23 octobre 2026.

| Contrôle | Observation |
|---|---|
| BRODY_HTTP_STATUS | 200, une ligne POST `/api/brody/chat` dans le journal d'accès |
| STUDIO_HTTP_STATUS | 200, une ligne POST `/api/generate` dans le journal d'accès |
| BRODY_NATIVE_AUTHOR | true, `BRODY_NATIVE_EDITORIAL_V1`, `model_calls=0` |
| EDITORIAL_PLAN_PRESENT | true, condition obligatoire vérifiée sur la réponse Brody par le validateur Studio épinglé |
| SELECTED_PROPOSITIONS_PRESENT | true, sélection et plan recalculés et comparés par ce même validateur |
| PROVENANCE_VERIFIED | true, `lineage_verified=true` |
| POST_ARTIFACT_PRESENT | true, texte Studio identique au contenu POST reçu |
| HUMAN_REVIEW_REQUIRED | true, aucune approbation humaine enregistrée |
| PUBLICATION_PERMITTED | false |

Un seul appel Studio, un seul appel Brody observé ; zéro retry, fallback,
appel modèle ou requête de publication. Latence HTTP Studio : **14,4 secondes**.
Les champs internes de sélection/plan ne sont pas récupérés par un second appel :
leur présence est établie par l'exécution réussie des vérifications obligatoires
du validateur dont l'empreinte est inchangée pendant l'essai. Le contrat public
Studio retourne une provenance minimale et ne conserve pas le reçu complet.

## Déploiement et authentification

Les **1 535 fichiers** ont été vérifiés avant et après l'essai.
Base : `cbad01257c027e5861a1c0610d418dfd02fc8342`.
Overlay WIP : sources épinglées depuis `474afd9ca4b77bf127c31ce22599d52438a7ff37`.
Manifeste : `ff2006c5159cc49b60739180f36268d987be771cc8dc99e74f696136b5a41c0c`.

Clé locale DPAPI existante, chargée uniquement en mémoire et transmise dans les
environnements des services. Aucune valeur secrète affichée ou enregistrée.
Brody : OpenAPI sans clé 401, avec clé 200 ; GET authentifié sur la route chat
405 ; POST réel transmis par Studio 200. Authentification non désactivée.

## Brouillon reçu, sans modification

Une petite entreprise commencerait par une seule tâche répétitive, avec un budget plafonné.

L’équipe choisirait une tâche chronophage et un résultat facile à relire. L’équipe relirait le brouillon avant tout usage. L’équipe vérifierait chaque information avant tout usage.

Un premier essai avec l’IA porterait sur un brouillon de réponse à une demande récurrente, sans données privées.

L’équipe comparerait le temps passé avec et sans assistance avant de poursuivre.

## Limites et contrôles finaux

Le PASS atteste le parcours et le contrat du compositeur natif borné, pas une
qualité rédactionnelle universelle ni la correction factuelle de connaissances
externes. La revue du brouillon reste humaine.

E11 conserve `CONTEXT_LIMITED` et trois inconnues. Mémoire :
`MEMORY_NOT_REQUIRED`, sans promotion en preuve de vérité. Motifs conservés :
`B6_UNKNOWNS`, `E11_UNRESOLVED_REQUESTS`, `RECEIPT_DEGRADED`,
`RECEIPT_SURFACES_UNAVAILABLE`. Aucun statut B7/M41 n'est déclaré validé.

Services maintenus opérationnels, mêmes identités au contrôle final :

- Brody : PID **23484**, `127.0.0.1:8000`, Python autonome 3.13.3,
  démarré depuis la copie productrice Studio vérifiée, sans reload.
- Studio : PID **20612**, `127.0.0.1:8108`, environnement Python existant,
  mode `brody_native`, LOT1=0, autopilot désactivé, sans reload.

Horodatages, exécutables, commandes et listeners concordent avec le lancement.
Les fichiers applicatifs Studio, les posts et les images sont inchangés.
Santé Brody finale : readonly=true, memory_write=false, KX108_ONLY.
`MEMORY_WRITE_HOLD` est une condition obligatoire de l'admission native réussie.

L'orchestrateur Brody peut écrire son ledger de session sous la copie Studio :
huit fichiers y ont été observés après l'essai, sans lecture de leur contenu.
Leur nombre ne constitue pas un décompte de nouvelles écritures de cette passe.
Ce ledger technique ne vaut ni admission de connaissance ni écriture mémoire
canonique autorisée. Aucun dépôt producteur, kernel, C273/C274 ou B8 modifié.

L'écart initial du contrôle d'identité final provenait de la conversion
automatique des dates JSON par PowerShell. La comparaison des timestamps UTC,
des commandes et des exécutables confirme les deux identités sans changement
de service ni nouvel appel cognitif.

Les preuves sont dans `data/experiments/native_editorial_real_trial_20261023` :
`service_start_report.json`, `http_observation.json`, `result.json`,
`final_service_checks.json`, `DRAFT.txt`. Le SHA-256 du texte UTF-8 brut est
`5109fd0bf82608356ee9eb3ac0af625c4ddf15e34686550d9509c4e5c05b9488`.
L'empreinte `draft_sha256` productrice utilise sa sérialisation JSON canonique ;
elle est distincte de l'empreinte des octets UTF-8 bruts.

**STOP après cet essai.** Aucun second essai, commit, push ou publication.
