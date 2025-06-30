# 🤖 HardstyleRanking Twitter Bot

Bienvenue dans le dépôt du bot Twitter automatisé **HardstyleRanking** \! Ce projet a pour mission de faire vibrer les fans de Hardstyle en publiant automatiquement des tweets réguliers sur les classements de titres, les actualités et les artistes du monde du Hardstyle.

Le bot est propulsé par une combinaison d'APIs :

  * **Une source de données Hardstyle** (API personnalisée ou base de données, à spécifier si elle existe).
  * **Mistral AI** pour la génération de tweets créatifs et engageants.
  * **API Twitter (X API)** pour la diffusion des messages.

L'automatisation est gérée par **GitHub Actions**, assurant une présence constante et de qualité sur Twitter.

-----

## ✨ Fonctionnalités

  * **🎧 Classements et Actualités Hardstyle :** Récupération des dernières informations sur les classements de morceaux, les actualités du genre, et les artistes émergents ou établis.
  * **🧠 Génération de Tweets Intelligente :** Utilisation de Mistral AI pour transformer les données brutes en tweets concis et captivants, formatés pour Twitter, avec des hashtags pertinents.
  * **🐦 Publication Automatisée :** Publication directe des tweets sur le compte @HardstyleRanking (ou le nom de votre compte Twitter) via l'API Twitter.
  * **⏰ Ordonnancement Régulier :** Exécution programmée plusieurs fois par jour grâce à GitHub Actions.
  * **🔒 Sécurité des Clés :** Toutes les clés d'API sont stockées en toute sécurité via les Secrets GitHub.

-----

## 🚀 Comment ça marche ?

Le workflow est simple et efficace :

1.  **Déclenchement :** GitHub Actions lance le script Python selon un **calendrier défini** (par exemple, plusieurs fois par jour) ou peut être déclenché manuellement.
2.  **Collecte de données Hardstyle :** Le script interroge une source de données Hardstyle (qui pourrait être une base de données, un fichier JSON, ou une API que vous utilisez pour vos classements).
3.  **Rédaction du tweet :** Les informations collectées sont envoyées à Mistral AI. L'IA rédige un tweet unique et percutant, incluant des hashtags et potentiellement des liens vers les morceaux ou articles.
4.  **Publication :** Le tweet généré est envoyé à l'API Twitter (X API v2) pour être publié sur le compte HardstyleRanking.
5.  **Fin d'exécution :** La tâche GitHub Actions se termine, en attendant la prochaine exécution programmée.

-----

## 🛠️ Configuration et Installation

Pour faire fonctionner ce bot, vous devrez obtenir plusieurs clés d'API et les configurer correctement.

### 1\. Clés d'API requises

  * **API Twitter (X API) :**
      * Créez un compte développeur sur [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard).
      * Créez une nouvelle application avec des **permissions d'écriture (Read and Write)**.
      * Notez vos : `API Key`, `API Key Secret`, `Access Token`, `Access Token Secret`.
  * **Mistral AI API :**
      * Inscrivez-vous sur [console.mistral.ai](https://console.mistral.ai/).
      * Générez une `API Key`.
  * **Source de données Hardstyle :**
      * (Si vous avez une API spécifique pour vos classements ou actualités Hardstyle, vous devrez générer la clé correspondante ici. Si c'est une base de données ou un fichier local, cette section peut être adaptée.)

### 2\. Configuration des Secrets GitHub

Pour des raisons de sécurité, **ne jamais inclure vos clés API directement dans le code**. Utilisez les Secrets GitHub.

1.  Sur votre dépôt GitHub, allez dans **`Settings`** (Paramètres).
2.  Dans le menu latéral, cliquez sur **`Security`** (Sécurité) \> **`Secrets and variables`** (Secrets et variables) \> **`Actions`**.
3.  Cliquez sur **`New repository secret`** (Nouveau secret de dépôt) pour ajouter chacun des secrets suivants avec leurs valeurs respectives :
      * `MISTRAL_API_KEY`
      * `TWITTER_API_KEY`
      * `TWITTER_API_SECRET`
      * `TWITTER_ACCESS_TOKEN`
      * `TWITTER_ACCESS_TOKEN_SECRET`
      * `(Votre clé d'API pour la source de données Hardstyle, si applicable, par exemple HARDSTYLE_DATA_API_KEY)`

### 3\. Fichiers du Dépôt

Assurez-vous que votre dépôt contient les fichiers suivants :

```
HardstyleRanking-Twitter-Bot/
├── .github/
│   └── workflows/
│       └── tweet.yml  # Configuration du workflow GitHub Actions
├── hardstyle_ranking_bot.py   # Le script Python du bot
└── README.md             # Ce fichier
```

  * **`hardstyle_ranking_bot.py` :** Contient le code Python principal du bot. Vous devrez l'adapter pour récupérer vos données Hardstyle spécifiques.
  * **`.github/workflows/tweet.yml` :** Configure le workflow GitHub Actions pour exécuter le bot.

-----

## 🏃 Lancement du Bot

1.  **Poussez vos modifications :** Une fois tous les fichiers (`hardstyle_ranking_bot.py`, `tweet.yml`, et ce `README.md`) ajoutés et les Secrets GitHub configurés, poussez-les vers votre dépôt GitHub.
    ```bash
    git add .
    git commit -m "Initial commit for HardstyleRanking Twitter Bot"
    git push origin main # ou master, selon votre branche principale
    ```
2.  **Vérifiez le workflow :**
      * Allez dans l'onglet **`Actions`** de votre dépôt GitHub.
      * Vous devriez voir le workflow "Daily Hardstyle Tweet" (ou le nom que vous lui avez donné dans `tweet.yml`).
      * Il se déclenchera automatiquement aux heures programmées (voir le fichier `tweet.yml`).
      * Vous pouvez également le déclencher manuellement en cliquant sur "Run workflow" dans le menu latéral du workflow.

Consultez les logs d'exécution du workflow pour vérifier le bon fonctionnement ou déboguer d'éventuels problèmes.

-----

## 🤝 Contribution

Les contributions sont les bienvenues \! Si vous avez des idées d'amélioration, des corrections de bugs ou de nouvelles fonctionnalités, n'hésitez pas à ouvrir une issue ou à soumettre une pull request.

-----

## 📜 Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT).

-----
