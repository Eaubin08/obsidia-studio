# OBSIDIA Studio — diagnostic 10J des limites E11 / B6 / B7 / SENS

Audit du 17 octobre 2026. Aucun POST, redémarrage, replay du parseur, import applicatif producteur, accès à l'index mémoire ou nouvelle récupération. Aucune correction runtime ni modification productrice. Seuls ce rapport et des preuves techniques sous Studio sont ajoutés. KX108_ONLY.

## Périmètre et statut des preuves

Le diagnostic porte sur les **cinq expériences 10I réellement conservées**, fournies par la copie existante du repo `Eaubin08/obsidia-x108-proofs`, branche d'origine déclarée `feat/jarvis-advanced-obsidia-integration-v0`, checkpoint `cbad01257c027e5861a1c0610d418dfd02fc8342`. Il ne constitue pas un inventaire des autres branches ou de toute la stack.

Les six empreintes d'artefacts 10I, les six empreintes du code Studio chargé pendant la campagne et le manifeste producteur de 1526 fichiers sont revérifiés. Détails : `data/experiments/e11_lot1/passe10j/audit_evidence.json`. Le manifeste producteur reste `d64f9ac43d1157c52876ea8f265a26fddd95b80b8c6114504d152e88ab5fb26a`.

Sources : `RAPPORT_CAMPAGNE_E11_10I.md`, `passe10i/campaign_result.json`, `run_report.json`, `privacy_and_ledger_check.json`, `campaign.py`, les événements existants et le code figé référencé ci-dessous. Le reçu complet n'a pas été persisté ; les ledgers fournisseur contiennent une trace de question/réponse, pas un substitut du reçu E11 intégral. Les règles sont lues, jamais réexécutées pour inventer un reçu manquant.

Notation : **OBSERVÉ** = enregistré pendant 10I ; **DÉDUIT** = conséquence des observations et du code vérifié ; **STATIQUE** = capacité/règle présente dans ce checkpoint ; **INCONNU** = donnée non conservée. Une déduction n'est pas une nouvelle observation runtime.

## Reconstruction des cinq scénarios

Les fixtures publiques restent disponibles dans `passe10i/campaign.py::CASES` ; aucun texte privé n'est recopié dans ce rapport.

| Cas | Objectif de la fixture | HTTP / verdict | Mémoire | État SENS observé | Inconnues / omissions B6 | Demandes E11 |
|---|---|---|---|---|---|---:|
| A | Rôles de Brody, mémoire native et KX108 | 200 / LIMITED | NOT_REQUIRED, 0 item | 1 OPEN, 0 ERROR | 1 / 0 | 1 |
| B | Rappel documentaire explicite sur ces rôles | 200 / LIMITED | USABLE, 5 items | 1 OPEN, 0 ERROR | 1 / 5 | 1 |
| C | Coréférence potentiellement ambiguë de « il » | 200 / LIMITED | NOT_REQUIRED, 0 item | 1 OPEN, 0 ERROR | 1 / 0 | 1 |
| D | Deux affirmations opposées sur la validation d'un dossier | 200 / LIMITED | NOT_REQUIRED, 0 item | 1 OPEN, 0 ERROR | 1 / 0 | 3 |
| E | Frontière entre contexte consultatif et action/publication | 200 / LIMITED | NOT_REQUIRED, 0 item | 1 OPEN, 0 ERROR | 1 / 0 | 2 |

Dans les cinq cas : reçu C1 V1 présent et accepté, E11/B6 contractuellement valides, B6 limité, décision consultative CONTEXT_ALLOWED, aucune permission de publication, reçu DEGRADED et surfaces indisponibles signalées. Aucun snapshot M41 non vide observé.

## A. Les cinq omissions B6 du cas B

### Ce qui peut maintenant être établi

Le rapport 10I distinguait prudemment cinq éléments récupérés et cinq états omis sans attribuer leur identité. **La lecture des règles permet de préciser la catégorie et le motif par déduction**, sans retrouver leurs identifiants.

Chaîne de justification, dans le checkpoint vérifié :

