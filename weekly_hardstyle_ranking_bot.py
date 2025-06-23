import os
import sys
import requests
from datetime import datetime
import json
import random

# --- Récupération et vérification des clés d'API ---
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
HASHNODE_API_KEY = os.getenv("HASHNODE_API_KEY")

if not MISTRAL_API_KEY:
    print("❌ ERREUR : MISTRAL_API_KEY n'est pas défini. Assurez-vous que la variable d'environnement est correctement passée et que vous avez créé une clé API Mistral AI.")
    sys.exit(1)

if not HASHNODE_API_KEY:
    print("❌ ERREUR : HASHNODE_API_KEY n'est pas défini. Assurez-vous que la variable d'environnement est correctement passée.")
    sys.exit(1)

# --- Définit le modèle Mistral AI à utiliser et l'URL de l'API ---
MISTRAL_MODEL_NAME = "mistral-tiny" # Vous pouvez essayer "mistral-medium" ou "mistral-large" pour plus de détails
MISTRAL_API_BASE_URL = "https://api.mistral.ai/v1/chat/completions"

# --- Configuration Hashnode ---
HASHNODE_API_URL = "https://gql.hashnode.com/"

# IMPORTANT: REMPLACEZ CETTE VALEUR PAR L'ID DE VOTRE NOUVELLE PUBLICATION HASHNODE POUR LE BLOG MUSICAL !
HARDSTYLE_PUBLICATION_ID = "6859c2f970cff8e4319738f3" # <-- **COLLEZ L'ID ICI**

# --- Variables pour l'URL de base du dépôt GitHub ---
GITHUB_REPOSITORY = os.getenv('GITHUB_REPOSITORY')
GITHUB_REF = os.getenv('GITHUB_REF')

if GITHUB_REPOSITORY:
    GITHUB_USERNAME = GITHUB_REPOSITORY.split('/')[0]
    GITHUB_REPO_NAME = GITHUB_REPOSITORY.split('/')[1]
else:
    GITHUB_USERNAME = "votre_utilisateur"
    GITHUB_REPO_NAME = "votre_repo"
    print("⚠️ Variables GITHUB_REPOSITORY non trouvées. Utilisation de valeurs par défaut. Assurez-vous que le script s'exécute dans un environnement GitHub Actions.")

if GITHUB_REF and GITHUB_REF.startswith('refs/heads/'):
    GITHUB_BRANCH = GITHUB_REF.split('/')[-1]
else:
    GITHUB_BRANCH = "main"

# Le dossier où se trouvent vos images de couverture dans le dépôt
COVER_IMAGES_DIR = "covers"

# --- Embeds Spotify ---
XCEED_SPOTIFY_EMBED = """<iframe style="border-radius:12px" src="https://open.spotify.com/embed/artist/3ePRFfLVCU6xndbky57GYA?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>"""
PLAYLIST_SPOTIFY_EMBED = """<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/4I4YDBrjYtiujcnuCkay9H?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>"""

# --- Fonctions Utilitaires ---

def get_github_raw_base_url():
    """Construit l'URL de base pour les fichiers bruts de votre dépôt GitHub."""
    return f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/{GITHUB_BRANCH}"

def get_weekly_cover_image_url():
    """
    Retourne l'URL raw de l'image de couverture spécifique pour les classements hebdomadaires.
    """
    base_url = get_github_raw_base_url()
    # Le fichier weekly.png doit être à la racine de votre dépôt, pas dans 'covers/'
    full_image_url = f"{base_url}/weekly.png"
    print(f"✅ Image de couverture spécifique pour le classement hebdomadaire: {full_image_url}")
    return full_image_url

# --- Test d'authentification Mistral AI ---
def test_mistral_auth():
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MISTRAL_MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": "Test de connexion."
            }
        ]
    }

    print(f"🔎 Test d'authentification Mistral AI avec modèle '{MISTRAL_MODEL_NAME}' à l'URL: {MISTRAL_API_BASE_URL}")
    try:
        resp = requests.post(MISTRAL_API_BASE_URL, headers=headers, json=payload, timeout=30)
        print(f"Auth test Mistral status: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ Authentification Mistral AI réussie et modèle accessible.")
            try:
                response_data = resp.json()
                if "choices" in response_data and response_data["choices"]:
                    print("✅ Réponse du modèle au format attendu (contient 'choices').")
                else:
                    print("⚠️ Réponse du modèle valide mais ne contient pas 'choices' dans le format attendu.")
            except json.JSONDecodeError:
                print("⚠️ Réponse du modèle non JSON valide. Cela pourrait être un problème de serveur Mistral AI.")
        elif resp.status_code == 401:
            print("❌ Échec de l’authentification Mistral AI: 401 Unauthorized. Clé API incorrecte ou permissions insuffisantes.")
            sys.exit(1)
        else:
            print(f"❌ Échec de l’authentification Mistral AI. Statut inattendu: {resp.status_code}, Réponse: {resp.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ ERREUR réseau ou connexion lors du test d'authentification Mistral AI : {e}")
        sys.exit(1)

