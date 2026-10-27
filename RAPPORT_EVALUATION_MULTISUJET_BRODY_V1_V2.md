# Évaluation multisujet native Brody V1/V2 — campagne réelle

**CAMPAIGN_EXECUTED — EDITORIAL_COVERAGE=0/8 — V1_DEFAULT_PRESERVED**

Mode : tests et évaluation uniquement. Moteurs inchangés. KX108_ONLY, V2 opt-in, DRAFT_ONLY. SESSION_LEDGER_ALLOWED, CANONICAL_MEMORY_WRITE_HOLD.

## Résultat principal

Les huit demandes prévues ont été exécutées séquentiellement. **8 POST Studio /api/generate → 8 POST Brody /api/brody/chat**, sans retry, fallback, autre scénario ou génération de contrôle. Brody retourne HTTP 200 dans les huit cas ; Studio refuse les huit sorties avec HTTP 409 et le motif exact **`BRODY_NATIVE_ARTIFACT_INVALID`**. Aucun brouillon natif admissible n’est disponible.

Ces résultats établissent une limite du parcours public actuel sur ces briefs ; ils ne permettent pas de comparer la qualité littéraire de V1 et V2 ni d’attribuer une cause plus précise au moteur. Le 200 Brody n’est pas un succès rédactionnel.

## Tableau par sujet

Les latences mesurent le parcours complet jusqu’au refus Studio, pas la production d’un brouillon réussi.

| Sujet | Version | Brody HTTP | Studio HTTP | Latence (s) | Sortie | Provenance native |
|---|---|---:|---:|---:|---|---|
| A — Communication commerciale | V1 | 200 | 409 | 4.658 | Refus | Non vérifiable, aucun artefact admis |
| A — Communication commerciale | V2 | 200 | 409 | 4.611 | Refus | Non vérifiable, aucun artefact admis |
| B — Vulgarisation technique | V1 | 200 | 409 | 4.601 | Refus | Non vérifiable, aucun artefact admis |
| B — Vulgarisation technique | V2 | 200 | 409 | 4.547 | Refus | Non vérifiable, aucun artefact admis |
| C — Présentation d’Obsidia | V1 | 200 | 409 | 7.054 | Refus | Non vérifiable, aucun artefact admis |
| C — Présentation d’Obsidia | V2 | 200 | 409 | 5.686 | Refus | Non vérifiable, aucun artefact admis |
| D — Publication personnelle | V1 | 200 | 409 | 5.355 | Refus | Non vérifiable, aucun artefact admis |
| D — Publication personnelle | V2 | 200 | 409 | 4.576 | Refus | Non vérifiable, aucun artefact admis |

Latence moyenne des refus : V1 **5.417 s**, V2 **4.855 s**. Une observation par sujet/version, avec refus systématique, ne mesure pas une supériorité rédactionnelle ou une performance générale.

## Les huit sorties, sans réécriture

Aucun brouillon n’est créé pour remplacer un refus. Les corps d’erreur utiles et les lignes de journal HTTP sont conservés dans `results.json`.

### A — Communication commerciale

Sujet exact : « Comment une petite entreprise peut utiliser l'IA pour améliorer son service client sans perdre le contact humain ? »

**A/V1 — REFUS HTTP 409**, Brody HTTP 200, 4.658 s.

```json
{"detail":"BRODY_NATIVE_ARTIFACT_INVALID"}
```
Aucun texte admis ; aucune provenance d’auteur ni inconnue chiffrée exposée par cette réponse Studio.

**A/V2 — REFUS HTTP 409**, Brody HTTP 200, 4.611 s.

```json
{"detail":"BRODY_NATIVE_ARTIFACT_INVALID"}
```
Aucun texte admis ; aucune provenance d’auteur ni inconnue chiffrée exposée par cette réponse Studio.

Le service client et le maintien du contact humain ne peuvent pas être évalués : aucune formulation, aucun exemple et aucun arbitrage humain/IA n’ont été livrés par le parcours admis. Le sujet est proche du domaine IA/petite entreprise de la baseline, mais cela n’a pas suffi à obtenir un brouillon.

### B — Vulgarisation technique

Sujet exact : « Pourquoi une IA doit distinguer compréhension, proposition, autorisation et exécution ? »

**B/V1 — REFUS HTTP 409**, Brody HTTP 200, 4.601 s.

```json
{"detail":"BRODY_NATIVE_ARTIFACT_INVALID"}
```
Aucun texte admis ; aucune provenance d’auteur ni inconnue chiffrée exposée par cette réponse Studio.

**B/V2 — REFUS HTTP 409**, Brody HTTP 200, 4.547 s.