1. E11 construit exactement une entrée SENS et adapte les cinq éléments mémoire observés : six entrées au total. Le registre B6 n'ajoute pas d'autre catégorie dans cette composition (`cognition_shadow_memory_v0.py::run_cognition_shadow_with_memory`).
2. La limite est 64 entrées : `ENTRY_LIMIT` est exclu ici. L'entrée SENS observée est OPEN ; elle est LONG dans l'adaptateur. Les éléments mémoire valides sont LONG. Les branches d'erreur mémoire sont visibles comme ERROR/UNKNOWN, mais B6 ne compte qu'un état non KNOWN, déjà SENS : les cinq autres sont donc KNOWN. `visibility_hide` est exclu.
3. `project_entries` inclut systématiquement un état non KNOWN non caché. Avant toute réduction de taille, SENS est donc inclus. Pour les cinq entrées mémoire KNOWN, les seuls résultats restants sont `tag_match` ou `irrelevant_to_query` : elles portent toujours au moins le tag `native_memory`.
4. Une omission pour dépassement de taille ne peut survenir qu'après réduction de **toutes** les entrées encore incluses à SHORT, avec raison `PACKET_SIZE_LIMIT:reduced_to_SHORT`. Toute entrée restante garderait cette raison et Studio produirait `B6_REDUCED_VISIBILITY`.
5. Ce motif n'est présent dans aucune réponse 10I. B6 n'est pas vide : deux références de provenance sont observées et `assemble_context` ne les construit qu'à partir d'entrées exposées. Il n'y a donc ni réduction de taille restante ni omission `PACKET_SIZE_LIMIT` dans ce cas.
6. SENS reste inclus ; les cinq omissions sont donc les cinq entrées mémoire, chacune par `irrelevant_to_query`. La provenance B6 limitée aux deux références SENS est cohérente avec cette déduction.

Ce raisonnement dépend des règles et métadonnées vérifiées, pas du seul compteur « 5 ». Il ne récupère ni les noms de documents, ni les tags effectifs, ni le contenu des éléments. Aucun index n'a été relu pour les reconstituer.

| Repère d'audit* | Catégorie | Motif déduit | Provenance connue / inconnue | Attendu ou problématique | Impact Studio |
|---|---|---|---|---|---|
| O1 | NATIVE_MEMORY_ITEM | irrelevant_to_query | Adaptateur natif connu ; source documentaire et state_id inconnus | Attendu selon la règle de tags ; qualité de l'exclusion non vérifiable | Absent du paquet B6 projeté ; conservé dans E11.memory_entries |
| O2 | NATIVE_MEMORY_ITEM | irrelevant_to_query | Même provenance technique ; document individuel inconnu | Même distinction | Même impact |
| O3 | NATIVE_MEMORY_ITEM | irrelevant_to_query | Même provenance technique ; document individuel inconnu | Même distinction | Même impact |
| O4 | NATIVE_MEMORY_ITEM | irrelevant_to_query | Même provenance technique ; document individuel inconnu | Même distinction | Même impact |
| O5 | NATIVE_MEMORY_ITEM | irrelevant_to_query | Même provenance technique ; document individuel inconnu | Même distinction | Même impact |

\* O1–O5 sont des repères rédactionnels, **pas** les state_id d'origine ni les rangs de retrieval. Leur correspondance avec chaque document est INCONNUE.

Provenance technique de ces entrées : `apps.obsidia_api.brody_obsidia_native_memory`, portée par `native_memory_state_entries`. Le `source_ref` documentaire individuel est conservé dans la réponse originale mais absent du résumé persistant.

### Cause de l'écart retrieval → projection

Native Memory classe par correspondances de titre, source/chemin, texte et tags, avec sous-chaînes et variantes underscore (`_score_record`). B6 compare seulement l'intersection des tokens de la question avec les **tags entiers** de l'entrée. L'adaptateur met les tags en minuscules ; B6 ne décompose pas un tag composé en ses mots pour cette comparaison.

Ainsi « matériau récupéré » n'implique pas « état sélectionné par B6 ». La déduction précise ici que l'intersection était vide, sans dévoiler les tags. Cela constitue un point de compatibilité entre politiques existantes ; l'exactitude documentaire des cinq exclusions reste inconnue.

