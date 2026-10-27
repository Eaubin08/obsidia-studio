# OBSIDIA — Carte de reprise du jalon Studio

**26 octobre 2026 — AUDIT DOCUMENTAIRE / READ_ONLY / NON_FREEZE**  
**KX108_ONLY · MEMORY_WRITE_HOLD · NO_PUBLICATION**

Cette carte indexe l’état local, les preuves et les limites du jalon. Elle ne crée ni checkpoint Git, ni nouvelle autorité, ni freeze, ni approbation humaine. Seul ce document est créé pendant cette passe ; aucun test, appel HTTP, redémarrage ou rapprochement de branches n’est exécuté.

## 1. Résumé exécutif

Le parcours **Studio → Brody authentifié → composition native → brouillon consultatif → validation humaine** est démontré sur le brief LinkedIn de référence, en V1 puis en V2 explicitement sélectionnée. Un parcours distinct d’**observation logicielle Oracle vérifiée** est également démontré en HTTP, en V1 : **200 Brody / 200 Studio, 14,031 secondes**, un seul appel de chaque côté. Le texte décrit deux exécutions du logiciel ; `validated_causal_proof=false`, sans autorisation de publication. [P1][P2][P8]

Le faux HOLD du runner après cet essai ne provenait pas de Brody ou de KX108 : il exigeait `memory_write=false` directement dans un record de ledger qui ne définit pas ce champ. Le post-contrôle versionné vérifie les indicateurs canoniques explicites et l’intégrité de la trace. Il donne PASS ; **le HOLD brut, le runner HTTP historique et les preuves E2E restent inchangés**. Dernière régression Studio conservée : **831 PASS + 17 sous-tests PASS, 0 FAIL / 0 ERROR** ; 70 tests ciblés du ledger PASS. Aucun GREEN global producteur. [P9][P10]

L’état n’est pas décrit par un SHA unique :

- **Studio** : branche `main`, HEAD `637dd86dd1dba47dccf7cffa592cab98e1687ea8`, avec cinq fichiers suivis modifiés et de nombreux fichiers non suivis, dont les connecteurs, validateurs et rapports.
- **Producteur de développement** : branche `feat/jarvis-advanced-obsidia-integration-v0`, HEAD `5ae7f49021e2180d51a8285d280c5876a34bc57f`, avec WIP suivi et non suivi.
- **Copie servie sous Studio** : export sans worktree Git propre, base `cbad01257c027e5861a1c0610d418dfd02fc8342`, overlay WIP documenté depuis `72809eb3528e74f6a027cda50aebdb2c4b83974e`, identité effective par manifeste et empreintes. **1537 fichiers conformes** au contrôle documentaire actuel. Les HEAD d’origine ne rendent pas les fichiers WIP committés. [G][P6][C1]

Le jalon est **opérationnel sur ses cas démontrés, borné et NON_FREEZE**. La généralisation explicative, l’admission multisujet et une boucle d’apprentissage avec écriture canonique ne sont pas déduites de ces réussites. [P3][P4][P5][C2][C3]

## 2. Chronologie du jalon

Les compteurs ci-dessous appartiennent à des suites et états différents : ils ne s’additionnent pas. `CODE` signifie implémentation inspectée, souvent WIP ; `TEST` désigne une exécution conservée ; `RUNTIME` distingue Python hors réseau et HTTP. `HOLD` est toujours qualifié par sa portée. **FREEZE=NON à toutes les étapes de ce jalon**, même lorsque des octets sont épinglés.

| Étape | CODE / identité | TEST conservé | RUNTIME démontré | HOLD / limites | FREEZE |
|---|---|---|---|---|---|
| 1 — Composition native V1, 23/10 | `compose_native_editorial`, réalisation True Voice, raccord au responder ; overlay WIP et admission Studio | Intégration Studio : 450 PASS + 17 sous-tests | HTTP 200/200, 14,4 s, un POST Studio et un POST Brody, auteur natif | Brief de référence IA/petite entreprise/gain de temps ; pas une rédaction universelle | NON [P1][P11] |
| 2 — V2 explicite, 23–24/10 | `_v2_operations`, `_v2_select_and_plan`, `_realize_brody_editorial_v2` ; version explicite, V1 par défaut | Producteur V2 : 191 PASS / 8 FAIL historiques ; intégration Studio : 549 PASS + 17 sous-tests | HTTP V2 200/200, 16,301 s, même brief que V1 | Qualité améliorée sur cet exemple ; huit nouveaux sujets/versions refusés ensuite | NON [P2][P3][P12][P13] |
| 3 — Qualification de l’expérience Oracle, avant le raccord interne du 24/10 | `evaluate_oracle_freshness` : âge 301 s, seuils 302 puis 300, horloge fixe | Source et sorties effectivement exécutées ; étape documentaire : 417 PASS / 10 FAIL | Observation logicielle locale ; pas encore une explication publique admissible | Pas d’attestation B8 causale indépendante ; le port documentaire lexical ne peut pas devenir une autorité causale générale | NON [P5] |
| 4 — Adaptateur `OBSERVED_DEPENDENCY`, 24/10 | `InternalObservationReference`, `verify_internal_observation`, sélection et réalisation natives à partir des champs vérifiés | Acquisition séparée : 1 PASS ; 43 tests contractuels ; régression 460 PASS / 10 FAIL | Explication V1/V2 produite hors réseau | Rejeu exact et portée locale ; ni loi causale, ni vérification indépendante B8 | NON [P7] |
| 5 — Raccord public Brody, 24/10 | Identifiant opaque → catalogue serveur → pipeline → admission finale ; schémas d’observation distincts | 54 tests publics PASS ; régression productrice 514 PASS / 10 FAIL / 0 ERROR | V1/V2 normal/compact via vrai responder appelé comme fonction Python, sans HTTP | Catalogue vide par défaut ; absence de preuve/métadonnées ⇒ HOLD, sans modèle de secours | NON [P14] |
| 6 — Admission et déploiement Studio, 24/10 puis clôture de validation le 26/10 | Huit fichiers ciblés transférés sous Studio ; manifeste 1537 ; `studio_internal_observation` ; sélection explicite côté client | Régression achevée le 24/10 : 761 PASS + 17 sous-tests ; reprise : huit admissions PASS avec le Python Brody existant | Les quatre variantes observation et quatre variantes éditoriales ordinaires admises hors réseau | Deux échecs initiaux d’assertion V2 corrigés ; services/catalogue encore à charger à la fin de cette étape | NON [P6] |
| 7 — Essai réel Oracle, 26/10 | Bootstrap Studio charge le catalogue vérifié, sans modifier le producteur | Empreintes et contrats contrôlés avant/après ; pas de campagne négative HTTP supplémentaire | **Un POST Studio → un POST Brody, 200/200, 14,031 s ; observation V1** | `CONTEXT_LIMITED`, reçu dégradé, inconnues préservées ; faux HOLD de post-check après réponse valide | NON [P8] |
| 8 — Correction du post-contrôle ledger, 26/10 | Nouveau validateur pur et runner de relecture hors réseau ; ancien runner conservé comme preuve | **70 tests ciblés PASS**, vrais champs de promotion, intégrité/session/provenance et frontières éditoriales testés | Relecture de la trace existante seulement ; aucun nouvel appel Brody | Le `HOLD_POST_CHECK` historique reste archivé ; nouveau résultat séparé PASS | NON [P9][C4] |
| 9 — Régression finale Studio, 26/10 | Code applicatif et déploiement préexistants inchangés pendant la correction | **831 PASS + 17 sous-tests PASS**, 0 FAIL / 0 ERROR ; 65 fichiers protégés inchangés | Aucun nouvel essai HTTP ou redémarrage | Dix FAIL producteurs historiques distincts et non réexécutés sur le HEAD actuel | NON [P9][P10] |

