# OBSIDIA Studio — enrichissement minimal des diagnostics E11, passe 10K

Verdict : **STUDIO_DIAGNOSTICS_ENRICHED — KX108_ONLY**.

Les changements sont implémentés et testés sur disque. Aucun POST réel, redémarrage, changement producteur, activation LOT1, publication, commit/push ou nouvelle infrastructure. Le processus Studio existant n'a pas été rechargé ; les nouveaux diagnostics ne sont donc pas présentés comme observés sur un reçu réel.

## Périmètre des changements

| Fichier | Changement |
|---|---|
| `studio_e11_receipt_diagnostics.py` | Nouveau module pur : extraction depuis le reçu accepté et normalisation de huit champs par listes blanches. Aucun réseau, stockage, import producteur ou décision cognitive. |
| `studio_e11_contract.py` | Intégration additive au résultat accepté et à la normalisation commune ; version diagnostique V2. Les contrôles et décisions 10H sont inchangés. |
| `test_studio_e11_diagnostics.py` | Tests de provenance, UNKNOWN, confidentialité, bornes, cohérence API/client/journal, refus et comparaison aux décisions historiques. |
| `test_studio_e11_lot1.py` | Vérification d'absence d'import producteur étendue aux deux modules diagnostiques. |
| `E11_LOCAL_CONSULTATIVE.md` | Renvoi vers ce rapport ; historique conservé. |

Le journal et le client existants appellent déjà `diagnostic_summary` : ils reçoivent les champs supplémentaires via cette fonction commune, sans modification de leurs fichiers ni deuxième logique de classification. `server.py`, `studio_ai.py`, le garde de checkpoint, les clés et la configuration autopilot ne sont pas modifiés pendant cette passe.

Le schéma consommateur reste `OBSIDIA_STUDIO_E11_CONSUMPTION_V1`. L'enrichissement additif porte `diagnostics_version=OBSIDIA_STUDIO_E11_DIAGNOSTICS_V2` pour distinguer les nouveaux événements des historiques V1.

## Champs ajoutés et provenance exacte

Toutes les références ci-dessous sont relatives au reçu HTTP public accepté, conservé sans réécriture dans `original_receipt`. `E11` désigne son champ `cognition_shadow_memory`.

| Champ ajouté | Champ producteur réellement lu | Valeurs disponibles / UNKNOWN |
|---|---|---|
| `b6_omission_count` | `E11.context_packet.omitted` | Longueur de la liste explicite ; 0 si liste vide ; UNKNOWN si absente, mal formée ou hors borne. Aucune déduction depuis un autre compteur. |
| `b6_omission_categories` | `E11.context_packet.omitted[*].reason` | `irrelevant_to_query`, `visibility_hide`, `ENTRY_LIMIT`, `PACKET_SIZE_LIMIT`, `UNKNOWN`. Aucun motif attribué depuis un state_id ou une supposition. |
| `sens_closure_category` | `E11.state_entries` de type `SENS_FRAME`, puis `payload.semantic_closure.closed` | `CLOSED` pour true, `OPEN` pour false ; `MIXED` si plusieurs fermetures explicites diffèrent ; `UNKNOWN` si surface absente ou valeur non booléenne. Le seul statut d'état OPEN ne permet pas de remplir ce champ. |
| `sens_closure_reason_categories` | `payload.semantic_closure.reasons` des mêmes entrées | `NO_PREDICATE_UNIT`, `FRAME_MISSING`, `FRAME_AMBIGUITY`, `FRAME_CONTRADICTION`, `FRAME_UNRESOLVED_REFERENCE`, `FRAME_OBLIQUE_ROLE_UNRESOLVED`, `EVENT_REFERENCE`, `META_TARGET`, `INDEX_CONFLICT`, `UNKNOWN`. Préfixes structurés reconnus, suffixes libres non persistés. |
| `b7_request_count` | `E11.resolution_requests` | Longueur explicite, 0 si liste vide, sinon UNKNOWN lorsque la liste manque ou dépasse les bornes. |
| `b7_request_categories` | `E11.resolution_requests[*].unresolved_kind` | Les onze valeurs de `UnresolvedKind` au checkpoint, plus UNKNOWN. Aucune catégorie reconstruite depuis l'état OPEN, la question ou why_resolution_needed. |
| `c1_degradation_reasons` | `completeness`, valeurs de `components`, présence d'erreurs publiques | Codes fermés : `RECEIPT_DEGRADED`, `COMPONENT_UNAVAILABLE`, `COMPONENT_ERROR`, `UNKNOWN_COMPONENT_STATUS`, `PUBLIC_ERRORS_PRESENT`, `NPL_UNAVAILABLE`, `LYAPUNOV_UNAVAILABLE`, `UNKNOWN`. Le nom NPL/Lyapunov n'est associé à une indisponibilité que si son entrée existe avec un statut reconnu. |
| `cognitive_surface_availability` | Surfaces E11/B6 exposées, entrées SENS, tableau de demandes B7, entrées components NPL/Lyapunov, champ M41 explicite | Clés fixes `SENS`, `B6`, `B7`, `E11`, `NPL`, `LYAPUNOV`, `M41` ; valeurs `PRESENT`, `NOT_PRESENT`, `UNAVAILABLE`, `ERROR`, `SKIPPED_BY_POLICY`, `UNKNOWN`. |