Studio ne perd pas ces éléments au transport : le résultat contient `original_receipt` et `e11_context.memory_entries`. En revanche, un futur consommateur éditorial qui ne lirait que `context_packet.state` ne recevrait pas ces cinq éléments. Il faut rendre cette différence visible, sans réinjecter silencieusement les éléments omis dans B6 ni appeler de nouveau la mémoire.

## B. L'inconnue commune

**OBSERVÉ :** un état SENS OPEN et une entrée B6.unknowns dans chaque cas ; zéro état SENS ERROR. **DÉDUIT :** l'entrée unknowns est l'état `sens:frame`, produit par `sens_state_entries`, puis ajouté à unknowns par `assemble_context` dès que son statut n'est pas KNOWN. Elle ne provient ni d'une indisponibilité NPL/Lyapunov ni d'un défaut de retrieval.

Sa signification exacte est **non-fermeture de l'analyse SENS**, pas « une connaissance factuelle manquante ». L'adaptateur choisit OPEN quand `not semantic_closure.closed or not frame.closure`. Les raisons possibles comprennent : absence d'unité prédicative, contenu non analysé, références ouvertes, ambiguïtés, contradictions, obliques non résolus et raisons de la couche événementielle.

Le mécanisme B6 est générique : **une entrée d'état non KNOWN produit une entrée unknowns**, quelle que soit la quantité de raisons à l'intérieur. D et E ont chacun deux marqueurs missing mais toujours une seule entrée unknowns. Le compteur ne mesure donc pas le nombre de questions cognitives ouvertes.

Les libellés de `uncertainty`, les booléens de fermeture et le nombre de prédicats n'ont pas été conservés. Attribuer rétrospectivement `no_predicate_unit` aux cinq cas serait injustifié. C'est un mécanisme possible, pas une observation. Une non-fermeture peut refléter une limite de couverture grammaticale plutôt qu'une ambiguïté correctement détectée dans le sens de la question.

## C. Demandes E11 non résolues

E11 expose `resolution_requests` en appelant **B7.detect_unresolved sur les entrées SENS uniquement**, jamais sur les cinq éléments mémoire. B7 lit les marqueurs explicites ; il ne relit pas la question et n'utilise pas de modèle.

| Cas | Quantité observée | Informations permettant de borner l'origine | Informations absentes |
|---|---:|---|---|
| A | 1 | Aucun marqueur des quatre listes comptées ; état OPEN | Champ d'origine, kind, problem_refs, why_resolution_needed |
| B | 1 | Même profil ; requête non dérivée des items mémoire | Mêmes absences |
| C | 1 | Aucune ambiguïté/unresolved_reference explicite dans les compteurs | Impossible d'affirmer qu'il s'agit d'une demande de coréférence |
| D | 3 | Deux valeurs missing ; zéro contradiction/ambiguïté/unresolved_reference explicite | Identité/déduplication des missing et origine des autres marqueurs non sauvegardées |
| E | 2 | Deux valeurs missing ; mêmes zéros dans les autres listes | Même limite d'identification |

`_markers` examine aussi `semantic_closure.reasons` hors préfixe `frame:` et les obliques UNRESOLVED du semantic_frame, surfaces **non comptées par le client 10I**. S'il n'y a aucun marqueur et que l'état est OPEN/UNKNOWN, B7 crée une demande générique `OTHER_EXPLICIT_UNRESOLVED`, origine `status`.

Les listes sont dédupliquées avant création des demandes. Deux valeurs missing dans un compteur ne permettent pas, sans les valeurs, d'attester qu'elles sont distinctes. Pour D, on ne peut donc pas affirmer « deux demandes missing + telle troisième demande » ; pour E, « deux demandes missing » n'est pas démontré. De même, une unique demande A/B/C peut venir du fallback générique ou d'un champ non compté.

**Identification précise des demandes historiques : impossible au-delà de ces bornes.** Leur contenu existe dans le contrat et a été transmis à Studio, mais n'a pas été persisté. Aucun replay ni nouvel appel n'a été effectué pour remplacer cette preuve manquante.

## D. Dégradation C1

