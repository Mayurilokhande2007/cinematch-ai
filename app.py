import os
import json
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

@app.get("/")
def serve_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "index.html not found"}

@app.get("/api/movies")
def get_movies():
    return {
        "Inception": {
            "poster": "https://image.tmdb.org/t/p/w500/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg",
            "desc": "A thief who steals corporate secrets through the use of dream-sharing technology."
        },
        "The Dark Knight": {
            "poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "desc": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham."
        },
        "Interstellar": {
            "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "desc": "Explorers travel through a wormhole in space to ensure humanity's survival."
        },
        "Avatar": {
            "poster": "https://image.tmdb.org/t/p/w500/kyeOwessWXUXSoHNECAb4r5hRRE.jpg",
            "desc": "A paraplegic marine dispatched to the moon Pandora on a unique mission."
        },
        "Avengers: Endgame": {
            "poster": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
            "desc": "After the devastating events of Infinity War, the universe is in ruins."
        }
    }

@app.post("/api/signup")
def signup(data: dict = Body(...)):
    users = load_users()
    username = data.get("username")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    if isinstance(users, dict):
        if username in users:
            raise HTTPException(status_code=400, detail="User already exists")
        users[username] = {"password": password, "email": email, "phone": phone}
    elif isinstance(users, list):
        for u in users:
            if u.get("username") == username:
                raise HTTPException(status_code=400, detail="User already exists")
        users.append({"username": username, "email": email, "phone": phone, "password": password})
        
    save_users(users)
    return {"message": "Signup successful"}

@app.post("/api/login")
def login(data: dict = Body(...)):
    users = load_users()
    identifier = data.get("identifier")
    password = data.get("password")
    
    if isinstance(users, dict):
        if identifier not in users or users[identifier].get("password") != password:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    elif isinstance(users, list):
        valid = False
        for u in users:
            if (u.get("username") == identifier or u.get("email") == identifier or u.get("phone") == identifier) and u.get("password") == password:
                valid = True
                break
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid credentials")
            
    return {"message": "Login successful", "username": identifier}

@app.post("/api/forgot")
def forgot_password(data: dict = Body(...)):
    identifier = data.get("identifier")
    users = load_users()
    
    found = False
    if isinstance(users, dict):
        if identifier in users:
            found = True
    elif isinstance(users, list):
        for u in users:
            if u.get("username") == identifier or u.get("email") == identifier or u.get("phone") == identifier:
                found = True
                break
                
    if not found:
        raise HTTPException(status_code=404, detail="Not Found")
        
    reset_link = f"https://cinematch-ai-huli.onrender.com/?user={identifier}"
    return {
        "message": "Password reset link generated successfully.",
        "reset_link": reset_link
    }

@app.post("/api/reset-password")
def reset_password(data: dict = Body(...)):
    identifier = data.get("identifier")
    new_password = data.get("new_password")
    
    users = load_users()
    found = False
    
    if isinstance(users, dict):
        if identifier in users:
            users[identifier]["password"] = new_password
            found = True
    elif isinstance(users, list):
        for u in users:
            if u.get("username") == identifier or u.get("email") == identifier or u.get("phone") == identifier:
                u["password"] = new_password
                found = True
                break
                
    if not found:
        raise HTTPException(status_code=404, detail="User not found")
        
    save_users(users)
    return {"message": "Password updated successfully"}

@app.post("/api/chat")
def chat(data: dict = Body(...)):
    prompt = data.get("prompt", "").lower()
    response = "That sounds like a great movie choice! I recommend checking out Inception or Interstellar for an incredible sci-fi experience."
    if "action" in prompt:
        response = "For high-octane action, The Dark Knight or Avengers: Endgame are top choices!"
    elif "sci-fi" in prompt:
        response = "Interstellar and Inception are mind-bending masterpieces you will love."
    return {"response": response}
