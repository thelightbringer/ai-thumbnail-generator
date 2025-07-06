import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class GroqAPI:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
    def get_current_date_formatted(self):
        """Get current date in format like '6th July, 2025'"""
        now = datetime.now()
        day = now.day
        month = now.strftime("%B")  # Full month name
        year = now.year
        
        # Add ordinal suffix to day
        def get_ordinal_suffix(day):
            if 10 <= day % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            return suffix
        
        return f"{day}{get_ordinal_suffix(day)} {month}, {year}"
        
    def generate_thumbnail_text(self, video_idea: str) -> dict:
        """
        Generate heading, subheading, label, and date for a thumbnail based on video idea.
        """
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        current_date = self.get_current_date_formatted()
            
        prompt = f"""
        Based on this YouTube video idea: "{video_idea}"
        
        Generate a JSON response with the following structure:
        {{
            "heading": "A catchy, attention-grabbing title (max 50 characters)",
            "subheading": "A compelling subtitle that supports the heading (max 70 characters). You can use hinglish for this.",
            "label": "A short label like 'MUST SEE', 'TRENDING', 'BEWARE', 'CAUTION' etc (max 20 characters). Get the context from heading and subheading.",
            "date": "{current_date}"
        }}
        
        Make the text engaging, clickable, and suitable for a YouTube thumbnail.
        Keep all text concise and impactful.
        IMPORTANT: Always use the exact date format provided: "{current_date}"
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extract JSON from the response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                
                # Ensure the date is always the current date
                parsed_data["date"] = current_date
                
                return parsed_data
            else:
                # Fallback if JSON parsing fails
                return {
                    "heading": "Amazing Video",
                    "subheading": "You won't believe what happens next",
                    "label": "NEW",
                    "date": current_date
                }
                
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            # Return fallback data with current date
            return {
                "heading": "Amazing Video",
                "subheading": "You won't believe what happens next",
                "label": "NEW",
                "date": current_date
            }
