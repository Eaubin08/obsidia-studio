> Mise à jour du 17 octobre 2026 : le mode consultatif local est décrit dans [E11_LOCAL_CONSULTATIVE.md](E11_LOCAL_CONSULTATIVE.md). Les anciens verrous temporels, de PID et d’approbation répétitive ci-dessous sont historiques et ne conditionnent plus les essais locaux.

# État courant

Passe 10E.2 : services rétablis — Brody PID 29460 depuis une copie Git cbad0125 vérifiée sous Studio, Python Windows existant réutilisé ; Studio PID 21116 rechargé au même checkpoint, LOT1=0, autopilot inchangé et désactivé. Preuve commune `7591200c-da9f-4ab4-8a59-66c9f8402bc1`, PENDING_HUMAN_REVIEW, expiration 17 octobre 2026 09:42:57 Europe/Paris. Dossier : `data/experiments/e11_lot1/passe10e2/REVIEW.md`. Aucun POST cognitif. Les notes suivantes sont historiques.

Passe 10E.1 : candidat Studio aligné explicitement sur cbad01257c027e5861a1c0610d418dfd02fc8342, historique précédent aba5e8bb conservé. 248 PASS + 17 sous-tests PASS. Le relancement Brody a échoué au contrôle OpenAPI (APP_ENV vide), puis sa récupération a été bloquée par de nouveaux WIP concurrents. Brody arrêté, Studio PID 16152 inchangé et désactivé. Dossier courant : `data/experiments/e11_lot1/passe10e1/REVIEW.md`, EVIDENCE_INCOMPLETE, aucune approbation possible en l'état. La note suivante décrit l'état historique avant cette tentative.

Voir `E11_RACCORDEMENT_ACTUEL.md` pour la reprise du 17 octobre : service existant vérifié par GET, 246 PASS + 17 sous-tests PASS hors appel cognitif réel, refus explicite du modèle local, activation toujours en HOLD. Les sections suivantes conservent l'historique.

# Passe 9 — alignement explicite et authentification locale

Checkpoint historique immuable : `2729000c63915dd8a7749a3d6f6aa820eaab5d91`.
Checkpoint cible attendu : `aba5e8bbac68dfae707c6015d69e27eb948c4fed`.
La comparaison statique confirme les contrats E11, B6, Native Memory et le reçu C1 identiques ; cela ne valide pas sémantiquement B7/M41. Le champ supplémentaire reste conservé dans le reçu sans devenir une preuve de connaissance acceptée.

`BASELINE_CHECKPOINT` conserve l'origine ; `CHECKPOINT` désigne la cible. La provenance et les nouveaux événements conservent les deux. Aucun événement ni résultat historique n'est réécrit. Une preuve humaine absente, expirée, d'un autre endpoint ou au checkpoint initial est refusée. Une preuve technique de lancement en attente de revue humaine n'est jamais acceptée comme revue humaine.

Authentification : Brody utilise ses mécanismes existants `OBSIDIA_API_KEY` et `OBSIDIA_AUTH_ENABLED=true`. Studio reçoit la même clé dans `OBSIDIA_STUDIO_API_KEY`. La clé doit rester chiffrée localement, hors Git, arguments et journaux. Les contrôles de lancement utilisent uniquement des GET. L'autopilot reste désactivé et `OBSIDIA_STUDIO_ENABLE_E11_LOT1=0`.

Le bloc ci-dessous décrit la validation initiale et son checkpoint historique ; il est conservé comme historique. Validation passe 9 : 242 PASS + 17 sous-tests PASS, zéro échec/erreur/skip. Authentification contrôlée par GET (sans clé : 401 ; clé correcte : OpenAPI 200, GET chat 405). Preuve technique renouvelée sous `passe9/service_verification.pending.json` ; revue humaine explicitement PENDING, aucun enregistrement HUMAN_OPERATOR fabriqué. Le LOT 1 reste désactivé.

Les résultats de passe 9 se trouvent sous `data/experiments/e11_lot1/passe9/`.

---

# LOT 1 E11 — consommateur expérimental Studio

Implémenté uniquement dans Studio, sans commit/push. Base Studio : `main`, `637dd86dd1dba47dccf7cffa592cab98e1687ea8`, worktree propre avant intervention.

## Contrat et périmètre

Endpoint nouveau : `POST /api/experiments/e11/context`, corps JSON strict `{"text":"question consultative"}`. Aucun lien avec `/api/generate`, aucune création de post, publication, promotion ou autorisation d'action. L'endpoint est local, refuse une origine étrangère et retourne `Cache-Control: no-store`. Le transport est exécuté hors de la boucle ASGI.

