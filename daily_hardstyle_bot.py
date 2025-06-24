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
    GITHUB_USERNAME = "votre_utilisateur" # Fallback si pas en environnement GH Actions
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

def get_daily_cover_image_url():
    """
    Retourne l'URL raw de l'image de couverture spécifique pour les articles quotidiens.
    """
    base_url = get_github_raw_base_url()
    # Le fichier weekly.png doit être à la racine de votre dépôt, pas dans 'covers/'
    full_image_url = f"{base_url}/daily.png"
    print(f"✅ Image de couverture spécifique pour le quotidien: {full_image_url}")
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

# --- Génération de l'article Hardstyle Quotidien via Mistral AI API ---
def generate_daily_hardstyle_article():
    # Mots-clés pour des articles Hardstyle variés
    hardstyle_topics = [
        "the evolution of Hardstyle", "Hardstyle subgenres (Raw, Euphoric, Xtra Raw)",
        "Hardstyle's impact on the electronic music scene", "essential Hardstyle festivals",
        "Hardstyle production techniques", "the history of an iconic Hardstyle label",
        "the culture of Hardstyle raves", "legendary Hardstyle DJ sets",
        "the future of Hardstyle", "sound innovation in Hardstyle",
        "the energy and emotion of Hardstyle", "iconic Hardstyle melodies"
    ]
    chosen_topic = random.choice(hardstyle_topics)

    # CHANGED: Prompt en anglais, suppression de la signature, ajout de l'instruction pour la note
    article_prompt = (
        f"Write a professional, detailed, and captivating blog post of at least 1200 words in English on {chosen_topic} presenting a 'Top 10' or 'Top 15' or any Top Hardstyle artists of the day."
        "The article must resonate with electronic music and Hardstyle fans. "
        "Naturally integrate mentions of the artist **XCEED** and the **Spotify playlist 'SUMMER HARDSTYLE 2025🔥'**. "
        "Do NOT mention or include any notes about Spotify links being examples or placeholder. "
        "The title of the article must be included at the beginning of the content (H1 markdown format, e.g., # Your Catchy Hardstyle Title). "
        "The title should be impactful, SEO-friendly, and engaging for the Hardstyle audience. Do not start the title by 'Unleashing' or 'Unleash' or things like that"
        "Do not start the article with 'Title: ', 'Author: ', or 'Publication Date: '. "
        "Do NOT include any closing signature at the end of the article. "
        "Optimize the content for SEO by naturally including relevant keywords (Hardstyle, electronic music, DJ, festivals, XCEED, Spotify). "
        "Adopt a passionate and engaging tone, avoiding overly 'AI-like' formulations."
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
        "max_tokens": 2000 # Ajusté pour correspondre à 1200 mots
    }

    print(f"\n🚀 Attempting to generate daily Hardstyle article on '{chosen_topic}' with model '{MISTRAL_MODEL_NAME}'...")
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
            print("DEBUG: Response processed as Chat Completions API from Mistral AI.")
            
            # Post-traitement pour retirer la signature et la note si l'IA les ajoute par erreur
            article_content = article_content.replace("Par Nathan Remacle.", "").strip()
            article_content = article_content.replace("By Nathan Remacle.", "").strip()
            # Regex pour enlever la note sur les embeds, plus robuste
            article_content = re.sub(r'\*Note\s*:\s*(.*?)\s*\*', '', article_content, flags=re.IGNORECASE | re.DOTALL).strip()
            article_content = re.sub(r'Note\s*:\s*(.*?)\s*', '', article_content, flags=re.IGNORECASE | re.DOTALL).strip()


            # Insérer les embeds Spotify. L'IA devrait déjà les mentionner,
            # mais nous les ajoutons ici pour garantir leur présence et leur bon format.
            # On insère XCEED après le premier paragraphe ou introduction du titre.
            # On insère la playlist à la fin, avant la signature.
            
            # Placeholder pour insérer XCEED après l'intro ou le premier paragraphe
            # On compte le nombre de lignes pour trouver un bon endroit
            lines = article_content.split('\n')
            insert_point_xceed = min(len(lines), 3) # Après le 3ème paragraphe max

            # Insérer XCEED si le contenu est assez long
            if len(lines) > 5: # Si l'article a au moins quelques paragraphes
                # Vérifier si l'embed XCEED n'est pas déjà présent pour éviter les doublons
                if XCEED_SPOTIFY_EMBED not in article_content:
                    lines.insert(insert_point_xceed, "\n" + XCEED_SPOTIFY_EMBED + "\n")
                    article_content = "\n".join(lines)
                    print("DEBUG: Spotify embed for XCEED inserted.")

            # Insérer la playlist à la fin du contenu
            # Vérifier si l'embed de la playlist n'est pas déjà présent
            if PLAYLIST_SPOTIFY_EMBED not in article_content:
                article_content += "\n\n**Dive into the best of Hardstyle:**\n" + PLAYLIST_SPOTIFY_EMBED + "\n"
                print("DEBUG: Spotify playlist embed inserted.")

            return article_content
        else:
            raise ValueError(f"Mistral AI response does not contain the expected chat completions format. Full response: {data}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP ERROR generating article with Mistral AI : {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ DATA ERROR in Mistral AI response : {e}")
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
        # Fallback pour le titre, également en anglais
        extracted_title = "Hardstyle Article from " + datetime.now().strftime("%d %B %Y - %H:%M")

    # Suppression finale de toute signature ou note résiduelle
    content = content.replace("Par Nathan Remacle.", "").strip()
    content = content.replace("By Nathan Remacle.", "").strip()
    content = re.sub(r'\*Note\s*:\s*(.*?)\s*\*', '', content, flags=re.IGNORECASE | re.DOTALL).strip()
    content = re.sub(r'Note\s*:\s*(.*?)\s*', '', content, flags=re.IGNORECASE | re.DOTALL).strip()


    selected_cover_url = get_daily_cover_image_url() # Utilisation de l'image spécifique daily.png

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
                {"name": "Music", "slug": "music"},
                {"name": "Electronic Music", "slug": "electronic-music"}
            ],
        }
    }
    
    if selected_cover_url:
        variables["input"]["coverImageOptions"] = {
            "coverImageURL": selected_cover_url,
            "isCoverAttributionHidden": True
        }
        print(f"DEBUG: Hashnode cover image added to variables: {selected_cover_url}")
    else:
        print("DEBUG: No cover image added (no URL configured or list empty).")


    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {HASHNODE_API_KEY}"
    }

    print(f"\n✍️ Attempting to publish article '{extracted_title}' to Hashnode...")
    print(f"DEBUG: JSON Payload sent to Hashnode (without full content): {json.dumps(variables, indent=2)}")
    print(f"DEBUG: Start of Markdown content sent: {content[:200]}...")

    try:
        resp = requests.post(HASHNODE_API_URL, json={"query": mutation, "variables": variables}, headers=headers)
        
        print("Publish status:", resp.status_code)
        print("Publish response:", resp.text)
        
        response_data = resp.json()

        if 'errors' in response_data and response_data['errors']:
            print(f"❌ GraphQL ERROR from Hashnode when publishing article : {response_data['errors']}")
            sys.exit(1)

        post_url = None
        if 'data' in response_data and \
           'publishPost' in response_data['data'] and \
           'post' in response_data['data']['publishPost'] and \
           'url' in response_data['data']['publishPost']['post']:
            post_url = response_data['data']['publishPost']['post']['url']
            print(f"✅ Article published successfully : {extracted_title} at URL : {post_url}")
        else:
            print(f"✅ Article published successfully (URL not retrieved) : {extracted_title}")

    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP ERROR publishing article to Hashnode : {e}")
        print(f"Hashnode response on error : {resp.text if 'resp' in locals() else 'No response.'}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred during publication : {e}")
        sys.exit(1)

# --- Main Execution ---
if __name__ == "__main__":
    # Add re module import
    import re
    print("Starting daily Hardstyle bot.")
    try:
        article = generate_daily_hardstyle_article()
        publish_article(article)
        print("\n🎉 Daily Hardstyle bot successfully completed!")
    except Exception as e:
        print(f"\nFATAL ERROR: A critical error occurred : {e}")
        sys.exit(1)

