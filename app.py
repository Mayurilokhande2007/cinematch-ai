import os
import json
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    """Helper to find user in dict or list by username, email, or phone"""
    if not identifier:
        return None
    if isinstance(users, dict):
        if identifier in users:
            return identifier
        for k, v in users.items():
            if k == identifier or (isinstance(v, dict) and (v.get("email") == identifier or v.get("phone") == identifier)):
                return k
    elif isinstance(users, list):
        for u in users:
            if u.get("username") == identifier or u.get("email") == identifier or u.get("phone") == identifier:
                return u
    return None
    # Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "lokhandemayuri811@gmail.com"       # Replace with your Gmail address
SENDER_PASSWORD = "owaz bien latn yena"     # Replace with your 16-character Gmail App Password

def send_email_via_smtp(to_email, reset_link):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = "Password Reset Request - CinemaMatch AI"
        
        body = f"Hello,\n\nYou requested a password reset for your CinemaMatch AI account.\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you did not request this, please ignore this email."
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

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
    
    # Send the email directly to the user's inbox
    email_sent = send_email_via_smtp(user_email, reset_link)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send email. Check SMTP server configuration.")
        
    return {
        "message": f"Password reset link has been successfully sent to {user_email}."
    }

@app.post("/api/reset-password")
def reset_password(data: dict = Body(...)):
    identifier = data.get("identifier")
    new_password = data.get("new_password")
    
    users = load_users()
    user_key = find_user_key_or_obj(users, identifier)
    if not user_key:
        raise HTTPException(status_code=404, detail="User not found")
        
    if isinstance(users, dict):
        users[user_key]["password"] = new_password
    else:
        user_key["password"] = new_password
        
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
