import os
import json
import requests
import random
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CinemaMatch AI API",
    description="Backend for CinemaMatch AI Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                data = json.loads(content)
                return data if isinstance(data, (dict, list)) else {}
        except Exception:
            return {}
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def find_user_key_or_obj(users, identifier):
    if not identifier:
        return None
    if isinstance(users, dict):
        if identifier in users:
            return identifier
        for k, v in users.items():
            if k == identifier or (isinstance(v, dict) and (v.get("email") == identifier or v.get("phone") == identifier or v.get("username") == identifier)):
                return k
    elif isinstance(users, list):
        for u in users:
            if u.get("username") == identifier or u.get("email") == identifier or u.get("phone") == identifier:
                return u
    return None

@app.get("/")
def serve_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "index.html not found"}

# ==========================================
# EXPANDED MOVIE DATABASE (24 Movies with Posters)
# ==========================================
movies_db = {
    "Interstellar": {"genre": "Sci-Fi", "mood": "Mind-Bending", "lang": "English", "rating": 8.6, "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "desc": "Explorers travel through a wormhole in space to ensure humanity's survival."},
    "Inception": {"genre": "Sci-Fi", "mood": "Mind-Bending", "lang": "English", "rating": 8.8, "poster": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg", "desc": "A thief steals corporate secrets through the use of dream-sharing technology."},
    "The Dark Knight": {"genre": "Action", "mood": "Adrenaline & Hype", "lang": "English", "rating": 9.0, "poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "desc": "Batman must accept one of the greatest psychological and physical tests of his ability."},
    "Avatar": {"genre": "Sci-Fi", "mood": "Adrenaline & Hype", "lang": "English", "rating": 7.9, "poster": "https://image.tmdb.org/t/p/w500/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg", "desc": "A paraplegic Marine dispatched to the moon Pandora becomes torn between two worlds."},
    "Avengers: Endgame": {"genre": "Action", "mood": "Adrenaline & Hype", "lang": "English", "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg", "desc": "The Avengers assemble once more in order to reverse Thanos' actions."},
    "Joker": {"genre": "Thriller", "mood": "Dark & Thrilling", "lang": "English", "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/udDclJoHjfpt8cx6g5t1260Z6yV.jpg", "desc": "In Gotham City, mentally troubled comedian Arthur Fleck is disregarded by society."},
    "Parasite": {"genre": "Thriller", "mood": "Dark & Thrilling", "lang": "Korean", "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg", "desc": "Greed and class discrimination threaten the relationship between two families."},
    "Spider-Man: Into the Spider-Verse": {"genre": "Kids", "mood": "Adrenaline & Hype", "lang": "English", "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg", "desc": "Teen Miles Morales becomes the Spider-Man of his universe."},
    "Dune": {"genre": "Sci-Fi", "mood": "Adrenaline & Hype", "lang": "English", "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg", "desc": "A noble family becomes embroiled in a war for control over the galaxy's most valuable asset."},
    "The Matrix": {"genre": "Sci-Fi", "mood": "Mind-Bending", "lang": "English", "rating": 8.7, "poster": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", "desc": "A computer hacker learns from mysterious rebels about the true nature of his reality."},
    "Gladiator": {"genre": "Action", "mood": "Adrenaline & Hype", "lang": "English", "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvq0.jpg", "desc": "A former Roman General sets out to exact vengeance against the corrupt emperor."},
    "Fight Club": {"genre": "Thriller", "mood": "Mind-Bending", "lang": "English", "rating": 8.8, "poster": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg", "desc": "An insomniac office worker and a soap maker form an underground fight club."},
    "Pulp Fiction": {"genre": "Thriller", "mood": "Dark & Thrilling", "lang": "English", "rating": 8.9, "poster": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPbOYKQruz5.jpg", "desc": "The lives of two mob hitmen, a boxer, and a gangster intertwine."},
    "Forrest Gump": {"genre": "Comedy", "mood": "Feel-Good", "lang": "English", "rating": 8.8, "poster": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "desc": "Historical events unfold from the perspective of an Alabama man."},
    "The Shawshank Redemption": {"genre": "Thriller", "mood": "Feel-Good", "lang": "English", "rating": 9.3, "poster": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dENvU.jpg", "desc": "Two imprisoned men bond over a number of years, finding solace and redemption."},
    "Titanic": {"genre": "Romance", "mood": "Feel-Good", "lang": "English", "rating": 7.9, "poster": "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg", "desc": "An aristocrat falls in love with a kind but poor artist aboard the R.M.S. Titanic."},
    "La La Land": {"genre": "Romance", "mood": "Feel-Good", "lang": "English", "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fblsO0P2aU.jpg", "desc": "A pianist and an actress fall in love while attempting to reconcile their aspirations."},
    "Coco": {"genre": "Kids", "mood": "Feel-Good", "lang": "English", "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWlz1.jpg", "desc": "Aspiring musician Miguel enters the Land of the Dead to find his family."},
    "Toy Story": {"genre": "Kids", "mood": "Feel-Good", "lang": "English", "rating": 8.3, "poster": "https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg", "desc": "A cowboy doll is profoundly threatened when a new spaceman figure supplants him."},
    "Spirited Away": {"genre": "Kids", "mood": "Mind-Bending", "lang": "Japanese", "rating": 8.6, "poster": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkCwNeDq.jpg", "desc": "A sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits."},
    "Mad Max: Fury Road": {"genre": "Action", "mood": "Adrenaline & Hype", "lang": "English", "rating": 8.1, "poster": "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg", "desc": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler."},
    "John Wick": {"genre": "Action", "mood": "Adrenaline & Hype", "lang": "English", "rating": 7.4, "poster": "https://image.tmdb.org/t/p/w500/ps1M43DqY5p9R5aEayT3p9wZcO.jpg", "desc": "An ex-hit-man comes out of retirement to track down the gangsters that killed his dog."},
    "3 Idiots": {"genre": "Comedy", "mood": "Feel-Good", "lang": "Hindi", "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscw79zJXAc.jpg", "desc": "Two friends search for their long lost companion and revisit their college days."},
    "Tumbbad": {"genre": "Horror", "mood": "Dark & Thrilling", "lang": "Hindi", "rating": 8.2, "poster": "https://image.tmdb.org/t/p/w500/t9bEAAHXYL4xPqE76vj1g5jWJc9.jpg", "desc": "A mythological story about a goddess who created the entire universe."}
}

@app.get("/api/movies")
def get_movies():
    return movies_db

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================
@app.post("/api/signup")
def signup(data: dict = Body(...)):
    users = load_users()
    username = data.get("username")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    if find_user_key_or_obj(users, username) or (email and find_user_key_or_obj(users, email)):
        raise HTTPException(status_code=400, detail="User already exists")
    
    if isinstance(users, dict):
        users[username] = {"password": password, "email": email, "phone": phone}
    elif isinstance(users, list):
        users.append({"username": username, "email": email, "phone": phone, "password": password})
    else:
        users = {username: {"password": password, "email": email, "phone": phone}}
        
    save_users(users)
    return {"message": "Signup successful"}

@app.post("/api/login")
def login(data: dict = Body(...)):
    users = load_users()
    identifier = data.get("identifier")
    password = data.get("password")
    
    user_key = find_user_key_or_obj(users, identifier)
    if not user_key:
        raise HTTPException(status_code=400, detail="Invalid credentials")
        
    stored_pass = users[user_key].get("password") if isinstance(users, dict) else user_key.get("password")
    if stored_pass != password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
        
    actual_username = user_key if isinstance(users, dict) else user_key.get("username", identifier)
    return {"message": "Login successful", "username": actual_username}

@app.post("/api/forgot")
def forgot_password(data: dict = Body(...)):
    identifier = data.get("identifier")
    users = load_users()
    
    user_key = find_user_key_or_obj(users, identifier)
    if not user_key:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_data = users[user_key] if isinstance(users, dict) else user_key
    user_email = user_data.get("email")
    target_username = user_data.get("username") or user_key
    
    if not user_email:
        raise HTTPException(status_code=400, detail="No email address associated with this account")
        
    reset_link = f"https://cinematch-ai-huli.onrender.com/?user={target_username}"
    
    script_url = os.environ.get("GOOGLE_SCRIPT_URL")
    if not script_url:
        raise HTTPException(status_code=500, detail="Google Script URL not configured on server.")
        
    payload = {
        "to": user_email,
        "subject": "Password Reset Request - CinemaMatch AI",
        "html": f'<p>Hello,</p><p>You requested a password reset for your CinemaMatch AI account.</p><br><p><a href="{reset_link}" style="padding: 10px 15px; background: #0084ff; color: #fff; text-decoration: none; border-radius: 5px;">Reset Password</a></p><br><p>If you did not request this, please ignore this email.</p>'
    }
    
    try:
        response = requests.post(script_url, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to send email via Google.")
    except Exception as e:
        print(f"Request error: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Google API.")
        
    return {
        "message": f"Password reset link has been successfully sent to {user_email}."
    }

@app.post("/api/reset-password")
def reset_password(data: dict = Body(...)):
    username = data.get("username")
    new_password = data.get("new_password")
    
    if not username or not new_password:
        raise HTTPException(status_code=400, detail="Username and new password required")
        
    users = load_users()
    user_key = find_user_key_or_obj(users, username)
    
    if not user_key:
        raise HTTPException(status_code=404, detail="User not found")
        
    if isinstance(users, dict):
        users[user_key]["password"] = new_password
    elif isinstance(users, list):
        for u in users:
            if u.get("username") == username or u.get("email") == username:
                u["password"] = new_password
                break
                
    save_users(users)
    return {"message": "Password updated successfully! You can now log in."}

# ==========================================
# AI ASSISTANT ENDPOINT
# ==========================================
@app.post("/api/chat")
def chat_with_ai(data: dict = Body(...)):
    prompt = data.get("prompt", "").lower()
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    recommended = []
    
    # NLP Keyword matching
    if "sci-fi" in prompt or "space" in prompt or "mind" in prompt or "future" in prompt:
        recommended.extend(["Interstellar", "Inception"])
    elif "action" in prompt or "hero" in prompt or "fight" in prompt or "marvel" in prompt:
        recommended.extend(["The Dark Knight", "Avengers: Endgame"])
    elif "comedy" in prompt or "laugh" in prompt or "funny" in prompt:
        recommended.extend(["3 Idiots", "Forrest Gump"])
    elif "horror" in prompt or "scary" in prompt or "ghost" in prompt:
        recommended.extend(["Tumbbad", "Parasite"])
    else:
        # If no keywords match, pick two random movies from the database
        all_movie_keys = list(movies_db.keys())
        recommended.extend(random.sample(all_movie_keys, 2))
    
    # Format the AI response beautifully with Markdown-style bolding
    movie_list_str = ", ".join([f"**{m}**" for m in recommended])
    response_msg = f"Based on your request, I highly recommend checking out {movie_list_str}. Would you like me to add them to your Watchlist?"
    
    return {"response": response_msg}
