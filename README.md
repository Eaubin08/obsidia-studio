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


## IA locale Obsidia / Qwen (sans interface Monde)

Depuis l'adaptateur `studio_ai.py`, les générations demandées par le Studio sont envoyées à un serveur **local compatible avec l'API OpenAI**. Ni Monde ni CSSA ne sont nécessaires. Le Studio ne lance **pas** Qwen, Brody ou Obsidure : il les appelle uniquement si un endpoint local compatible est disponible.

Par défaut : `http://127.0.0.1:8080/v1/chat/completions`, modèle `local` (**valeurs de configuration, non vérifiées sur votre PC**). Dans PowerShell, avant `python server.py` :

```powershell
$env:OBSIDIA_STUDIO_AI_URL="http://127.0.0.1:8080/v1"
$env:OBSIDIA_STUDIO_AI_MODEL="local"
python server.py
```

Si Qwen expose un autre port ou un autre identifiant de modèle, adaptez ces deux variables. Consultez `GET /api/ai/status` pour la configuration lue par le Studio : ce diagnostic **ne confirme pas la disponibilité réelle** du modèle. Un appel à `/api/generate` vérifie la connexion et renvoie une erreur explicite si le service est absent. Les modèles locaux doivent respecter le contrat Chat Completions non-streaming (`choices[0].message.content`). Le serveur n'envoie aucune requête vers Internet depuis cet adaptateur : seul HTTP loopback est autorisé.

Les prompts sont enrichis avec les documents locaux existants et **seules les preuves marquées `public=true`** sont transmises depuis `proofs.json`. Les brouillons produits doivent encore être vérifiés par l'utilisateur. Certaines étiquettes historiques du code parlent encore de « Claude » : elles seront remplacées dans une passe d'interface ultérieure.

Les autres sources locales et `data/` restent privées et exclues de Git. Aucun appel à une API de publication n'est ajouté.
