from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from groq import GroqAPI
from unsplash import UnsplashAPI
from thumbnail import ThumbnailGenerator

load_dotenv()

app = FastAPI(title="AI Thumbnail Generator", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API clients
groq_api = GroqAPI()
unsplash_api = UnsplashAPI()
thumbnail_generator = ThumbnailGenerator()

class VideoIdeaRequest(BaseModel):
    video_idea: str

class ThumbnailResponse(BaseModel):
    thumbnails: List[str]
    text_data: dict
    original_urls: List[str]

class RegenerateRequest(BaseModel):
    video_idea: str
    text_data: dict
    selected_index: int

class UpdateThumbnailsRequest(BaseModel):
    image_urls: List[str]
    text_data: dict

@app.get("/")
def read_root():
    return {"message": "AI Thumbnail Generator API is running!"}

@app.post("/api/generate-thumbnails", response_model=ThumbnailResponse)
async def generate_thumbnails(request: VideoIdeaRequest):
    """
    Generate 3 thumbnails based on the video idea.
    """
    try:
        # Generate text metadata using Groq
        text_data = groq_api.generate_thumbnail_text(request.video_idea)
        
        # Search for relevant images using Unsplash
        image_urls = unsplash_api.search_images(request.video_idea, count=3)
        
        # Generate thumbnails with text overlay
        thumbnails = []
        for image_url in image_urls:
            thumbnail = thumbnail_generator.create_thumbnail(image_url, text_data)
            thumbnails.append(thumbnail)
        
        return ThumbnailResponse(
            thumbnails=thumbnails,
            text_data=text_data,
            original_urls=image_urls
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating thumbnails: {str(e)}")

@app.post("/api/regenerate-images", response_model=ThumbnailResponse)
async def regenerate_images(request: RegenerateRequest):
    """
    Regenerate images for the same text data (new backgrounds).
    """
    try:
        # Search for new images using Unsplash
        image_urls = unsplash_api.search_images(request.video_idea, count=3)
        
        # Generate new thumbnails with existing text data
        thumbnails = []
        for image_url in image_urls:
            thumbnail = thumbnail_generator.create_thumbnail(image_url, request.text_data)
            thumbnails.append(thumbnail)
        
        return ThumbnailResponse(
            thumbnails=thumbnails,
            text_data=request.text_data,
            original_urls=image_urls
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating images: {str(e)}")

@app.post("/api/regenerate-all", response_model=ThumbnailResponse)
async def regenerate_all(request: VideoIdeaRequest):
    """
    Regenerate both text and images completely.
    """
    try:
        # Generate new text metadata
        text_data = groq_api.generate_thumbnail_text(request.video_idea)
        
        # Search for new images
        image_urls = unsplash_api.search_images(request.video_idea, count=3)
        
        # Generate new thumbnails
        thumbnails = []
        for image_url in image_urls:
            thumbnail = thumbnail_generator.create_thumbnail(image_url, text_data)
            thumbnails.append(thumbnail)
        
        return ThumbnailResponse(
            thumbnails=thumbnails,
            text_data=text_data,
            original_urls=image_urls
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating all: {str(e)}")

@app.post("/api/update-thumbnails", response_model=ThumbnailResponse)
async def update_thumbnails(request: UpdateThumbnailsRequest):
    """
    Overlay user-edited text on the provided images.
    """
    try:
        thumbnails = []
        for image_url in request.image_urls:
            thumbnail = thumbnail_generator.create_thumbnail(image_url, request.text_data)
            thumbnails.append(thumbnail)
        return ThumbnailResponse(
            thumbnails=thumbnails,
            text_data=request.text_data,
            original_urls=request.image_urls
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating thumbnails: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
