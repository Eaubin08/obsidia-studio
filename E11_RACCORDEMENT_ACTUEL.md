> Mise à jour du 17 octobre 2026 : le mode consultatif local est décrit dans [E11_LOCAL_CONSULTATIVE.md](E11_LOCAL_CONSULTATIVE.md). Les anciens verrous temporels, de PID et d’approbation répétitive ci-dessous sont historiques et ne conditionnent plus les essais locaux.

# Raccordement E11 — reprise du 17 octobre 2026

Mise à jour passe 10E.2 : Brody rétabli sous PID 29460 depuis la copie Git cbad0125 située sous Studio ; Studio rechargé sous PID 21116, LOT1=0 et autopilot inchangé/désactivé. Preuve commune 7591200c-da9f-4ab4-8a59-66c9f8402bc1, PENDING_HUMAN_REVIEW, détails dans `data/experiments/e11_lot1/passe10e2/REVIEW.md`. Les observations et procédures ci-dessous précèdent ce rétablissement ; le nouveau dossier prévaut pour l'identité du service et les chemins de données.

Ce document décrit l'état actuel. `LOT1_E11.md` conserve l'historique des passes.
Studio consomme le service existant sur `http://127.0.0.1:8000` ; aucune infrastructure supplémentaire n'est requise ni créée.

## Ce qui est raccordé

`server.py::experiment_e11_context` → `studio_ai.py::run_e11_experiment` → un seul `POST /api/brody/chat` authentifié par `X-API-Key` → `studio_e11_contract.py::consume_envelope` → journal de métadonnées.

L'entrée Studio est exclusivement `{"text":"question consultative"}` sur `POST /api/experiments/e11/context`. Le client ne fournit ni clé ni paramètres d'autorité. L'origine et le pair doivent être locaux. Ce chemin n'appelle ni `/api/generate`, ni Qwen, ni un autre retrieval Studio.

Flags envoyés explicitement à false : `allow_provider`, `allow_local_model`, `allow_memory_candidate`, `allow_manual_apply`, `compact`, `debug`, `debug_full`. Le refus explicite du modèle local est ajouté dans cette reprise ; les anciennes versions de Brody peuvent ignorer ce champ supplémentaire.

Contrats acceptés sans changement :

| Élément | Version |
|---|---|
| Consommateur | OBSIDIA_STUDIO_E11_CONSUMPTION_V1 |
| Reçu | REAL_COGNITIVE_JOIN_C1_V1 |
| Rail | SHADOW_READONLY_SUPERPOSED |
| E11 | COGNITION_SHADOW_MEMORY_V0 |
| B6 | B6_STATE_EXPLICIT_CONTEXT_PACKET_V1 |
| Mémoire | OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1 |

Versions inconnues, enveloppe incomplète, types non conformes, autorité contradictoire et effets actifs : refus, sans contexte. HOLD et BLOCK restent distincts. Reçu, provenance, inconnues et omissions sont conservés dans le résultat accepté. M41 reste une donnée non validée. MEMORY_USABLE exprime une disponibilité documentaire, pas la vérité.

Transport : deadline totale HTTP et timeout de 30 secondes, réponse limitée à 5 Mo, aucun retry, proxy ou redirection. Un 401/403 devient AUTH_REJECTED ; un 503 devient SERVICE_UNAVAILABLE, sans déduire sa cause à partir d'un corps potentiellement privé. Timeout et erreurs réseau ne donnent aucun contexte et ne déclenchent aucun fallback.

Journal : `data/experiments/e11_lot1/events.jsonl`, liste blanche de métadonnées uniquement : identifiant, date, versions/checkpoints déclarés, statut/code, compteurs, latence et taille. Aucun texte de question, mémoire, reçu intégral, clé ou réponse. Échec du journal : contexte retenu, JOURNAL_UNAVAILABLE.

## Vérifications de cette reprise

| Contrôle réel GET | Résultat |
|---|---|
| Brody `/api/health` | 200 |
| Brody `/openapi.json`, sans clé | 401 |
| Brody `/openapi.json`, clé locale existante | 200 |
| Brody `/api/brody/chat`, GET authentifié | 405 ; route POST déclarée |
| Studio `/openapi.json` | 200 ; routes POST E11 et generate présentes |

Brody : PID 23492, démarrage observé le 16 octobre à 20:08:23 Europe/Paris. Studio : PID 25936, démarrage à 20:08:49. Les deux écoutent uniquement sur 127.0.0.1, ports 8000 et 8108. Python313, uvicorn sans reload. Aucun processus n'est redémarré pendant cette reprise.

Le rapport de lancement existant rattache Brody au checkpoint aba5e8bbac68dfae707c6015d69e27eb948c4fed. Le HEAD producteur sur disque est désormais 4627be6fa4ff9aa13ded7e49a1ec0df7f3f3e9b7. Le même PID ne prouve pas une fermeture de tous les imports différés sur l'ancien code. Ne pas attribuer le HEAD courant au code chargé. Un fichier de test producteur est devenu modifié pendant les lectures : travail concurrent, non modifié par cette reprise.

Le diff ciblé aba5e8bb..4627be6f conserve auth.py, le join cognitif, l'adaptateur Native Memory, E11 et l'assemblage B6. La route Brody ajoute notamment le contexte B6 aux projections et une consultation de modèle local opt-in. Cela ne prouve pas le reçu réellement renvoyé par le processus : OpenAPI ne décrit pas son schéma de sortie détaillé.