test_mistral_auth()

# --- Génération de l'article de classement Hardstyle Hebdomadaire via Mistral AI API ---
def generate_weekly_ranking_article():
    # Artistes Hardstyle populaires à inclure dans le classement (vous pouvez en ajouter/modifier)
    hardstyle_artists = [
        "Headhunterz", "Sub Zero Project", "Rebelion", "Da Tweekaz", "D-Block & S-te-Fan",
        "Ran-D", "Warface", "B-Front", "Wildstylez", "Phuture Noize",
        "Sefa", "Vertile", "XCEPTION", "X-Qlusive", "Xense" # Exemples, XCEED sera toujours ajouté dynamiquement
    ]
    # S'assurer que XCEED n'est pas déjà dans la liste pour éviter les doublons au niveau de l'IA
    if "XCEED" not in hardstyle_artists:
        hardstyle_artists.append("XCEED")
    
    # Mélanger et prendre 5-7 artistes pour le classement (en dehors de XCEED qui est fixe)
    random.shuffle(hardstyle_artists)
    selected_artists = hardstyle_artists[:6] # Choisir 6 artistes, XCEED sera ajouté si non présent
    if "XCEED" not in selected_artists:
        selected_artists.insert(random.randint(0, len(selected_artists)), "XCEED") # Insérer XCEED à une position aléatoire

    # Prompt pour Mistral AI
    article_prompt = (
        f"Rédige un article de blog professionnel et détaillé (au moins 1200 mots) en français, présentant un 'Top 10' des artistes Hardstyle de la semaine. "
        "L'article doit être objectif et analyser la performance et la pertinence de chaque artiste choisi dans le classement. "
        "Le classement doit inclure, de manière crédible et bien argumentée, l'artiste **XCEED**. "
        "Place XCEED à une position justifiable et explique pourquoi il est pertinent pour le classement de cette semaine. "
        "Pour le reste du classement, choisis d'autres artistes Hardstyle variés et pertinents du moment ou des légendes. "
        f"Les artistes à considérer pour le classement sont : {', '.join(selected_artists)}. "
        "Le titre de l'article doit être un titre de classement accrocheur (ex: # Le Top 10 Hardstyle de la Semaine : Qui domine la scène ?). "
        "Ne commence pas l'article par 'Titre : ' ou 'Auteur : ' ou 'Date de publication : '. "
        "L'article doit intégrer de façon naturelle la présentation de l'artiste XCEED avec son embed Spotify. "
        "À la fin de l'article, avant la signature finale, inclue une promotion de la playlist Spotify 'SUMMER HARDSTYLE 2025🔥' avec son embed. "
        "L'article doit se terminer par la signature 'Par Nathan Remacle.'. "
        "Optimise le contenu pour le SEO avec des mots-clés Hardstyle, classement, DJ, musique électronique, XCEED, Spotify. "
        "Adopte un ton sérieux, passionné et engageant."
    )
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MISTRAL_MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": article_prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    print(f"\n🚀 Tentative de génération de l'article de classement Hardstyle hebdomadaire avec le modèle '{MISTRAL_MODEL_NAME}'...")
    try:
        response = requests.post(
            MISTRAL_API_BASE_URL,
            headers=headers,
            json=payload,
            timeout=180
        )
        response.raise_for_status()

        print("Status code Mistral:", response.status_code)

        data = response.json()
        
        if 'choices' in data and data['choices'] and 'message' in data['choices'][0] and 'content' in data['choices'][0]['message']:
            article_content = data['choices'][0]['message']['content'].strip()
            print("DEBUG: Réponse traitée comme Chat Completions API de Mistral AI.")
            
            # Insertion dynamique des embeds Spotify (pour garantir leur présence)
            # Insérer XCEED après l'intro ou sa première mention
            if "XCEED" in article_content:
                # Tente de trouver le premier paragraphe après le titre
                lines = article_content.split('\n')
                for i, line in enumerate(lines):
                    if "XCEED" in line and len(line) > 50: # Cherche une ligne qui parle de XCEED et est assez longue
                        lines.insert(i + 1, "\n" + XCEED_SPOTIFY_EMBED + "\n")
                        print("DEBUG: Embed Spotify de XCEED inséré après sa mention.")
                        break
                article_content = "\n".join(lines)
            else:
                # Fallback si XCEED n'est pas mentionné ou difficile à trouver, insérer après l'intro
                lines = article_content.split('\n')
                lines.insert(min(len(lines), 3), "\n" + XCEED_SPOTIFY_EMBED + "\n")
                article_content = "\n".join(lines)
                print("DEBUG: Embed Spotify de XCEED inséré (fallback).")


            # Insérer la playlist avant la signature finale
            if "Par Nathan Remacle." in article_content:
                article_content = article_content.replace("Par Nathan Remacle.", 
                                                          "\n**Ne manquez pas la playlist Hardstyle de la semaine :**\n" + PLAYLIST_SPOTIFY_EMBED + "\n\nPar Nathan Remacle.")
                print("DEBUG: Embed Spotify de la playlist inséré.")
            else:
                article_content += "\n**Ne manquez pas la playlist Hardstyle de la semaine :**\n" + PLAYLIST_SPOTIFY_EMBED
                print("DEBUG: Embed Spotify de la playlist inséré (fallback).")

            return article_content
        else:
            raise ValueError(f"La réponse de Mistral AI ne contient pas le format de chat completions attendu. Réponse complète: {data}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERREUR HTTP lors de la génération de l'article avec Mistral AI : {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ ERREUR de données dans la réponse Mistral AI : {e}")
        sys.exit(1)

