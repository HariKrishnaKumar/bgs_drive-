from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import pyotp
from itsdangerous import Signer, BadSignature

app = FastAPI()

# --- Security and Data ---
SECRET_KEY = "EEE6EILOQJQG4YSTVYIO7H2RGO2I3DNQ" # The key from setup_2fa.py
SESSION_SECRET = pyotp.random_base32() # A new secret just for cookies
signer = Signer(SESSION_SECRET)
totp = pyotp.TOTP(SECRET_KEY)

FILES_DATABASE = []

# --- Path to your frontend folder ---
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# --- Authentication Dependency ---
async def get_current_user(request: Request):
    """
    A dependency that checks for a valid session cookie.
    If the cookie is missing or invalid, it raises an error.
    """
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        raise HTTPException(status_code=401, detail="You are not authorized to access the portel ")
    try:
        # Verify the cookie's signature to ensure it hasn't been tampered with
        signer.unsign(session_cookie.encode('utf-8'))
    except BadSignature:
        raise HTTPException(status_code=401, detail="Invalid session")
    return True

# --- API Endpoints ---

@app.post("/api/login")
async def login(request: Request, response: Response):
    """Handles login and SETS a session cookie on success."""
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    otp = data.get("otp")

    is_password_correct = (email == "myadmin@bgs.com" and password == "BgsDrive@2025")
    is_otp_valid = totp.verify(otp)

    if is_password_correct and is_otp_valid:
        # Create and set a secure session cookie
        session_data = "user_is_logged_in".encode('utf-8')
        signed_session = signer.sign(session_data).decode('utf-8')
        response.set_cookie(key="session", value=signed_session, httponly=True)
        return {"success": True, "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials or OTP")

@app.get("/api/files")
def get_files():
    """Provides the file list (publicly accessible)."""
    return JSONResponse(content=FILES_DATABASE)

@app.post("/api/files", dependencies=[Depends(get_current_user)])
async def add_file(request: Request):
    """
    Adds a new file. This route is now PROTECTED.
    Only users with a valid session cookie can access this.
    """
    new_file = await request.json()
    FILES_DATABASE.append(new_file)
    return JSONResponse({"success": True, "message": "File added successfully"})

# --- Page Serving ---

@app.get("/")
def get_login_page():
    """Serves the main login page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "static", "index.html"))

@app.get("/admin", dependencies=[Depends(get_current_user)])
def get_admin_page():
    """
    Serves the admin page. This route is now PROTECTED.
    FastAPI will automatically return an error if the user is not logged in.
    """
    return FileResponse(os.path.join(FRONTEND_DIR, "static", "admin.html"))

@app.get("/client")
def get_client_page():
    """Serves the simplified client download page (publicly accessible)."""
    return FileResponse(os.path.join(FRONTEND_DIR, "static", "client.html"))