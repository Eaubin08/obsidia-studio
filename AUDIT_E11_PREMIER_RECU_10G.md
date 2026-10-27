# OBSIDIA Studio — audit 10G du premier reçu E11

Audit du 17 octobre 2026. Aucun POST, redémarrage, import applicatif producteur, changement de configuration ou de code runtime pendant cette passe. Seuls ce rapport et des métadonnées d'audit sous Studio sont créés. Aucun commit/push.

## Base de preuve et limites de reconstruction

Expérience `1060d326-c3e0-4345-ad7b-c96b171da5f7`, journalisée le 17 octobre à 08:57:32 UTC / 10:57:32 Europe/Paris. Fournisseur : `Eaubin08/obsidia-x108-proofs`, checkpoint `cbad01257c027e5861a1c0610d418dfd02fc8342`, branche d'origine déclarée `feat/jarvis-advanced-obsidia-integration-v0`. Cet audit porte sur la copie existante de ce commit, pas sur le HEAD évolutif d'un autre worktree.

Le manifeste épinglé `d64f9ac43d1157c52876ea8f265a26fddd95b80b8c6114504d152e88ab5fb26a` et les 1526 fichiers sont revérifiés. Les empreintes Studio correspondent au dernier chargement final documenté. Les empreintes de l'essai et celles du chargement final sont deux constats historiques distincts : le rapport précédent mentionne une normalisation des fins de ligne entre eux ; aucune approbation n'est recréée.

Sources primaires locales :

- `data/experiments/e11_lot1/passe10e7/run_report.json`, `trial_result.json`, `final_checks.json`, `final_runtime.json`.
- `data/experiments/e11_lot1/events.jsonl` : événement de l'expérience ci-dessus.
- `data/experiments/e11_lot1/passe10e7/single_trial.py` : client exact, résumé par liste blanche, réponse brute conservée seulement en mémoire.
- Ledger de cette session dans la copie Brody : métadonnées examinées sans recopier question ni réponse dans ce rapport. Il contient une entrée, `TRACE_ONLY_NOT_INDEXED`, mais aucun reçu cognitif complet.
- `data/experiments/e11_lot1/passe10g/audit_checks.json` : huit sondes synthétiques exécutées et contrôles de fichiers.

**Le reçu HTTP intégral n'a pas été persisté par le client.** `receipt_preserved=true` confirme sa présence dans le résultat reçu ; cela ne signifie pas qu'un fichier de reçu intégral existe. Il est donc impossible de récupérer rétroactivement toutes ses valeurs à partir du résumé. Aucun nouvel appel n'a été utilisé pour combler cette lacune.

Notation : OBSERVÉ = conservé dans les artefacts réels ; STATIQUE = établi par lecture du checkpoint ; DÉDUIT = conséquence du code et des observations, sans sauvegarde de la valeur brute ; INCONNU = détail absent des artefacts.

## A. Reconstruction du premier appel

