# OBSIDIA Studio — clôture LOT 1, passe 10L

Verdict : **LOT1_CLOSED — KX108_ONLY**. Clôture du consommateur consultatif E11, avec LOT1 désactivé. Cette clôture ne valide ni la cognition globale de la stack, ni une restitution éditoriale prête à publier.

## Vérification du 17 octobre 2026

Studio a été redémarré une seule fois pour charger les sources 10K : PID 4144 remplacé par **15376**, créé à 12:10:26 Europe/Paris. Commande : Python 3.13, `-B -m uvicorn server:app --host 127.0.0.1 --port 8108`, cwd Studio, sans reload. Le flag effectif est resté **LOT1=0** ; la clé sortante est présente ; aucun PYTHONPATH/PYTHONHOME externe n'est configuré. Autopilot est désactivé avant et après, sa configuration est inchangée.

Brody reste **PID 29460**, créé à 08:43:03, sur **127.0.0.1:8000**. Aucun redémarrage ou changement producteur. Son cwd et son `--app-dir` désignent la copie figée existante `data/experiments/e11_lot1/passe10e2/producer_cbad0125/source`. Le nom historique du dossier du Python autonome ne définit pas le checkpoint du code servi.

Checkpoint vérifié : **cbad01257c027e5861a1c0610d418dfd02fc8342**, 1526 fichiers conformes au manifeste épinglé SHA-256 `d64f9ac43d1157c52876ea8f265a26fddd95b80b8c6114504d152e88ab5fb26a`. Ce contrôle des fichiers et l'identité du processus constituent une preuve opérationnelle locale ; ils ne sont pas une attestation cryptographique distante du contenu mémoire du processus.

Contrat consommateur inchangé : `OBSIDIA_STUDIO_E11_CONSUMPTION_V1`. Diagnostics : `OBSIDIA_STUDIO_E11_DIAGNOSTICS_V2`. Les empreintes des sept modules Studio contrôlés sont identiques avant/après redémarrage ; celles des modules 10K correspondent au rapport de cette passe. HEAD Studio : `637dd86dd1dba47dccf7cffa592cab98e1687ea8`, modifications préexistantes conservées, aucun commit/push.

## Routes et authentification

| Contrôle GET sans cognition | Résultat |
|---|---|
| Brody `/api/health` | HTTP 200 |
| Brody `/openapi.json`, sans clé | HTTP 401 |
| Brody `/openapi.json`, clé existante | HTTP 200 |
| Brody `/api/brody/chat`, GET authentifié | HTTP 405, méthode incorrecte |
| OpenAPI Brody | POST `/api/brody/chat` déclaré |
| OpenAPI Studio | POST `/api/experiments/e11/context` et POST `/api/generate` déclarés |
| Studio `/api/autopilot` | `enabled=false` |

Le POST Brody utilise explicitement `Depends(require_api_key)` dans le code figé vérifié ; `OBSIDIA_AUTH_ENABLED=true` et présence de clé sont observés dans le processus. La clé DPAPI existante a été utilisée uniquement en mémoire ; aucune valeur secrète n'est enregistrée dans les rapports ou arguments. Aucun POST n'a servi à tester l'authentification pendant 10L.

L'authentification par clé concerne Studio → Brody. L'endpoint expérimental Studio utilise ses gardes existantes : flag, loopback, Origin, JSON strict et taille bornée ; il ne dispose pas d'une authentification entrante par clé indépendante. Avec LOT1=0, son code refuse avant toute consommation. Ce comportement est testé localement, sans POST sur le service réel.

## Reproduction locale des huit diagnostics

**334 tests PASS + 17 sous-tests PASS ; 0 FAIL, 0 ERROR, 0 SKIP.** Le XML contient 351 cas. Les dix fichiers racine de la suite Studio ont été exécutés explicitement, avec mocks/ASGI en mémoire, plugins et cache pytest désactivés. Aucun test de producteur n'a été importé ou lancé.

| Champ | Vérification locale |
|---|---|
| `b6_omission_count` | Compte explicite ; absence ou valeur mal formée → UNKNOWN |
| `b6_omission_categories` | Motifs présents seulement, liste fermée, aucun texte libre |
| `sens_closure_category` | Booléen explicite ; OPEN ne permet pas d'inventer une cause |
| `sens_closure_reason_categories` | Codes normalisés ; suffixes libres supprimés |
| `b7_request_count` | Nombre des demandes présentes, sans résolution supposée |
| `b7_request_categories` | Catégories effectivement exposées, sinon UNKNOWN |
| `c1_degradation_reasons` | Motifs présents et normalisés ; pas de reconstruction historique |
| `cognitive_surface_availability` | Surfaces fixes ; PRESENT ne signifie pas capacité validée |

Les exemples synthétiques reproduisent exactement les huit valeurs 10K et le cas des champs absents. La suite vérifie la cohérence API/client/journal, les limites de taille, la confidentialité, les statuts inconnus, MEMORY_NOT_REQUIRED, HOLD/BLOCK et la conservation du reçu. Les **22 profils** comparés au consommateur 10H vérifié gardent les mêmes décisions, contenu, provenance et limitations ; seul l'enrichissement diagnostique est ajouté.

