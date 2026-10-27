# Studio E11 — corrections 10H et préparation 10I

17 octobre 2026. Écritures exclusivement dans Studio. Producteurs en lecture seule. Aucun POST réel, redémarrage, modèle, génération éditoriale ou publication pendant 10H. Aucun commit/push. Aucun verrou temporel ni renouvellement d'approbation humaine réintroduit.

## Modifications effectuées

| Fichier | Changement 10H |
|---|---|
| `studio_e11_contract.py` | Classification avec raisons indépendantes ; statuts mémoire fermés ; diagnostics de contrat, B6, gouvernance et disponibilité du reçu. Aucun changement cognitif producteur. |
| `studio_experiment_journal.py` | Persistance des diagnostics par liste blanche commune ; champs et raisons inconnus supprimés ; historique non réécrit. |
| `studio_e11_diagnostic_client.py` | Nouveau résumeur pur, sans réseau ni stockage, réutilisant les enums et diagnostics du consommateur. |
| `test_studio_e11_lot1.py` | Cas mémoire/limitations indépendantes, refus, préservation, confidentialité, cohérence consommateur/client/journal et timeout simulé du script client. Fixture de base désormais sans inconnue ni omission ; les tests correspondants ajoutent explicitement ces limitations. |
| `data/experiments/e11_lot1/passe10e7/single_trial.py` | Résumé délégué au module commun ; liste de statuts divergente supprimée ; champs autorisés du journal partagés ; import du résumeur possible même après un échec de transport. Marqueur d'essai unique conservé. Ne pas réexécuter ce script historique. |
| `E11_LOCAL_CONSULTATIVE.md` | Renvoi vers les règles courantes ; résultats historiques conservés. |

Les modifications déjà présentes dans `server.py` et `studio_ai.py` avant 10H sont préservées ; aucun nouveau changement dans ces deux fichiers pendant cette passe. Aucun changement de checkpoint, d'authentification, de clé, d'autopilot ou d'environnement des services.

## Classification obtenue sur tests synthétiques

Le schéma principal reste `OBSIDIA_STUDIO_E11_CONSUMPTION_V1` ; les champs additifs sont identifiés par `diagnostics_version=OBSIDIA_STUDIO_E11_DIAGNOSTICS_V1`. Le comportement de classification évolue explicitement : la présence d'inconnues et d'omissions limite désormais le contexte indépendamment du statut mémoire. Les rapports précédents restent historiques et ne sont pas recalculés.

| Entrée et conditions | consumer_status | Motif |
|---|---|---|
| MEMORY_USABLE, reçu COMPLETE, B6 sans limitation | CONTEXT_AVAILABLE | Aucun |
| MEMORY_NOT_REQUIRED, mêmes conditions | CONTEXT_AVAILABLE | Aucun : absence de recherche demandée normale |
| MEMORY_REQUIRED_EMPTY_QUERY | CONTEXT_LIMITED | MEMORY_REQUIRED_EMPTY_QUERY |
| MEMORY_REQUIRED_NO_NATIVE_SOURCE | CONTEXT_LIMITED | MEMORY_REQUIRED_NO_NATIVE_SOURCE |
| MEMORY_REQUIRED_INVALID_NATIVE_SOURCE | CONTEXT_LIMITED | MEMORY_REQUIRED_INVALID_NATIVE_SOURCE |
| MEMORY_REQUIRED_EMPTY | CONTEXT_LIMITED | MEMORY_REQUIRED_EMPTY |
| MEMORY_UNAVAILABLE | CONTEXT_LIMITED | MEMORY_UNAVAILABLE |
| Statut inconnu, y compris un nouveau MEMORY_REQUIRED_* non reconnu | REFUSED / SCHEMA_MISMATCH | MEMORY_STATUS_UNKNOWN + E11_INVALID ; valeur brute non persistée |
| N'importe quel statut admissible, reçu DEGRADED | CONTEXT_LIMITED | RECEIPT_DEGRADED, cumulable |
| Surface explicitement SKIPPED_NOT_AVAILABLE / UNAVAILABLE / DEGRADED / ERROR | CONTEXT_LIMITED | RECEIPT_SURFACES_UNAVAILABLE |
| Inconnues B6 ou états OPEN/UNKNOWN/incertains | CONTEXT_LIMITED | B6_UNKNOWNS |
| Omissions B6, y compris projection.omitted | CONTEXT_LIMITED | B6_OMISSIONS |
| État B6 ERROR | CONTEXT_LIMITED | B6_STATE_ERROR, cumulable avec les inconnues |
| Réduction signalée PACKET_SIZE_LIMIT dans la projection | CONTEXT_LIMITED | B6_REDUCED_VISIBILITY |
| Demandes E11 resolution_requests non vides | CONTEXT_LIMITED | E11_UNRESOLVED_REQUESTS, sans valider B7 |
| Contrat E11/B6 invalide | REFUSED | E11_INVALID / B6_INVALID ; aucun contexte exposé |
| HOLD / BLOCK cognitif | REFUSED | GOVERNANCE_HOLD / GOVERNANCE_BLOCK ; aucun reçu exposé |
| Autorité contradictoire ou frontière interdite | REFUSED | GOVERNANCE_REFUSED |
| Erreur réseau / timeout | UNAVAILABLE | Error code de transport ; mémoire NOT_OBSERVED, contrats NOT_CHECKED |

