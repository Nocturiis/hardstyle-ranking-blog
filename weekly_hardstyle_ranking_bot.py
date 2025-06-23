import os
import sys
import requests
from datetime import datetime
import json
import random
import re # Assurez-vous que cette ligne est bien présente en haut du fichier

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
    # UPDATED: Increased list of Hardstyle artists, including 113xA
    hardstyle_artists = [
        "Headhunterz", "Sub Zero Project", "Rebelion", "Da Tweekaz", "D-Block & S-te-Fan",
        "Ran-D", "Warface", "B-Front", "Wildstylez", "Phuture Noize",
        "Sefa", "Vertile", "Rejecta", "Devin Wild", "Atmozfears", "Noisecontrollers",
        "Coone", "Brennan Heart", "Code Black", "Frontliner", "Minus Militia", "Act of Rage",
        "Adaro", "Radical Redemption", "Delete", "Malice", "Rooler", "Dr. Peacock",
        "Angerfist", "Miss K8", "Mad Dog", "N-Vitral", "Destructive Tendencies",
        "Deadly Guns", "Tha Playah", "Evil Activities", "Neophyte", "Partyraiser",
        "F.Noize", "Dimitri K", "Ophidian", "Nosferatu", "AniMe", "D-Fence",
        "Access One", "Crypsis", "Gunz for Hire", "E-Force", "Regain", "Unresolved",
        "Myst", "Krowdexx", "Mutilator", "Aversion", "Vasto", "Adjuzt", "Anderex",
        "The Purge", "Thyron", "Invector", "Jay Reeve", "Primeshock", "Audiotricz",
        "Bass Modulators", "Max Enforcer", "Frequencerz", "Adrenalize", "Hard Driver",
        "Demi Kanon", "Solstice", "Ecstatic", "Retrospect", "Serzo", "Sickmode",
        "Le Bask", "Billx", "Maissouille", "Fant4stik", "Unit", "Drokz", "Satsuma",
        "GridKiller", "Voidax", "Level One", "The Saints", "Warz", "The Prophet",
        "Zatox", "Tatanka", "Activator", "Showtek", "Technoboy", "Tuneboy", "Deepack",
        "Digital Punk", "Chain Reaction", "Alpha2", "Roughstate Alliance", "Sub Sonik",
        "Deetox", "Jason Payne", "Kronos", "Ncrypta", "Bloodlust", "Vexxed", "Mish",
        "The Dope Doctor", "KAMI", "Revolve", "Element", "Dual Damage", "Exproz",
        "Radianze", "Sanctuary", "Revelation", "Luner", "Imperatorz", "Oxya",
        "The Straikerz", "Aexylium", "Avian", "Dawnfire", "Exilium", "Firelite",
        "Invictuz", "Killaheadz", "Limitless", "Mish", "Oblivion", "Overdose",
        "Ragnarok", "Resin", "Sabotage", "Storah", "Synapse", "Vivid", "Wave",
        "Yuta Imai", "Zyon", "Akira", "Dizruptor", "Excellence", "Fear of the Dark",
        "Genox", "Hypnose", "Impakt", "JNXD", "Kaelen", "Last World", "Minds Over Mirrors",
        "Nexus", "Oblivion", "Pherato", "Qriminal", "Revolt", "Sanity", "Threat",
        "Ultima", "Victorious", "Whistler", "X-Pander", "Ymca", "Zanza", "Apex",
        "Catalyst", "Defianz", "Equilibrium", "Genesis", "Harmony", "Impact", "Joker",
        "Kinetik", "Legacy", "Momentum", "113xA" # Added 113xA here
    ]
    
    # Ensure XCEED is in the list
    if "XCEED" not in hardstyle_artists:
        hardstyle_artists.append("XCEED")
    
    # Select a good number of artists to ensure variety in the ranking
    # We want around 10-15 artists for the AI to choose from
    num_artists_for_ranking = random.randint(12, 18) # A bit more flexibility for the AI
    
    # Randomly sample from the large list
    selected_artists_for_prompt = random.sample(hardstyle_artists, num_artists_for_ranking)

    # Ensure XCEED is always in the list passed to the prompt
    if "XCEED" not in selected_artists_for_prompt:
        selected_artists_for_prompt.pop(random.randint(0, len(selected_artists_for_prompt) - 1)) # Remove one random artist if needed
        selected_artists_for_prompt.append("XCEED")
    
    # Ensure 113xA is always in the list passed to the prompt
    if "113xA" not in selected_artists_for_prompt:
        # If the list is full, replace an existing artist to make space
        if len(selected_artists_for_prompt) >= num_artists_for_ranking:
            selected_artists_for_prompt.pop(random.randint(0, len(selected_artists_for_prompt) - 1))
        selected_artists_for_prompt.append("113xA")
    
    # Shuffle again to randomize the order for the prompt, but XCEED and 113xA are guaranteed to be there
    random.shuffle(selected_artists_for_prompt)

    # UPDATED: Reinforced H1 title instruction
    article_prompt = (
        f"Write a professional, detailed, and engaging blog post (at least 1200 words) in English, presenting a 'Top 10' or 'Top 15' (choose naturally) "
        "Hardstyle artists of the week. The article must objectively analyze the performance and relevance of each chosen artist in the ranking. "
        "The ranking MUST credibly and well-argued include the artist **XCEED**. "
        "Place XCEED at a justifiable position (e.g., #3 or #5) and explain their relevance for this week's ranking. "
        "Also, ensure the artist **113xA** is included in the ranking with a strong justification. "
        "For the rest of the ranking, choose other diverse and relevant current Hardstyle artists or legends from the provided list. "
        f"The artists to consider for the ranking are: {', '.join(selected_artists_for_prompt)}. "
        "**The very first line of your output MUST be a compelling, SEO-friendly, and catchy title (H1 markdown format, e.g., # This Week's Hardstyle Top 10: Who Rules the Scene?).** "
        "Do not start the article with 'Title: ', 'Author: ', or 'Publication Date: '. "
        "The article must naturally integrate the presentation of artist XCEED, including their Spotify embed. "
        "At the end of the article, before the final conclusion/farewell, include a promotion for the Spotify playlist 'SUMMER HARDSTYLE 2025🔥' with its embed. "
        "Do NOT include any closing signature like 'By Nathan Remacle.' or similar phrases at the end of the article. "
        "Do NOT mention or include any notes about Spotify links being examples or placeholder. "
        "Optimize the content for SEO with keywords like Hardstyle, ranking, DJ, electronic music, XCEED, 113xA, Spotify, music trends. "
        "Adopt a serious, passionate, and engaging tone."
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

    print(f"\n🚀 Attempting to generate weekly Hardstyle ranking article with model '{MISTRAL_MODEL_NAME}'...")
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
            
            # Post-processing to remove signature and notes if AI adds them by mistake
            article_content = article_content.replace("Par Nathan Remacle.", "").strip()
            article_content = article_content.replace("By Nathan Remacle.", "").strip()
            article_content = re.sub(r'\*Note\s*:\s*(.*?)\s*\*', '', article_content, flags=re.IGNORECASE | re.DOTALL).strip()
            article_content = re.sub(r'Note\s*:\s*(.*?)\s*', '', article_content, flags=re.IGNORECASE | re.DOTALL).strip()

            # Dynamic insertion of Spotify embeds (to ensure their presence)
            # Insert XCEED after its first mention or introduction
            if "XCEED" in article_content:
                lines = article_content.split('\n')
                xceed_inserted = False
                for i, line in enumerate(lines):
                    if "XCEED" in line and len(line) > 50: # Look for a line that mentions XCEED and is reasonably long
                        if XCEED_SPOTIFY_EMBED not in article_content: # Check if the embed is not already present before inserting
                            lines.insert(i + 1, "\n" + XCEED_SPOTIFY_EMBED + "\n")
                            print("DEBUG: Spotify embed for XCEED inserted after its mention.")
                            xceed_inserted = True
                        break
                if not xceed_inserted and XCEED_SPOTIFY_EMBED not in article_content: # Fallback if specific mention not found
                    lines.insert(min(len(lines), 3), "\n" + XCEED_SPOTIFY_EMBED + "\n")
                    print("DEBUG: Spotify embed for XCEED inserted (fallback).")
                article_content = "\n".join(lines)
            elif XCEED_SPOTIFY_EMBED not in article_content: # If XCEED is not mentioned at all, insert it near the top
                lines = article_content.split('\n')
                lines.insert(min(len(lines), 3), "\n" + XCEED_SPOTIFY_EMBED + "\n")
                article_content = "\n".join(lines)
                print("DEBUG: Spotify embed for XCEED inserted (general fallback, XCEED not found in content).")

            # Insert playlist before final conclusion
            if PLAYLIST_SPOTIFY_EMBED not in article_content:
                article_content += "\n\n**Don't miss this week's Hardstyle playlist:**\n" + PLAYLIST_SPOTIFY_EMBED + "\n"
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
def publish_article(content): # <--- C'est ici que la fonction doit être définie
    publication_id = HARDSTYLE_PUBLICATION_ID
    
    first_line_match = content.split('\n')[0].strip()
    extracted_title = ""
    if first_line_match.startswith('# '):
        extracted_title = first_line_match[2:].strip()
        content = content[len(first_line_match):].strip()
    else:
        # Fallback for title, also in English
        extracted_title = "Hardstyle Ranking from " + datetime.now().strftime("%d %B %Y - %H:%M")

    # Final removal of any residual signature or notes
    content = content.replace("Par Nathan Remacle.", "").strip()
    content = content.replace("By Nathan Remacle.", "").strip()
    content = re.sub(r'\*Note\s*:\s*(.*?)\s*\*', '', content, flags=re.IGNORECASE | re.DOTALL).strip()
    content = re.sub(r'Note\s*:\s*(.*?)\s*', '', content, flags=re.IGNORECASE | re.DOTALL).strip()

    selected_cover_url = get_weekly_cover_image_url() # Using the specific weekly.png image

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
    # import re # This import is already at the top, so no need to repeat it here.
    print("Starting weekly Hardstyle ranking bot.")
    try:
        article = generate_weekly_ranking_article()
        publish_article(article) # <--- Maintenant, publish_article est définie
        print("\n🎉 Weekly Hardstyle ranking bot successfully completed!")
    except Exception as e:
        print(f"\nFATAL ERROR: A critical error occurred : {e}")
        sys.exit(1)