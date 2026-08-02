from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import json
import smtplib
from email.message import EmailMessage

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
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(USERS_DB, f, indent=4)

USERS_DB = load_users()

MOVIES_DB = {
    "Inception": {"genre": "Sci-Fi", "year": 2010, "lang": "English", "rating": 8.8, "runtime": "2h 28m", "director": "Christopher Nolan", "cast": "Leonardo DiCaprio", "desc": "A thief who steals corporate secrets through the use of dream-sharing technology.", "poster": "https://image.tmdb.org/t/p/w500/8Z8dptEIwZVIKCwD1DqOawR500m.jpg", "trailer": "https://www.youtube.com/watch?v=YoHD9XEInc0", "mood": "Excited", "reason": "Because you enjoy mind-bending Sci-Fi."},
    "Interstellar": {"genre": "Sci-Fi", "year": 2014, "lang": "English", "rating": 8.6, "runtime": "2h 49m", "director": "Christopher Nolan", "cast": "Matthew McConaughey", "desc": "Explorers travel through a wormhole in space to ensure humanity's survival.", "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "trailer": "https://www.youtube.com/watch?v=zSWdZVtXT7E", "mood": "Sad", "reason": "Because you like emotional space epics."},
    "The Matrix": {"genre": "Sci-Fi", "year": 1999, "lang": "English", "rating": 8.7, "runtime": "2h 16m", "director": "The Wachowskis", "cast": "Keanu Reeves", "desc": "A computer hacker learns about the true nature of his reality.", "poster": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", "trailer": "https://www.youtube.com/watch?v=vKQi3bBA1y8", "mood": "Excited", "reason": "A cyberpunk classic based on your history."},
    "The Dark Knight": {"genre": "Action", "year": 2008, "lang": "English", "rating": 9.0, "runtime": "2h 32m", "director": "Christopher Nolan", "cast": "Christian Bale, Heath Ledger", "desc": "Batman must accept one of the greatest psychological tests of his ability to fight injustice.", "poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "trailer": "https://www.youtube.com/watch?v=EXeTwQWrcwY", "mood": "Excited", "reason": "Top-rated action masterpiece."},
    "Spider-Man: No Way Home": {"genre": "Action", "year": 2021, "lang": "English", "rating": 8.2, "runtime": "2h 28m", "director": "Jon Watts", "cast": "Tom Holland, Zendaya", "desc": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help.", "poster": "https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1R80vO0t9XQdG9.jpg", "trailer": "https://www.youtube.com/watch?v=JfVOs4VSpmA", "mood": "Happy", "reason": "Because you follow the Marvel Cinematic Universe."},
    "Superbad": {"genre": "Comedy", "year": 2007, "lang": "English", "rating": 7.6, "runtime": "1h 53m", "director": "Greg Mottola", "cast": "Jonah Hill, Michael Cera", "desc": "Two co-dependent high school seniors are forced to deal with separation anxiety.", "poster": "https://image.tmdb.org/t/p/w500/ek8e8txUyUwd2BNqj6lFEerJfbq.jpg", "trailer": "https://www.youtube.com/watch?v=4eaZ_48ZYIQ", "mood": "Happy", "reason": "A great laugh based on your comedy ratings."},
    "3 Idiots": {"genre": "Comedy", "year": 2009, "lang": "Hindi", "rating": 8.4, "runtime": "2h 50m", "director": "Rajkumar Hirani", "cast": "Aamir Khan, R. Madhavan", "desc": "Two friends are searching for their long lost companion.", "poster": "https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscw79zH021.jpg", "trailer": "https://www.youtube.com/watch?v=K0eDlFX9GMc", "mood": "Happy", "reason": "Highly rated feel-good Bollywood hit."},
    "PK": {"genre": "Comedy", "year": 2014, "lang": "Hindi", "rating": 8.1, "runtime": "2h 33m", "director": "Rajkumar Hirani", "cast": "Aamir Khan", "desc": "An alien on Earth loses the only device he can use to communicate with his spaceship.", "poster": "https://image.tmdb.org/t/p/w500/80HQLvHGK2tN53K5k5L0iV66eio.jpg", "trailer": "https://www.youtube.com/watch?v=SOXWc32k4zA", "mood": "Happy", "reason": "Since you loved 3 Idiots."},
    "The Notebook": {"genre": "Romance", "year": 2004, "lang": "English", "rating": 7.8, "runtime": "2h 3m", "director": "Nick Cassavetes", "cast": "Ryan Gosling", "desc": "A poor yet passionate young man falls in love with a rich young woman.", "poster": "https://image.tmdb.org/t/p/w500/rNzQyW4f8B8cQeg7Dgj3n6eT5k9.jpg", "trailer": "https://www.youtube.com/watch?v=FC6biTjEyZw", "mood": "Romantic", "reason": "A classic romance for a cozy evening."},
    "Dangal": {"genre": "Drama", "year": 2016, "lang": "Hindi", "rating": 8.3, "runtime": "2h 41m", "director": "Nitesh Tiwari", "cast": "Aamir Khan", "desc": "Former wrestler Mahavir Singh Phogat and his two wrestler daughters struggle towards glory.", "poster": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg", "trailer": "https://www.youtube.com/watch?v=x_7YlGv9u1g", "mood": "Excited", "reason": "Inspiring sports drama with huge global ratings."},
    "Parasite": {"genre": "Thriller", "year": 2019, "lang": "Korean", "rating": 8.5, "runtime": "2h 12m", "director": "Bong Joon Ho", "cast": "Song Kang-ho", "desc": "Greed and class discrimination threaten the relationship between two families.", "poster": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAY623XISSZAM.jpg", "trailer": "https://www.youtube.com/watch?v=5xV11mYntIE", "mood": "Excited", "reason": "Oscar-winning masterpiece."},
    "Train to Busan": {"genre": "Horror", "year": 2016, "lang": "Korean", "rating": 7.6, "runtime": "1h 58m", "director": "Yeon Sang-ho", "cast": "Gong Yoo", "desc": "Passengers struggle to survive on a train from Seoul to Busan during a zombie virus outbreak.", "poster": "https://image.tmdb.org/t/p/w500/1RzB27b1B3J382Xz81D29n1sZp6.jpg", "trailer": "https://www.youtube.com/watch?v=pyWuHv2-Abk", "mood": "Excited", "reason": "Because you watch high-stakes thrillers."},
    "The Invisible Guest": {"genre": "Thriller", "year": 2016, "lang": "Spanish", "rating": 8.0, "runtime": "1h 46m", "director": "Oriol Paulo", "cast": "Mario Casas", "desc": "A successful entrepreneur accused of murder has less than three hours to come up with an impregnable defense.", "poster": "https://image.tmdb.org/t/p/w500/v1GqV2Lw0Rz1p6IeBf7pM9mY3Qz.jpg", "trailer": "https://www.youtube.com/watch?v=epCg2RbyF80", "mood": "Excited", "reason": "A brilliant Spanish mystery."},
    "Spirited Away": {"genre": "Animation", "year": 2001, "lang": "Japanese", "rating": 8.6, "runtime": "2h 5m", "director": "Hayao Miyazaki", "cast": "Rumi Hiiragi", "desc": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits.", "poster": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkQlCEcwZ.jpg", "trailer": "https://www.youtube.com/watch?v=ByXuk9QqQkk", "mood": "Relaxed", "reason": "A visually stunning, relaxing adventure."},
    "Your Name": {"genre": "Animation", "year": 2016, "lang": "Japanese", "rating": 8.4, "runtime": "1h 46m", "director": "Makoto Shinkai", "cast": "Ryunosuke Kamiki", "desc": "Two teenagers share a profound, magical connection upon discovering they are swapping bodies.", "poster": "https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg", "trailer": "https://www.youtube.com/watch?v=xU47nhruN-Q", "mood": "Romantic", "reason": "Because you love emotional, beautifully animated stories."}
}

@app.get("/api/movies")
def get_movies():
    return MOVIES_DB

@app.get("/reset-password")
def serve_reset_page():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    raise HTTPException(status_code=404, detail="Page not found")

@app.post("/api/signup")
def signup_user(payload: dict = Body(...)):
    username = payload.get("username", "").strip()
    email = payload.get("email", "").strip()
    phone = payload.get("phone", "").strip()
    password = payload.get("password", "").strip()

    if not username or not email or not phone or not password:
        raise HTTPException(status_code=400, detail="All fields are required.")
    
    if username in USERS_DB:
        raise HTTPException(status_code=400, detail="User already exists. Please login.")

    USERS_DB[username] = {"email": email, "phone": phone, "password": password}
    save_users()
    return {"message": "Account created successfully!", "username": username}

@app.post("/api/login")
def login_user(payload: dict = Body(...)):
    identifier = payload.get("identifier", "").strip()
    password = payload.get("password", "").strip()

    user = USERS_DB.get(identifier)
    if not user:
        for uname, udata in USERS_DB.items():
            if udata.get("phone") == identifier or udata.get("email") == identifier:
                user = udata
                identifier = uname
                break
    
    if not user or user["password"] != password:
        raise HTTPException(status_code=400, detail="Invalid credentials or account not found. Please sign up first.")
    
    return {"message": "Login successful", "username": identifier}

@app.post("/api/forgot")
def forgot_password(payload: dict = Body(...)):
    identifier = payload.get("identifier", "").strip()
    user_key = None
    target_email = None

    if identifier in USERS_DB:
        user_key = identifier
        target_email = USERS_DB[user_key].get("email")
    else:
        for uname, udata in USERS_DB.items():
            if udata.get("email") == identifier or udata.get("phone") == identifier:
                user_key = uname
                target_email = udata.get("email")
                break

    if not user_key or not target_email:
        raise HTTPException(status_code=404, detail="Email or phone number not registered.")

    reset_link = f"http://127.0.0.1:8000/reset-password?user={user_key}"

    # SMTP Configuration
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "lokhandemayuri811@gmail.com"     # Put your Gmail here
    SENDER_PASSWORD = "owaz bien latn yena"   # Put your Google App Password here

    msg = EmailMessage()
    msg.set_content(f"Hello,\n\nWe received a request to reset your password for CinemaMatch AI.\n\nClick the link below to set a new password:\n{reset_link}\n\nIf you did not request this, please ignore this email.")
    msg["Subject"] = "Password Reset Instructions - CinemaMatch AI"
    msg["From"] = SENDER_EMAIL
    msg["To"] = target_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"\n[SMTP ERROR]: {str(e)}\n[FALLBACK LINK]: {reset_link}\n")
        return {
            "message": f"Email service offline. Use direct reset link for testing.",
            "reset_link": reset_link
        }

    return {"message": f"Password reset instructions have been successfully sent to {target_email}!"}

@app.post("/api/reset-password")
def reset_password_action(payload: dict = Body(...)):
    identifier = payload.get("identifier", "").strip()
    new_password = payload.get("new_password", "").strip()

    if not identifier or not new_password:
        raise HTTPException(status_code=400, detail="Identifier and new password are required.")

    user_key = None
    if identifier in USERS_DB:
        user_key = identifier
    else:
        for uname, udata in USERS_DB.items():
            if udata.get("email") == identifier or udata.get("phone") == identifier:
                user_key = uname
                break

    if not user_key:
        raise HTTPException(status_code=404, detail="User account not found.")

    USERS_DB[user_key]["password"] = new_password
    save_users() # Permanently saves new password to users.json
    return {"message": "Password successfully updated! You can now login with your new password."}

@app.post("/api/chat")
def chat_assistant(payload: dict = Body(...)):
    prompt = payload.get("prompt", "").lower()
    if "sci-fi" in prompt or "interstellar" in prompt:
        reply = "I suggest **Inception** or **The Matrix**. They both explore complex sci-fi themes."
    elif "hindi" in prompt or "comedy" in prompt:
        reply = "For Bollywood comedy, I highly recommend **3 Idiots** and **PK**!"
    elif "sad" in prompt:
        reply = "If you want something emotional, try **The Notebook** or **Interstellar**."
    else:
        reply = "Based on your profile, I suggest checking out the 'Trending This Week' section on your dashboard!"
    return {"response": reply}