**OBSERVÉ :** `receipt_completeness=DEGRADED` et `RECEIPT_SURFACES_UNAVAILABLE` dans les cinq cas. Le consommateur n'accepte que le reçu READY_SHADOW_READONLY, le composant E11 OK et une liste d'erreurs publiques vide.

**STATIQUE / DÉDUIT du chemin exécuté :** la jointure C1 initialise et ne réaffecte pas :

- NPL = `SKIPPED_NOT_AVAILABLE:NPL_RUNTIME_NOT_MATERIALIZED` ;
- LYAPUNOV = `SKIPPED_NOT_AVAILABLE:NO_STRUCTURED_METRICS_FROM_UPSTREAM`.

Son calcul de complétude retourne DEGRADED si au moins un composant commence par SKIPPED_NOT_AVAILABLE, ou si errors est non vide. Ces deux surfaces suffisent donc à expliquer les cinq complétudes dégradées, indépendamment de SENS, B6, B7 et du résultat mémoire.

Il n'est pas justifié d'attribuer **toute** la dégradation à elles seules : d'autres surfaces peuvent être indisponibles, et le détail components n'a pas été persisté. SIGMA peut par exemple être marqué indisponible si domaine absent/non pris en charge ; son état exact par cas est inconnu. La route filtre aussi les diagnostics d'erreur avant exposition : errors public vide n'est pas une preuve qu'aucune erreur interne n'a jamais existé.

Cette dégradation est une complétude déclarée de la jointure, pas une panne E11, un refus KX108 ni une autorisation de reconstruire NPL/Lyapunov dans Studio.

## E. Surfaces : disponible / exécutée / observée / non démontrée

| Surface du déploiement figé | Disponible dans le code/contrat | Exécution établie | Observation 10I | Non démontré / indisponibilité |
|---|---|---|---|---|
| SENS → état | Oui | Cinq appels par la composition E11 | Un OPEN, zéro ERROR par cas ; compteurs de marqueurs | Compréhension générale, fermeture exacte et raisons textuelles |
| B6 | Oui | Cinq assemblages | Contrat valide, un unknown ; cinq omissions pour B | Pertinence sémantique globale ; libellés/source individuels absents |
| B7 — détecteur | Oui | Demandes générées par E11 | Comptes 1/1/1/3/2 | Identification précise des demandes, justesse du diagnostic |
| B7 — candidats/validation | Présent dans une composition conditionnelle Brody | Non attesté par les métadonnées | Aucun verdict candidat conservé | Résolution effective / validation cognitive |
| E11 | Oui, déjà composé à SENS/B6/B7 | Cinq fois | Schéma et frontières acceptés ; snapshot mémoire partagé | Aucun caractère de publication finale |
| Native Memory | Oui | Retrieval effectif pour B ; retour NOT_REQUIRED pour les autres | Cinq items pour B, activation MEMZUM true, axe 0,85 | Vérité des éléments ; sources individuelles non enregistrées |
| NPL, surface C1 | Emplacement déclaré, runtime non matérialisé selon C1 | Aucun calcul NPL attesté par cette jointure | Indisponibilité agrégée observée | Capacité NPL utilisable sur ce chemin non démontrée |
| Lyapunov, surface C1 | Emplacement déclaré, métriques structurées amont absentes selon C1 | Aucun calcul attesté | Même limite d'observation agrégée | Capacité Lyapunov utilisable sur ce chemin non démontrée |
| M41 | Types et composition conditionnelle présents | Non attesté pour la construction d'hypothèses | Aucun snapshot non vide | Ni hypothèses exploitables ni validité démontrées |
| KX108 — frontière consultative | Contrôles et ticket dry-run disponibles | Vérifiés dans les cinq consommations | CONTEXT_ALLOWED, publication false | Aucun exercice runtime HOLD/BLOCK pendant cette matrice ; pas d'autorisation d'action |

« Indisponible dans la jointure C1 de ce checkpoint » n'est pas « absent de tous les dépôts/branches ». Aucune nouvelle recherche multirepos n'est menée ici.

M41 exige une demande B7 COREFERENCE et d'autres conditions avant de produire son snapshot. Une exception est absorbée par None. En outre, les résultats `_res1`/`_res2` des validations B7 ne conditionnent pas la construction des deux hypothèses. Aucune de ces branches n'est attestée par un snapshot vide/absent ; les champs existants ne prouvent pas la capacité.

