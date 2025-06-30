# 🤖 HardstyleRanking Bot

Bienvenue dans le dépôt du bot Twitter automatisé **HardstyleRanking** \! Ce projet contient le code qui automatise la génération et la publication de contenu pour le blog [HardstyleRanking sur Hashnode](https://hardstyleranking.hashnode.dev/)

## ✨ Fonctionnalités

Ce dépôt héberge deux bots distincts pour la publication de contenu sur Hashnode :

  * **Daily Hardstyle Article Bot (`daily_hardstyle_bot.py`) :**

      * Génère un article de blog quotidien sur un sujet Hardstyle aléatoire.
      * Intègre des mentions de l'artiste **XCEED** et de la **playlist Spotify 'SUMMER HARDSTYLE 2025🔥'**.
      * Utilise Mistral AI pour créer un contenu captivant et détaillé d'au moins 1200 mots.
      * Publie l'article sur votre blog Hashnode avec une image de couverture spécifique (`daily.png`).
      * Applique des **tags SEO** pertinents comme "Hardstyle", "Music", "Electronic Music".

  * **Weekly Hardstyle Ranking Bot (`weekly_hardstyle_ranking_bot.py`) :**

      * *(Note: Ce fichier est mentionné mais son contenu n'est pas fourni. Le README suppose qu'il génère des classements hebdomadaires.)*
      * Génère un article de blog hebdomadaire, probablement axé sur les classements de morceaux ou d'artistes Hardstyle.
      * Publie l'article sur votre blog Hashnode, potentiellement avec une autre image de couverture spécifique (`weekly.png`).

  * **Automatisation Robuste :** Les deux bots sont déclenchés et exécutés automatiquement via **GitHub Actions** selon des horaires prédéfinis.

  * **Sécurité des Clés :** Toutes les clés d'API (Mistral AI, Hashnode) sont stockées en toute sécurité via les **Secrets GitHub**.

-----

## 🚀 Comment ça marche ?

Chaque bot (quotidien et hebdomadaire) suit un processus similaire, orchestré par GitHub Actions :

1.  **Déclenchement :** Un workflow GitHub Actions (`.github/workflows/`) lance le script Python (`daily_hardstyle_bot.py` ou `weekly_hardstyle_ranking_bot.py`) selon un calendrier défini (par exemple, tous les jours pour le bot quotidien, une fois par semaine pour le bot hebdomadaire) ou peut être déclenché manuellement.
2.  **Génération de Contenu (Mistral AI) :**
      * Le script contacte l'API Mistral AI avec un prompt spécifique au sujet du jour/de la semaine.
      * Mistral AI génère un article de blog détaillé en Markdown, incluant les mots-clés et les intégrations spécifiées (comme XCEED et la playlist Spotify).
      * Le contenu est post-traité pour assurer la conformité et la suppression des éventuels artefacts.
3.  **Publication sur Hashnode :**
      * Le script extrait le titre de l'article généré.
      * Il prépare une requête API GraphQL pour Hashnode, incluant le contenu Markdown, le titre, l'ID de votre publication Hashnode, des tags prédéfinis et l'URL de l'image de couverture.
      * L'article est publié sur votre blog HardstyleRanking sur Hashnode.
4.  **Fin d'exécution :** La tâche GitHub Actions se termine, en attendant la prochaine exécution programmée.

-----

## 🛠️ Structure du Dépôt

```
HardstyleRanking-Blog-Automation-Bot/
├── .github/
│   └── workflows/      # Fichiers de configuration pour GitHub Actions
│       └── daily_post.yml  # Exemple pour le bot quotidien
│       └── weekly_post.yml # Exemple pour le bot hebdomadaire
├── daily.png               # Image de couverture pour les articles quotidiens
├── weekly.png              # Image de couverture pour les articles hebdomadaires
├── daily_hardstyle_bot.py      # Code Python pour la génération et publication quotidienne
├── weekly_hardstyle_ranking_bot.py # Code Python pour la génération et publication hebdomadaire
├── requirements.txt        # Liste des dépendances Python
└── README.md               # Ce fichier
```

-----

## ⚙️ Configuration et Installation

Pour faire fonctionner ce bot, vous devrez obtenir et configurer plusieurs clés d'API.

### 1\. Clés d'API requises

  * **Mistral AI API :**
      * Inscrivez-vous sur [console.mistral.ai](https://console.mistral.ai/).
      * Générez une `API Key`.
  * **Hashnode API :**
      * Dans votre tableau de bord Hashnode, allez dans `Settings` (Paramètres) \> `Developer` (Développeur).
      * Générez une `Personal Access Token`. Notez cette clé.

### 2\. Configuration des Secrets GitHub

Pour des raisons de sécurité, **ne jamais inclure vos clés API directement dans le code**. Utilisez les Secrets GitHub.

1.  Sur votre dépôt GitHub, allez dans **`Settings`** (Paramètres).
2.  Dans le menu latéral, cliquez sur **`Security`** (Sécurité) \> **`Secrets and variables`** (Secrets et variables) \> **`Actions`**.
3.  Cliquez sur **`New repository secret`** (Nouveau secret de dépôt) pour ajouter chacun des secrets suivants avec leurs valeurs respectives :
      * `MISTRAL_API_KEY`
      * `HASHNODE_API_KEY`

### 3\. ID de Publication Hashnode

Vous devez configurer l'ID de votre publication Hashnode directement dans le code Python :

  * Dans `daily_hardstyle_bot.py` (et `weekly_hardstyle_ranking_bot.py` si applicable), mettez à jour la ligne suivante avec l'ID de votre blog HardstyleRanking :
    ```python
    HARDSTYLE_PUBLICATION_ID = "YOUR_HASHNODE_PUBLICATION_ID_HERE"
    ```
    Vous pouvez trouver cet ID dans l'URL de votre publication lorsque vous êtes connecté à votre tableau de bord Hashnode, ou via l'API GraphQL de Hashnode.

### 4\. Dépendances Python

Les bibliothèques Python nécessaires sont listées dans `requirements.txt`. GitHub Actions les installera automatiquement.

```
requests
```

-----

## 🚀 Lancement du Bot

1.  **Poussez vos modifications :** Une fois tous les fichiers (`daily_hardstyle_bot.py`, `weekly_hardstyle_ranking_bot.py`, `requirements.txt`, vos images `daily.png`, `weekly.png` et les fichiers de workflow sous `.github/workflows/`) ajoutés et les Secrets GitHub configurés, poussez-les vers votre dépôt GitHub.
    ```bash
    git add .
    git commit -m "Initial commit for HardstyleRanking Blog Automation Bot"
    git push origin main # ou master, selon votre branche principale
    ```
2.  **Vérifiez les workflows :**
      * Allez dans l'onglet **`Actions`** de votre dépôt GitHub.
      * Vous devriez voir les workflows correspondants à vos fichiers `.yml` (par exemple, "Daily Hardstyle Post" et "Weekly Hardstyle Ranking").
      * Ils se déclencheront automatiquement aux heures programmées.
      * Vous pouvez également les déclencher manuellement en cliquant sur le nom du workflow, puis "Run workflow".

Consultez les logs d'exécution du workflow pour vérifier le bon fonctionnement ou déboguer d'éventuels problèmes.

-----

## 🤝 Contribution

Les contributions sont les bienvenues \! Si vous avez des idées d'amélioration, des corrections de bugs ou de nouvelles fonctionnalités, n'hésitez pas à ouvrir une [issue](https://www.google.com/search?q=https://github.com/votre_utilisateur/votre_repo/issues) ou à soumettre une [pull request](https://www.google.com/search?q=https://github.com/votre_utilisateur/votre_repo/pulls).

-----

## 📜 Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT).

-----
