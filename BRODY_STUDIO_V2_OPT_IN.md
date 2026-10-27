# Studio — Brody V2 opt-in

V1 reste la valeur par défaut de `GenIn.editorial_version` et `studio_ai.generate()`. Le choix est un enum fermé, sans sélection implicite selon le sujet ou le résultat.

Pour un futur essai explicitement autorisé, le corps de `/api/generate` peut contenir :

```json
{"idea":"Comment une petite entreprise des Ardennes peut-elle utiliser l’intelligence artificielle pour gagner du temps sans gros budget ni compétences techniques ?","network":"linkedin","editorial_version":"V2"}
```

Ce document ne déclenche aucun appel. Ne pas exécuter cette requête pendant la validation hors réseau.

Conditions opérationnelles avant l’essai : charger les nouveaux fichiers par un redémarrage contrôlé ultérieur ; vérifier les processus, origines, authentification `X-API-Key` existante et le manifeste ; conserver autopilot désactivé et LOT1=0. Le parcours natif exige les activations existantes `OBSIDIA_STUDIO_EDITORIAL_MODE=brody_native` et `OBSIDIA_STUDIO_ALLOW_BRODY_NATIVE=1`. L’opt-in V2 ne constitue aucun fallback depuis Ingress : V2 + Ingress est refusé avant transport.

Studio exige un artefact `BRODY_PUBLIC_EDITORIAL_ARTIFACT_V2` et une composition `BRODY_NATIVE_EDITORIAL_V2`, liés à la demande V2, au brief réellement envoyé, au checkpoint et aux empreintes locales. Il recalcule seulement la grammaire, les propositions, le plan, la réalisation et C275 depuis les fonctions natives vérifiées. Aucun second Router, modèle, SENS ou retrieval n’est exécuté par le validateur.

Le snapshot, ses inconnues, le reçu C1 et le résultat E11/B6 sont conservés. `CONTEXT_LIMITED` n’est pas une réussite factuelle ; `MEMORY_NOT_REQUIRED` n’est pas une preuve de vérité. Les contradictions, inconnues indispensables, HOLD/BLOCK, autorités incompatibles et sorties Qwen restent refusés. La version V1 reçue ne satisfait pas une demande V2 et inversement.

La lignée est une vérification locale du déploiement, pas une attestation cryptographique distante du processus. `model_calls=0` concerne la composition native ; les références auxiliaires du reçu restent distinctes. Aucun statut B7/M41 n’est promu.

Le résultat est un brouillon consultatif : `human_approval_required=true`, `publication_permitted=false`, `MEMORY_WRITE_HOLD`. Pas de sauvegarde automatique du texte dans un journal minimal ni de publication.

Un seul futur essai, sans retry ni fallback : examiner HTTP Studio/Brody, source native V2, plan, sélection, réalisation, provenance, E11, inconnues et frontières. Un timeout ne garantit pas l’annulation côté Brody. Un appel réel peut écrire un ledger de session côté producteur ; aucun tel appel n’a été effectué dans cette passe.

## Retour arrière

Pour les demandes suivantes, omettre `editorial_version` ou choisir `V1` : ce retour fonctionnel utilise la même copie vérifiée, sans transfert inverse.

Pour revenir au déploiement initial : arrêter les services concernés lors d’une opération ultérieure autorisée, restaurer ensemble les quatre fichiers de `data/experiments/native_editorial_v2_integration_20261024/before/source`, les manifestes de `before/deployment` et `before/studio/studio_e11_deployment.py`, puis vérifier les empreintes et redémarrer de manière contrôlée. Ne jamais modifier seulement le pin ou un manifeste pour accepter un fichier différent. Les sauvegardes du consommateur sont dans `before/studio` ; préserver tout WIP ultérieur avant restauration.

Aucun retour arrière ni redémarrage n’est exécuté par ce protocole.
