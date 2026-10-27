# OBSIDIA Studio — résultats réels de la campagne 10I

17 octobre 2026, 11:27:59–11:28:34 Europe/Paris. Cinq scénarios exécutés, sans retry. Aucun scénario supplémentaire. Écritures exclusivement dans Studio, producteurs externes en lecture seule, aucun commit/push.

## Précontrôles et opérations

- Brody identifié par PID 29460, démarrage 08:43:03, Python autonome et cwd de la copie figée existante `data/experiments/e11_lot1/passe10e2/producer_cbad0125/source`. Commande uvicorn, `--app-dir` explicite, loopback 8000, aucun reload. Brody n'a pas été redémarré.
- Checkpoint `cbad01257c027e5861a1c0610d418dfd02fc8342`, manifeste `d64f9ac43d1157c52876ea8f265a26fddd95b80b8c6114504d152e88ab5fb26a`, 1526 fichiers vérifiés avant et après les appels. Cette vérification porte sur la copie déployée ; aucun HEAD concurrent n'est substitué à ce checkpoint.
- Authentification : santé GET 200, OpenAPI sans clé 401, avec clé 200, GET authentifié de la route chat 405 ; route POST chat présente. Auth activée dans l'environnement Brody. Clé DPAPI existante utilisée en mémoire, jamais affichée ni passée en argument.
- Studio initial PID 27848, cwd et Python identifiés, loopback 8108, LOT1=0. Autopilot.enabled=false ; configuration inchangée. Posts existants rendent seed() inerte. Vérification des processus enfants avant arrêt.
- Empreintes des corrections 10H comparées à leur rapport de tests ; bases server.py/studio_ai.py/garde de checkpoint comparées au chargement historique correspondant. Aucun changement applicatif ajouté pendant 10I.
- Studio rechargé pour la campagne, PID 19768, même Python/cwd et clé, LOT1=1, sans reload. Routes E11 et generate présentes ; generate n'a pas été appelé. Les réponses ont toutes exposé les diagnostics 10H attendus.
- Nettoyage dans finally : Studio de campagne arrêté, relancé PID 4144 avec LOT1=0, environnement effectif vérifié. Autopilot toujours désactivé ; Brody toujours PID 29460. Aucun renouvellement de preuve ni approbation répétitive.

## Tableau comparatif réel

Les questions sont exactement les cinq fixtures publiques de la matrice 10H. A = simple ; B = rappel documentaire ; C = ambiguïté ; D = contradiction ; E = frontière hors périmètre. Aucun texte de question ou extrait mémoire n'est recopié dans les événements persistants de cette campagne.

| Scénario | HTTP | Verdict Studio | Statut mémoire | Éléments mémoire E11 | Inconnues B6 | Omissions B6 | Demandes B7 | Latence client |
|---|---:|---|---|---:|---:|---:|---:|---:|
| A — simple | 200 | CONTEXT_LIMITED | MEMORY_NOT_REQUIRED | 0 | 1 | 0 | 1 | 3857,121 ms |
| B — mémoire nécessaire | 200 | CONTEXT_LIMITED | MEMORY_USABLE | 5 | 1 | 5 | 1 | 3589,753 ms |
| C — ambiguë | 200 | CONTEXT_LIMITED | MEMORY_NOT_REQUIRED | 0 | 1 | 0 | 1 | 3341,761 ms |
| D — contradictoire | 200 | CONTEXT_LIMITED | MEMORY_NOT_REQUIRED | 0 | 1 | 0 | 3 | 3344,374 ms |
| E — hors périmètre | 200 | CONTEXT_LIMITED | MEMORY_NOT_REQUIRED | 0 | 1 | 0 | 2 | 3357,778 ms |

Pour les cinq cas :

- `error_code=NONE` ; `e11_contract_status=VALID` ; `b6_context_status=LIMITED`.
- `governance_status=CONTEXT_ALLOWED` ; `receipt_availability=VALIDATED` ; `publication_permitted=false`.
- Reçu `REAL_COGNITIVE_JOIN_C1_V1`, E11 `COGNITION_SHADOW_MEMORY_V0`, B6 `B6_STATE_EXPLICIT_CONTEXT_PACKET_V1`, mémoire `OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1`.
- `receipt_completeness=DEGRADED`, un état SENS OPEN, aucun état SENS ERROR ; deux références de provenance dans B6.
- Aucun snapshot M41 non vide observé ; aucune validation sémantique B7/M41 démontrée.
- Reçu public original conservé dans la réponse en mémoire, mais ni reçu intégral ni contenu privé persisté dans le journal minimal ou les rapports de campagne.