Catégories B7 reconnues : COREFERENCE, SOURCE_SCOPE, CONDITIONAL_ATTACHMENT, TEMPORAL_REFERENCE, DEIXIS, ENTITY_IDENTITY, CONTRADICTION, UNKNOWN_TERM_OR_PREDICATE, DOMAIN_SPECIFIC_AMBIGUITY, WORLD_OR_PHYSICAL_REFERENCE, OTHER_EXPLICIT_UNRESOLVED. Une valeur future ou manquante reste UNKNOWN ; elle n'est pas convertie en problème résolu.

Pour C1, le normaliseur reconnaît les tokens de statut du contrat et le format public existant `STAGE:DEGRADED:TypeException` pour une liste fermée de stages. Il n'enregistre ni le type d'exception, ni le message, ni le nom de composant non reconnu. Les détails d'indisponibilité ne sont jamais remplis à partir des conclusions statiques 10J.

## Sens et bornes des valeurs

- `PRESENT` signifie **surface présente dans la réponse**, pas capacité exécutée avec succès, connaissance vraie ou hypothèse validée. Une liste de demandes B7 vide reste une surface présente avec zéro demande.
- `NOT_PRESENT` repose sur une absence explicite dans le champ observé : par exemple snapshot M41 null/dictionnaire vide ou liste d'états vide. Un champ absent ou d'un type inconnu reste UNKNOWN. Aucun test ne transforme la présence de M41 en validation.
- Les nombres sont des entiers stricts entre 0 et 65 535 ; booléens exclus. Une valeur hors borne devient UNKNOWN, sans saturation trompeuse.
- Les catégories sont uniques et triées. Leur nombre est borné par les enums ; les listes d'entrée hors borne deviennent UNKNOWN. Les noms et valeurs de surfaces sont fixes. Un test vérifie que les huit champs restent sous 4096 octets, même avec toutes les catégories répétées et de longues valeurs privées injectées.
- Une liste explicitement vide produit `[]`, distinct de `['UNKNOWN']`. Un reçu COMPLETE sans motif de dégradation présent peut produire une liste vide ; un composant manquant ou non reconnu n'est pas remplacé par une cause supposée.

## Conservation du contenu et de l'autorité

L'extraction s'effectue **après l'acceptation du contrat**. Elle n'ajoute ni n'enlève aucun motif `context_limit_reasons`, ne choisit aucune hypothèse et ne modifie aucun ticket, élément mémoire, état, omission ou provenance du reçu d'origine. Les diagnostics restent extérieurs à `original_receipt` et `e11_context`.

Les refus HOLD/BLOCK, l'autorité KX108_ONLY, les frontières readonly et le refus des statuts mémoire inconnus restent identiques. MEMORY_NOT_REQUIRED conserve son traitement 10H : il n'est pas à lui seul une dégradation et ne masque aucune limitation indépendante.

Pour un reçu refusé ou une erreur de transport, les nouveaux champs restent UNKNOWN. Le résumeur ne fouille pas un reçu non accepté pour reconstruire des catégories qui n'ont pas été exposées. Les diagnostics 10H de refus/transport restent disponibles séparément.

Un résultat connu portant des diagnostics incomplets n'est pas reclassé par l'enrichissement ; UNKNOWN décrit l'information diagnostique manquante. Un **statut mémoire inconnu** reste, lui, un refus du consommateur. Cette distinction préserve la non-régression décisionnelle demandée.

## Confidentialité et cohérence

Un seul extracteur et une seule normalisation sont utilisés. L'API fournit les champs ; le client et le journal les normalisent par la même fonction, sans recalculer les décisions.