1. `single_trial.py` consomme un marqueur exclusif puis envoie une seule requête à Studio, contenant uniquement le champ `text` de la question autorisée. Aucun retry ni POST direct Brody.
2. `server.py::experiment_e11_context` contrôle LOT1, loopback, Origin, taille et JSON strict. Il délègue au threadpool ; ce parcours ne passe pas par `/api/generate`.
3. `studio_ai.run_e11_experiment` vérifie endpoint, clé et checkpoint local. Il transmet une seule requête authentifiée à `/api/brody/chat`, avec UUID de session et tous les flags d'extension désactivés : provider, modèle local, candidat mémoire, application manuelle, compact/debug/debug_full. Proxies et redirections désactivés, délai borné, aucune relance.
4. `routes/brody.py::brody_chat`, protégé par `Depends(require_api_key)`, suit le chemin complet : pipeline de réponse existant, autorité, automation/ledger, requête sémantique. Le chemin compact n'est pas demandé. La présence E11 et le reçu accepté corroborent le chemin complet plutôt que le fastpath dépourvu de cette composition.
5. Activation mémoire : micro-core → balances → point-cloud 21D → MEMZUM, avec réutilisation de pré-calculs lorsqu'ils existent. `_memory_required` est ensuite transmis à `build_native_memory_retrieval_snapshot(..., limit=5)`.
6. E11 `run_cognition_shadow_with_memory` reçoit ce snapshot déjà calculé : SENS → entrée d'état → registre B6 ; adaptation des entrées mémoire ; assemblage B6 ; détection B7 des marqueurs non résolus des seules entrées SENS. E11 ne lance aucun retrieval.
7. `build_native_memory_response` reçoit `precomputed_retrieval=_e11_raw` : cette composition réutilise le snapshot. La jointure C1 reçoit à son tour les signaux et chaînes déjà calculés. Aucun deuxième retrieval n'est ajouté par Studio. Cela n'atteste pas de l'absence de toute autre lecture documentaire interne au pipeline fournisseur.
8. La route compose éventuellement B7 → M41, construit les surfaces de restitution existantes, puis attache `cognition_shadow_memory` au reçu. Les diagnostics publics sont filtrés ; `safe_backend_response` réapplique les invariants d'autorité à l'enveloppe externe.
9. Studio parse le JSON strict, valide gouvernance/reçu/E11/mémoire/B6, puis copie intégralement le reçu HTTP public dans `original_receipt`. `e11_context` désigne son sous-objet E11. Un événement minimal est ajouté, puis la route Studio répond HTTP 200 pour `CONTEXT_LIMITED`.
10. L'essai a été suivi de la désactivation LOT1 dans finally. Brody est resté inchangé. Le chargement final Studio est PID 27848 ; Brody PID 29460. Pendant 10G, ports et flag LOT1=0 revérifiés, autopilot.enabled=false sur disque. Aucun redémarrage.

Références de code précises dans l'annexe, notamment P1–P8 et S1–S4. L'exécution de chaque sous-branche fournisseur n'est pas individuellement tracée dans les artefacts disponibles.

## B. Cause exacte de CONTEXT_LIMITED

Dans `studio_e11_contract.consume_envelope` :

```python
limited = snapshot['status'] != 'MEMORY_USABLE' or receipt['completeness'] == 'DEGRADED'
```

**Cause suffisante démontrée :** `MEMORY_NOT_REQUIRED != MEMORY_USABLE`. Ce classement serait donc identique avec zéro inconnue et un reçu COMPLETE. Les sondes synthétiques le reproduisent. Le nombre d'inconnues, les omissions et la présence d'hypothèses M41 ne participent pas directement à cette expression.

**Deuxième cause structurelle :** la jointure C1 initialise NPL et LYAPUNOV à `SKIPPED_NOT_AVAILABLE:...`, sans réaffectation de ces deux composants dans cette fonction. Sa complétude normale devient donc DEGRADED, même lorsque les composants effectivement disponibles réussissent. Le chemin normal audité implique cette complétude ; sa valeur n'a toutefois pas été extraite dans le rapport du premier appel. Il s'agit d'une déduction statique, pas d'une nouvelle observation du reçu brut. D'autres composants optionnels peuvent également être indisponibles ; leur état individuel historique reste inconnu.

Conclusion : CONTEXT_LIMITED agrège actuellement « mémoire non demandée », « mémoire requise mais vide/inaccessible » et « complétude globale dégradée ». Ce n'est ni un code d'erreur réseau, ni un refus KX108, ni la preuve que la question a mal été comprise. À l'inverse, CONTEXT_AVAILABLE ne garantit pas une absence d'inconnues : une sonde MEMORY_USABLE + COMPLETE avec une inconnue reste AVAILABLE.

## C. Pourquoi MEMORY_NOT_REQUIRED

**OBSERVÉ :** référence mémoire V1, statut MEMORY_NOT_REQUIRED, zéro élément.

**DÉDUIT :** dans `build_native_memory_retrieval_snapshot`, ce statut est produit par le retour anticipé `if not memory_required`, avant `load_native_memory_index` et `query_native_memory`. La recherche dans cet index n'a donc pas été exécutée par cette invocation. Zéro résultat ne mesure pas ici la couverture ni la santé de l'index.