Le serveur a été relancé contre les sources vérifiées. L'extracteur étant chargé à la demande dans le parcours E11, son fonctionnement est attesté par ces tests locaux ; aucune exécution sur nouveau reçu réel dans ce processus n'est revendiquée. Aucun debug endpoint ou mécanisme d'injection n'a été ajouté.

## Capacités et niveau de preuve

| Niveau | Bilan |
|---|---|
| Réellement démontré, historique 10E7/10I | Parcours Studio → Brody authentifié → reçu C1/E11/B6 → validation et journal minimal ; cinq scénarios 10I HTTP 200 / CONTEXT_LIMITED ; mémoire native transportée au scénario B (5 éléments), MEMORY_NOT_REQUIRED aux quatre autres ; provenance et inconnues conservées. |
| Démontré localement, 10K reproduit en 10L | Huit diagnostics bornés, confidentialité, cohérence API/client/journal ; refus HOLD/BLOCK et statuts inconnus ; erreurs transport simulées ; aucune variation des décisions sur 22 profils. |
| Accessible dans le contrat, sans validation sémantique | États SENS, demandes B7 et surfaces conditionnelles M41 ; leur présence n'est ni une résolution correcte ni une connaissance acceptée. |
| Non démontré | Compréhension générale des ambiguïtés/contradictions, résolution B7, validation M41, vérité des documents, contexte complet, surfaces NPL/Lyapunov opérationnelles dans ce chemin, rédaction éditoriale aboutie. |

Les cinq expériences 10I ont toutes fourni un reçu C1 dégradé, une inconnue B6 et des demandes E11 non résolues. Le scénario B conserve cinq omissions B6. Les catégories non persistées à l'époque ne sont pas recréées. Le diagnostic 10J reste la référence pour les déductions statiques complémentaires. Aucun résultat historique n'est réécrit par 10L.

## Gouvernance, confidentialité et effets secondaires

Aucune logique cognitive ou autorité KX108 n'est modifiée pendant cette passe. Les nouveaux diagnostics sont additifs, non décisionnels. HOLD/BLOCK restent des refus ; une mémoire utilisable ne devient pas une preuve factuelle. Aucun fallback Qwen, deuxième retrieval, générateur éditorial ou publication n'a été appelé.

**Zéro POST cognitif pendant 10L.** Les empreintes des posts, images et ledgers de session couverts par le contrôle sont inchangées pendant le redémarrage. `seed()` ne s'exécute pas sur ce Studio non vide ; `apply_schedule()` ne fait que charger la configuration en mémoire. La boucle autopilot existe mais son garde `enabled=false` empêche les campagnes automatiques. Aucun enfant applicatif de l'ancien Studio n'était actif avant son arrêt.

Le fournisseur peut écrire un ledger de session contenant question/réponse lors d'un futur appel cognitif ; ce stockage est distinct du journal minimal Studio. Un timeout n'annule pas nécessairement le travail côté Brody. Les lectures documentaires externes du fournisseur et l'absence de confinement système supplémentaire restent des limites documentées. Aucune nouvelle isolation n'a été introduite.

## Suites envisageables, non lancées

1. Présenter les diagnostics V2 déjà reçus dans une vue Studio, sans transformer UNKNOWN en résultat.
2. Examiner séparément la pertinence du contexte mémoire brut et les omissions de sa projection B6 ; réutiliser le snapshot fourni, sans nouveau retrieval.
3. Évaluer les interfaces existantes de restitution structurée Brody et Audience/Format après comparaison de contrats ; ne pas reconstruire ces capacités dans Studio.
4. Examiner B7/M41 comme informations expérimentales sans autorité ni promotion automatique.

Aucun de ces raccordements n'est implémenté ou lancé par cette clôture. Une éventuelle observation réelle V2 sera une expérience distincte, avec activation explicite et désactivation dans finally, sans renouvellement artificiel de preuve ni approbation répétitive.

## Artefacts et état final

- `data/experiments/e11_lot1/passe10l/service_report.json` : identités, commandes non secrètes, heures, ports, contrôles HTTP et empreintes.
- `data/experiments/e11_lot1/passe10l/studio_all.xml` : nouvelle exécution complète.
- `data/experiments/e11_lot1/passe10l/local_validation.json` : comparaison synthétique exacte 10K et versions.
- `data/experiments/e11_lot1/passe10l/final_checks.json` : vérification finale des services et du checkpoint.
- `data/experiments/e11_lot1/passe10l/verify_and_reload.ps1` : procédure exécutée ; elle contient l'ancien PID et ne doit pas être relancée sans actualisation.

**FAIT :** un redémarrage Studio, aucune intervention sur Brody, validation locale et bilan produits uniquement dans Studio.

**PROUVÉ :** 334 PASS + 17 sous-tests ; huit diagnostics reproductibles ; checkpoint et authentification contrôlés ; Studio LOT1=0 et autopilot désactivé ; aucun POST cognitif de cette passe.

**INCERTAIN :** disponibilité des catégories sur un futur reçu réel V2 ; validité sémantique B7/M41 et vérité documentaire non démontrées.

**RESTANT :** aucun blocage pour la clôture du consommateur LOT 1 ; les raccordements et observations supplémentaires ci-dessus sont des suites optionnelles, non lancées.

**LOT1_CLOSED / LOT1_DISABLED / AUTOPILOT_DISABLED / NO_REAL_POST / NO_PUBLICATION / KX108_ONLY**.
