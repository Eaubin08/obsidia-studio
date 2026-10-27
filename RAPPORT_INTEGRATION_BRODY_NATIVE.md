# Intégration du brouillon natif Brody — validation hors réseau

## Résultat

| Contrôle | Résultat |
|---|---|
| PRODUCER_DEPLOYED | YES — copie Studio uniquement |
| STUDIO_CONSUMER_UPDATED | YES |
| NATIVE_ARTIFACT_ACCEPTED | YES — fonctions publiques, normal et compact, hors réseau |
| UNVERIFIED_OUTPUT_REJECTED | YES — mutants et anciennes sorties sans lignée native |
| PROVENANCE_VERIFIED | YES — manifeste local épinglé et lignée native recalculée |
| REGRESSION_RESULTS | 450 PASS, 17 sous-tests PASS, 0 FAIL Studio |
| READY_FOR_ONE_REAL_TRIAL | CONDITIONNEL — contrat validé, services à lancer et vérifier |

Aucun GREEN global producteur : les huit échecs historiques du rapport précédent
ne sont pas requalifiés par les tests Studio et n'ont pas été rejoués ici.
L'ancien test de capacité Studio utilisait un autre contrat ; sa clôture n'est
pas déduite des nouveaux tests du véritable artefact public.

## État préservé et déploiement

Studio conserve HEAD `637dd86dd1dba47dccf7cffa592cab98e1687ea8`, avec son WIP.
Le producteur conserve HEAD `474afd9ca4b77bf127c31ce22599d52438a7ff37`.
Aucune écriture productrice n'a été effectuée. Les seize sources copiées ont
les mêmes empreintes au contrôle final. Un fichier concurrent non suivi
`app/cognition/b11/brody_evidence_store.py` est apparu : ni copié, ni modifié.
Le statut Git producteur a donc évolué ; il n'est pas présenté comme inchangé.

La sauvegarde est dans
`data/experiments/native_editorial_integration_20261023/before`.
Le plan, les empreintes avant/après et le delta Studio sont dans ce même dossier.
Les anciennes preuves/approbations et les journaux d'expérience ne sont pas modifiés.

Déploiement existant :
`data/experiments/e11_lot1/passe10e2/producer_cbad0125/source`.

- Base historique : `cbad01257c027e5861a1c0610d418dfd02fc8342`, 1 527 fichiers.
- Overlay : 16 fichiers, dont huit ajouts ; total vérifié **1 535 fichiers**.
- État de l'overlay : WIP, pas un nouveau checkpoint commité.
- Manifeste SHA-256 : `ff2006c5159cc49b60739180f36268d987be771cc8dc99e74f696136b5a41c0c`.
- Le manifeste, sa somme, l'index d'empreintes et les exclusions sont cohérents.
- Le canon lexical déjà réparé et son blob restent inchangés.

Les quatre fichiers principaux repris sont :

| Fichier producteur copié | Point réutilisé |
|---|---|
| `apps/obsidia_api/brody_real_response_pipeline.py` | `run_brody_real_response_pipeline` |
| `apps/obsidia_api/brody_editorial_composition.py` | `compose_native_editorial`, sélection/plan, reconnaissance du brief |
| `apps/obsidia_api/brody_true_voice_adapter.py` | `realize_brody_editorial_plan`, `expose_public_editorial_artifact` |
| `apps/obsidia_api/routes/brody.py` | `brody_chat`, exposition finale après C1/E11 |

Leurs dépendances nécessaires sont les quatre modules linguistiques
`french_grammar`, `lexicon`, `lexical_corpus`, `native_realization`, le
préraisonnement et ses trois modules lexicaux, puis quatre fichiers du corpus
public épinglé. La liste exacte et chaque SHA figurent dans `deployment_plan.json`.
Les autres WIP cognitifs, B10 et les nouveaux adaptateurs documentaires ne sont
pas ajoutés au déploiement. B6/B7 et leurs primitives existantes sont conservés.

Le corpus SQLite linguistique de 555 843 584 octets est identifié par
`a9583d24334169b518521394efb72f1524267b5b4a79c17fb27ce67cd38e04dd`.
Sa provenance épinglée est issue de `d4e93f994155a9bec26cc53c6ea5dc9a781bd71a`.
Ce corpus lexical n'est pas une mémoire de connaissances admises.

## Consommateur Studio

Fichiers applicatifs modifiés/créés :

- `studio_native_editorial.py` : admission du contrat public natif.
- `studio_ai.py` : raccordement et refus des anciennes sorties non prouvées.
- `editorial_intent.py` : brief explicite, sans double enveloppe de consignes.
- `studio_e11_deployment.py` : nouveau manifeste épinglé, hachage en flux,
  distinction base/overlay.

Tests modifiés/créés : `test_studio_native_editorial.py`, `test_studio_ai.py`,
`test_brody_editorial_repair.py`, `test_editorial_intent.py`,
`test_lexical_deployment_repair.py`.
`server.py`, le contrat E11, ses diagnostics et la configuration autopilot ne
sont pas modifiés par cette passe.

L'admission exige `BRODY_PUBLIC_EDITORIAL_ARTIFACT_V1` et
`BRODY_NATIVE_EDITORIAL_V1`, un POST explicite identique dans les trois champs
publics, une provenance épinglée, un brief concordant, une sélection, un plan,
la trace de réalisation et C275 concordants. La réalisation est recalculée
uniquement pour vérifier l'identité du texte reçu, jamais pour remplacer une
réponse invalide. Les chemins reçus ne sont jamais utilisés comme chemins à ouvrir.

