# Obsidia Studio

Studio local de planification, storytelling et préparation de contenus pour LinkedIn, Facebook, Instagram, YouTube et X.

**État : V0 — reprise du build GitHub le 15 octobre 2026.** Le code est public ; le serveur et les données de travail restent locaux.

## Démarrage (Windows)

Prérequis : Python 3.10+, Chrome pour le rendu des visuels, et facultativement Claude Code disponible dans le PATH pour la génération IA.

```powershell
cd "C:\Users\User\obsidia-studio"
python -m pip install -r requirements.txt
python server.py
```

Puis ouvrir http://127.0.0.1:8108 (ou lancer `lancer.bat`).

## Fonctionnalités présentes dans le code

- calendrier, brouillons et campagnes multi-réseaux ;
- propositions d'idées, adaptations, templates et génération via Claude Code ;
- visuels PNG et carrousels PDF via Chrome local ;
- journal de bord, banque de preuves, audit des avancées, statistiques et pilote de préparation.

**Aucune publication automatique sur les réseaux.** Les validations et publications restent manuelles.

## Données locales : précaution indispensable

Le répertoire `data/` est ignoré par Git et **n'est pas livré par le dépôt**. Il contient notamment les posts, images, campagnes, templates, profils, guides, journaux, preuves et configuration du pilote. Conserver ce répertoire lors des `git pull` ; ne pas lancer `git clean -fdx`.

Certaines fonctions dépendent de données déjà créées dans l'installation locale initiale. Sur une nouvelle machine, le code ne suffit donc pas encore à reproduire entièrement l'environnement. La portabilité et l'initialisation des données sont des chantiers à terminer.

Les commandes Claude utilisent actuellement aussi `%USERPROFILE%\.claude\linkedin\` et les skills `li-human`, qui restent externes à ce dépôt.

## Cycle de développement

Les changements de code sont poussés sur `main`. Sur le PC local :

```powershell
cd "C:\Users\User\obsidia-studio"
git pull --ff-only origin main
python server.py
```

Avant de modifier les fonctionnalités, contrôler le statut Git et tester les parcours critiques dans le navigateur. Ne jamais versionner de jetons, profils personnels ou documents internes.


## IA Obsidia — Brody en premier (sans Monde ni CSSA)

Le raccordement éditorial passe par l'API cognitive de la stack Obsidia, **pas directement par Qwen**. Chaîne cible : Studio → `POST /api/brody/chat` → Brody / routeur cognitif interne → Qwen **seulement si nécessaire** → proposition de texte → vérification éditoriale → validation humaine.

Ce contrat provient des intégrations Jarjar / OpenJarvis ; nous réutilisons le point d'entrée, **pas leur interface**. Studio ne modifie aucun dépôt de la stack.

Adresse par défaut : `http://127.0.0.1:8000`. Si l'API Brody écoute ailleurs, configurer dans le terminal AVANT le démarrage :

```powershell
$env:OBSIDIA_STUDIO_BRODY_URL="http://127.0.0.1:8000"
python server.py
```

`GET /api/ai/status` indique la configuration et tente de consulter `/openapi.json`. La route `/api/brody/chat` attend `message`, `language`, `session_id`, `allow_provider` ; la réponse doit fournir un texte sous `response`, `final_answer` ou `response_md`. La conformité effective au runtime actuel doit encore être testée sur le PC. L'absence d'API (ou de Qwen interne) produit une erreur explicite, **jamais un appel direct silencieux de Studio vers Qwen ni Claude**.

Les contextes locaux sont lus par le serveur Studio ; seules les preuves `public=true` sont incluses dans l'extrait de la banque de preuves. Les textes générés restent des propositions, sans autorité d'exécution ni publication automatique. `data/` est exclu de Git.


## Moteur éditorial local indépendant (Studio uniquement)

Le mode `studio_local_model` demande un véritable brouillon à un modèle déjà
disponible sur **Ollama local**, via `http://127.0.0.1:11434/api/chat`.
Il n'édite ni Jarvis, ni Brody, ni aucun autre dépôt. Il **n'est pas** un
repli automatique après HOLD : il faut le sélectionner explicitement.
Ce brouillon est identifié comme `STUDIO_LOCAL_OLLAMA`, jamais comme Brody.

Dans PowerShell, avant de lancer Studio :

```powershell
$env:OBSIDIA_STUDIO_EDITORIAL_MODE="studio_local_model"
$env:OBSIDIA_STUDIO_OLLAMA_MODEL="nom-exact-du-modele-deja-installe"
python server.py
```

Vérifier les modèles disponibles avec `ollama list`. Si Ollama ou le
modèle ne sont pas installés, le mode renvoie une erreur explicite ;
aucun texte préfabriqué n'est prétendu généré. Le modèle n'effectue aucune
publication : vérification et approbation humaine restent nécessaires.
Les modes `governed_ingress` et `brody_native` sont conservés séparément.