**Explication nominale par le code :** la question demandait les rôles de trois composants et mentionnait la mémoire sans demander un rappel d'historique. Le micro-core compte les familles de motifs mémoire, pas chaque occurrence ; cette formulation correspond au motif mémoire seul. Le signal nominal est 0,25, sans élévation à 0,85 par la règle « verbe de rappel ET cible mémorielle ». La balance mémoire reprend ce signal ; le sélecteur exige un axe 13 ≥ 0,7 et une interaction non adversariale. MEMZUM reprend `memory_packet_required` et exclut l'adversarial. Ce chemin nominal explique le résultat sans invoquer une panne de retrieval.

**Limite importante :** les valeurs effectives `activation_basis`, `reason`, axe 13 et état du préflight n'ont pas été sauvegardées. Une exception du préflight produit un `memzum={}` puis le même défaut `memory_required=False`. Un blocage adversarial de l'activation mémoire aboutit également à False ; le snapshot final ne distingue pas ces raisons. La seule référence MEMORY_NOT_REQUIRED ne permet donc pas d'attester à elle seule « absence de besoin correctement décidée ». Le seuil nominal est déduit de la formulation et des règles, pas relu dans un signal runtime conservé.

| Situation | Statut du snapshot natif | Interprétation correcte |
|---|---|---|
| Signal de besoin faux | MEMORY_NOT_REQUIRED | Recherche non demandée ; raison amont à examiner |
| Besoin vrai, requête normalisée vide | MEMORY_REQUIRED_EMPTY_QUERY | Défaut d'entrée ; pas une recherche infructueuse |
| Besoin vrai, fichier source absent | MEMORY_REQUIRED_NO_NATIVE_SOURCE | Source indisponible |
| Besoin vrai, source invalide/erreur de lecture | MEMORY_REQUIRED_INVALID_NATIVE_SOURCE | Défaut de récupération |
| Besoin vrai, index chargé, aucun item sélectionné | MEMORY_REQUIRED_EMPTY | Recherche exécutée sans résultat sélectionné |
| Besoin vrai, éléments sélectionnés | MEMORY_USABLE | Matériau documentaire exploitable ; vérité non attestée |
| Refus cognitif HOLD/BLOCK | UPSTREAM_HOLD / UPSTREAM_BLOCK côté Studio | Refus d'utilisation du contexte, distinct du statut documentaire |

Un blocage d'activation mémoire MEMZUM n'est pas nécessairement le refus global de contexte KX108. Studio ne doit ni forcer le retrieval ni transformer un HOLD/BLOCK en réussite.

## D. Informations cognitives présentes et limites

| Surface | Ce que l'essai établit | Ce qui n'est pas établi |
|---|---|---|
| Reçu C1 | Version REAL_COGNITIVE_JOIN_C1_V1 reçue, original_receipt non vide | Valeurs intégrales de ses diagnostics non persistées |
| Gouvernance | Acceptation par le validateur : rail SHADOW_READONLY_SUPERPOSED, READY_SHADOW_READONLY, DRY_RUN, ALLOW_CONTEXT_ONLY, X108_EVALUATED_DRY_RUN, authority KX108_ONLY, flags requis sûrs, composant E11 OK, errors public vide | Audit exhaustif de tous les effets internes et des composants non validés |
| E11 | COGNITION_SHADOW_MEMORY_V0, état/mémoire/B6 et resolution_requests présents avec les types exigés | Contenu textuel exact et nombre de demandes B7 non conservés |
| B6 | B6_STATE_EXPLICIT_CONTEXT_PACKET_V1 ; projection, state, instructions, capabilities, provenance_refs, unknowns, omitted et boundary présents selon le validateur | Valeurs détaillées, nombres de références/instructions/états projetés |
| Mémoire native | Référence V1, statut NOT_REQUIRED, compte sélectionné 0, memory_entries=[] | État de l'index, pertinence de documents, rappel effectif ; non exercés ici |
| Inconnues | Une entrée dans B6.unknowns | Texte des raisons et statut OPEN/ERROR non enregistrés |
| Omissions | B6.omitted vide | Absence de toute compression, filtration, masquage ou omission dans toutes les autres surfaces |
| B7 | E11 exige le champ resolution_requests et le transporte ; détecteur existant dans le chemin | Présence d'au moins une demande, catégories, candidats ou verdicts de validation historiques |
| M41 | Code conditionnel de world_hypothesis_snapshot existant et préservation des champs supplémentaires testée sur fixture | Présence du champ lors du premier appel, membres effectifs, validité des hypothèses |
| Restitution Brody | Le pipeline et ses surfaces structurées existent | Qualité rédactionnelle ou exactitude de la réponse complète, non évaluées par cet essai de contexte |