## 3. Capacités démontrées

### 3.1 Brody rédacteur natif

Le compositeur sélectionne et ordonne des propositions consultatives identifiables, construit un plan et utilise la réalisation grammaticale/True Voice. Il s’agit d’un mécanisme déterministe borné par les relations et opérateurs disponibles, pas d’une capacité rédactionnelle ouverte validée sur tous sujets. Les formulations complètes du brief de référence sont conservées dans les deux rapports HTTP, sans réécriture. [C5][P1][P2]

| Capacité | Niveau établi | Limite de la conclusion |
|---|---|---|
| V1, publication LinkedIn de référence | **RUNTIME HTTP** : brouillon natif admis, plan et propositions recomputés par Studio | Ne prouve ni qualité universelle ni validité factuelle de connaissances externes [P1] |
| V2, même brief | **RUNTIME HTTP** : accroche interrogative, conseils impératifs, coordination et conclusion ; provenance V2 | Aucun changement du défaut ; l’amélioration qualitative reste partielle et soumise au jugement humain [P2][P13] |
| Service client, sujet A | **TEST producteur hors réseau** : projection COMPLETE, V1 6 propositions/4 étapes, V2 7/5 ; brouillons disponibles | Pas de nouvelle réussite HTTP multisujet prouvée ; possesseur non résolu conservé [P4] |
| Pourquoi distinguer compréhension/proposition/autorisation/exécution, sujet B | Projection COMPLETE dans les tests producteur, mais 0 proposition/plan utilisable | HOLD : justification causale admissible absente [P4] |
| Présentation d’Obsidia, sujet C | Projection partielle ; défauts grammaticaux et inconnues séparés | HOLD sur contenu essentiel non analysé/inconnu ; ne pas masquer par un gabarit [P4] |
| Construction d’une technologie indépendante, sujet D | Projection COMPLETE, mais 0 proposition/plan justifié | HOLD : pas de causalité justifiée pour composer l’explication demandée [P4] |
| Explication Oracle | **TEST** V1/V2 normal/compact ; **RUNTIME HTTP V1** | Seulement la dépendance des sorties de cette version aux deux seuils testés [P6][P7][P8] |

Les huit refus HTTP de la campagne multisujet restent des résultats acquis : Brody HTTP 200, Studio HTTP 409, `BRODY_NATIVE_ARTIFACT_INVALID`, **0/8 brouillon admis**. Les améliorations ultérieures hors réseau ne réécrivent pas cette campagne. [P3][P4]

### 3.2 Admission et refus Studio

`server.GenIn` conserve V1 par défaut et accepte V2 sur sélection explicite. Le mode natif est explicitement autorisé par configuration ; il n’est pas un fallback automatique après un refus Ingress. `studio_ai.generate()` maintient les flags d’appel auxiliaire, provider, candidat mémoire et application manuelle à false sur les requêtes éditoriales concernées. Authentification sortante `X-API-Key` conservée. [C6][C7]

Le validateur natif vérifie le déploiement, la version demandée, le brief, les propositions sélectionnées, le plan, les réalisations, les empreintes de composants, les inconnues et les frontières C1/E11/B6. Pour le contrat ordinaire, `evidence_refs=[]` et la forme des inconnues restent volontairement bornés. Une sortie B6 seule ou un texte Qwen balisé `<POST>` ne suffit jamais. [C1][C2]

Le contrat d’observation a une admission séparée et explicite : `internal_observation_id`, schémas `BRODY_PUBLIC_INTERNAL_OBSERVATION_ARTIFACT_V1/V2`, `INTERNAL_OBSERVATION_EXPLANATION`, preuve locale épinglée, rejeu contrôlé et correspondance exacte de la vue publique. Le client ne peut pas fournir son propre catalogue ou une auto-attestation. Les paths de preuve restent sous Studio ; les champs de preuve arbitraires sont refusés dans le schéma d’entrée. [C3][C6]