Le chargeur privé ne reprend que les fonctions pures déployées de grammaire,
sélection/plan, réalisation et C275. Il ne lance ni Router, ni SENS, ni cognition,
ni retrieval, ni modèle. Ses connexions au corpus sont explicitement en lecture
seule. Les modules privés et connexions sont nettoyés après validation.
Le validateur E11 existant est réutilisé sans modification ni assouplissement.

Une inconnue accessoire conservée n'autorise aucune assertion à son sujet.
La grammaire, le brief et les objets des prédicats essentiels sont contrôlés ;
une dépendance inconnue masquée maintient le refus. Ce contrat borné ne reprend
que des opérations consultatives conditionnelles, sans affirmation factuelle
ni promotion documentaire. HOLD/BLOCK, KX108_ONLY, MEMORY_WRITE_HOLD restent actifs.
Une simple balise POST, B6_ADVISORY_CONTEXT, un libellé de source Brody, une
sortie Qwen ou un texte Ingress « sufficient » sans artefact public sont refusés.

## Preuves et tests

Deux exécutions hors réseau de la vraie fonction publique déployée `brody_chat`,
une normale et une compacte, avec le brief public : deux artefacts natifs obtenus.
Ce sont des appels Python, **pas des POST HTTP**. Le Python autonome Windows
3.13.3 du dernier lancement Brody documenté a été utilisé ; aucun processus
Brody actif n'est supposé correspondre à cet historique.

Les 107 modules applicatifs relevés proviennent tous de la copie déployée.
Les deux tentatives de sonde Graphiti et les deux tentatives de ledger de
session ont été bloquées par le harnais. Aucun accès réseau n'a abouti et aucune
écriture de ledger ou de mémoire réelle n'a été autorisée. Les connexions SQLite
de ces tests sont forcées en lecture seule. Ces sondes bornées ne prouvent pas
l'absence universelle d'effets secondaires du producteur.

Résultat conservé, jamais transformé en succès documentaire :

- C1 : `READY_SHADOW_READONLY`, complétude `DEGRADED`.
- E11 : `CONTEXT_LIMITED`, B6 valide mais limité.
- Mémoire : `MEMORY_NOT_REQUIRED`, zéro élément mémoire.
- Trois inconnues conservées ; aucune dépendance essentielle déclarée admise.
- Motifs : `B6_UNKNOWNS`, `E11_UNRESOLVED_REQUESTS`, `RECEIPT_DEGRADED`,
  `RECEIPT_SURFACES_UNAVAILABLE`.
- Aucun appel Qwen ; aucun statut M41/B7 promu en connaissance validée.

Régression Studio complète : **450 PASS + 17 sous-tests PASS**, zéro FAIL.
Commande : `python -X utf8 -B data/experiments/native_editorial_integration_20261023/run_studio_tests.py`.
Le runner refuse réseau, subprocess et écritures hors artefacts. Son journal
rapporte zéro tentative de ces trois types pendant la suite Studio.
Les mutants couvrent provenance, plan, sélection, texte, réalisation, auteur,
faits non vérifiés, contradictions, préraisonnement d'un autre brief, endpoint
différent, inconnue essentielle masquée, champs obligatoires absents,
statuts mémoire inconnus, schémas E11/B6, admission C1 et HOLD/BLOCK.

Les anciens tests positifs fondés sur une source déclarative seule ont été
migrés : leurs sorties insuffisantes sont maintenant explicitement refusées,
et les cas positifs utilisent l'artefact public natif complet. Les assertions
de refus n'ont pas été affaiblies pour obtenir des PASS.

## Limites et prochaine action

Le compositeur reste un prototype déterministe borné au sujet IA / gain de
temps / petite entreprise. Sa prose conditionnelle et son plan natif sont
traçables ; cela ne démontre ni rédaction générale libre, ni connaissance
géographique sur les Ardennes, ni qualité éditoriale universelle.
L'empreinte locale n'est pas une attestation distante de l'identité d'un service.
L'authentification est testée par doubles de transport, pas par un serveur actif.

Au dernier contrôle : aucun listener 8000/8108 et aucun uvicorn Python observé.
Aucun redémarrage, POST, appel modèle, commit, push ou publication effectué.
Autopilot désactivé, configuration inchangée ; LOT1 reste désactivé.

Une seule prochaine action : lancer/vérifier les deux services lors de la passe
d'essai autorisée, puis réaliser un unique POST `/api/generate` selon
`BRODY_NATIVE_ONE_TRIAL.md`. Aucun essai n'est lancé automatiquement ici.

## FAIT / PROUVÉ / INCERTAIN / RESTANT

| État | Conclusion |
|---|---|
| FAIT | Overlay minimal Studio, manifeste sauvegardé/actualisé, admission stricte et tests ajoutés. |
| PROUVÉ | 1 535 fichiers vérifiés ; deux sorties publiques natives hors réseau admises ; 450 PASS + 17 sous-tests ; source productrice copiée inchangée. |
| INCERTAIN | Identité/authentification d'un futur processus, qualité réelle sur d'autres sujets, huit FAIL producteurs historiques non rejoués. |
| RESTANT | Contrôle des services au lancement puis essai HTTP unique et évaluation humaine du brouillon. |