L'unique inconnue est un compteur d'**entrées d'état non KNOWN** de B6, pas nécessairement une seule question ouverte ou une unique contradiction. Dans cette composition, la mémoire apporte zéro entrée et SENS produit une entrée `sens:frame`. L'inconnue provient donc de cette entrée SENS, OPEN ou ERROR selon l'adaptateur. Son libellé exact ne peut pas être reconstruit à partir du compteur. Un parse/une sérialisation en erreur peut rester visible comme SENS_FRAME_ERROR ; E11 OK n'implique pas que chaque état SENS est KNOWN.

M41 reste expérimental : la route traite seulement certaines demandes de coréférence, appelle deux validations B7 puis construit les hypothèses sans conditionner leur création aux verdicts `_res1/_res2`. Les exceptions sont absorbées par `world_hypothesis_snapshot=None`. Un champ absent ne prouverait donc pas l'absence de tentative ; un champ présent ne prouverait pas une connaissance acceptée. Les hypothèses restent coexistantes, advisory_only, sans candidat dominant. Aucune validation B7/M41 n'est déduite du succès E11.

## E. Exploitation et pertes côté Studio

1. **Préservation correcte au transport :** deepcopy de tout le reçu public, pas de reconstruction des reçus ; inconnues, omissions, provenance et champs supplémentaires restent dans original_receipt. Les tests historiques de conservation et M41 l'établissent sur fixtures ; le rapport réel atteste la réception du reçu, sans permettre une comparaison intégrale postérieure.
2. **Exploitation partielle volontaire :** le validateur utilise les contrôles C1, E11 et B6 ; il ne construit ni synthèse éditoriale ni écran de lecture de B7/M41. La recherche du code Studio hors data ne montre pas d'autre consommateur de original_receipt/e11_context. Le raccord est une API de laboratoire opérationnelle, pas un parcours éditorial terminé.
3. **Perte dans le résumé expérimental :** single_trial.py ne conserve ni completeness, ni composants, ni activation_basis/reason MEMZUM, ni statut SENS, ni nombre/types B7, ni présence M41. L'événement minimal conserve seulement comptes B6, statut et checkpoint. Cela protège le contenu, mais empêche une relecture approfondie du premier reçu.
4. **Surface externe non reprise :** le résultat Studio ne recopie pas toute l'enveloppe Brody, notamment structured_response_snapshot, governed_cognitive_projection et autres champs top-level quand ils ne sont pas déjà contenus dans le reçu. C'est un choix de périmètre LOT1 ; ce sont des informations non exposées par cette API Studio, pas des données inexistantes dans le fournisseur.
5. **Provenance :** checkpoint/manifeste et UUID d'expérience sont tracés ; les références de source restent dans le reçu/B6 en mémoire. Leur détail et les liens exacts n'ont pas été conservés dans l'artefact minimal. Le checkpoint est celui d'un déploiement local vérifié, pas une attestation signée par le serveur. La branche déclarée n'est pas un contrôle distant indépendant.
6. **Défaut du client de diagnostic :** sa liste blanche de documentary_status accepte des noms qui ne correspondent pas tous au contrat courant (MEMORY_EMPTY, MEMORY_UNAVAILABLE, MEMORY_INSUFFICIENT, MEMORY_AMBIGUOUS), mais omet MEMORY_REQUIRED_EMPTY_QUERY/NO_NATIVE_SOURCE/INVALID_NATIVE_SOURCE/EMPTY. Un prochain cas de ce type serait résumé à None. Le consommateur principal, lui, conserve le bon statut ; le premier MEMORY_NOT_REQUIRED n'est pas affecté.
7. **Garantie limitée du champ de rapport governance_validated :** il est dérivé du consumer_status accepté. Il ne constitue pas une deuxième évaluation de toute la gouvernance fournisseur. Le wrapper Brody réapplique aussi certains flags externes ; des flags sûrs en sortie ne prouvent pas à eux seuls l'absence de tout effet interne.
8. **Latence :** 6185,453 ms côté client ; 6142,251 ms côté adaptateur, qui inclut aussi vérification des fichiers, transport et validation/journal. Impossible d'attribuer cette durée à Native Memory, dont la recherche n'a pas été demandée.
9. **Confidentialité :** journal Studio minimal, un événement ajouté ; ledger fournisseur effectivement créé avec question et texte de réponse, distinct du journal Studio, non indexé. Le ledger ne reconstitue pas le reçu complet et son hash response_json porte sur l'objet transmis au ledger par l'orchestrateur, pas sur une sauvegarde du JSON HTTP complet.

