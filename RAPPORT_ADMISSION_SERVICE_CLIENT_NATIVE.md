# Studio — Admission native du brief service client

26 octobre 2026. APPLY / BUILD CIBLÉ / HORS RÉSEAU / NON_FREEZE.
KX108_ONLY — BRODY_NATIVE_AUTHOR — HUMAN_REVIEW_REQUIRED — MEMORY_WRITE_HOLD.

## Verdicts

| Champ | Résultat |
|---|---|
| SERVICE_CLIENT_NATIVE_V1 | YES — composition existante réutilisée, responder public déployé conforme |
| SERVICE_CLIENT_NATIVE_V2 | YES — sélection explicite V2, composition existante réutilisée |
| STUDIO_ADMISSION_V1 | PASS — normal et compact |
| STUDIO_ADMISSION_V2 | PASS — normal et compact |
| PROVENANCE_PRESERVED | YES — IR, opérateurs sémantiques, plan, réalisation et inconnues recomputés |
| NEGATIVE_GATES_PASS | 197 tests ciblés PASS ; aucune assertion de test préexistante affaiblie |
| REGRESSION_RESULTS | 1028 PASS + 17 sous-tests PASS ; 0 FAIL / 0 ERROR |
| DEPLOYMENT_HASHES | 1537 conformes ; manifeste et producteur inchangés ; zéro transfert |
| READY_FOR_REAL_HTTP_TRIAL | YES_OFFLINE — rechargement contrôlé de Studio requis avant un futur essai ; aucun essai dans cette passe |

Aucun GREEN global producteur. Les dix FAIL producteurs historiques restent séparés et ne sont pas réexécutés.

## Preuves existantes et contrat exact

Sources historiques : `C:/Users/User/.codex/visualizations/2026/10/16/01a14555-4da0-79f3-a5bc-76c3d8477dc6/editorial_explanatory_20261024/A_V1_COMPOSITION.json` et `A_V2_COMPOSITION.json`. Leurs chemins, empreintes et drafts sont référencés dans `historical_A_V1.json` / `historical_A_V2.json`. Le rapport producteur `docs/BRODY_EDITORIAL_EXPLANATORY_LANGUAGE_OFFLINE.md` documentait déjà les compositions, avec les inconnues de possession conservées.

Brief exact conservé : « Rédige une publication LinkedIn expliquant Comment une petite entreprise peut utiliser l'IA pour améliorer son service client sans perdre le contact humain ? ».

Quatre appels du véritable `routes.brody.brody_chat()` comme **fonction Python**, avec le Python Brody autonome existant, ont produit les schémas `BRODY_PUBLIC_EDITORIAL_ARTIFACT_V1` et `BRODY_PUBLIC_EDITORIAL_ARTIFACT_V2`, snapshots `BRODY_NATIVE_EDITORIAL_V1/V2`, statut `CONSULTATIVE_DRAFT_AVAILABLE`, en normal/compact. Ce ne sont pas des POST HTTP. Les textes et drafts sont exactement ceux des compositions historiques ; aucune phrase n’a été réécrite dans Studio.

## Diagnostic causal limité

Le premier refus Studio a été reproduit avant modification, dans les quatre variantes. `DIAGNOSIS_BEFORE.json` pointe l’ancienne ligne 147 de `studio_native_editorial.py` : l’assertion n’attendait que `[UNRESOLVED_SYMBOL...]` et rejetait l’entrée supplémentaire **POSSESSOR_UNRESOLVED** pourtant produite par le compositeur pour « son service client ».

- Projection du sujet : **correcte**, égale à la projection IR recalculée.
- Sélection/plan : existants, natifs, 6 propositions et 4 étapes en V1 ; 7 et 5 en V2.
- Contrat public : déjà conforme dans la copie servie ; aucun manque producteur démontré.
- Provenance : branche `SEMANTIC_RELATIONS`, avec composant `_semantic_operations`, absent de la liste attendue par l’ancien consommateur ordinaire.
- Consommateur : le profil ancien restait limité aux inconnues lexicales et à la provenance de la baseline temps/budget ; il ne prenait pas en compte ce profil sémantique.
- Déploiement : les six sources pertinentes comparées au producteur ont les mêmes empreintes. Les sept autres écarts documentés dans la carte ne nécessitent aucun transfert pour ce lot et n’ont pas été synchronisés.