### 3.3 Provenance, mémoire et autorité

- **Provenance** : base Git et overlay WIP distingués ; manifeste SHA-256 ; source/test/JUnit/trace/brief épinglés pour Oracle ; proposition → réalisation → phrase ; hash du brouillon et de l’artefact. Le consommateur revalide les fonctions pures dans des modules privés. La vue publique ne prétend pas être les octets originaux du reçu. [C1][C2][C3][C8][P8]
- **Qwen** : aucun rôle de rédacteur final dans les parcours démontrés, `model_calls=0`. Pour l’observation explicitement sélectionnée, le responder refuse le recours modèle même en cas de perte de métadonnées. Les autres mécanismes de consultation éventuels ne deviennent ni preuves factuelles ni connaissances admises par cette carte. [C7][C9][P1][P2][P8]
- **Native Memory** : récupération documentaire et vérité restent séparées. La campagne E11 10I avait observé un cas `MEMORY_USABLE` avec cinq éléments, mais `CONTEXT_LIMITED` et cinq omissions ; les autres cas étaient `MEMORY_NOT_REQUIRED`. Le cas Oracle réel reste `MEMORY_NOT_REQUIRED`. Aucun second retrieval Studio ni writer canonique n’est démontré ou autorisé par ce jalon. [P15][P8][C7]
- **Mémoire gouvernée** : `MEMORY_WRITE_HOLD`, `memory_write=false` à la frontière cognitive et aucune promotion canonique automatique. Le ledger autorisé est une trace de session, `TRACE_ONLY_NOT_INDEXED`, sans intake/indexation/promotion ; ce n’est pas une admission de connaissance Native Memory/B8. [C4][C10][P9]
- **KX108** : `KX108_ONLY`, HOLD/BLOCK préservés ; ticket réel `ALLOW_CONTEXT_ONLY`, receipt shadow/readonly, aucune habilitation d’action ou d’écriture déduite d’un PASS de test. La validation humaine du brouillon demeure obligatoire et `publication_permitted=false`. Aucun jugement humain n’a été simulé. [C2][C3][C4][P8]

## 4. Limites et HOLD

| Frontière | État et conséquence | Référence |
|---|---|---|
| Généralisation causale | `OBSERVED_DEPENDENCY` ne devient pas `VALIDATED_CAUSAL_PROOF` ; pas de loi générale ni justification universelle du seuil | [C8][P5][P7][P8] |
| Qualification documentaire | Une attestation lexicale B8 n’est pas une preuve causale ; absence d’attestation indépendante applicable maintient le refus du port documentaire concerné | [P5] |
| Périmètre Oracle | Un identifiant, une preuve locale, une source et un brief exacts ; âge 301, seuils 302/300, horloge fixe. Reformulation ou autre mécanisme : pas d’admission silencieuse | [C3][C8][P6] |
| Multisujet Studio | Les succès producteur hors réseau ne démontrent pas une admission ordinaire générale. Le validateur ordinaire exige notamment une forme stricte d’inconnues et de composants de provenance ; les branches sémantiques productrices ajoutent des éléments distincts | [C2:147][C5:358][P3][P4] |
| SENS/B6/B7/M41 | Limites, inconnues et reçu dégradé restent visibles ; un champ ou module présent n’établit pas une exécution/qualification cognitive complète | [P15][P8] |
| Écriture mémoire/apprentissage | Aucun writer de production KX108/Binder habilité ou cycle d’acquisition durable n’est certifié par les preuves de ce jalon | [P8][P9] |
| Authentification Studio | Lien sortant authentifié vers Brody ; Studio demeure un service loopback sans garde globale de clé entrante. Ne pas annoncer une authentification utilisateur inexistante | [P2][P8] |
| Statut de livraison | Nombreux fichiers WIP/non suivis ; export épinglé sous Studio ≠ version productrice courante ≠ release/freeze | [G][C1][P6] |

**Anomalies corrigées, sans réouverture :** restauration du canon lexical antérieure ; liaison des versions V1/V2 ; gestion JSON des tuples/listes et du contrat V2 effectivement exposé ; refus sur perte de métadonnées d’observation ; faux HOLD ledger ; comparaison UTC des créations de processus dans le diagnostic de l’essai. Leurs preuves et résultats initiaux restent conservés. [P6][P8][P9][P14]

**Anomalies encore ouvertes :** dix FAIL producteurs historiques, limites grammaticales/conceptuelles du sujet C, absence de justification causale pour B/D, absence de nouvelle admission HTTP multisujet, absence de writer canonique habilité démontré dans ce jalon. Les identifier n’ouvre aucun chantier automatiquement. [P4][P5][P6][P9]

## 5. Branches et worktrees

### 5.1 Périmètre principal — relevé direct actuel

Les états `[G]` ont été relevés dans cette passe par `git branch --show-current`, `git rev-parse HEAD`, `git status --short`, `git worktree list --porcelain` et `git for-each-ref`, sans fetch ni synchronisation. Les comptages de WIP portent sur les **entrées** du statut court, pas sur le nombre de fichiers contenus dans une entrée de répertoire non suivi. Ils précèdent la création de cette carte.