```json
{"detail":"BRODY_NATIVE_ARTIFACT_INVALID"}
```
Aucun texte admis ; aucune provenance d’auteur ni inconnue chiffrée exposée par cette réponse Studio.

Impossible de juger si les quatre notions sont correctement définies, distinguées et illustrées. HTTP 200 Brody n’est pas une démonstration de compréhension ou de pédagogie.

### C — Présentation d’Obsidia

Sujet exact : « Présenter Obsidia comme une architecture qui sépare les décisions, les preuves et les actions, sans prétendre que ses capacités expérimentales sont déjà toutes opérationnelles. »

**C/V1 — REFUS HTTP 409**, Brody HTTP 200, 7.054 s.

```json
{"detail":"BRODY_NATIVE_ARTIFACT_INVALID"}
```
Aucun texte admis ; aucune provenance d’auteur ni inconnue chiffrée exposée par cette réponse Studio.

**C/V2 — REFUS HTTP 409**, Brody HTTP 200, 5.686 s.

```json
{"detail":"BRODY_NATIVE_ARTIFACT_INVALID"}
```
Aucun texte admis ; aucune provenance d’auteur ni inconnue chiffrée exposée par cette réponse Studio.

Aucun texte de présentation n’est disponible. La prudence demandée sur les capacités expérimentales ne peut donc pas être notée. Le rejet empêche l’acceptation automatique d’une sortie non vérifiée ; il ne prouve pas à lui seul la justesse d’une description d’Obsidia.

### D — Publication personnelle

Sujet exact : « Expliquer pourquoi construire une technologie indépendante demande des expérimentations, des erreurs et des validations successives. »

**D/V1 — REFUS HTTP 409**, Brody HTTP 200, 5.355 s.

```json
{"detail":"BRODY_NATIVE_ARTIFACT_INVALID"}
```
Aucun texte admis ; aucune provenance d’auteur ni inconnue chiffrée exposée par cette réponse Studio.

**D/V2 — REFUS HTTP 409**, Brody HTTP 200, 4.576 s.

```json
{"detail":"BRODY_NATIVE_ARTIFACT_INVALID"}
```
Aucun texte admis ; aucune provenance d’auteur ni inconnue chiffrée exposée par cette réponse Studio.

Aucun récit ou argumentaire n’est disponible. Le ton personnel, les transitions et l’absence de témoignage inventé ne sont pas évaluables. Il serait trompeur de remplacer ce manque par un texte rédigé manuellement ou une sortie Qwen.

## Évaluation éditoriale 0–5

L’échelle demandée reste 0–5 : 0 correspondrait à un texte livré mais inadéquat, 3 à un texte utilisable après révision, 5 à un texte abouti sur le critère considéré. **Un refus n’est pas un texte : la note est N/A, pas 0.** Aucune note ne peut valider une provenance invalide ou compenser une assertion injustifiée.

| Sortie | Pertinence | Respect du sujet | Structure | Fluidité | Originalité | Précision | Accroche | Conclusion |
|---|---|---|---|---|---|---|---|---|
| A/V1 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| A/V2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| B/V1 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| B/V2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| C/V1 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| C/V2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| D/V1 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| D/V2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

Les observations concrètes figurent pour chaque sujet ci-dessus. Faute de brouillons, une moyenne qualitative, un classement V1/V2 ou une évaluation de la factualité du texte seraient artificiels. Aucun texte Qwen ni rédaction manuelle n’a été substitué.

## Provenance, refus et inconnues

- V1 est demandée par omission du champ, selon le défaut existant ; V2 est explicitement transmise par `editorial_version="V2"`.
- L’identité des processus et les origines de code correspondent au déploiement vérifié de l’essai V2 précédent. Les schémas exposent V1 par défaut.
- Le motif Studio identifie la frontière d’admission de l’artefact natif. Il ne dit pas si la cause première est un brief non pris en charge, un plan absent, une inconnue indispensable, un contrat ou une provenance rejetée.
- Les réponses HTTP 409 de Studio n’exposent pas le reçu, les inconnues, le plan ou les motifs fins producteurs. Ces valeurs sont **UNKNOWN / NON OBSERVÉES**, et non zéro ou absentes côté cognition.
- Les huit réponses textuelles du ledger de session ne contiennent pas de marqueur `<POST>`. Ce ledger est une trace d’orchestration ; il ne remplace pas le reçu cognitif public et ne démontre pas à lui seul ce que le producteur a exposé ensuite.
- Le contrôle de code montre une composition déterministe bornée : le vocabulaire natif actuel porte surtout des conseils IA/tâche répétitive/relecture/mesure du temps. Cela explique pourquoi la baseline validée ne suffit pas à prouver une compétence multisujet ; **ce constat statique ne constitue pas le diagnostic exact de chacun des huit refus runtime**.

