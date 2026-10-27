# Essai unique du brouillon natif — préparé, non exécuté

Le contrat est vérifié hors réseau. Aucun POST ni redémarrage n'a été effectué
pendant cette intégration. Les ports 8000 et 8108 étaient libres au contrôle final.

1. Codex vérifiera les ports, l'autopilot désactivé et le manifeste épinglé
   `ff2006c5159cc49b60739180f36268d987be771cc8dc99e74f696136b5a41c0c`.
   Base conservée : `cbad01257c027e5861a1c0610d418dfd02fc8342` ; overlay WIP
   documenté depuis `474afd9ca4b77bf127c31ce22599d52438a7ff37`. Ne pas annoncer
   que l'ensemble du déploiement correspond à un commit unique.
2. Sur autorisation d'exécution, Codex lancera seulement Brody depuis la copie
   Studio vérifiée et Studio, sans `--reload`. Brody restera authentifié, lié à
   `127.0.0.1:8000`; la même clé sera transmise par `X-API-Key`, jamais affichée.
   Une clé absente entraîne HOLD. Vérifier santé, OpenAPI et origine des processus.
   Un simple endpoint joignable ne constitue pas une preuve d'identité du code.
3. Studio : `OBSIDIA_STUDIO_EDITORIAL_MODE=brody_native`,
   `OBSIDIA_STUDIO_ALLOW_BRODY_NATIVE=1`,
   `OBSIDIA_STUDIO_USE_INGRESS=0`, `OBSIDIA_STUDIO_ENABLE_E11_LOT1=0`.
   Autopilot désactivé. Aucun service Qwen ou Ingress n'est nécessaire à ce test.
4. Envoyer exactement un POST à `http://127.0.0.1:8108/api/generate`, sans retry :

```json
{
  "network": "linkedin",
  "idea": "Rédige une publication LinkedIn expliquant comment une petite entreprise des Ardennes peut utiliser l'IA pour gagner du temps sans gros budget.",
  "source_text": ""
}
```

Le brief est le brief public testé, conservé tel quel. Les formulations ou sujets
non couverts par le compositeur borné peuvent rester en HOLD ; ne pas les
réécrire silencieusement pour forcer une admission.

5. Vérifier HTTP, `<POST>`, provenance `BRODY_NATIVE_EDITORIAL_V1`, lignée vérifiée,
   plan et réalisation natifs. Montrer le texte complet uniquement si admis,
   avec `human_approval_required=true`, `publication_permitted=false`.
   Conserver séparément `CONTEXT_LIMITED`, les inconnues et les omissions.
   Un refus HTTP 409 est un résultat valide, sans fallback ni seconde tentative.
6. Dans un `finally`, maintenir LOT1=0 et autopilot désactivé. Enregistrer seulement
   statuts, durée, compteurs et empreintes dans le diagnostic. Ne pas persister
   de reçu intégral, clé ou mémoire privée. Aucun appel de publication/sauvegarde
   automatique de post. Un timeout Studio ne garantit pas l'annulation Brody.

Effets connus de Brody : son orchestrateur peut tenter d'écrire un ledger de
session et de sonder Graphiti. Les deux appels de fonction hors réseau ont
rencontré deux tentatives de chaque type, toutes bloquées par le harnais.
Un test HTTP futur peut produire ce ledger local : ne pas le confondre avec une
écriture autorisée de connaissance. `MEMORY_WRITE_HOLD` reste obligatoire.

Retour arrière : utiliser exclusivement le dossier de sauvegarde
`data/experiments/native_editorial_integration_20261023/before` et
`deployment_plan.json`. Restaurer les huit fichiers déployés remplacés, retirer
uniquement les huit ajouts identifiés après vérification d'empreinte, puis
restaurer manifeste, sidecars et garde Studio ensemble. Préserver tout nouveau
WIP local. Ne pas employer Git reset, une copie globale ou une référence
productrice mouvante. Aucun rollback n'est exécuté pendant cette passe.
