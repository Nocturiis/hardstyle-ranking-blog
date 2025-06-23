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
        "l'évolution du Hardstyle", "les sous-genres du Hardstyle (Raw, Euphoric, Xtra Raw)",
        "l'impact du Hardstyle sur la scène électronique", "les festivals Hardstyle incontournables",
        "les techniques de production Hardstyle", "l'histoire d'un label Hardstyle emblématique",
        "la culture des raves Hardstyle", "les DJ sets Hardstyle légendaires",
        "le futur du Hardstyle", "l'innovation sonore dans le Hardstyle",
        "l'énergie et l'émotion du Hardstyle", "les mélodies iconiques du Hardstyle"
    ]
    chosen_topic = random.choice(hardstyle_topics)

    # Prompt pour Mistral AI
    article_prompt = (
        f"Rédige un article de blog professionnel et détaillé d'au moins 1200 mots en français sur le thème de {chosen_topic} dans le Hardstyle. "
        "L'article doit captiver les fans de musique électronique et de Hardstyle. "
        "Intègre naturellement des mentions de l'artiste **XCEED** et de la **playlist Spotify 'SUMMER HARDSTYLE 2025🔥'**. "
        "Tu peux placer des extraits d'embeds Spotify de XCEED ou de la playlist à des endroits pertinents. "
        "Le titre de l'article doit être inclus au début du contenu (premier niveau de titre H1, ex: # Titre de l'Article). "
        "Le titre doit être percutant et accrocheur pour le public Hardstyle. "
        "Ne commence pas l'article par 'Titre : ' ou 'Auteur : ' ou 'Date de publication : '. "
        "L'article doit se terminer par la signature 'Par Nathan Remacle.'. "
        "Optimise le contenu pour le SEO en incluant des mots-clés pertinents (Hardstyle, musique électronique, DJ, festivals, XCEED, Spotify). "
        "Adopte un ton passionné et engageant, évitant les formulations trop 'IA'."
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

    print(f"\n🚀 Tentative de génération d'article Hardstyle quotidien sur '{chosen_topic}' avec le modèle '{MISTRAL_MODEL_NAME}'...")
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
                lines.insert(insert_point_xceed, "\n" + XCEED_SPOTIFY_EMBED + "\n")
                article_content = "\n".join(lines)
                print("DEBUG: Embed Spotify de XCEED inséré.")

            # Insérer la playlist avant la signature finale
            # On doit trouver la signature et insérer avant
            if "Par Nathan Remacle." in article_content:
                article_content = article_content.replace("Par Nathan Remacle.", 
                                                          "\n**Écoutez le meilleur du Hardstyle :**\n" + PLAYLIST_SPOTIFY_EMBED + "\n\nPar Nathan Remacle.")
                print("DEBUG: Embed Spotify de la playlist inséré.")
            else:
                # Fallback si la signature est manquante (rare)
                article_content += "\n**Écoutez le meilleur du Hardstyle :**\n" + PLAYLIST_SPOTIFY_EMBED
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
        extracted_title = "Article Hardstyle du " + datetime.now().strftime("%d %B %Y - %H:%M")

    # Assurez-vous que la signature est présente (si elle n'a pas été incluse par l'IA ou manipulée)
    if "Par Nathan Remacle." not in content:
        content += "\n\nPar Nathan Remacle."

    selected_cover_url = get_daily_cover_image_url() # Utilisation d'une image aléatoire du dossier covers/

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
                {"name": "Electronic Music", "slug": "electronic-music"} # Correction pour un slug plus standard
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
    print("Démarrage du bot Hardstyle quotidien.")
    try:
        article = generate_daily_hardstyle_article()
        publish_article(article)
        print("\n🎉 Bot Hardstyle quotidien terminé avec succès !")
    except Exception as e:
        print(f"\nFATAL ERROR: Une erreur critique est survenue : {e}")
        sys.exit(1)