## Correction minimale, sans cognition nouvelle

Un seul fichier applicatif est modifié : **studio_native_editorial.py**.

1. Chargement privé des trois modules existants de projection de flux lorsque le validateur doit examiner les relations sémantiques. Aucun Router, SENS, modèle, mémoire native ou application n’est exécuté par Studio.
2. Reconstruction exacte des incertitudes depuis le préraisonnement et l’IR : inconnues lexicales, possesseur non résolu avec unité/span/résolution d’origine, audience inconnue si elle existe. Aucune catégorie arbitraire ni effacement d’inconnue n’est admis. La qualification canonique des inconnues doit rester cohérente avec la liste préservée.
3. Comparaison exacte du contexte explicatif linguistique et ajout du composant de provenance `_semantic_operations` uniquement lorsque la projection vérifiée est `SEMANTIC_RELATIONS`. Une relation linguistique ne devient pas une preuve causale.
4. Contrôle des dépendances essentielles sur les objets et sujets réellement projetés, sans effacer les inconnues ; sélection, plan, texte et provenance recalculés avec les fonctions productrices déjà présentes.
5. Refus d’un flag explicite contradictoire de publication ou de validation humaine. V2 exige toujours ses flags producteurs explicites. Le contrat public V1 historique ne comporte pas de flag producteur `human_review_required` obligatoire : Studio conserve sa propre obligation de revue (`human_approval_required=true`) et refuse toute valeur explicite false. Aucun champ absent n’est réinventé dans l’artefact.

V1 reste le défaut et V2 reste explicite. `evidence_refs=[]` reste exigé pour ce chemin consultatif ordinaire ; aucune assertion factuelle non qualifiée n’est ajoutée. Les briefs sans propositions natives justifiées ne gagnent pas un plan artificiel. Le contrat Oracle reste séparé et n’est pas élargi.

## Textes réellement composés puis admis

### V1

Une petite entreprise utiliserait l'IA pour améliorer son service client.

Une petite entreprise viserait à ne pas perdre le contact humain, examinerait son service client et vérifierait les limites de cet essai.

Un premier essai porterait sur son service client.

Une petite entreprise comparerait les résultats de cet essai avec l’objectif retenu.

### V2

Est-ce qu'une petite entreprise peut aider à améliorer son service client ?

Une petite entreprise utiliserait l'IA pour améliorer son service client. Une petite entreprise viserait à ne pas perdre le contact humain, examinerait son service client et vérifierait les limites de cet essai.

Par exemple, un premier essai porterait sur son service client.

Avant de poursuivre, une petite entreprise comparerait les résultats de cet essai avec l’objectif retenu.

Ces textes gardent leur perspective source et leur conditionnel ; le possesseur non résolu reste tracé. L’admission démontre leur origine et leur conformité, pas une qualité rédactionnelle universelle ou la vérité de faits externes.

## Tests exécutés et limites de l’exécution