| DÉPÔT / EMPLACEMENT | BRANCHE | HEAD | WIP | RÔLE | PREUVE | ACTION RESTANTE |
|---|---|---|---|---|---|---|
| Studio : `C:\Users\User\obsidia-studio` | `main` | `637dd86dd1dba47dccf7cffa592cab98e1687ea8` | 5 suivis modifiés ; 35 entrées non suivies avant ce rapport | Consommateur, validation, orchestration locale, preuves | [G], [C1–C4], [P9] | Préserver le WIP ; ne pas confondre HEAD et fonctionnalités locales |
| Producteur : `C:\Users\User\Desktop\obsidia-jarvis-advanced-integration-v0` | `feat/jarvis-advanced-obsidia-integration-v0` | `5ae7f49021e2180d51a8285d280c5876a34bc57f` | 13 suivis modifiés ; 74 entrées non suivies | Développement Brody/linguistique/connecteurs ; pas la racine du service actuellement lancé | [G], [P4][P14] | Aucun transfert automatique ; qualifier chaque besoin futur |
| Export : `C:\Users\User\obsidia-studio\data\experiments\e11_lot1\passe10e2\producer_cbad0125\source` | Aucune branche propre | Base `cbad01257c027e5861a1c0610d418dfd02fc8342` ; overlay déclaré `72809eb3528e74f6a027cda50aebdb2c4b83974e` + pins WIP | Export et overlays ; ce répertoire n’est pas un worktree producteur | Source servie, 1537 fichiers scellés par manifeste | [C1][P6][P8] | Conserver l’identité exacte ; pas de `git HEAD` déduit depuis le dépôt Studio parent |
| Amont linguistique : `C:\Users\User\Desktop\obsidia-claude-linguistique` | `feat/claude-linguistic-repair-m42-v0` | `d6a5cf0697f5dcd44019bd5aef41dc36b1d2ba57` | 1 document suivi modifié, `docs/education/oxygen_r4/R4_4_DEV_EXPLORATORY_DEVIATION.md` ; aucun non suivi | Source linguistique distincte, pas le runtime Studio | [G] | Aucun transfert ; ne pas étendre les validations du jalon à ce HEAD |
| Worktree primaire du même dépôt de preuves : `C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B` | `feat/gps-real-passive-capture-v0` | `b1bbb2d15127376aa67e16a97373daa04b9c7992` | 29 entrées non suivies, aucun suivi modifié | Autre chantier ; ne définit pas le canon Studio | [G] | Aucun rapprochement pour ce jalon |

Fichiers suivis modifiés Studio : `editorial_intent.py`, `server.py`, `studio_ai.py`, `test_editorial_intent.py`, `test_studio_ai.py`. Les modules E11, `studio_native_editorial.py`, `studio_internal_observation.py`, les tests associés et les rapports sont actuellement non suivis. Les répertoires d’artefacts ne sont pas rendus versionnés par leur simple présence. [G]

WIP producteur directement pertinent : grammaire FR, réalisation native, préraisonnement, adaptateur neural, pipeline réel, True Voice, route Brody, calibrateur/qualificateur lexical, Ingress et décision de routage. Compositeur éditorial, adaptateurs d’observation/preuve documentaire et plusieurs tests restent non suivis. Du WIP B11 et des fichiers auxiliaires coexistent sans être inclus dans la validation Studio. [G]

Autres références locales identifiées : `main` et `exp/semantic-grammar-cognitive-lattice-v0` pointent toutes deux sur `553df13d7bc8746ba582649d08a07a7f1478d081` ; la branche linguistique pointe sur `d6a5cf06…`. La requête exacte pour `feat/gps-p4-p5-brody-semantic-closure-v0` n’a retourné aucune branche locale ; cela ne démontre pas son absence distante. Aucun fetch effectué. [G]

### 5.2 Écarts entre worktree producteur et copie servie

Comparaison actuelle **par SHA-256 sur les 1537 chemins du manifeste** : zéro fichier déployé non conforme, zéro chemin de ce manifeste absent du producteur, **sept contenus différents**. Il s’agit d’une comparaison des chemins sélectionnés, pas d’une affirmation que les deux arbres complets sont identiques. Les fichiers supplémentaires/WIP hors manifeste ne sont pas automatiquement embarqués. [G, comparaison de fichiers][C1]

Les sept chemins différents sont :

1. `apps/obsidia_api/brody_neural_generation_adapter.py`
2. `periphery/common.py`
3. `periphery/merge.py`
4. `periphery/sigma_bridge.py`
5. `scripts/obsidia_cognitive_ingress_v0.py`
6. `scripts/obsidia_gateway_route_decision_v0.py`
7. `sigma/domains/meta_agents.py`

La sémantique de ces deltas n’est pas réauditée ici. Leur existence interdit de déclarer la copie servie identique au HEAD/WIP courant ou d’y étendre automatiquement les tests historiques. Aucune synchronisation n’est réalisée. [G]

Les huit fichiers du dernier transfert restent, eux, identiques au worktree producteur et aux pins de `transfer.json` :

| Fichier relatif | SHA-256 déployé et producteur actuel |
|---|---|
| `apps/obsidia_api/brody_internal_observation_adapter.py` | `5ce0644c36bdf513b1c7ad1ccfc027ad97c4e759f8ab2f087e27713563f6128c` |
| `apps/obsidia_api/brody_editorial_composition.py` | `d8dd17389cccb722fa63b1346f8ecf330cd70ca9a98be70ebb6264bd1ee6754b` |
| `apps/obsidia_api/brody_true_voice_adapter.py` | `edad2d6fe8460818fc29371ccc564036f8e4e23c7e69be5bdd7f954ca1aa801b` |
| `apps/obsidia_api/brody_real_response_pipeline.py` | `69f8e0b1ae54b1c89aff8c64601b87cacadce635c8a46670569010fc152d1c10` |
| `apps/obsidia_api/routes/brody.py` | `577088238eb324c3012d6f4d6d1d2a2b2b727dcf6e20e20611f50776451336b9` |
| `app/semantic/lattice/french_grammar.py` | `cd46ed874f12763eb1aaf3fa4025b72b4c961faad411696db3c0d24abccd2ce9` |
| `app/semantic/lattice/native_realization.py` | `687b7601d0b77f35ae2893b9d74537f64263a27108162e87bc6c342c79ca0828` |
| `tests/integration_cognition/test_brody_internal_observation_capture.py` | `2ec0fcc177ee9ea32f008cfabf29113d2d6133beac63552df695435b91b9001a` |

