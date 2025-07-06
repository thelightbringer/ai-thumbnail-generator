import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.requests import Request
from pydantic import BaseModel
from typing import List

from dotenv import load_dotenv
from groq import GroqAPI
from unsplash import UnsplashAPI
from thumbnail import ThumbnailGenerator

# Load .env
load_dotenv()

# --- App Initialization ---
app = FastAPI(title="AI Thumbnail Generator", version="1.0.0")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "https://thumbnail-gen-w7sb.onrender.com",  # Old frontend (optional)
        "https://nseprofitmaker.onrender.com"  # Current deployed URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Clients ---
groq_api = GroqAPI()
unsplash_api = UnsplashAPI()
thumbnail_generator = ThumbnailGenerator()

# --- Pydantic Models ---
class VideoIdeaRequest(BaseModel):
    video_idea: str

class RegenerateRequest(BaseModel):
    video_idea: str
    text_data: dict
    selected_index: int

class UpdateThumbnailsRequest(BaseModel):
    image_urls: List[str]
    text_data: dict

class ThumbnailResponse(BaseModel):
    thumbnails: List[str]
    text_data: dict
    original_urls: List[str]

# --- Routes ---
@app.get("/api")
def read_root():
    return {"message": "AI Thumbnail Generator API is running!"}

@app.post("/api/generate-thumbnails", response_model=ThumbnailResponse)
async def generate_thumbnails(request: VideoIdeaRequest):
    try:
        text_data = groq_api.generate_thumbnail_text(request.video_idea)
        image_urls = unsplash_api.search_images(request.video_idea, count=3)
        thumbnails = [thumbnail_generator.create_thumbnail(url, text_data) for url in image_urls]
        return ThumbnailResponse(thumbnails=thumbnails, text_data=text_data, original_urls=image_urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating thumbnails: {str(e)}")

@app.post("/api/regenerate-images", response_model=ThumbnailResponse)
async def regenerate_images(request: RegenerateRequest):
    try:
        image_urls = unsplash_api.search_images(request.video_idea, count=3)
        thumbnails = [thumbnail_generator.create_thumbnail(url, request.text_data) for url in image_urls]
        return ThumbnailResponse(thumbnails=thumbnails, text_data=request.text_data, original_urls=image_urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating images: {str(e)}")

@app.post("/api/regenerate-all", response_model=ThumbnailResponse)
async def regenerate_all(request: VideoIdeaRequest):
    try:
        text_data = groq_api.generate_thumbnail_text(request.video_idea)
        image_urls = unsplash_api.search_images(request.video_idea, count=3)
        thumbnails = [thumbnail_generator.create_thumbnail(url, text_data) for url in image_urls]
        return ThumbnailResponse(thumbnails=thumbnails, text_data=text_data, original_urls=image_urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating all: {str(e)}")

@app.post("/api/update-thumbnails", response_model=ThumbnailResponse)
async def update_thumbnails(request: UpdateThumbnailsRequest):
    try:
        thumbnails = [thumbnail_generator.create_thumbnail(url, request.text_data) for url in request.image_urls]
        return ThumbnailResponse(thumbnails=thumbnails, text_data=request.text_data, original_urls=request.image_urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating thumbnails: {str(e)}")

# --- Serve Frontend (React) ---
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc):
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Not Found"}

# --- Uvicorn CLI entrypoint (optional for local) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