Aucun texte de question, extrait mémoire, état complet, receipt complet, titre, chemin, state_id, problem_ref, identifiant de candidat ou message d'exception n'est ajouté au journal. Les suffixes libres des raisons SENS/C1 sont remplacés par une catégorie fermée ; une valeur non reconnue devient UNKNOWN. Les noms de surfaces non autorisés sont ignorés.

Les tests injectent des valeurs privées dans les marqueurs, noms de composants, exceptions, champs de journal et métadonnées mal formées. Les résumés client et événements persistés n'en contiennent aucune. Le reçu original reste intact dans la réponse en mémoire, comme avant.

Les journaux historiques et les cinq résultats 10I ne sont pas réécrits. Leurs catégories absentes ne sont pas rétroactivement déduites des compteurs. Les exemples produits pendant 10K sont explicitement marqués **SYNTHETIC_FIXTURE_NOT_REAL_RECEIPT**.

## Résultats des tests

Suite complète Studio explicite de dix fichiers, exécutée avec Python `-B`, plugins externes désactivés, cache pytest désactivé et répertoire temporaire sous Studio. Mocks/ASGI en mémoire uniquement ; aucun import du serveur complet avec ses hooks de démarrage.

**Résultat final : 334 tests PASS + 17 sous-tests PASS ; 0 FAIL, 0 ERROR, 0 SKIP.** Le XML contient 351 cas.

Points vérifiés :

1. Catégories réellement présentes, absentes, inconnues, vides ou mal formées ; booléens et dépassements de bornes.
2. Absence de reconstruction depuis OPEN, un état mémoire, un nom de surface ou des conclusions statiques.
3. Catégories B7 du contrat, motifs d'omission, fermeture SENS et formats de diagnostics C1.
4. Égalité des diagnostics entre l'API ASGI, le client et le journal ; absence de fuite et conservation du reçu.
5. HOLD/BLOCK, statuts mémoire inconnus, erreurs de contrat, confidentialité et transports simulés.
6. **22 profils comparés à la version 10H réellement utilisée en 10I**, dont l'empreinte source est `a4af70baeebdbfad2e6afc3a730049a462ffd37fc99764b45c8692bdd7141eba`. Tous les champs préexistants sont comparés, sauf le numéro de version diagnostique : mêmes verdicts, erreurs, limitations, frontières, contenu et provenance. Le nouveau module n'introduit aucune différence sur ces profils.

La copie de référence est un fichier `.snapshot` du consommateur Studio pour tests, pas un export producteur ni une nouvelle infrastructure. Son empreinte correspond exactement au rapport 10I. Aucun producteur n'est importé dans ces comparaisons.

Artefacts : `data/experiments/e11_lot1/passe10k/studio_final.xml`, `implementation_report.json`, `diagnostic_examples.json`, `consumer_10h.snapshot`. L'exécution intermédiaire 332 PASS est conservée dans un autre XML.

## Limites et état final

Les catégories disponibles dépendent des champs fournis au prochain appel ; aucun reçu réel n'a été consommé pendant 10K. Les raisons exactes perdues dans 10I restent perdues. L'extracteur ne démontre pas la compréhension SENS, la correction d'une demande B7, la vérité d'un document ou la validité M41.

Le code est prêt sur disque mais n'a pas été rechargé dans Studio, conformément à l'interdiction de redémarrage. Autopilot reste désactivé sur disque ; aucune activation LOT1 ni modification de configuration n'a été faite. Le manifeste du producteur figé et ses 1526 fichiers sont revérifiés sans écriture.

**FAIT :** huit champs diagnostiques ajoutés, seam commun conservé, tests et rapport produits dans Studio seulement.

**PROUVÉ :** 334 PASS + 17 sous-tests, cohérence API/client/journal, bornes et confidentialité testées, décisions inchangées sur 22 profils de référence ; code producteur intact.

**INCERTAIN :** disponibilité effective de chaque nouveau champ dans de futurs reçus ; code non rechargé en service ; aucune observation réelle V2, aucune reconstruction des catégories historiques manquantes.

**RESTANT :** charger les corrections lors d'une prochaine passe de service explicitement engagée. Aucune campagne, activation ni opération supplémentaire n'est lancée automatiquement.

VERDICT : **STUDIO_DIAGNOSTICS_ENRICHED / NO_REAL_POST / NO_SERVICE_RESTART / PRODUCERS_READ_ONLY / KX108_ONLY**.