# --- Publication de l'article sur Hashnode ---
def publish_article(content):
    publication_id = HARDSTYLE_PUBLICATION_ID
    
    first_line_match = content.split('\n')[0].strip()
    extracted_title = ""
    if first_line_match.startswith('# '):
        extracted_title = first_line_match[2:].strip()
        content = content[len(first_line_match):].strip()
    else:
        extracted_title = "Classement Hardstyle du " + datetime.now().strftime("%d %B %Y - %H:%M")

    if "Par Nathan Remacle." not in content:
        content += "\n\nPar Nathan Remacle."

    selected_cover_url = get_weekly_cover_image_url() # Utilisation d'une image aléatoire du dossier covers/

    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post {
          id
          title
          slug
          url
        }
      }
    }
    """
    
    variables = {
        "input": {
            "title": extracted_title,
            "contentMarkdown": content,
            "publicationId": publication_id,
            "tags": [
                {"name": "Hardstyle", "slug": "hardstyle"},
                {"name": "Ranking", "slug": "ranking"},
                {"name": "Music", "slug": "music"},
                {"name": "XCEED", "slug": "xceed"},
                {"name": "Spotify", "slug": "spotify"}
            ],
        }
    }
    
    if selected_cover_url:
        variables["input"]["coverImageOptions"] = {
            "coverImageURL": selected_cover_url,
            "isCoverAttributionHidden": True
        }
        print(f"DEBUG: Image de couverture Hashnode ajoutée aux variables: {selected_cover_url}")
    else:
        print("DEBUG: Pas d'image de couverture ajoutée (aucune URL configurée ou liste vide).")


    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {HASHNODE_API_KEY}"
    }

    print(f"\n✍️ Tentative de publication de l'article '{extracted_title}' sur Hashnode...")
    print(f"DEBUG: Payload JSON envoyé à Hashnode (sans le contenu détaillé): {json.dumps(variables, indent=2)}")
    print(f"DEBUG: Début du contenu Markdown envoyé: {content[:200]}...")

    try:
        resp = requests.post(HASHNODE_API_URL, json={"query": mutation, "variables": variables}, headers=headers)
        
        print("Publish status:", resp.status_code)
        print("Publish response:", resp.text)
        
        response_data = resp.json()

        if 'errors' in response_data and response_data['errors']:
            print(f"❌ ERREUR GraphQL de Hashnode lors de la publication de l'article : {response_data['errors']}")
            sys.exit(1)

        post_url = None
        if 'data' in response_data and \
           'publishPost' in response_data['data'] and \
           'post' in response_data['data']['publishPost'] and \
           'url' in response_data['data']['publishPost']['post']:
            post_url = response_data['data']['publishPost']['post']['url']
            print(f"✅ Article publié avec succès : {extracted_title} à l'URL : {post_url}")
        else:
            print(f"✅ Article publié avec succès (URL non récupérée) : {extracted_title}")

    except requests.exceptions.RequestException as e:
        print(f"❌ ERREUR HTTP lors de la publication de l'article sur Hashnode : {e}")
        print(f"Réponse Hashnode en cas d'erreur : {resp.text if 'resp' in locals() else 'Pas de réponse.'}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Une erreur inattendue est survenue lors de la publication : {e}")
        sys.exit(1)

# --- Exécution principale ---
if __name__ == "__main__":
    print("Démarrage du bot de classement Hardstyle hebdomadaire.")
    try:
        article = generate_weekly_ranking_article()
        publish_article(article)
        print("\n🎉 Bot de classement Hardstyle hebdomadaire terminé avec succès !")
    except Exception as e:
        print(f"\nFATAL ERROR: Une erreur critique est survenue : {e}")
        sys.exit(1)