## F. Pourquoi C et D n'exposent pas les marqueurs visés

### C : ambiguïté du pronom sujet

Le contrat sait porter ambiguities, unresolved_references et les demandes de COREFERENCE. Mais `_resolve_references` travaille principalement sur des **arguments objets PRONOUN** d'unités reconnues ; la règle de sujet relatif « qui » est un autre cas spécifique. Cela ne constitue pas une résolution générale du pronom sujet « il » dans une suite libre de phrases.

Le lemme `concerner` n'est pas dans le lexique de ce checkpoint. Les copules attributives comme « est incomplet » sont traitées par des règles d'analyse partielle distinctes, pas par une compréhension générale de propriétés d'objet. Ces limites structurelles et lexicales rendent le scénario C peu couvert par le chemin effectivement disponible.

**Observé :** zéro marqueur explicite d'ambiguïté et de référence non résolue, un état OPEN et une demande. **Non établi :** la séquence exacte de branches de parsing qui a produit cet état. Studio n'a pas supprimé un marqueur explicite compté : le compteur extrait directement les listes de l'entrée SENS reçue et indique zéro.

### D : contradiction factuelle/passive

`_contradictions` détecte une incompatibilité ciblée **requête positive vs interdiction négative** sur un prédicat et des objets compatibles. Ce n'est pas un détecteur général de deux assertions factuelles opposées.

Un autre mécanisme, `_occurrence_conflict_candidates`, peut signaler dans ambiguities un conflit d'occurrence entre deux clauses ASSERTED, chacune avec une unité reconnue et une signature strictement comparable. Il ne suffit pas d'avoir « X est validé / X n'est pas validé » dans le texte : la représentation de ces unités doit exister.

Le lexique ne connaît pas `valider` ni `présenter` dans ce checkpoint. La grammaire garde certaines copules/constructions non analysées comme missing au lieu d'inventer leur sémantique. Les deux missing observés sont cohérents avec cette couverture limitée, mais leurs libellés exacts ne sont pas conservés : on ne les attribue donc pas formellement aux deux clauses sans preuve.

**Conclusion :** aucune contradiction explicite n'a été observée dans les champs SENS mesurés. Un état OPEN ou trois demandes ne prouvent pas que la contradiction visée a été reconnue. Le problème n'est pas réparable en traduisant ces compteurs en « contradiction détectée » côté Studio.

## G. Pertes d'information côté Studio

| Passage | Données / réduction | Diagnostic |
|---|---|---|
| Native Memory → B6 | Les cinq éléments du cas B sont exclus de la projection par tags | Sélection productrice réelle ; pas une suppression du transport Studio |
| État complet → vue B6 LONG | `render_entry` peut limiter payload_preview à 2048 caractères et marque payload_truncated | Réduction explicite prévue au contrat ; fréquence 10I non enregistrée. Les états complets restent dans E11.state_entries/memory_entries |
| Brody → résultat Studio accepté | deepcopy du reçu public et sous-objet E11 | Pas de suppression de ces champs par le consommateur principal |
| Résultat complet → résumé client/journal | Libellés unknowns, state_id/motifs détaillés d'omission, champs B7 et détail components non sauvegardés | Perte de capacité d'audit historique, volontaire pour confidentialité mais trop agrégée |
| État SENS → compteurs de campagne | Listes missing/ambiguities/contradictions/unresolved_references seulement | semantic_closure.reasons et obliques non comptés ; impossible d'identifier toutes les demandes |
| Enveloppe Brody externe → API LOT1 | Certaines surfaces top-level ne sont pas recopiées si absentes du reçu | Périmètre consommateur, pas disparition des capacités du fournisseur |

Les marqueurs peuvent donc exister dans **les contrats et la réponse en mémoire** sans être retrouvables dans les rapports. En revanche, des compteurs explicitement nuls dans les listes SENS lues ne doivent pas être interprétés comme des marqueurs positifs perdus par la seule journalisation.

## H. Carte des capacités réellement accessibles à Studio

