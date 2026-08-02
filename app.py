import os
import json
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app first
app = FastAPI(
    title="CinemaMatch AI API",
    description="Backend for CinemaMatch AI Platform",
    version="1.0.0"
)

# Enable CORS
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
                return json.load(f)
        except Exception:
            return {}
    return {}

# Serve index.html at the root URL
@app.get("/")
def serve_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "index.html not found"}

@app.post("/api/signup")
def signup(data: dict = Body(...)):
    users = load_users()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    if isinstance(users, dict):
        if username in users:
            raise HTTPException(status_code=400, detail="User already exists")
        users[username] = {"password": password}
    elif isinstance(users, list):
        for u in users:
            if u.get("username") == username:
                raise HTTPException(status_code=400, detail="User already exists")
        users.append({"username": username, "password": password})
        
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)
        
    return {"message": "Signup successful"}

@app.post("/api/login")
def login(data: dict = Body(...)):
    users = load_users()
    username = data.get("username")
    password = data.get("password")
    
    if isinstance(users, dict):
        if username not in users or users[username].get("password") != password:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    elif isinstance(users, list):
        valid = False
        for u in users:
            if u.get("username") == username and u.get("password") == password:
                valid = True
                break
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid credentials")
            
    return {"message": "Login successful", "username": username}

@app.post("/api/change-password")
def change_password(data: dict = Body(...)):
    username = data.get("username")
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    users = load_users()
    
    if isinstance(users, dict):
        if username not in users:
            raise HTTPException(status_code=400, detail="User not found")
        if users[username]["password"] != old_password:
            raise HTTPException(status_code=400, detail="Incorrect old password")
        users[username]["password"] = new_password
    elif isinstance(users, list):
        user_found = False
        for user in users:
            if user.get("username") == username:
                user_found = True
                if user.get("password") != old_password:
                    raise HTTPException(status_code=400, detail="Incorrect old password")
                user["password"] = new_password
                break
        if not user_found:
            raise HTTPException(status_code=400, detail="User not found")
            
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)
        
    return {"message": "Password updated successfully"}