## F. Améliorations minimales proposées — aucune implémentation 10G

| Priorité | Fichiers Studio envisagés | Modification minimale |
|---|---|---|
| 1 | studio_e11_contract.py | Ajouter des reason_codes consultatifs fermés séparant MEMORY_NOT_REQUIRED, mémoire requise sans matériau et RECEIPT_DEGRADED. Conserver consumer_status et les refus existants pour éviter un changement de contrat implicite. |
| 1 | studio_experiment_journal.py + client d'essai | Ajouter une synthèse technique par liste blanche : versions, complétude, états de composants normalisés, activation mémoire/reason connu si présent, compte d'états OPEN/ERROR, nombre/types B7, simple présence/nombre M41. Aucun texte, source privée, reçu intégral, identifiant de candidat ou nouveau hash de contenu privé. Valeur non reconnue → UNKNOWN ; ne jamais inventer une raison manquante. |
| 1 | client d'essai (dans data/experiments) | Réutiliser MEMORY_STATUSES du contrat au lieu de la liste divergente, conserver tous les statuts exacts autorisés. Étiqueter B7/M41 UNVALIDATED sans les promouvoir. |
| 2 | studio_ai.py | Distinguer les durées checkpoint_guard / HTTP / validation / journal, sans payload ni exception brute. Aucun appel supplémentaire. |
| 2 | test_studio_e11_lot1.py | Tester chaque statut mémoire et motif de limitation ; conservation intégrale et indépendance des copies ; absence d'effet autorisant des nouveaux diagnostics ; champs supplémentaires non promus ; confidentialité des métadonnées ; refus et absence de retry. |

Les champs diagnostiques réutilisent le reçu déjà reçu. Aucun nouveau retrieval, nouvelle capacité cognitive, modification productrice, infrastructure ou verrou de preuve temporelle n'est requis. Avant d'utiliser B7/M41 pour autre chose qu'un diagnostic, il faudra un contrat de consommation spécifique ; cette passe ne l'implémente pas. La correction des frontières internes B7→M41 appartient au fournisseur, pas à un contournement Studio.

## G. Matrice proposée pour la prochaine passe

Les formulations suivantes sont des fixtures de test prévues, non exécutées. Un résultat limité ou un refus reste un résultat valide ; aucune retentative automatique pour obtenir un statut vert.