Source épinglée : `Eaubin08/obsidia-x108-proofs`, branche `feat/jarvis-advanced-obsidia-integration-v0`, SHA `2729000c63915dd8a7749a3d6f6aa820eaab5d91`.

Un seul appel authentifié `POST /api/brody/chat`, sans wrapper éditorial, retry, redirection, proxy d'environnement, modèle ou retrieval supplémentaire. Texte limité à 4 096 caractères ; corps entrant limité à 64 Kio ; réponse à 5 000 000 octets. Timeout réseau 30 s et interruption par deadline de l'opération HTTP. Tous les flags provider/memory candidate/manual apply/compact/debug sont false.

Versions acceptées :

- `REAL_COGNITIVE_JOIN_C1_V1`
- `SHADOW_READONLY_SUPERPOSED`
- `COGNITION_SHADOW_MEMORY_V0`
- `OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1`
- `B6_STATE_EXPLICIT_CONTEXT_PACKET_V1`

Sortie Studio : `OBSIDIA_STUDIO_E11_CONSUMPTION_V1`, statut `CONTEXT_AVAILABLE`, `CONTEXT_LIMITED`, `REFUSED` ou `UNAVAILABLE`. `human_review_required=true`, `publication_permitted=false`. `MEMORY_USABLE` demeure un statut documentaire, jamais une preuve factuelle. Aucun import producteur, B10 ou appel R12/M32.

Le validateur exige les champs de contrat et booléens stricts, refuse versions inconnues, valeurs absentes/null, clés JSON dupliquées, nombres non finis, autorité contradictoire, effets actifs et tickets HOLD/BLOCK. Les refus amont restent identifiables par `UPSTREAM_HOLD`/`UPSTREAM_BLOCK`. Le ticket accepté est uniquement `ALLOW_CONTEXT_ONLY` en dry-run, pas une autorisation réelle.

Le reçu original est détaché sans modification et les inconnues, omissions et provenance sont conservées. Sur refus ou échec du journal, aucun reçu/contexte n'est remis au consommateur. Le blocage d'un sandbox d'action et les citations documentaires ne sont pas traités comme une autorisation ou un refus de contexte.

## Activation réelle : HOLD_ACTIVATION

Valeur par défaut : `OBSIDIA_STUDIO_ENABLE_E11_LOT1` absent ou différent de `1` → désactivé, zéro HTTP et zéro événement journal.

L'activation exige aussi :

1. Service loopback réellement disponible et identifié au checkpoint épinglé.
2. Authentification du service vérifiée ; clé serveur dans `OBSIDIA_STUDIO_API_KEY`, transmise uniquement par `X-API-Key`.
3. Preuve externe de déploiement revue par l'opérateur, distincte du SHA configuré et de la disponibilité d'un port.
4. Tests du contrat réellement exposé et décision humaine d'activation.

Aucun dossier de vérification valide n'est fourni ou créé automatiquement. Le consommateur lit uniquement `data/experiments/e11_lot1/service_verification.json` sous Studio. Son contrat est :

```text
schema = OBSIDIA_STUDIO_SERVICE_VERIFICATION_V1
status = HUMAN_REVIEWED_EXTERNAL_EVIDENCE
verification_method = HUMAN_REVIEWED_DEPLOYMENT
verified_by = HUMAN_OPERATOR
checkpoint = SHA épinglé ci-dessus
base_url = URL loopback configurée exacte, sans chemin
auth_required = true
evidence_id = UUID référençant la vérification externe
verified_at / expires_at = timestamps avec fuseau
```

La période maximale est une heure. Une preuve absente, expirée, future, non revue ou discordante interdit l'appel HTTP. Il s'agit d'une **preuve déclarée et revue humainement**, pas d'une attestation distante produite par Brody, ni d'une détection automatique du binaire servi. Un redémarrage/changement du service invalide la revue : retirer le dossier de vérification avant de reprendre. Ne jamais remplir ces champs sur la seule base d'un HEAD, d'un SHA configuré ou d'un port ouvert. Si l'identité servie ne peut pas être déterminée, conserver HOLD_ACTIVATION.

Variables, à renseigner seulement après les vérifications et la validation humaine :

```powershell
$env:OBSIDIA_STUDIO_BRODY_URL = 'http://127.0.0.1:8000'
# Fournir OBSIDIA_STUDIO_API_KEY par un mécanisme serveur local ; ne pas la coller dans les rapports.
$env:OBSIDIA_STUDIO_ENABLE_E11_LOT1 = '1'
```

Ces variables n'ont pas été activées dans la configuration persistante pendant l'implémentation. Aucun service producteur n'a été lancé, modifié ou interrogé en HTTP réel.

## Journal et confidentialité