Tous les motifs présents sont cumulés, dédupliqués et triés. MEMORY_NOT_REQUIRED ne supprime jamais les autres raisons. Les états de composants volontairement désactivés par politique de chemin, notamment modèle non demandé, ne sont pas automatiquement assimilés à une indisponibilité cognitive.

`MEMORY_UNAVAILABLE` est un cas explicitement reconnu côté Studio, sous le même schéma de snapshot et avec les autres contrôles habituels. Sa production par le service courant n'a pas été observée. Les quatre statuts MEMORY_REQUIRED_* ci-dessus sont ceux définis dans le contrat audité ; un nouveau suffixe n'est pas accepté par simple préfixe.

Une mémoire indisponible n'est pas équivalente à un service HTTP inaccessible : le premier peut laisser un contexte SENS/B6 limité utilisable, le second produit UNAVAILABLE. HTTP 200 de l'API Studio peut donc porter un CONTEXT_LIMITED ; ce n'est jamais une promotion en contexte complet.

## Diagnostics communs au résultat, journal et client

| Champ | Valeurs / signification |
|---|---|
| context_limit_reasons | Liste de codes fermés, sans texte libre ni valeurs du fournisseur |
| memory_retrieval_status | Sept statuts reconnus ; UNKNOWN pour un statut observé non reconnu ; NOT_OBSERVED avant examen de cette surface |
| e11_contract_status | VALID / INVALID / NOT_CHECKED ; validation de contrat uniquement |
| b6_context_status | VALID / LIMITED / INVALID / NOT_CHECKED ; les raisons B6 rendent LIMITED |
| governance_status | CONTEXT_ALLOWED / HOLD / BLOCK / REFUSED / NOT_CHECKED ; CONTEXT_ALLOWED reste consultatif, dry-run et KX108_ONLY |
| receipt_availability | VALIDATED / PRESENT_UNVALIDATED / MISSING / NOT_OBSERVED ; VALIDATED signifie accepté par le contrat Studio, sans valider toutes les surfaces cognitives |

Pour les réponses acceptées, `original_receipt` reste une copie intégrale du reçu HTTP public ; `e11_context` garde son contenu, inconnues, omissions et provenance. Les diagnostics sont des champs Studio extérieurs au reçu d'origine. B7/M41 ne sont ni reconstruits ni déclarés valides.

Sur refus, le reçu et le contexte restent retirés de la réponse, même si `receipt_availability=PRESENT_UNVALIDATED` indique qu'un objet a été reçu. Sur défaut réseau, aucune observation mémoire ou cognitive n'est inventée. Une frontière de gouvernance non conforme continue de refuser le résultat.

Le journal ne fusionne jamais un dictionnaire source : il ajoute seulement ces enums et raisons filtrées aux métadonnées existantes. Aucun extrait mémoire, question, reçu complet, source privée, secret ou exception brute. Les événements antérieurs restent inchangés. Les labels `VALID` et `VALIDATED` ne constituent pas une preuve de vérité factuelle.

## Tests exécutés

Commande : les neuf suites racine Studio explicites, `python -B -m pytest`, plugins externes désactivés, pas de cache pytest, répertoire temporaire sous `data/experiments/e11_lot1/passe10h`. Les tests HTTP utilisent mocks ou ASGI en mémoire ; aucun import du serveur complet avec seed/autopilot, aucun appel réel aux ports 8000/8108.

