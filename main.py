from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import pyotp
from itsdangerous import Signer, BadSignature
import json

app = FastAPI()

# --- Security and Data ---
SECRET_KEY = "EEE6EILOQJQG4YSTVYIO7H2RGO2I3DNQ" # The key from setup_2fa.py
SESSION_SECRET = pyotp.random_base32() # A new secret for signing cookies
signer = Signer(SESSION_SECRET)
totp = pyotp.TOTP(SECRET_KEY)

# --- NEW: Robust Database File Handling ---
DATABASE_FILE = "database.json"

def load_database():
    """Loads the file list from database.json on startup."""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            try:
                # Handle cases where the file might be empty
                content = f.read()
                if not content:
                    return []
                return json.loads(content)
            except json.JSONDecodeError:
                # If file is corrupted, start with an empty list
                return []
    return []

def save_database():
    """Saves the current file list to database.json."""
    try:
        with open(DATABASE_FILE, "w") as f:
            json.dump(FILES_DATABASE, f, indent=4)
        # Add a confirmation print to the terminal
        print(f"Database successfully saved to {DATABASE_FILE}")
    except Exception as e:
        # Print any error that occurs during saving
        print(f"!!! CRITICAL ERROR: Could not save database. Reason: {e}")

# Load the database when the server starts
FILES_DATABASE = load_database()
print(f"Loaded {len(FILES_DATABASE)} files from database.")
# --- END NEW ---

# --- Path to your frontend folder ---
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# --- Authentication Dependency ---
async def get_current_user(request: Request):
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        signer.unsign(session_cookie.encode('utf-8'))
    except BadSignature:
        raise HTTPException(status_code=401, detail="Invalid session")
    return True

# --- API Endpoints ---

@app.post("/api/login")
async def login(request: Request, response: Response):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    otp = data.get("otp")

    is_password_correct = (email == "myadmin@bgs.com" and password == "BgsDrive@2025")
    is_otp_valid = totp.verify(otp)

    if is_password_correct and is_otp_valid:
        session_data = "user_is_logged_in".encode('utf-8')
        signed_session = signer.sign(session_data).decode('utf-8')
        response.set_cookie(key="session", value=signed_session, httponly=True)
        return {"success": True, "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials or OTP")

@app.get("/api/files")
def get_files():
    return JSONResponse(content=FILES_DATABASE)

@app.post("/api/files", dependencies=[Depends(get_current_user)])
async def add_file(request: Request):
    new_file = await request.json()
    FILES_DATABASE.append(new_file)
    save_database()  # Instantly saves the data to the file
    return JSONResponse({"success": True, "message": "File added successfully"})

# --- Page Serving ---

@app.get("/")
def get_login_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "static", "index.html"))

@app.get("/admin", dependencies=[Depends(get_current_user)])
def get_admin_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "static", "admin.html"))

@app.get("/client")
def get_client_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "static", "client.html"))