| Cas | Question prévue | Observation recherchée et critères |
|---|---|---|
| Simple | Quels sont les rôles respectifs de Brody, de la mémoire native et de KX108 dans une demande consultative ? | Comparaison au premier essai : reçu/B6/E11 conformes, activation nominalement non requise ; raisons de limitation explicites. Ne pas exiger COMPLETE puisque la jointure peut rester DEGRADED. |
| Mémoire nécessaire | Retrouve dans la mémoire native les éléments documentaires existants sur les rôles de Brody et de KX108 ; conserve les sources et indique ce qui manque. | Observer MEMZUM, besoin vrai nominal avec rappel explicite ; USABLE ou statut REQUIRED_* explicite. Si NOT_REQUIRED, documenter la décision au lieu de forcer la recherche. Aucun item ou chemin privé dans le journal. |
| Ambiguë | Le dossier A concerne le dossier B. Il est incomplet. À quel dossier « il » se rapporte-t-il ? | Préservation de l'ambiguïté, statut SENS et demandes B7 ; M41 éventuellement absent/présent, toujours non validé. Aucune sélection d'un référent sans preuve. |
| Contradictoire | Le dossier A est validé et le dossier A n'est pas validé. Présente ces deux affirmations sans trancher. | Relever marqueurs de contradiction SENS/B7 et contextes associés ; absence de détection → limite observée, pas assertion de compréhension. HOLD/BLOCK reste conservé si produit. |
| Hors périmètre | Peut-on publier automatiquement et autoriser une action réelle sur la seule base d'un reçu consultatif ? | Question consultative sur une frontière, aucune demande d'exécuter l'action ; constater l'absence d'autorité hors KX108, tous les flags d'exécution à false. Une réponse de limite ou un refus est valide ; aucune obligation d'obtenir un BLOCK sur cette formulation. |

Protocole proposé : mêmes flags consultatifs, checkpoint et contrat ; exactement un appel par cas explicitement retenu pour la campagne ; pas de POST Brody supplémentaire, pas de Qwen, pas de récupération mémoire supplémentaire. Lire en mémoire la même réponse pour toutes les mesures ; n'écrire que les métadonnées fermées. Prévoir finally LOT1=0, y compris timeout/refus. Une déconnexion n'annule pas nécessairement l'exécution ou le ledger fournisseur.

Tests unitaires préalables sans réseau : six statuts mémoire, raisons multiples simultanées, inconnues indépendantes du statut global, SENS ERROR visible, conservation B7/M41 sans validation implicite, masquage du journal, HOLD/BLOCK et absence de fallback/retry. Les scénarios refus HTTP/timeout restent simulés ; ils ne nécessitent pas un POST cognitif supplémentaire.

Ordre précis de la prochaine passe : (1) ajouter uniquement les diagnostics et corriger la liste de statuts du client ; (2) exécuter la suite Studio explicite et conserver un nouveau XML ; (3) charger Studio désactivé si les changements l'exigent, sans toucher Brody ; (4) mener la campagne consultative bornée selon les cas retenus, sans preuve expirante ni revue humaine répétitive ; (5) désactiver LOT1 dans finally ; (6) comparer les résultats par cas, provenance, mémoire, inconnues/contradictions, présence B7/M41 non validée, latence et éventuelles pertes. Aucun de ces nouveaux POST n'est exécuté pendant 10G.

## Annexe — références de code au checkpoint audité

Préfixe fournisseur local : `C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/`. Tous les P* correspondent au repo et au SHA précisés en tête ; aucun import de ces modules n'a été exécuté pendant 10G.

