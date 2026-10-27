# Studio → Brody : réparation locale et essai éditorial unique

**Résultat : raccord authentifié réparé ; rédaction Brody non démontrée. Arrêt sur une limite productrice, sans substitution.**

## Réconciliation locale

Studio reste sur `main`, HEAD `637dd86dd1dba47dccf7cffa592cab98e1687ea8`. Aucun pull, checkout, reset, staging, commit, merge ou push. Les modifications préexistantes de `server.py` et `studio_ai.py`, ainsi que les fichiers LOT 1 / E11 / 10K non suivis, ont été préservés.

La PR [#1](https://github.com/Eaubin08/obsidia-studio/pull/1), branche `fix/studio-brody-editorial-auth-20261017`, a été lue au SHA `6694b0756d29466558ace04f64c3985f2b501ac5`, base identique au HEAD local. Elle ne modifie que `studio_ai.py` et `test_studio_ai.py`. Sa correction X-API-Key / absence de proxy / refus de redirection est intégrée au code local enrichi ; ses deux scénarios de test sont repris dans `test_brody_editorial_repair.py`, avec les cas de clé invalide et de confidentialité supplémentaires. Il ne s'agit pas d'une fusion de branche.

Les cinq fichiers existants concernés ont été sauvegardés sous `data/experiments/brody_editorial_repair_20261017/before`. `pr1.diff` conserve la diff distante ; `changes_local.diff` compare uniquement cette intervention à l'état local initial, séparément des changements antérieurs.

## CORRIGÉ

| Fichier | Intervention |
|---|---|
| `studio_ai.py` | Authentification native et sonde avec `OBSIDIA_STUDIO_API_KEY`, proxies et redirections refusés ; erreurs sans détail secret ni corps fournisseur ; réponse bornée et JSON strict ; drapeaux d'appel sans modèle local, fournisseur, candidat mémoire ou application manuelle. |
| `studio_ai.py` | Refus des enveloppes non readonly, autorités contradictoires, HOLD/BLOCK, demandes de résolution présentes et projections Qwen ; réutilisation du validateur LOT 1 pour le reçu natif lorsqu'il est exposé, sans retrieval ou journal supplémentaire ; provenance du champ et de la source native pour un éventuel véritable `<POST>`. |
| `editorial_intent.py` | La demande de brouillon, le réseau et la préparation pour revue humaine accompagnent désormais le sujet exact et les sources explicitement fournies. Le sujet n'est plus envoyé comme une simple question consultative. Aucune instruction ALLOW, BRODY_SUFFICIENT ou forçage de route. |
| `server.py` | Modes modèle/gabarit refusés comme rédacteur final ; aucun basculement natif automatique lorsque le mode Ingress est désactivé ; pas d'injection des documents historiques de `_studio_context()` dans la requête native ; reçu de provenance conservé ; un refus ne devient plus un texte utilisateur recopié avec HTTP 200. |
| `test_studio_ai.py`, `test_editorial_intent.py` | Attentes alignées sur la rédaction explicite et le refus d'une projection Qwen comme auteur. |
| `test_brody_editorial_repair.py` | Tests hors réseau de l'authentification PR, secrets, transformations, origine, gouvernance, absence de retry/fallback et comportement du endpoint Studio compilé sans ses hooks de démarrage. |

Les anciens moteurs auxiliaires restent sur disque ; ils ne sont pas autorisés comme auteur final par `/api/generate`. Aucune capacité cognitive nouvelle n'a été reconstruite.

Les déclarations `E11NoRedirect`, `E11Deadline`, `verify_e11_service` et `run_e11_experiment` sont structurellement identiques à la sauvegarde initiale. Les quatre fichiers contrat / extracteur 10K / client / journal E11 conservent exactement les empreintes du rapport 10K. Les fins de ligne des portions inchangées ont été conservées ; leur restauration n'a modifié aucun AST applicatif après l'essai.

## TESTÉ

Version finale : **367 tests PASS + 17 sous-tests PASS ; 0 FAIL, 0 ERROR, 0 SKIP**, XML de 384 cas. Onze fichiers racine explicites, plugins pytest externes et cache désactivés. Aucun producteur importé par cette suite, aucun appel réseau réel de ses tests.

Un premier passage ciblé avait un échec d'attente du texte d'erreur : le refus HOLD intervenait désormais plus tôt avec GOVERNANCE_REFUSED. L'attente a été corrigée ; aucune frontière n'a été assouplie. Le passage complet intermédiaire de 365 tests et la suite finale sont conservés séparément. `git diff --check` passe.

## Blocage Ingress : reproduction locale distincte de l'essai réel

Source consultée en lecture seule : dépôt `obsidia-x108-proofs`, worktree `C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0`, HEAD observé `9113300de191a77eae17ebd61e003a5a89081714`, fichier `scripts/obsidia_cognitive_ingress_v0.py`, fonction `_evaluate_brody_sufficiency`.

La fonction pure et ses constantes ont été extraites par AST, sans importer le runtime producteur. Fixture synthétique : route `ROUTER_OK / ALLOW`, aucune contradiction d'autorité, rail sans erreur, candidat présent, W3 prêt, aucune fermeture structurelle critique manquante, mais `llm_activation.required=false` et résolution sémantique encore requise. Résultat reproduit :

```
status = SEMANTIC_RESOLUTION_REQUIRED
sufficient = false
model_required = false
reason = BRODY_PRE_REASONING_RESOLUTION_REQUIRED
next_stage = HUMAN_REVIEW
```

La condition est précisément : `not model_route_required and semantic_resolution_required`. Le second booléen vaut `reasoning_directive.resolution_required OR qualified_unresolved_unknowns non vide`. Le routeur ALLOW n'atteste donc pas la clôture sémantique. Une autre branche refuse d'abord les champs critiques `intent`, `target_layer`, `intention_cible` manquants. Le fichier et son empreinte sont enregistrés dans `semantic_gate_reproduction.json`.

Cette reproduction est **SYNTHETIC_GATE_REPRODUCTION_NO_COGNITIVE_RUNTIME**, pas un deuxième essai cognitif ni une observation d'Ingress sur la question réelle. Le gateway actuel importe directement le runtime Python producteur : il n'achemine pas son appel natif via l'API HTTP authentifiée de Brody, et la signature `run_cognitive_ingress` ne prévoit pas d'injection d'une réponse HTTP précalculée. Aucune deuxième cognition n'a été ajoutée pour combiner ces interfaces.

## Services et choix du parcours réel

Au début, Brody PID 16668 avait ses variables d'authentification absentes ; GET `/openapi.json` répondait 200 sans clé. Le conserver aurait contredit le besoin d'un Brody authentifié. Il a été relancé avec le Python autonome déjà utilisé, la même copie figée et le mécanisme existant `APP_ENV=dev`, `OBSIDIA_AUTH_ENABLED=true`, clé DPAPI existante en environnement. Aucun fichier producteur modifié. Absence de reload.

Checkpoint du service Brody : **cbad01257c027e5861a1c0610d418dfd02fc8342**. Avant et après l'essai : 1526 fichiers vérifiés avec le manifeste épinglé `d64f9ac43d1157c52876ea8f265a26fddd95b80b8c6114504d152e88ab5fb26a`. Le HEAD concurrent 9113300 n'est pas présenté comme celui de ce service figé.

Avant tout appel réel, le mode existant **brody_native** a été explicitement choisi pour exercer Studio → API Brody authentifiée. Il ne s'agit pas d'un retry après un refus Ingress. Studio a été relancé pour charger la réparation et la clé ; Ingress et Qwen restent inchangés et ne sont pas appelés. La réponse native conserve ses frontières et peut être refusée ; aucune suffisance ou clôture n'est fabriquée.

| Service final | PID | Port | Configuration |
|---|---:|---:|---|
| Brody | 30544 | 8000 | Clé présente, AUTH_ENABLED=true, localhost ; OpenAPI sans clé 401, avec clé 200. |
| Studio | 19600 | 8108 | brody_native, clé sortante présente, LOT1=0, autopilot désactivé, modèle local désactivé. |
| Cognitive Ingress | 19708 | 8110 | Processus existant conservé, non appelé. |
| Qwen local | 27828 | 8080 | Processus existant conservé, non appelé par cette expérience. |

Les routes POST generate et E11 sont présentes. Le code natif refuse les redirections et les proxies pour éviter de transférer la clé. Aucun secret affiché, ajouté aux arguments, enregistré en rapport ou commité.

## ESSAI RÉEL UNIQUE / PUBLICATION

Question utilisée, sans modification : « Comment une petite entreprise des Ardennes peut-elle utiliser l'intelligence artificielle pour gagner du temps sans gros budget ni compétences techniques ? »

**Un POST Studio `/api/generate` → un POST Brody `/api/brody/chat`.** Les traces d'accès attestent HTTP **200 chez Brody**, puis HTTP **409 chez Studio**. Latence client : **4793,959 ms**. Zéro retry, zéro fallback, zéro POST E11, aucun appel direct supplémentaire à Brody.

Diagnostic exact remonté :

```
Brody a répondu sans artefact éditorial <POST>.
Aucun brouillon produit.
final_answer_source=B6_ADVISORY_CONTEXT
source=PRE_REASONING_UNRESOLVED_SYMBOL
```

**BRODY RÉDACTEUR : non prouvé pour cet essai. PUBLICATION : aucun texte éditorial produit à présenter.** La restitution consultative n'est ni un brouillon original ni une réussite de rédaction.

Dans le checkpoint réellement servi, `apps/obsidia_api/brody_real_response_pipeline.py` sélectionne `PRE_REASONING_UNRESOLVED_SYMBOL` lorsque `resolution_required` est vrai, `resolution_targets` est non vide et la demande n'est pas une commande terminale commençant par `:`. Cette branche construit une réponse de non-résolution et empêche le responder normal de traiter le symbole comme connu.

`apps/obsidia_api/brody_true_voice_adapter.py` choisit `B6_ADVISORY_CONTEXT` quand le contexte B6 contient des états non résolus. Cette branche préserve l'incertitude au lieu de produire un post. Les noms individuels des symboles non résolus ne sont pas conservés dans notre diagnostic minimal ; ils ne sont pas inventés. On ne peut pas répartir précisément la dette entre le sujet et les instructions éditoriales sans autre preuve.

La réparation restante relève d'un contrat producteur de rédaction et de résolution sémantique opérationnel, compatible avec l'intention réelle. Retirer cette intention, rebaptiser le contexte B6 en publication, forcer BRODY_SUFFICIENT ou remplacer le rédacteur par Qwen contournerait le problème. Aucun de ces contournements n'a été appliqué.

## État final et limites

Studio reste **LOT1=0**, autopilot désactivé ; Brody reste authentifié. Aucun contenu publié sur Internet, aucune nouvelle campagne E11, aucun commit/push, aucun changement KX108. Les sources productrices sont intactes ; la vérification du manifeste ne porte pas sur les fichiers de sessions non suivis. Comme documenté précédemment, un appel Brody peut écrire un ledger de session dans sa copie sous Studio et un timeout ne garantit pas son annulation.

Artefacts sous `data/experiments/brody_editorial_repair_20261017` : `reconciliation.json`, `changes_local.diff`, `studio_final.xml`, `regression_evidence.json`, `semantic_gate_reproduction.json`, `service_report.json`, `trial_result.json`, `final_checks.json`. Aucune réponse productrice intégrale ni clé n'y a été ajoutée. Le marqueur `single_trial.started` empêche le script d'effectuer une deuxième tentative.

**KX108_ONLY — BRODY_AUTHOR_REQUIRED — NO_BRODY_DRAFT — PRODUCER_SEMANTIC_RESOLUTION_BLOCK — NO_PUBLICATION.**