Destination : `data/experiments/e11_lot1/events.jsonl`, déjà exclue par la règle existante `data/` du `.gitignore`. Aucun changement du `.gitignore` nécessaire.

Liste blanche : UUID d'expérience, date, version du consommateur, checkpoint configuré, statut de vérification et UUID de preuve, statut/code d'erreur bornés, compteurs, latence, taille de réponse. Aucun texte, extrait, reçu, payload, référence source privée, chemin, clé, en-tête, exception brute ou hash de contenu privé.

Les reçus restent en mémoire pour la durée de la requête ; aucun cache persistant ou interface de publication n'est ajouté. Le journal ne permet volontairement pas de reconstruire le contenu après redémarrage. Échec du journal → contexte retenu, `JOURNAL_UNAVAILABLE`, sans nouvelle tentative. Les écritures hors Studio et les cibles à liens multiples sont refusées.

## Tests et limites

Tests créés avant l'implémentation. RED préparé : 66 FAIL et 21 erreurs dues aux modules encore absents. Les cas étendus ont ensuite fermé les refus distincts et l'incohérence mémoire vide/items présents.

Validation finale : **235 PASS, 0 FAIL, 0 ERROR, 0 SKIP**, plus **17 sous-tests PASS**, incluant les tests Studio existants. Les tests LOT 1 sont hors réseau ; les routes nouvelles sont exécutées en ASGI avec HTTP Brody simulé. Pour éviter les effets de seed/scheduler/autopilot de `server.py`, le harnais compile exactement les deux nouvelles déclarations de route à partir de son AST. Il ne remplace pas un démarrage complet du serveur Studio.

Couverture : schémas/champs/types, JSON invalide/dupliqué/non fini, HOLD/BLOCK/autorité/effets, receipt absent/dégradé, mémoire vide, provenance/inconnues/omissions, auth/redirection/proxy, timeout/troncature/taille, journal privé/échec, désactivation/rollback, endpoint local/origine/champs interdits. Les scénarios utilisent uniquement des données synthétiques.

Preuves : `data/experiments/e11_lot1/validation/studio_all.xml`, `studio_all.log`, `red_ready.xml`, `red_ready.log`, `verification.json`, `implementation.diff`.

Commande de test : Python 3.13 avec `-B -m pytest -p no:cacheprovider`, plugins externes désactivés, `--basetemp` et XML sous Studio. Aucun package installé. Les erreurs de préparation initiales de répertoire temporaire et d'identifiant pytest trop long sous Windows ont été corrigées dans le harnais ; elles ne sont pas comptées comme régressions produit.

Limites : aucun service Brody réel interrogé, aucune mesure éditoriale A/B/C, aucun verdict RUNTIME_OBSERVED. Les métadonnées d'une revue humaine ne garantissent pas automatiquement que le service n'a pas changé depuis sa revue. Les modes éditoriaux existants sont laissés intacts, y compris les limites diagnostiquées dans les passes précédentes.

## Producteur concurrent

HEAD initial producteur : `2729000c63915dd8a7749a3d6f6aa820eaab5d91`. Relevé final : `a4753012183362cde7df01eba6e1c55c4a975369`, commit concurrent `test(cognition): establish B7 M41 Brody causal RED`, une avance locale sur origin. Aucun changement suivi/indexé restant ; WIP non suivi conservé. Cet avancement n'est pas une mutation effectuée par cette implémentation et n'est pas réaudité ici. Le consommateur reste épinglé à 2729000c. Ne pas déclarer que tous les producteurs sont restés globalement figés pendant le run.

## Rollback et prochaine passe

Rollback : remettre `OBSIDIA_STUDIO_ENABLE_E11_LOT1=0` ou supprimer cette variable, puis retirer toute preuve de service périmée. Les nouvelles requêtes sont désactivées sans appel réseau ni journal. Les requêtes déjà en cours peuvent se terminer dans leur délai ; pour un arrêt immédiat, arrêter le processus Studio. Aucun fallback vers Qwen/ingress/Brody natif, aucune restauration productrice requise.

Prochaine passe : identifier en lecture seule le service réellement disponible, son code servi et son authentification ; décider du checkpoint applicable face à l'avancement concurrent ; maintenir HOLD si cette identité reste inconnue. Ensuite seulement, revue humaine de la preuve, activation ponctuelle et essai de contexte réel. La comparaison A/B/C et l'évaluation rédactionnelle restent ultérieures et ne publient rien.

Verdict : STUDIO_LOT1_IMPLEMENTED ; DEFAULT_DISABLED ; NO_PUBLICATION ; NO_GIT_PUSH ; TEST_RESULTS_REPORTED. Producteurs non modifiés par cette intervention ; avancement concurrent signalé. Activation réelle : HOLD_ACTIVATION.