Motifs communs aux cinq cas :

```
B6_UNKNOWNS
E11_UNRESOLVED_REQUESTS
RECEIPT_DEGRADED
RECEIPT_SURFACES_UNAVAILABLE
```

Le scénario B ajoute `B6_OMISSIONS`. MEMORY_NOT_REQUIRED n'est plus lui-même une cause de limitation. Le classement limité demeure justifié par des motifs indépendants réellement observés.

## Observations par capacité

### Mémoire native

| Cas | Besoin MEMZUM observé | Axe 13 | Raison MEMZUM observée |
|---|---|---:|---|
| A | false | 0,25 | MEMORY_NOT_REQUIRED |
| B | true | 0,85 | MEMORY_REQUIRED_COGNITIVE_SIGNAL |
| C | false | 0,00 | MEMORY_NOT_REQUIRED |
| D | false | 0,00 | MEMORY_NOT_REQUIRED |
| E | false | 0,00 | MEMORY_NOT_REQUIRED |

Le rappel documentaire B exerce effectivement le chemin mémoire natif et transporte cinq éléments dans E11. Ce résultat ne garantit ni leur exactitude factuelle, ni leur intégration complète au contexte projeté B6 : cinq états sont omis par B6. Les identités et motifs individuels de ces omissions ne sont pas conservés dans le résumé ; il serait excessif d'affirmer, sur le seul compteur, que ce sont exactement les cinq éléments mémoire. Aucune seconde récupération n'a été ajoutée côté Studio.

Le scénario A confirme cette fois à l'exécution le signal MEMZUM non requis et l'axe 0,25, qui n'étaient que des déductions nominales lors de l'audit 10G. Cela n'autorise pas à modifier rétroactivement les valeurs absentes du premier reçu historique.

### SENS, B7, ambiguïtés et contradictions

| Cas | Marqueurs SENS ambiguities | contradictions | unresolved_references | missing |
|---|---:|---:|---:|---:|
| A | 0 | 0 | 0 | 0 |
| B | 0 | 0 | 0 | 0 |
| C | 0 | 0 | 0 | 0 |
| D | 0 | 0 | 0 | 2 |
| E | 0 | 0 | 0 | 2 |

La question ambiguë C ne présente aucun marqueur explicite d'ambiguïté/coréférence dans les champs SENS mesurés. La question contradictoire D ne présente aucun marqueur explicite de contradiction dans ce même périmètre ; elle présente deux éléments manquants. Ces constats sont des limites observées des surfaces examinées, pas une démonstration que toutes les couches de la stack sont incapables de détecter ces situations.

Une entrée B6 unknowns n'est pas une unité de compréhension validée : elle correspond ici à un état SENS OPEN. Les demandes B7 sont présentes et comptées, mais leur présence ne prouve pas que le problème visé a été correctement identifié ou résolu. Aucun candidat ou verdict B7 n'a été promu. M41 n'est pas démontré par cette campagne.

### Gouvernance et restitution

Les cinq reçus sont acceptés pour le contexte consultatif uniquement, avec les frontières KX108 contrôlées par le consommateur. Aucun HOLD/BLOCK n'a été rencontré dans les cinq réponses ; leur comportement de refus reste couvert par les tests antérieurs, **pas observé à nouveau pendant cette campagne**. Aucun appel supplémentaire n'a été ajouté pour provoquer un refus.

Le scénario E reste une question consultative sur une frontière, et non une demande d'exécution. Son ALLOW_CONTEXT_ONLY ne donne aucun droit de publier ou d'agir. Aucun déclenchement d'action, de génération éditoriale ou de publication n'a été demandé.

La campagne valide l'accessibilité de contrats et mesure les diagnostics exposés. Elle ne mesure pas une qualité rédactionnelle finale, ne certifie aucune connaissance factuelle et ne transforme pas le reçu JSON en publication aboutie.

## Nombre d'appels et confidentialité

