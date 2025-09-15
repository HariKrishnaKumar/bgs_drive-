from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# --- File Data ---
# In a real application, you would get this from a database.
# For now, we'll define the files here on the server.
# This list should contain the files you want clients to see.
CLIENT_FILES = [
    {
        "name": "Project Plan Q4.docx",
        "url": "https://example.com/path/to/project-plan.docx", # Replace with actual URL
        "type": "document"
    },
    {
        "name": "Company Logos.zip",
        "url": "https://example.com/path/to/logos.zip", # Replace with actual URL
        "type": "other"
    },
    {
        "name": "Product Demo.mp4",
        "url": "https://example.com/path/to/demo.mp4", # Replace with actual URL
        "type": "video"
    }
]

# --- Path to your frontend folder ---
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

# --- Serve Static Files (CSS, JS, etc.) ---
# This allows HTML files to access other files in the 'static' directory
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")


# --- API Endpoint to Get File List ---
@app.get("/api/files")
def get_files():
    """Provides the list of files to the client page."""
    return JSONResponse(content=CLIENT_FILES)


# --- Page for Admins ---
@app.get("/")
def get_admin_page():
    """Serves the main admin interface."""
    # This path is now corrected to include "static"
    return FileResponse(os.path.join(FRONTEND_DIR, "static", "index.html"))


# --- Page for Clients ---
@app.get("/client")
def get_client_page():
    """Serves the new, simplified client download page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "static", "client.html"))