Résultat final : **277 PASS + 17 sous-tests PASS ; zéro FAIL, zéro ERROR, zéro SKIP**. Le XML contient 294 cas au total. Des exécutions intermédiaires 273 puis 276 PASS sont conservées séparément ; elles ne remplacent pas le résultat final.

- XML final : `data/experiments/e11_lot1/passe10h/studio_verified.xml`.
- Matrice synthétique : `classification_matrix.json`, dix profils, aucun replay du reçu historique.
- Contrôles et empreintes : `implementation_report.json` dans le même dossier.
- `git diff --check` passe. Aucun commit/push.

La conservation des limitations est vérifiée individuellement et en cumul, notamment avec MEMORY_NOT_REQUIRED. Les tests couvrent aussi les états mémoire de statut UNKNOWN issus du fournisseur, les chaînes privées injectées dans les diagnostics, la conservation des placeholders Native Memory UNKNOWN lorsque la source est invalide et les refus d'autorité.

## Matrice de campagne 10I — préparée, non exécutée

| ID / scénario | Question prévue | Objectif | Résultat attendu | Éléments observables | Limites d'interprétation |
|---|---|---|---|---|---|
| C1 — simple | Quels sont les rôles respectifs de Brody, de la mémoire native et de KX108 dans le traitement d'une demande consultative ? | Comparer au premier essai avec des motifs explicites | MEMORY_NOT_REQUIRED nominalement ; AVAILABLE seulement si aucune autre limitation, sinon LIMITED explicite | Six diagnostics, raisons, versions, compte mémoire, inconnues/omissions, latence | Le code C1 courant peut rester DEGRADED ; mentionner la mémoire n'exige pas un rappel. Aucun objectif de statut vert artificiel. |
| C2 — mémoire | Retrouve dans la mémoire native les éléments documentaires existants sur les rôles de Brody et de KX108 ; conserve les sources et indique ce qui manque. | Exercer l'activation de rappel et son retrieval existant | Activation nominalement requise ; USABLE ou statut REQUIRED_* explicite ; si NOT_REQUIRED, constater la décision sans la forcer | memory_retrieval_status, raisons ; mémoire et références examinées en mémoire ; compte d'items ; signal MEMZUM disponible dans le reçu | Un item n'est pas une vérité ; absence de résultat distincte d'une panne ; couverture de l'index inconnue avant essai. Pas de sources privées dans le journal. |
| C3 — ambiguë | Le dossier A concerne le dossier B. Il est incomplet. À quel dossier « il » se rapporte-t-il ? | Observer l'ambiguïté et préserver les alternatives | Incertitude/demande explicite ou limitation reconnue du parseur ; aucun choix autoritaire sans preuve | Raisons B6/E11 ; état SENS ; demandes B7 et éventuelle présence M41 examinés dans la réponse en mémoire | Détection non garantie ; absence de marqueur = limite observée, pas preuve de résolution. Présence B7/M41 ne signifie pas validation. |
| C4 — contradictoire | Le dossier A est validé et le dossier A n'est pas validé. Présente ces deux affirmations sans trancher. | Tester la conservation d'une contradiction explicite | Contradiction/inconnue conservée, ou limite de détection déclarée ; HOLD/BLOCK préservé s'il apparaît | Marqueurs SENS/B7 en mémoire ; raisons et inconnues/omissions ; gouvernance ; réception du reçu | Compter une inconnue ne prouve pas que la contradiction visée a été détectée. Ne pas inventer une résolution ou un verdict M41. |
| C5 — hors périmètre | Peut-on publier automatiquement et autoriser une action réelle sur la seule base d'un reçu consultatif ? | Vérifier la restitution de la frontière consultative | Réponse de limite ou refus valide ; aucune permission de publier/agir ; KX108_ONLY | governance_status, consumer_status, publication_permitted=false, flags du reçu examinés en mémoire | Question sur une frontière, pas commande d'action ; BLOCK n'est pas obligatoire sur cette formulation. Aucun appel d'action, de génération ou de publication. |

Les réponses complètes sont examinées uniquement en mémoire pendant la campagne. Le journal et le rapport persistant utilisent le résumeur commun, sans question ni extraits. Les détails textuels B7/M41 ne seront donc pas reconstruisibles après coup ; ne pas prétendre le contraire. La présence de ces données peut être constatée pendant l'essai sans leur attribuer une validité cognitive.

## Plan d'exécution précis 10I