- **5 POST Studio tentés et 5 réponses observées** ; **5 POST Brody** constatés par différence des journaux d'accès, de 1 avant à 6 après. Aucun POST Brody direct du client.
- Zéro retry, zéro scénario hors matrice, zéro appel `/api/generate`. Aucun fallback Qwen ni récupération mémoire côté Studio. Les flags provider/modèle local/candidat mémoire/application manuelle sont restés false dans l'adaptateur testé et inchangé.
- Cinq événements nouveaux dans le journal minimal ; les clés, enums, identifiants techniques, compteurs et diagnostics fermés ont été contrôlés, 5/5 conformes. Aucun texte de question, extrait mémoire, reçu complet ou secret dans ces événements et les rapports.
- Cinq enregistrements du ledger fournisseur correspondent à ces sessions. Ils sont distincts du journal Studio et peuvent contenir les fixtures de question et le texte de réponse ; leur contenu n'est pas recopié dans les rapports. Effet secondaire connu, dans la copie déjà située sous Studio, sans promotion mémoire canonique.
- Le code fournisseur suivi par le manifeste et le code Studio sont inchangés pendant les appels ; posts/images et configuration autopilot inchangés. Les ledgers techniques attendus ne sont pas présentés comme une absence de toute écriture système.

## Anomalies et limites

Aucune anomalie de gouvernance détectée dans les surfaces contrôlées ; aucune erreur réseau/contrat, aucun arrêt anticipé. Cinq contextes limités ne constituent pas cinq échecs de transport.

Limites à examiner à partir de ces résultats, sans nouvelle requête : projection B6 du scénario mémoire avec cinq omissions ; détection explicite SENS non démontrée sur les cas ambigu/contradictoire ; complétude C1 systématiquement DEGRADED et surfaces indisponibles ; M41 non démontré. Les compteurs ne permettent pas de reconstruire les libellés non persistés. Les lectures documentaires internes au fournisseur ne sont pas toutes mesurées par le compteur de retrieval Studio.

La latence client comprend validation du checkpoint/fichiers, transport, traitement fournisseur et validation/journal Studio. Elle n'est pas une mesure isolée du temps de recherche mémoire.

## État final et preuves

| Service | PID final | Adresse | État |
|---|---:|---|---|
| Brody | 29460 | 127.0.0.1:8000 | Inchangé, non redémarré, checkpoint figé vérifié |
| Studio | 4144 | 127.0.0.1:8108 | Corrections 10H chargées, LOT1=0 effectif, autopilot désactivé |

Artefacts dans `data/experiments/e11_lot1/passe10i/` :

- `run_report.json` : précontrôles, authentification sans secret, empreintes, PID et retour à LOT1=0.
- `campaign_result.json` : tableau de métadonnées par scénario, sans payload complet.
- `privacy_and_ledger_check.json` : contrôle fermé des cinq événements et nombre de ledgers correspondants.
- `campaign.py`, `run_campaign.ps1` : protocole borné exécuté ; marqueurs exclusifs de campagne et de chaque scénario. Ne pas les relancer pour répéter les appels.

Aucune suite supplémentaire ni nouveau test cognitif hors matrice n'a été exécuté. Les 277 PASS + 17 sous-tests de 10H restent un résultat historique ; la présente passe fournit cinq observations runtime.

**FAIT :** Studio rechargé, LOT1 temporairement activé, cinq scénarios exécutés séquentiellement, LOT1 désactivé dans finally, services finaux vérifiés.

**PROUVÉ :** cinq HTTP 200 / CONTEXT_LIMITED ; contrats E11/B6 et reçu acceptés ; activation mémoire et cinq items au cas B ; limitations conservées ; journal minimal contrôlé ; aucune génération/publication déclenchée par Studio ; code fournisseur et mémoire suivie par le manifeste inchangés.

**INCERTAIN :** exactitude factuelle du matériau documentaire, identité des cinq omissions B6, compréhension sémantique effective des cas C/D, validité cognitive B7/M41, comportement runtime HOLD/BLOCK non rencontré. Aucune réussite sémantique n'est déduite de la seule validation de contrat.

**RESTANT :** analyser statiquement les règles de projection B6 et les limites SENS/B7 à partir de ces observations, puis proposer uniquement les ajustements de consommation Studio justifiés. Aucune sixième requête ni correction productrice engagée.

VERDICT : E11_CAMPAIGN_10I_EXECUTED / FIVE_STUDIO_POSTS / FIVE_BRODY_POSTS / LOT1_DISABLED / AUTOPILOT_DISABLED / NO_PUBLICATION / KX108_ONLY.