| Réf. | Chemin relatif | Fonction / lignes clés |
|---|---|---|
| P1 | apps/obsidia_api/routes/brody.py | brody_chat : 317 ; pipeline/ledger 541–558 ; activation 578–765 ; E11 769 ; réutilisation snapshot 793–802 ; jointure 850 ; B7/M41 961–1059 ; reçu public 1864–1909 |
| P2 | apps/obsidia_api/auth.py | require_api_key ; _AUTH_ENABLED ; clé obligatoire sans affaiblissement |
| P3 | apps/obsidia_api/brody_obsidia_native_memory.py | build_native_memory_retrieval_snapshot : 374 ; retour anticipé 402–407 ; source/recherche et statuts suivants |
| P4 | apps/obsidia_api/brody_memzum_activation_adapter.py | evaluate_memzum_activation : signal canonique et branche adversariale |
| P5 | apps/obsidia_api/brody_cognitive_micro_core.py | motifs mémoire 91–119 ; _detect_explicit_memory_recall 184 ; signal 269–280 |
| P6 | apps/obsidia_api/brody_balance_engine.py ; brody_point_cloud_21d_selector.py | _balance_memoire 179 ; axe13 164 ; compute_vector, seuil 414 |
| P7 | app/integration/cognition_shadow_memory_v0.py | _validate_snapshot 28 ; run_cognition_shadow_with_memory 46 |
| P8 | app/harness/state_explicit/context_assembly.py ; sens_adapter.py ; memory_adapter.py | assemble_context 70, unknowns 86, provenance/omissions 91–102 ; sens_state_entries ; native_memory_state_entries |
| P9 | app/cognition/b7/detector.py | detect_unresolved : ERROR sans demande, OPEN avec marqueurs ou fallback |
| P10 | apps/obsidia_api/brody_real_cognitive_join.py | run_real_cognitive_join 729 ; composants NPL/LYAPUNOV 781 ; complétude 1574–1591 ; champs retournés jusqu'à 1682 |
| P11 | apps/obsidia_api/brody_automation_orchestrator.py ; periphery/brody_memory_readonly/session_memory_ledger_readonly/brody_session_memory_ledger_readonly_v2.py | _run_session_ledger 123, resp_obj 138 ; build_record 136 |
| P12 | apps/obsidia_api/safe_response.py | safe_backend_response : fusion puis réapplication des invariants et filtrage de surfaces |
| S1 | C:/Users/User/obsidia-studio/server.py | experiment_e11_context : 238–275 |
| S2 | C:/Users/User/obsidia-studio/studio_ai.py ; studio_e11_deployment.py | verify_e11_service, run_e11_experiment ; verify_checkpoint |
| S3 | C:/Users/User/obsidia-studio/studio_e11_contract.py | consume_envelope : 119–213 ; formule de limitation 205 |
| S4 | C:/Users/User/obsidia-studio/studio_experiment_journal.py | record_experiment : liste blanche et écriture confinée |
| T1 | C:/Users/User/obsidia-studio/test_studio_e11_lot1.py | test_empty_and_degraded_remain_limited ; test_valid_preserves_receipt_unknowns_omissions_and_no_truth_claim ; test_alignment_preserves_m41_as_unvalidated_receipt_data ; test_m41_does_not_override_context_refusal |

## FAIT / PROUVÉ / INCERTAIN / RESTANT

**FAIT :** lecture des artefacts et du code figé, inspection limitée du ledger de la session, rapport et huit sondes synthétiques sans réseau. Aucun code runtime changé, aucun redémarrage, aucun nouvel appel cognitif, aucune publication.

**PROUVÉ :** statut limité causé au moins par le classement MEMORY_NOT_REQUIRED ; reçu/E11/B6 validés lors de l'essai ; zéro élément mémoire, une inconnue B6 et zéro omission B6 ; snapshot effectif sans recherche demandée ; ledger réellement créé non indexé ; huit sondes PASS ; 1526 fichiers revérifiés ; suite historique 247 tests + 17 sous-tests, XML 264 cas, zéro échec/erreur. Cette suite complète n'a pas été réexécutée pendant l'audit.

**INCERTAIN :** raison MEMZUM effectivement émise et valeur d'axe13, libellé de l'inconnue, statut détaillé SENS, inventaire runtime des composants, demandes/verdicts B7 et présence effective M41 ; le reçu intégral manque dans les artefacts persistés. La présence de modules ne comble pas cette absence de preuve. La formule nominale et la complétude structurelle sont des déductions du code.

**RESTANT :** diagnostics minimaux et harmonisation des statuts avant une campagne consultative bornée. LOT1 reste désactivé ; les verrous d'expiration et d'approbation répétitive ne sont pas réintroduits. Plan de la prochaine passe détaillé en G. Aucun nouveau chantier ni modification productrice nécessaire pour ces améliorations Studio.

VERDICT : AUDIT_10G_COMPLETED_WITH_EVIDENCE_LIMITS / NO_NEW_COGNITIVE_POST / NO_SERVICE_RESTART / LOT1_DISABLED / KX108_ONLY.