- **197 PASS ciblés** (`targeted.log`, `targeted.xml`). La régression finale réexécute ces mêmes 197 cas avec preuve explicite d’un seul transport simulé et aucun fallback, y compris sur refus.
- **1028 PASS + 17 sous-tests PASS**, zéro échec/erreur dans la régression Studio/E11 complète (`regression.log`, `studio_regression.xml`). Référence précédente : 831 PASS + 17 sous-tests ; les 197 nouveaux cas portent sur ce lot.
- Relectures finales indépendantes, sans transport : quatre admissions service client, quatre admissions Oracle et quatre admissions des brouillons historiques normaux/compacts V1/V2.
- Tests négatifs : retrait/résolution fictive du possesseur, span falsifié, catégories inventées, effacement d’inconnues, contradiction, essentialité, provenance manquante ou fausse, Qwen/copier-coller, fait prétendument vérifié, faux plan, mauvaise portée/version, HOLD/BLOCK, publication permise, absence de revue requise V2, écriture mémoire et C275 refusant.
- Les tests de schéma/client et l’entrée `server.generate()` sont exercés avec transport simulé ; aucun import de serveur démarrant l’autopilot et aucun HTTP réel.
- Garde de régression : zéro tentative réseau, subprocess ou écriture hors du nouveau dossier d’artefacts. Lors des appels Python du responder pour les fixtures, 4 sondes réseau Graphiti et 4 écritures de ledger ont été **bloquées** par le harnais ; zéro communication/écriture productrice de ces tentatives. Le harnais Python n’est pas présenté comme un confinement Windows complet.

## Empreintes et fichiers livrés

- Manifeste inchangé : `e017a794b73c57688841ab4b2bc168d3765f0585e9d5ebb853602a9d442d4ddc` ; **1537 fichiers vérifiés**, zéro écart, base `cbad01257c027e5861a1c0610d418dfd02fc8342`, overlay `72809eb3528e74f6a027cda50aebdb2c4b83974e` et ses pins WIP conservés.
- Sauvegarde du manifeste, du garde de déploiement et du validateur antérieur dans `before/` ; diff exact du seul fichier applicatif dans `studio_native_editorial.diff`.
- Fichiers de code : `studio_native_editorial.py` **modifié** ; `test_studio_service_client.py` **ajouté**. Aucun autre fichier applicatif, test préexistant, configuration, rapport antérieur ou preuve existante n’est modifié.
- Artefacts nouveaux uniquement sous `data/experiments/service_client_admission_20261026` : préparation/snapshot, fixtures publiques, diagnostic avant correction, tests et gardes, drafts exacts, résultats d’admission, comparaison finale et inventaire SHA des livrables. Les répertoires temporaires de pytest ne font pas partie du code livré.
- Rapport ajouté : `RAPPORT_ADMISSION_SERVICE_CLIENT_NATIVE.md`.
- Aucun transfert ou changement producteur. HEAD producteur initial `5ae7f49021e2180d51a8285d280c5876a34bc57f`, actuel `918d8d6e86b899cb88cd122340431d8b849e9bb5` ; empreintes des sources comparées inchangées. WIP concurrents préservés.

## Préparation HTTP et état final

**Le contrat est prêt hors réseau.** Studio était déjà lancé avant la modification ; son module validateur peut encore être en cache dans le processus existant. Un prochain essai réel exige donc un rechargement contrôlé de **Studio seulement**, une vérification des identités/authentification et la conservation de LOT1=0/autopilot désactivé. Brody ne nécessite aucun transfert pour cette fonctionnalité. Aucun contrôle HTTP, redémarrage, campagne Oracle ou renouvellement de preuve artificiel n’est effectué ici.

Les brouillons historiques, les preuves Oracle, les manifestes et la configuration autopilot sont conservés. Aucun nouveau texte statique propre au sujet dans le code applicatif ; aucune substitution Qwen, écriture canonique, modification KX108/C273/C274/B8, publication, commit, push, merge ou reset.

| État | Constat |
|---|---|
| FAIT | Consommateur aligné sur le contrat sémantique natif existant ; aucun transfert. |
| PROUVÉ | V1/V2 normaux/compacts admis, textes historiques identiques, provenance et inconnues préservées, 197 tests ciblés et 1028 + 17 de régression PASS. |
| INCERTAIN | Comportement du processus Studio avant rechargement et réussite HTTP du nouveau brief non observés dans cette passe ; qualité et revue restent humaines. |
| RESTANT | Rechargement Studio et essai HTTP ciblé uniquement dans une prochaine passe explicitement autorisée ; aucun changement du défaut V1. |

STOP — BRODY_NATIVE_AUTHOR / KX108_ONLY / MEMORY_WRITE_HOLD / HUMAN_REVIEW_REQUIRED / NON_FREEZE.
