# Essai HTTP réel unique — Brody natif V2

**STUDIO_BRODY_V2_E2E=PASS** — KX108_ONLY, DRAFT_ONLY, HUMAN_REVIEW_REQUIRED.

| Critère | Observation réelle |
|---|---|
| BRODY_HTTP_STATUS | 200 |
| STUDIO_HTTP_STATUS | 200 |
| EDITORIAL_VERSION | V2 |
| NATIVE_AUTHORSHIP_VERIFIED | YES |
| PROVENANCE_VERIFIED | YES — admission native et origines chargées |
| POST_ARTIFACT_PRESENT | YES |
| HUMAN_REVIEW_REQUIRED | true |
| PUBLICATION_PERMITTED | false |
| Latence Studio complète | 16.301 s |
| Appels | 1 POST Studio /api/generate → 1 POST Brody /api/brody/chat |
| Retry / fallback / publication | 0 / 0 / 0 |

## Brouillon reçu, intégral et inchangé

Est-ce que votre équipe peut gagner du temps avec l’IA sans gros budget ?

Commencez par une seule tâche répétitive, avec un budget plafonné. Choisissez une tâche chronophage et un résultat facile à relire. Relisez le brouillon et vérifiez chaque information avant tout usage.

Par exemple, un premier essai avec l’IA porterait sur un brouillon de réponse à une demande récurrente, sans données privées.

Avant de poursuivre, comparez le temps passé avec et sans assistance.

## Provenance et validation

Le texte vient de `BRODY_NATIVE_EDITORIAL_V2` ; `model_calls=0`, auteur natif Brody, aucun Qwen rédacteur. Les contrôles obligatoires du consommateur vérifient les propositions sélectionnées, le plan, les opérations de réalisation et la provenance par recalcul des fonctions pures épinglées. Ces champs ne sont pas renvoyés intégralement par /api/generate ; leur preuve est l’admission exécutée par ce validateur, dont l’origine chargée est contrôlée, et non une seconde récupération du reçu auprès de Brody.

Le compositeur producteur est effectivement importé depuis la copie Studio pendant cet essai, confirmé par sa trace d’import. `studio_ai.py` a utilisé un cache Python : le code objet du cache est égal au code objet compilé depuis la source actuelle. Le consommateur natif, le garde de déploiement et le contrat E11 sont chargés depuis Studio. Les processus ont été lancés sans --reload depuis les répertoires contrôlés.

Déploiement : **1 535 fichiers vérifiés avant et après** ; base `cbad01257c027e5861a1c0610d418dfd02fc8342` ; overlay WIP documenté depuis `b8c06be7d7f0e4b7ce3b60092377ccc5ea07da4c`, sans prétendre que les fichiers WIP sont committés à ce SHA. Manifeste `f9fffba9a94efeb30d7a7190a6dbc488aaa65d84b6edec52cd9a5a4eeb8265a5`.

Authentification : Brody /openapi.json retourne 401 sans clé, 200 avec la clé DPAPI existante ; GET authentifié /api/brody/chat retourne 405. La clé n’est ni affichée, ni persistée en clair, ni transmise sur la ligne de commande. Le POST réussi confirme que Studio transmet une authentification acceptée par Brody. Studio reste une interface locale sans garde de clé globale entrante ; ne pas confondre ce fonctionnement avec l’authentification du lien sortant Studio → Brody.

`MEMORY_WRITE_HOLD` est exigé par l’admission du snapshot et de l’artefact. Santé Brody : readonly=true, memory_write=false, KX108_ONLY. Aucun writer mémoire activé. Aucun changement KX108, C273/C274 ou B8.

## Comparaison factuelle avec V1

Même brief public que l’essai V1 ; aucun essai V1 supplémentaire effectué. Le texte V1 historique n’est pas modifié.

| Mesure | V1 historique | V2 réelle |
|---|---|---|
| HTTP Studio / Brody | 200 / 200 | 200 / 200 |
| Latence | 14,4 s | 16.301 s |
| Accroche | Une petite entreprise commencerait… | Question liée au besoin temps/budget |
| Structures | Répétition « L’équipe… » | Impératifs et coordination « Relisez… et vérifiez… » |
| Modalité | Plusieurs conditionnels | Conseils à l’impératif ; exemple conservé au conditionnel |
| Conclusion | Comparaison du temps avant de poursuivre | Même conseil, transition « Avant de poursuivre » |
| Contenu factuel | Conseils consultatifs | Même périmètre ; aucun chiffre, témoignage ou fait local ajouté |
| Autorité / publication | KX108_ONLY / false | KX108_ONLY / false |

Écart de latence observé : +1.901 s ; une seule observation par version ne permet pas une conclusion de performance générale. Le brouillon V2 reçu est identique à celui produit hors réseau. La réalisation est déterministe et bornée au domaine actuellement couvert ; cet essai ne démontre pas une capacité éditoriale générale ni une connaissance factuelle des Ardennes. Les améliorations observables concernent surtout la formulation et la structure des mêmes conseils. La qualité reste à juger par l’humain.

## Limites cognitives conservées

- E11 : **CONTEXT_LIMITED**.
- Mémoire : **MEMORY_NOT_REQUIRED**, pas une preuve de vérité factuelle.
- Inconnues : **3**, conservées.
- Limitations : B6_UNKNOWNS, E11_UNRESOLVED_REQUESTS, RECEIPT_DEGRADED, RECEIPT_SURFACES_UNAVAILABLE.
- B7/M41 ne sont pas validés par cet essai.

## État final et effets

Brody : **PID 26472**, 127.0.0.1:8000, Python autonome 3.13.3, répertoire de la copie Studio vérifiée. Studio : **PID 18320**, 127.0.0.1:8108, Python existant, racine Studio. Deux rechargements contrôlés nécessaires pour charger V2 ; aucun autre service démarré. Les mêmes PID et instants de création sont confirmés après l’essai. Le premier contrôle de date final a comparé une chaîne formatée à une date JSON convertie automatiquement ; la comparaison correcte des instants a confirmé l’identité inchangée. Aucun second appel cognitif pour cette vérification.

V1 reste le défaut dans les deux schémas OpenAPI. V2 a été choisi uniquement dans ce POST. LOT1=0 au lancement du processus Studio inchangé ; autopilot=false observé via GET et fichier inchangé. Les sources Studio, le manifeste et les posts/images sont inchangés après l’essai. Aucune sauvegarde automatique de publication ni publication externe.

Effet connu : l’orchestrateur Brody peut écrire un ledger de session dans `_local_audits/brody_sessions` de la copie Studio. **4 fichiers de ledger modifiés depuis le rechargement ont été observés par leurs métadonnées seulement** ; aucun contenu de session n’a été copié dans ce rapport. Ce ledger ne constitue pas une admission de connaissance canonique et ne lève pas MEMORY_WRITE_HOLD. Le dossier expérimental contient le brouillon public demandé et des diagnostics minimaux, aucun reçu intégral ou extrait mémoire.

Preuves : `result.json`, `http_observation.json`, `service_start_report.json`, `preflight_imports.json`, `final_service_checks.json`, `DRAFT.txt` dans `data/experiments/native_editorial_v2_real_trial_20261024`.

**STOP après l’essai unique.** Aucune modification opportuniste, aucun commit/push.