Base de déploiement conservée et manifeste actuel : **`e017a794b73c57688841ab4b2bc168d3765f0585e9d5ebb853602a9d442d4ddc`**. Source Oracle : `8dc5b03555898103ccbab07266fc4386ff81567a6f1a7dbdaaee0dd158a43049`. Ces empreintes établissent une identité technique ; elles ne constituent pas un freeze ou une preuve causale. [P6][P7][C1]

### 5.3 Autres worktrees enregistrés du dépôt de preuves

Ce relevé évite de perdre la carte Git ; il n’étend pas l’audit fonctionnel. **WIP non inspecté et rôle hors jalon** pour les lignes suivantes ; preuve : enregistrement Git `[G]`, pas une certification de leur contenu. Action restante : aucune pour ce jalon, sauf besoin futur explicitement justifié. Un nom contenant « freeze » ne gèle pas Studio.

| Worktree enregistré | Branche / état | HEAD |
|---|---|---|
| `C:\Users\User\AppData\Local\Obsidia\R8_C3B5_HANG_DIAG\hang84-20260904-183122` | détaché | `88272064e90263800d17a25ddf819fd3b58fefe4` |
| `C:\Users\User\Desktop\obsidia-clean-wt` | `obsidia-clean-wt` | `7ff4365592e220a1c7254e3bde08d85e78997691` |
| `C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-r8-selfhost-bootstrap` | `feat/r8-selfhost-bootstrap-20260903` | `6d27f14d9a53e3dcd48d15d31b73df28ed528faa` |
| `C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\.claude\worktrees\agent-a5ec820ba367e07b5` | `worktree-agent-a5ec820ba367e07b5`, verrou enregistré | `65117524c7fb98e5ff95e4587b6042e85a83045f` |
| `C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\.claude\worktrees\agent-ad2ed2cf6c9ed653f` | `worktree-agent-ad2ed2cf6c9ed653f`, verrou enregistré | `65117524c7fb98e5ff95e4587b6042e85a83045f` |
| `C:\Users\User\Desktop\obsidia-f7-cli-handoff` | `feat/obsidure-f7-cli-r12-handoff` | `5ce4c802e6bda9c3a349e8708f5b98818af524cf` |
| `C:\Users\User\Desktop\obsidia-f7-r10-isolated` | `codex/obsidure-f7-r10-isolated` | `59138c89762266e2b64ddc40d869f761b20e097e` |
| `C:\Users\User\Desktop\obsidia-g16-freeze-check` | détaché | `069b42491b3b0a69532f9a6b461fafbf2c6f756f` |
| `C:\Users\User\Desktop\obsidia-g16-head-check` | détaché | `23f61774b7633a586b1362caecdddb9e01283fff` |
| `C:\Users\User\Desktop\obsidia-openjarvis-g3` | `local/obsidia-g3-test` | `a4080e31ef3582208bea5482a4c57db5433eb1d1` |
| `C:\Users\User\Desktop\obsidia-openjarvis-install-v0` | `build/openjarvis-full-install` | `8aef3e13c0ac6f45a73cdbb19b44673ad178b416` |
| `C:\Users\User\Desktop\obsidia-r12-e2e-clean` | `test/r12-e2e-clean` | `5ce4c802e6bda9c3a349e8708f5b98818af524cf` |
| `C:\Users\User\Desktop\obsidia-r12-f6-d3e-isolated` | `codex/r12-f6-d3e-f9-evidence-convergence` | `0dbf8d73898c2e1a7719bfa5e1e692939afef9a1` |
| `C:\Users\User\Desktop\obsidia-recovery-a-shazam34` | `recovery/a-shazam-34-trees-v0` | `553df13d7bc8746ba582649d08a07a7f1478d081` |
| `C:\Users\User\Desktop\OBSIDIA_UDIP` | `codex/udip-domain-packs-v0` | `c15249aafd72c7e05c1adfa16cf3b516c20054d6` |

### 5.4 Identité runtime observée, sans HTTP

Une lecture actuelle des listeners et des commandes de processus retrouve `127.0.0.1:8000`, PID **47432**, Python autonome existant, bootstrap `internal_observation_real_trial_20261026/serve_brody.py`, création `2026-10-26T19:08:47.8793590+01:00` ; et `127.0.0.1:8108`, PID **32060**, `python -B -m uvicorn server:app`, création `2026-10-26T19:09:09.9567010+01:00`. [G, observation système en lecture seule]

Cela confirme les identités de processus/listeners au relevé ; **la santé/authentification HTTP n’a pas été retestée ici**. Les derniers contrôles HTTP positifs et la configuration du catalogue se trouvent dans les preuves du 26/10. Le bootstrap configure le catalogue explicitement ; le module producteur reste vide par défaut. Les flags LOT1=0 et autopilot désactivé ont été confirmés lors de la dernière validation et sont consignés dans ses preuves ; aucun paramètre n’est changé ici. [P8][P9][P16][C11]

## 6. Matrice de preuves

### 6.1 Accès rapide aux preuves exécutées