1. **Accessible et observé :** appel Brody authentifié local, reçu cognitif public, E11 JSON, états SENS, assemblage B6, conservation de provenance/inconnues/omissions, détection mécanique de demandes B7, activation mémoire sélective et retrieval documentaire avec cinq éléments pour B.
2. **Accessible avec une limite de projection :** matériau mémoire brut déjà présent dans E11.memory_entries ; il n'est pas sélectionné dans B6 sur le cas B. Une restitution Studio doit distinguer ces deux surfaces, sans transformer leur désaccord en validation factuelle.
3. **Diagnostic disponible, sémantique non démontrée :** résolution de l'ambiguïté C, détection de la contradiction D, candidats/validations B7, hypothèses M41. Les compteurs ne constituent pas ces capacités.
4. **Non utilisable dans cette composition selon C1 :** NPL non matérialisé et métriques Lyapunov structurées non fournies. Ne pas les reconstruire ni masquer leur absence.
5. **Hors résultat de cette campagne :** brouillon éditorial abouti, autorisation d'action, écriture mémoire canonique, génération/publication automatique. Le contexte consultatif demeure non souverain ; KX108_ONLY reste l'autorité.

## I. Corrections Studio proposées — non implémentées pendant 10J

Priorité minimale : améliorer l'observabilité de la **même réponse**, pas rappeler Brody ni la mémoire.

| Correction proposée | Fichiers envisageables | Garde de confidentialité / gouvernance |
|---|---|---|
| `omission_reason_counts` et `omission_state_type_counts` en rapprochant en mémoire state_id et entrées E11 | studio_e11_diagnostic_client.py + diagnostic/journal commun | N'enregistrer que des catégories fermées ; aucun ID, titre, chemin, excerpt ni hash de contenu privé |
| Compte des unités SENS, booléens de fermeture, catégories de raisons de fermeture | Même seam diagnostique | Codes de préfixes fermés uniquement ; aucun suffixe de marqueur libre ; inconnu → catégorie UNKNOWN, pas résolution |
| Compteurs B7 par unresolved_kind et champ d'origine, distinction demande générique OPEN vs problème nommé | Même seam et tests Studio | Aucun problem_ref, why_resolution_needed libre ou identifiant candidat persisté ; aucune promotion de candidat |
| Détail par composant C1 normalisé en READY / UNAVAILABLE / SKIPPED_BY_POLICY / ERROR / UNKNOWN | Contrat/résumeur/journal commun | Ne pas réinterpréter DEGRADED comme COMPLETE ; UNKNOWN ne constitue pas un succès |
| Compte de vues B6 tronquées/réduites et comparaison « récupéré / projeté / omis » | Résumeur existant | Aucun re-ranking ni réinjection automatique des éléments omis ; pas de second retrieval |
| Explication des limites dans le laboratoire Studio | Documentation/restitution diagnostique existante | Étiqueter explicitement état ouvert, document pertinent, preuve factuelle et hypothèse non validée |

Le transport principal et la gouvernance n'ont pas besoin d'être assouplis. Les limites lexicales et règles de cognition restent celles du fournisseur. Ne pas ajouter dans Studio un second détecteur de coréférence/contradiction pour « réparer » la campagne, ni modifier les tags pour forcer B6 à sélectionner les résultats.

Tests proposés pour cette correction : fixtures sans réseau couvrant tous les motifs d'omission connus, IDs absents/inconnus, closure sans prédicat, OPEN générique, catégories B7 inconnues, composants manquants, payload_truncated, confidentialité et non-mutation du reçu, HOLD/BLOCK. Aucune fixture ne doit être présentée comme une observation du reçu historique manquant.

## Références précises de code

Préfixe producteur local : `C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/`. Tous les fichiers P ci-dessous correspondent au repo/branche/SHA indiqué en tête, revérifié par manifeste.