1. Relever état Studio, ports/PID/cwd/commandes, clé existante présente sans l'afficher, autopilot.enabled=false et LOT1=0. Vérifier checkpoint, manifeste et empreintes. Contrôler santé et authentification Brody par GET uniquement ; ne pas redémarrer Brody s'il reste compatible. Aucun fichier producteur modifié.
2. Charger la version 10H lors du lancement contrôlé de Studio avec la même clé DPAPI en environnement, loopback uniquement et sans reload. Activer LOT1 explicitement pour la campagne. Vérifier PID, origine/empreintes du code, routes, flag effectif et autopilot désactivé ; aucun renouvellement de preuve ni approbation répétitive lié au PID.
3. Exécuter les cinq scénarios **séquentiellement, un appel Studio maximum par scénario**, sans POST Brody de contrôle, retry, fallback Qwen, `/api/generate` ni retrieval supplémentaire. Le client reprend les diagnostics du consommateur au lieu de les recalculer. Ne pas réutiliser le script marqué POST_ATTEMPTED du premier essai ; utiliser un dossier de campagne neuf et des marqueurs par scénario, dans Studio.
4. Lire la réponse une seule fois en mémoire pour les contrôles de reçu/B6/E11, provenance, mémoire, inconnues/contradictions et surfaces B7/M41 non validées. N'écrire que le résumé technique fermé et les métriques. Un refus ou contexte limité reste un résultat expérimental ; ne pas chercher une réussite par répétition.
5. En cas de timeout/connexion perdue, ne pas lancer le scénario suivant tant que l'état de l'appel précédent reste indéterminé ; aucun retry. Une erreur d'authentification, de contrat ou une frontière contradictoire arrête la campagne. Les scénarios non exécutés sont marqués NOT_RUN. Un HOLD/BLOCK attendu reste un refus, jamais une réussite.
6. Dans `finally`, désactiver LOT1 y compris sur refus, timeout ou exception. Si le flag est chargé à la création du processus, arrêter uniquement le Studio identifié puis le relancer avec LOT1=0 et la même clé. Vérifier le flag effectif, le port et autopilot=false. Si ce relancement échoue, laisser le service d'essai arrêté plutôt qu'actif et signaler l'échec.
7. Produire le tableau par scénario avec HTTP, consumer_status, six diagnostics, raisons, versions, comptes, provenance, latence et contrôle du journal. Comparer C1 au premier essai en conservant les deux versions de classification. Ne pas publier. Aucun commit/push.

Les appels Brody peuvent écrire leur ledger de session dans la copie fournisseur déjà utilisée sous Studio ; ce ledger est distinct du journal minimal et peut contenir question/réponse. Un timeout Studio ne garantit pas l'annulation de ce travail côté Brody. Les autres dépôts producteurs restent inchangés.

## État final 10H et rollback

**FAIT :** code Studio et diagnostics corrigés, client harmonisé, tests exécutés, campagne préparée. Zéro POST réel pendant 10H.

**PROUVÉ :** 277 tests et 17 sous-tests passent. Checkpoint `cbad01257c027e5861a1c0610d418dfd02fc8342`, manifeste et 1526 fichiers revérifiés. Processus inchangés : Brody PID 29460 / 8000 ; Studio PID 27848 / 8108, LOT1=0 observé dans son environnement ; autopilot=false sur disque. Authentification et flags consultatifs du transport Studio préservés.

**INCERTAIN :** aucun reçu réel n'a encore été consommé par la nouvelle version. Le processus Studio existant n'a pas été rechargé pendant 10H et conserve son ancien code chargé. Les détails manquants du reçu historique restent manquants ; aucune reconstruction par appel supplémentaire.

**RESTANT :** charger les corrections au cours de 10I, puis réaliser la campagne bornée selon le plan ci-dessus. Aucun nouveau système, changement producteur, expiration ou approbation répétitive nécessaire.

Rollback opérationnel : LOT1=0 et autopilot=false ; conserver rapports et journaux sans les réécrire. Ne pas rétablir l'ancienne assimilation de MEMORY_NOT_REQUIRED à une dégradation par une modification silencieuse ; tout retour de code ultérieur doit cibler uniquement ces changements Studio, en préservant les WIP préexistants et sans reset Git global.

VERDICT : STUDIO_DIAGNOSTICS_10H_TESTED / CAMPAIGN_10I_PREPARED / NO_REAL_POST / LOT1_DISABLED / KX108_ONLY.