| Référence | Objet réellement établi | Preuve directe conservée | Ce qui n’en découle pas |
|---|---|---|---|
| P1 | V1 HTTP 200/200, 14,4 s | [Rapport V1](C:/Users/User/obsidia-studio/RAPPORT_ESSAI_REEL_BRODY_NATIVE.md), [résultat brut V1](C:/Users/User/obsidia-studio/data/experiments/native_editorial_real_trial_20261023/result.json) | Couverture universelle ou publication autorisée |
| P2 | V2 HTTP 200/200, 16,301 s | [Rapport V2](C:/Users/User/obsidia-studio/RAPPORT_ESSAI_REEL_BRODY_V2.md), [résultat brut V2](C:/Users/User/obsidia-studio/data/experiments/native_editorial_v2_real_trial_20261024/result.json) | V2 par défaut ou supériorité multisujet démontrée |
| P3 | Huit refus multisujets, pas de brouillon admis | [Campagne multisujet](C:/Users/User/obsidia-studio/RAPPORT_EVALUATION_MULTISUJET_BRODY_V1_V2.md), [artefacts campagne](C:/Users/User/obsidia-studio/data/experiments/native_editorial_multisubject_20261024) | Validation des correctifs producteur ultérieurs en HTTP |
| P4 | Progrès linguistiques/éditoriaux, REF et A disponibles hors réseau ; B/C/D HOLD | [Rapport explicatif producteur](C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/docs/BRODY_EDITORIAL_EXPLANATORY_LANGUAGE_OFFLINE.md) | Admission générale dans Studio |
| P5 | Observation logicielle disponible, port documentaire causal non habilité | [Frontière documentaire causale](C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/docs/BRODY_DOCUMENTED_CAUSAL_BOUNDARY_OFFLINE.md) | Attestation B8 ou causalité générale |
| P6 | Déploiement/admission 1537, 761 + 17, huit variantes avec Python Brody | [Rapport admission](C:/Users/User/obsidia-studio/RAPPORT_ADMISSION_OBSERVATIONS_INTERNES_BRODY.md), [validation finale](C:/Users/User/obsidia-studio/data/experiments/internal_observation_integration_20261024/FINAL_VALIDATION.json), [JUnit Studio](C:/Users/User/obsidia-studio/data/experiments/internal_observation_integration_20261024/studio_regression.xml), [huit admissions](C:/Users/User/obsidia-studio/data/experiments/internal_observation_integration_20261024/actual_python_validation.json) | Nouveau test de services ou V2 Oracle en HTTP |
| P7 | Acquisition/réexécution Oracle et adaptateur interne | [Rapport interne](C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/docs/BRODY_INTERNAL_OBSERVATION_OFFLINE.md), [observation déployée](C:/Users/User/obsidia-studio/data/experiments/internal_observation_integration_20261024/ACQUIRED_OBSERVATION.json), [capture JUnit](C:/Users/User/obsidia-studio/data/experiments/internal_observation_integration_20261024/capture.xml) | Indépendance B8 ou loi causale |
| P8 | Oracle réel V1, 200/200, 14,031 s, un seul essai | [Rapport HTTP Oracle](C:/Users/User/obsidia-studio/RAPPORT_ESSAI_REEL_OBSERVATION_INTERNE_BRODY.md), [résultat brut avec HOLD du runner](C:/Users/User/obsidia-studio/data/experiments/internal_observation_real_trial_20261026/result.json), [observation amont](C:/Users/User/obsidia-studio/data/experiments/internal_observation_real_trial_20261026/upstream_observation_1.json), [texte reçu](C:/Users/User/obsidia-studio/data/experiments/internal_observation_real_trial_20261026/DRAFT.txt) | Transformation du HOLD logiciel cité en autorité cognitive |
| P9 | Faux HOLD ledger corrigé sans toucher aux originaux | [Rapport correction](C:/Users/User/obsidia-studio/RAPPORT_CORRECTION_POSTCONTROLE_LEDGER.md), [résultat corrigé séparé](C:/Users/User/obsidia-studio/data/experiments/ledger_postcheck_20261026/POSTCHECK_CORRECTED.json), [vérification finale](C:/Users/User/obsidia-studio/data/experiments/ledger_postcheck_20261026/FINAL_VERIFICATION.json) | Réécriture du résultat cognitif ou autorisation mémoire |
| P10 | 70 PASS ciblés ; 831 PASS + 17 sous-tests, 0 FAIL | [Ciblés](C:/Users/User/obsidia-studio/data/experiments/ledger_postcheck_20261026/targeted.log), [régression](C:/Users/User/obsidia-studio/data/experiments/ledger_postcheck_20261026/regression.log), [JUnit](C:/Users/User/obsidia-studio/data/experiments/ledger_postcheck_20261026/studio_regression.xml), [garde](C:/Users/User/obsidia-studio/data/experiments/ledger_postcheck_20261026/studio_test_guard.json) | GREEN global producteur |
| P11 | Intégration V1 hors réseau | [Rapport intégration native](C:/Users/User/obsidia-studio/RAPPORT_INTEGRATION_BRODY_NATIVE.md) | Freeze de la copie ou du dépôt |
| P12 | V2 opt-in Studio, 549 + 17 | [Rapport intégration V2](C:/Users/User/obsidia-studio/RAPPORT_INTEGRATION_BRODY_V2.md), [contrat Studio V2](C:/Users/User/obsidia-studio/BRODY_STUDIO_V2_OPT_IN.md) | Changement implicite du défaut |
| P13 | Composition V2 hors réseau | [Rapport V2 producteur](C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/docs/BRODY_NATIVE_EDITORIAL_V2_OFFLINE.md) | Qualité universelle |
| P14 | Raccord public observation, 54 PASS, 514/10 | [Contrat public et rapport](C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/docs/BRODY_PUBLIC_INTERNAL_OBSERVATION_OFFLINE.md) | HTTP réalisé à cette étape |
| P15 | Campagne E11 10I, cinq cas, mémoire documentaire et limites | [Rapport 10I](C:/Users/User/obsidia-studio/RAPPORT_CAMPAGNE_E11_10I.md), [diagnostic 10J](C:/Users/User/obsidia-studio/DIAGNOSTIC_LIMITES_E11_10J.md) | Mémoire documentaire = vérité ; B7/M41 validés |
| P16 | Dernier lancement, catalogue et contrôles finaux des services | [Lancement](C:/Users/User/obsidia-studio/data/experiments/internal_observation_real_trial_20261026/service_start_report.json), [bootstrap observé](C:/Users/User/obsidia-studio/data/experiments/internal_observation_real_trial_20261026/brody_startup.json), [contrôles finaux](C:/Users/User/obsidia-studio/data/experiments/internal_observation_real_trial_20261026/final_service_checks.json) | Vérification HTTP permanente ou preuve humaine |

