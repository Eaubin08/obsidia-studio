# E11 : mode consultatif local — 17 octobre 2026

Cette procédure remplace les anciens verrous d'expiration, de PID et de revue humaine répétitive pour les essais consultatifs locaux. Les anciennes preuves restent historiques ; elles ne sont ni modifiées ni approuvées artificiellement.

## Contrôles conservés

`studio_ai.verify_e11_service` délègue à `studio_e11_deployment.verify_checkpoint` : endpoint loopback épinglé, checkpoint `cbad01257c027e5861a1c0610d418dfd02fc8342`, manifeste SHA-256 épinglé et empreintes des 1526 fichiers de la copie déjà déployée. Aucune date, aucun PID ni fichier d'approbation humaine ne conditionne ce contrôle. Il vérifie les fichiers locaux ; ce n'est pas une attestation cryptographique distante du processus. Son origine et l'authentification sont contrôlées lors des opérations de service.

La clé existante reste protégée par DPAPI et transmise par environnement, jamais par argument de commande. Le POST Brody reste authentifié. Le validateur conserve les contrôles E11/B6/mémoire/reçu, les refus HOLD/BLOCK et KX108_ONLY. Le délai HTTP de 30 secondes reste en place : il ne s'agit pas de l'expiration d'une preuve.

Le résultat consultatif ne requiert plus d'approbation répétitive. `publication_permitted=false` reste obligatoire ; une publication reste soumise à revue humaine. Aucun fallback, aucune génération éditoriale, aucun retrieval supplémentaire.

## Essai unique exécuté

HTTP 200, CONTEXT_LIMITED, erreur NONE. Reçu REAL_COGNITIVE_JOIN_C1_V1, E11 COGNITION_SHADOW_MEMORY_V0, B6 B6_STATE_EXPLICIT_CONTEXT_PACKET_V1, mémoire OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1 : MEMORY_NOT_REQUIRED. Zéro élément mémoire, une inconnue, zéro omission. Reçu conservé dans la réponse, non persisté dans le journal Studio. Un POST Studio et un POST Brody constatés dans les journaux d'accès ; aucun retry. Latence client 6185 ms.

Un seul événement de métadonnées a été ajouté au journal : aucune question, aucun extrait, aucun reçu intégral ni secret. L'ancien historique n'a pas été réécrit. Studio est remis à LOT1=0 dans finally et l'autopilot reste désactivé. Brody n'a pas été redémarré. Les fichiers posts/images sont inchangés.

## Effets et limites

Brody peut écrire un ledger de session contenant la question/réponse dans sa copie existante, sous Studio ; ce ledger est distinct du journal minimal Studio. Un timeout client ne garantit pas l'annulation côté Brody. Des lectures documentaires externes restent possibles dans le code fournisseur ; aucune nouvelle isolation système n'est ajoutée. Les producteurs actifs ne sont pas modifiés. MEMORY_NOT_REQUIRED ne prouve pas une connaissance factuelle ; M41 n'est pas validé par cet essai. Un contexte E11 n'est pas une publication aboutie.

## Activation et retour arrière

L'activation reste explicite par OBSIDIA_STUDIO_ENABLE_E11_LOT1=1 au lancement de Studio ; l'absence du flag désactive le parcours. Le désactiver en relançant uniquement Studio avec la même clé et LOT1=0 ; conserver autopilot.enabled=false. Ne pas réexécuter le script de l'essai : son marqueur interdit un second appel. Aucun renouvellement de preuve n'est requis après un changement de PID. Les changements de checkpoint, d'endpoint ou d'empreintes restent bloquants et demandent une adaptation technique explicite.

Résultats détaillés : data/experiments/e11_lot1/passe10e7/run_report.json, final_checks.json et studio_all.xml.

État final vérifié : Studio PID 27848 sur 127.0.0.1:8108, LOT1=0, clé sortante présente, autopilot désactivé ; Brody PID 29460 inchangé sur 127.0.0.1:8000. La normalisation des fins de ligne a été suivie d’une nouvelle exécution complète : 247 PASS, 17 sous-tests PASS, zéro échec. Voir studio_final.xml et final_runtime.json pour la version finale. Aucun POST supplémentaire.

Règles de classification actuelles sur disque : [corrections diagnostiques 10H et plan 10I](E11_10H_DIAGNOSTICS_ET_CAMPAGNE_10I.md). MEMORY_NOT_REQUIRED ne constitue plus à lui seul une dégradation ; les autres limitations restent cumulées. Les résultats historiques ci-dessus sont conservés. Aucun rechargement de service pendant 10H.

Campagne 10I du 17 octobre 2026 : cinq POST Studio et cinq appels Brody, tous HTTP 200 / CONTEXT_LIMITED ; cinq éléments mémoire au scénario B. Studio final PID 4144, LOT1=0 et autopilot désactivé ; Brody PID 29460 inchangé. Voir [rapport comparatif réel 10I](RAPPORT_CAMPAGNE_E11_10I.md). Aucun nouveau POST au-delà des cinq scénarios.

Passe 10K : [diagnostics enrichis et résultats de régression](RAPPORT_DIAGNOSTICS_E11_10K.md), version diagnostique V2. Huit champs supplémentaires fondés uniquement sur le reçu, absences conservées en UNKNOWN. Code testé sur disque, sans POST réel ni rechargement des services pendant cette passe.

Passe 10L : [bilan final et clôture LOT 1](BILAN_FINAL_LOT1_10L.md). Studio rechargé PID 15376 avec LOT1=0, autopilot désactivé ; Brody PID 29460 inchangé. Résultats 10K reproduits : 334 PASS + 17 sous-tests, huit diagnostics synthétiques identiques, aucun POST cognitif. LOT1_CLOSED concerne le consommateur consultatif ; aucune validation sémantique B7/M41 ni génération éditoriale n'est déduite de cette clôture. Voir les artefacts `passe10l` pour les contrôles et leurs limites.
