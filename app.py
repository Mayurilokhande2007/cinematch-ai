import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    
    # Use your Gmail address here
    sender_email = "lokhandemayuri811@gmail.com"
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not app_password:
        raise HTTPException(status_code=500, detail="Server email not configured.")
        
    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset Request - CinemaMatch AI"
    message["From"] = f"CinemaMatch AI <{sender_email}>"
    message["To"] = user_email
    
    html_content = f"""
        <p>Hello,</p>
        <p>You requested a password reset for your CinemaMatch AI account.</p>
        <p><a href="{reset_link}" style="padding: 10px 15px; background: #0084ff; color: #fff; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p>If you did not request this, please ignore this email.</p>
    """
    message.attach(MIMEText(html_content, "html"))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, user_email, message.as_string())
    except Exception as e:
        print(f"SMTP error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email via Gmail SMTP.")
        
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