Les résultats de tests ci-dessus ont été **exécutés dans leurs passes d’origine**. Cette consolidation lit leurs logs/JUnit et compare des fichiers ; **elle n’en réexécute aucun**. Les observations Git, listeners et empreintes de la présente passe sont des inspections documentaires, pas de nouveaux tests E2E.

### 6.2 Dix FAIL producteurs historiques à conserver séparément

La dernière référence productrice présentée par [P14] est **514 PASS / 10 FAIL / 0 ERROR**, au contexte `72809eb3…` avec WIP. Elle n’est pas rejouée sur le HEAD courant `5ae7f490…`. Les 831 PASS Studio ne corrigent pas ces dix tests :

1. `tests.test_language_flow_projection::test_same_object_can_participate_in_temporal_epistemic_and_governance_flows`
2. `tests.integration_cognition.test_brody_public_editorial_v2_opt_in::test_current_studio_still_accepts_its_pinned_v1_and_rejects_new_producer_identity`
3. `tests.test_semantic_grammar_regressions::test_passive_under_modal`
4. `tests.test_semantic_grammar_regressions::test_infinitive_under_unrecognized_governor_is_embedded`
5. `tests.test_semantic_grammar_regressions::test_substring_is_not_a_verb`
6. `tests.test_semantic_grammar_regressions::test_negated_belief_keeps_embedded_event_positive`
7. `tests.test_semantic_grammar_regressions::test_requests_in_disguise_hold[essaie de lancer le script]`
8. `tests.test_semantic_lattice_primitives::test_connection_kinds_from_language`
9. `tests.integration_cognition.test_brody_native_linguistic_ownership_red::test_r8_b6_and_b7_advisory_context_retains_priority`
10. `tests.integration_cognition.test_native_editorial_capacity_required::test_level_c_original_brody_draft_and_studio_artifact`

La référence distingue huit FAIL historiques initiaux, l’ancien fixture Studio épinglé et le test de familles de flux. Ne ni les masquer, ni déclarer leur cause corrigée, ni les imputer sans reproduction aux dernières adaptations Studio. [P4][P7][P14]

### 6.3 Code de reprise, par frontière

- **C1** — [studio_e11_deployment.py](C:/Users/User/obsidia-studio/studio_e11_deployment.py:23), `verify_checkpoint()` ; [manifeste courant](C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/EXPORT_MANIFEST.json) et [dernier transfert](C:/Users/User/obsidia-studio/data/experiments/internal_observation_integration_20261024/transfer.json).
- **C2** — [studio_native_editorial.py](C:/Users/User/obsidia-studio/studio_native_editorial.py:90), `validate_native_artifact()` / `_validate()`. Repères statiques utiles : exigences `evidence_refs` à la ligne 139, inconnues à la ligne 147 ; ces contraintes sont distinctes de l’admission Oracle.
- **C3** — [studio_internal_observation.py](C:/Users/User/obsidia-studio/studio_internal_observation.py:18), `reference_for()` / `validate_observation_artifact()` ; [catalogue épinglé](C:/Users/User/obsidia-studio/data/experiments/internal_observation_integration_20261024/TRUSTED_OBSERVATIONS.json).
- **C4** — [ledger_postcheck.py](C:/Users/User/obsidia-studio/data/experiments/ledger_postcheck_20261026/ledger_postcheck.py), `validate_trace()` / `canonical_schema()` ; [runner corrigé hors réseau](C:/Users/User/obsidia-studio/data/experiments/ledger_postcheck_20261026/replay_postcheck.py), `run_postcheck()` ; [tests](C:/Users/User/obsidia-studio/test_studio_ledger_postcheck.py).
- **C5** — [compositeur déployé](C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/apps/obsidia_api/brody_editorial_composition.py), `compose_native_editorial()`, `_operations()`, `_semantic_operations()`, `_explanatory_context()`, sélections V1/V2 et opérations d’observation. Repère : extension des composants de provenance des relations sémantiques vers la ligne 358.
- **C6** — [server.py](C:/Users/User/obsidia-studio/server.py:129), `GenIn`, rejet des preuves client et `generate()` ; [editorial_intent.py](C:/Users/User/obsidia-studio/editorial_intent.py), conservation de l’intention.
- **C7** — [studio_ai.py](C:/Users/User/obsidia-studio/studio_ai.py:273), `generate()` ; `_call()` pour X-API-Key, absence de retry/fallback et sélection du transport.
- **C8** — [adaptateur interne déployé](C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/apps/obsidia_api/brody_internal_observation_adapter.py), `verify_internal_observation()` / catalogue / projection ; [Oracle](C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/periphery/blockchain/oracle_freshness_gate.py), `evaluate_oracle_freshness()`.
- **C9** — [route déployée](C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/apps/obsidia_api/routes/brody.py), `brody_chat()` ; [pipeline](C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/apps/obsidia_api/brody_real_response_pipeline.py) ; [True Voice](C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/apps/obsidia_api/brody_true_voice_adapter.py), `expose_public_editorial_artifact()` / `_realize_internal_observation()`.
- **C10** — [orchestrateur](C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/apps/obsidia_api/brody_automation_orchestrator.py), `run_brody_automation_layer()` / `_run_session_ledger()` ; [ledger V2](C:/Users/User/obsidia-studio/data/experiments/e11_lot1/passe10e2/producer_cbad0125/source/periphery/brody_memory_readonly/session_memory_ledger_readonly/brody_session_memory_ledger_readonly_v2.py), `BOUNDARY` / `build_record()`.
- **C11** — [bootstrap local](C:/Users/User/obsidia-studio/data/experiments/internal_observation_real_trial_20261026/serve_brody.py) ; [ancien runner HTTP, à ne pas rejouer](C:/Users/User/obsidia-studio/data/experiments/internal_observation_real_trial_20261026/one_trial.py) ; [rapport brut et rapprochement du post-check](C:/Users/User/obsidia-studio/data/experiments/internal_observation_real_trial_20261026/POSTCHECK_RECONCILIATION.json).
- **G** — Relevés directs de cette passe : commandes Git citées en §5, SHA-256 des chemins du manifeste comparés aux fichiers actuels, métadonnées Windows des listeners/processus. Aucune nouvelle capture de preuve annexe n’est créée : ces résultats sont consignés dans cette carte seulement.