Dernier relevé pendant cette reprise : HEAD 877bfa83a6d8933fb4cb67aebe27dd842a49a97a. Le commit supplémentaire 877bfa83 ajoute uniquement `tests/integration_cognition/test_brody_semantic_adversarial_red.py` (193 lignes) ; ce test producteur n'est pas exécuté ici. Le contrôle des cinq contrats ci-dessus reste sans delta depuis aba5e8bb. Cet avancement concurrent ne devient pas le SHA attribué au service exécuté.

Autopilot : `data/autopilot.json` conserve `enabled=false`. La boucle relit ce fichier et quitte l'itération avant audit/refill/draft. Le lancement Studio existant indique LOT1=0 ; il n'a pas été réactivé. Les changements de cette reprise sont sur disque, pas attestés comme rechargés dans le PID 25936.

Tests : **246 PASS + 17 sous-tests PASS**, suite Studio complète, sans POST cognitif réel. Transport simulé ; route E11 exécutée en ASGI par compilation de ses déclarations exactes, sans importer le serveur et son autopilot. Résultat : `data/experiments/e11_lot1/recadrage_20261017/studio_all.xml`.

Une première invocation a rencontré 41 erreurs de préparation parce que le parent de basetemp n'existait pas (205 tests passés). Son XML est conservé séparément dans `setup_failed.xml`. La suite a ensuite été relancée intégralement, avec zéro échec/erreur. Ce problème de préparation n'est pas présenté comme une régression produit.

## Effets secondaires externes connus

Le chemin Brody peut écrire un ledger dans `_local_audits/brody_sessions/<session_id>` : `brody_automation_orchestrator.py::_run_session_ledger` appelle `brody_session_memory_ledger_readonly_v2.py::build_record`. JSON, JSONL, Markdown et index peuvent contenir la demande et la restitution. Le nom « readonly » et memory_write=false ne garantissent pas l'absence d'écritures système. Aucun de ces appels n'a été effectué pendant cette reprise.

Le service peut lire des sources documentaires externes, y compris des chemins Downloads. Studio ne modifie ni ces sources ni la configuration productrice ; leur contenu peut évoluer. Le snapshot `_e11_raw` est partagé avec l'adaptateur via `precomputed_retrieval` : Studio ne refait pas la récupération mémoire. Aucun import B10 côté Studio, aucune promotion canonique ou autorisation d'action ajoutée.

Un timeout Studio ne garantit ni l'arrêt du calcul serveur ni l'annulation de ses écritures déjà effectuées. Aucun second essai automatique, même en cas d'erreur réseau.

## Procédure courte du premier appel réel — non exécutée

1. Autorisation humaine d'un essai unique sur une question non sensible, en tenant compte du ledger producteur. Renouveler la revue du service : aucune preuve approuvée n'est créée ici. Le fichier accepté `data/experiments/e11_lot1/service_verification.json` est actuellement absent ; l'ancienne approbation archivée est inutilisable. Le mécanisme existant exige une revue correspondant au checkpoint configuré aba5e8bb, au bon endpoint, avec auth_required=true et une fenêtre maximale d'une heure. Si cette identité ne peut être justifiée, préparer un alignement explicite côté Studio et le faire valider ; ne pas remplacer le SHA ou inventer une identité servie.
2. Charger uniquement Studio depuis son répertoire avec la clé locale existante, sans l'afficher, autopilot=false. Pour cette session autorisée seulement : OBSIDIA_STUDIO_BRODY_URL=http://127.0.0.1:8000 et OBSIDIA_STUDIO_ENABLE_E11_LOT1=1. Le flag est une variable du processus : le changer dans un autre terminal ne change pas le serveur existant. Rechargement contrôlé de Studio requis pour les changements de code/flag, sans reload automatique ; réexaminer seed/scheduler et les enfants avant ce redémarrage. Ne pas redémarrer Brody. Vérifier ensuite routes et revue valide ; si elle couvre aussi l'identité Studio, la renouveler après le changement de PID.
3. Envoyer exactement un POST au seul endpoint Studio, corps `{"text":"Quels sont les rôles respectifs de Brody, de la mémoire native et de KX108 dans le traitement d'une demande consultative ?"}`. Aucun POST Brody supplémentaire et aucun appel generate. Ne pas sauvegarder le résultat brut dans les diagnostics. Relever uniquement statut HTTP, consumer_status, documentary_status, versions, compteurs et latence. Un refus ou contexte limité est un résultat valide.
4. Dans un finally, remettre le flag du processus Studio à 0 via son relancement contrôlé désactivé, même après erreur ; conserver autopilot=false. Vérifier PID/routes et configuration de lancement, puis retirer/archiver la revue devenue obsolète. Aucun deuxième POST pour « vérifier » la désactivation. Vérifier le journal par sa liste blanche, sans copier de contenu privé dans le rapport.

Rollback : revenir aux valeurs Studio désactivées et retirer la revue de service acceptée ; ne pas effacer les journaux historiques. Un appel déjà parti peut finir côté producteur. Aucun rollback producteur ni reconstruction cognitive nécessaire.

## Décision

Le consommateur et ses erreurs sont testés hors réseau. Le service est accessible et son contrôle de clé observable. La compatibilité E11 de bout en bout reste à observer après autorisation et revue de service valide. Aucun POST réel, génération, publication, commit ou push pendant cette reprise. KX108_ONLY ; E11_ACTIVATION_HOLD.