## Mémoire et gouvernance

Le ledger a été explicitement autorisé par l’utilisateur pour cette campagne. Son mécanisme existant n’a été ni désactivé ni modifié. Les huit nouveaux enregistrements, séquences **5 à 12**, ont été contrôlés en lecture : continuité des événements et hashes vérifiés, `TRACE_ONLY_NOT_INDEXED`, KX108_ONLY, readonly, absence de décision mémoire, d’acte, de mutation kernel/X108, d’indexation Graphiti et d’intake mémoire dans leurs champs.

Le code `brody_automation_orchestrator.run_brody_automation_layer()` appelle le ledger séparément ; son protocole writable reste inactif et les indicateurs graphiti_write/neo4j_write/memory_write sont faux. `build_record()` écrit ses traces JSON/Markdown, son index et son JSONL sous le répertoire de session de la copie Studio. Aucun appel au writer canonique n’est effectué par ce composant. Les options Studio `allow_memory_candidate`, `allow_manual_apply`, `allow_local_model` et `allow_provider` restent fausses.

**MEMORY_WRITE_HOLD reste actif. Aucune promotion canonique n’est observée ni autorisée.** La preuve porte sur ces chemins de code, indicateurs, traces et fichiers manifestés ; il ne s’agit pas d’un audit global des écritures système. Les payloads de session ne sont pas recopiés dans ce rapport. Les contrôles de traces sont conservés dans `ledger_audit.json`.

## Références, état final et régressions

- Les deux preuves E2E V1/V2 et leurs brouillons historiques sont préservés par empreintes.
- **1 535 fichiers** du déploiement vérifiés avant et après ; manifeste `f9fffba9a94efeb30d7a7190a6dbc488aaa65d84b6edec52cd9a5a4eeb8265a5` inchangé ; base cbad0125 et overlay WIP b8c06be7 restent tracés séparément.
- Sources Python Studio et copie productrice manifestée inchangées. Aucun changement du dépôt producteur ; les seules nouvelles écritures demandées sont les artefacts de campagne et le ledger autorisé.
- Brody **PID 26472**, 127.0.0.1:8000 ; Studio **PID 18320**, 127.0.0.1:8108. Instants de création inchangés ; aucun redémarrage durant la campagne.
- Authentification Brody : 401 sans clé / 200 avec la clé existante, secret non affiché. Santé finale readonly=true, memory_write=false, KX108_ONLY.
- V1 reste le défaut ; V2 opt-in seulement ; LOT1=0 par identité du processus lancé avec ce flag ; autopilot=false observé via GET et fichier inchangé.
- Posts/images Studio inchangés. Aucune publication, aucun commit ou push.
- **Régression non démontrée** : ces quatre sujets n’avaient pas de baseline HTTP réussie comparable. Les sujets historiques ne sont pas rejoués pour respecter la limite de huit générations. Leurs succès E2E précédents restent des preuves conservées, pas de nouvelles observations.
- Les huit refus de cette campagne ne sont pas les huit FAIL historiques des tests producteurs. Aucune suite de régression des moteurs n’est exécutée ici ; leurs tests précédents ne sont pas présentés comme une nouvelle certification.

## Décision recommandée

**Maintenir V1 par défaut et conserver V2 en opt-in expérimental. Ne pas promouvoir V2 sur cette campagne.** La reformulation améliorée observée sur la baseline Ardennes demeure valable dans son périmètre ; elle ne se généralise pas aux quatre sujets testés, pour lesquels aucun texte n’a franchi l’admission.

**Prochaine action proposée, non exécutée :** identifier hors nouvelle génération la première condition d’admission responsable de ces refus, à partir des traces disponibles et du code exact, puis définir le plus petit complément de diagnostic ou de couverture nécessaire. Ne pas assouplir le validateur pour obtenir des textes notables artificiellement.

### FAIT / PROUVÉ / INCERTAIN / RESTANT

| État | Constat |
|---|---|
| FAIT | 8 demandes séquentielles V1/V2 ; textes non remplacés ; refus et latences conservés ; aucun moteur modifié. |
| PROUVÉ | 8 HTTP 200 Brody → 8 HTTP 409 Studio ; zéro brouillon admis ; références et empreintes inchangées ; 8 traces de session sans promotion déclarée. |
| INCERTAIN | Cause productrice fine, inconnues, plan et provenance des sorties rejetées ; qualité rédactionnelle multisujet ; audit physique global des mémoires externes non effectué. |
| RESTANT | Diagnostiquer le refus détaillé avant de décider une amélioration. Aucun neuvième appel ni défaut modifié. |

**STOP après la campagne et son rapport.**