| Réf. | Chemin / fonction | Points d'appui |
|---|---|---|
| P1 | app/integration/cognition_shadow_memory_v0.py::run_cognition_shadow_with_memory | L46 : composition, un snapshot partagé, requêtes B7 sur SENS uniquement |
| P2 | app/harness/state_explicit/projection.py::project_entries | L78 : entrée non KNOWN exposée, HIDE, limite et tags exacts |
| P3 | app/harness/state_explicit/context_assembly.py::assemble_context | L70 ; unknowns L86 ; références des seules entrées exposées L99–102 ; boucle réduction/omission L106–121 |
| P4 | app/harness/state_explicit/contracts.py | L30–34 : bornes ; render_entry L167 : vue LONG et troncature |
| P5 | app/harness/state_explicit/memory_adapter.py::native_memory_state_entries | Catégories, provenance technique, KNOWN/LONG et tags natifs |
| P6 | app/harness/state_explicit/sens_adapter.py::sens_state_entries | L44 : OPEN, payload complet, raisons et provenance SENS |
| P7 | app/semantic/lattice/semantic_closure.py::semantic_closure ; primitives.py::closure_blockers/closure | L42 et L343–361 : fermeture sémantique distincte de la vérité |
| P8 | app/cognition/b7/detector.py | classify_marker L36 ; _markers L65 ; detect_unresolved L81 |
| P9 | app/semantic/lattice/french_grammar.py | _copula_evidence L560 ; parse_utterance L2443 ; _resolve_references L4239 ; _occurrence_conflict_candidates L4318 ; _contradictions L4349 |
| P10 | app/semantic/lattice/lexicon.py | LEMMAS et tables : absence concerner/valider/présenter ; lookup retourne vide pour forme inconnue |
| P11 | apps/obsidia_api/brody_real_cognitive_join.py::run_real_cognitive_join | NPL/LYAPUNOV L781–785 ; complétude L1574–1591 |
| P12 | apps/obsidia_api/routes/brody.py::brody_chat | B7/M41 L961–1059 ; filtrage des erreurs et exposition du reçu L1864–1909 |
| P13 | apps/obsidia_api/brody_obsidia_native_memory.py::_score_record | L200 : ranking distinct du filtre B6 |
| S1 | C:/Users/User/obsidia-studio/studio_e11_contract.py::consume_envelope | Copie intégrale et motifs B6_OMISSIONS/B6_REDUCED_VISIBILITY ; refus conservés |
| S2 | C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10i/campaign.py::observations | Compteurs effectivement sauvegardés, sans détail des omissions/requêtes |
| S3 | C:/Users/User/obsidia-studio/studio_e11_diagnostic_client.py ; studio_experiment_journal.py | Résumé minimal et listes blanches ; aucun reçu intégral persisté |

## FAIT / PROUVÉ / INCERTAIN / RESTANT

**FAIT :** cinq scénarios reconstruits depuis les métadonnées, code de projection/fermeture/détection lu au checkpoint vérifié, diagnostic A–I rédigé. Aucun appel, redémarrage, replay cognitif, nouveau retrieval, code runtime modifié, commit ou push.

**PROUVÉ :** artefacts et code intègres ; inconnue commune = état SENS OPEN ; contrat de demandes présent et comptes 1/1/1/3/2 ; complétude DEGRADED observée avec causes structurelles NPL/Lyapunov ; préservation du reçu par Studio. Catégorie et motif des cinq omissions déduits des règles et observations, sans identité documentaire reconstruite.

**INCERTAIN :** sources et IDs individuels des omissions, pertinence réelle de leur exclusion, raisons textuelles de fermeture, contenu exact et types de chaque demande B7, inventaire runtime complet des composants, branches de parsing exactes pour C/D, exécution/validité M41. Ces informations ne sont pas récupérées par invention ou nouvel appel.

**RESTANT :** enrichir uniquement les métadonnées diagnostiques fermées et leurs tests hors réseau si cette suite est engagée. Conserver la distinction récupéré/projeté/omis, le reçu d'origine, les refus et KX108_ONLY.

**Prochaine étape proposée :** une passe Studio limitée à l'observabilité listée en I et aux tests synthétiques, sans campagne cognitive, sans changement producteur ni nouveau système. Ne pas relancer automatiquement 10I. Aucun autre chantier n'est lancé par le présent audit.

VERDICT : AUDIT_10J_COMPLETED_WITH_EXPLICIT_EVIDENCE_LIMITS / NO_POST / NO_RESTART / NO_RETRIEVAL / PRODUCERS_READ_ONLY / KX108_ONLY.