## 7. Travaux ouverts

| Travail | Ce qui existe déjà | Ce qui manque / statut | Ce qu’il ne faut pas refaire |
|---|---|---|---|
| Admission multisujet | Code/relations et tests hors réseau REF/A ; copies linguistiques et compositeur déjà présents | Délimiter un profil d’admission Studio fidèle à ces relations et inconnues ; réussite HTTP non prouvée | Nouveau moteur rédactionnel ou substitution Qwen [P3][P4][C2][C5] |
| Explications hors Oracle | IR de relations linguistiques, port documentaire lexical, adaptateur d’observation borné | Preuve admissible et portée pour un autre mécanisme ; HOLD sans elles | Généraliser Oracle ou recycler B8 lexical en preuve causale [P5][P7] |
| Frontière documentaire | Vérificateur et qualification existent ; références et catégories doivent correspondre | Ne pas annoncer de registre causal opérationnel sur la seule présence de tests/index | Fabriquer une attestation [P5] |
| Mémoire durable | Retrieval documentaire et traces séparées ; garde MEMORY_WRITE_HOLD | Habilitation/validation d’écriture canonique et apprentissage runtime non démontrés ici | Writer parallèle ou promotion automatique d’une proposition Qwen [P15][P9] |
| Régression productrice | Dix FAIL identifiés et conservés | Diagnostic/correction dans un périmètre producteur futur explicitement autorisé | Réouvrir toutes les validations ou annoncer GREEN global [P14] |
| Déploiement / branches | Manifeste, profils et historique d’overlay disponibles | Sept différences courantes connues ; impact non analysé dans cette passe | Synchronisation globale, reset, merge implicite [G][C1] |
| Qualité et revue | Brouillons V1/V2 réels, provenance native, présentation humaine | Évaluation rédactionnelle humaine et élargissement contrôlé de couverture | Déduire la qualité générale d’un HTTP 200 [P1][P2][P3] |

Le post-contrôle ledger n’est plus un blocage de validité de cette trace : utiliser son point d’entrée corrigé pour toute future préparation autorisée. L’ancien runner est une preuve historique, pas le modèle à recopier tel quel. Aucune nouvelle exécution de campagne n’est implicite. [P9][C4]

## 8. Route globale

La route déjà construite, sans nouvelle architecture, est :

1. **Intention éditoriale conservée et version explicite** dans Studio ; V1 reste le défaut. [C6][C7]
2. **Brody interprète et compose** à partir des représentations/propositions admissibles ; l’échec de compréhension ou l’absence de propositions justifiées conserve HOLD. Qwen ne devient pas auteur de secours. [C5][C9]
3. **Une preuve ne vaut que dans son contrat et sa portée** : contexte documentaire, attestation lexicale et observation logicielle restent des catégories distinctes. [P5][C8]
4. **Studio consomme et revalide**, sans refaire la cognition, le retrieval mémoire ou les décisions ; les inconnues et limites restent dans le reçu/snapshot. [C2][C3][P8]
5. **Brouillon consultatif et revue humaine**, avec provenance et publication interdite ; la trace de session conserve son rôle de trace. [P8][C10]
6. **Extension future seulement sur un périmètre choisi**, avec réemploi des composants existants et tests nouveaux limités au delta. La mémoire canonique/apprentissage demeure un chantier séparé tant que son autorité effective et son raccordement ne sont pas démontrés. [§7]

Le jalon de référence et Oracle peut être repris tel qu’il est documenté, sans le déclarer figé, fusionné ou universellement valide. Aucun besoin de Docker, WSL, nouvelle duplication productrice ou deuxième système cognitif n’est établi par ces preuves.

## 9. Prochaine décision unique

**Décider si le prochain lot porte exclusivement sur l’admission Studio du cas A « service client », déjà composé nativement hors réseau côté producteur, en préservant ses inconnues et sa provenance.** [P4][C2][C5]

Ce choix réutiliserait une capacité existante plutôt que d’étendre la causalité générale ou d’activer la mémoire. Avant toute implémentation ultérieure, le delta précis entre le contrat ordinaire Studio et la représentation sémantique du cas A devra être présenté ; aucun transfert des sept fichiers divergents, essai HTTP, changement de défaut V1/V2 ou écriture mémoire n’est autorisé par cette carte.

**Livraison documentaire seulement. NON_FREEZE. STOP.**
