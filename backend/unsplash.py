import os
import requests
from dotenv import load_dotenv

load_dotenv()

class UnsplashAPI:
    def __init__(self):
        self.access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.base_url = "https://api.unsplash.com"
        
    def search_images(self, query: str, count: int = 3) -> list:
        """
        Search for images on Unsplash based on the query.
        Returns a list of image URLs.
        """
        if not self.access_key:
            raise ValueError("UNSPLASH_ACCESS_KEY not found in environment variables")
            
        headers = {
            "Authorization": f"Client-ID {self.access_key}"
        }
        
        params = {
            "query": query,
            "per_page": count,
            "orientation": "landscape"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search/photos",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            images = []
            
            for photo in data.get("results", []):
                # Get the regular size image URL
                image_url = photo["urls"]["regular"]
                images.append(image_url)
                
            return images
            
        except Exception as e:
            print(f"Error fetching images from Unsplash: {e}")
            # Return fallback images
            return [
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=600&fit=crop"
            ]
