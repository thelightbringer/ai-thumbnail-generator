import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os

class ThumbnailGenerator:
    def __init__(self):
        # Font sizes (will be scaled based on image width)
        self.heading_size = 90
        self.subheading_size = 55
        self.label_size = 32
        self.date_size = 35
        
        # Colors
        self.heading_color = (255, 255, 255)  # White
        self.subheading_color = (255, 255, 255)  # White
        self.label_color = (255, 255, 255)  # White
        self.date_color = (255, 255, 255)  # White (changed to white for better contrast)
        
        # Background colors for labels and dates
        self.label_bg = (220, 38, 38)  # Red
        self.date_bg = (0, 0, 0, 180)  # Semi-transparent black
        
        # Shadow/Stroke colors
        self.shadow_color = (0, 0, 0)  # Black
        
        # Overlay opacity
        self.overlay_opacity = 0.4  # 40% opacity
        
        # Logo settings
        self.logo_path = "../frontend/src/assets/Logo.png"
        self.logo_size = (120, 120)  # Logo size in pixels
        
    def load_logo(self):
        """Load and resize the logo image."""
        try:
            if os.path.exists(self.logo_path):
                logo = Image.open(self.logo_path).convert('RGBA')
                logo = logo.resize(self.logo_size, Image.Resampling.LANCZOS)
                return logo
            else:
                print(f"Logo not found at {self.logo_path}")
                return None
        except Exception as e:
            print(f"Error loading logo: {e}")
            return None
        
    def download_image(self, url: str) -> Image.Image:
        """Download image from URL and return PIL Image object."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert('RGB')
            return image
        except Exception as e:
            print(f"Error downloading image: {e}")
            return Image.new('RGB', (1280, 720), (50, 50, 50))
    
    def get_font(self, size, bold=False, italic=False):
        """Get font with fallback options."""
        try:
            # Try to use Montserrat first, then Arial, then default
            if bold:
                return ImageFont.truetype("Montserrat-Bold.ttf", size)
            elif italic:
                return ImageFont.truetype("Montserrat-Italic.ttf", size)
            else:
                return ImageFont.truetype("Montserrat-Regular.ttf", size)
        except:
            try:
                if bold:
                    return ImageFont.truetype("arialbd.ttf", size)
                elif italic:
                    return ImageFont.truetype("ariali.ttf", size)
                else:
                    return ImageFont.truetype("arial.ttf", size)
            except:
                try:
                    # Try system fonts
                    if bold:
                        return ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", size)
                    elif italic:
                        return ImageFont.truetype("/System/Library/Fonts/Arial Italic.ttf", size)
                    else:
                        return ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
                except:
                    return ImageFont.load_default()
    
    def calculate_font_size(self, base_size, image_width):
        """Scale font size based on image width."""
        scale_factor = image_width / 1280.0
        return int(base_size * scale_factor)
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, force it
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def draw_text_with_stroke(self, draw, xy, text, font, text_color, stroke_color, stroke_width=3):
        """Draw text with stroke for better readability."""
        x, y = xy
        
        # Draw stroke (outline)
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx*dx + dy*dy <= stroke_width*stroke_width:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def draw_rounded_rectangle(self, draw, bbox, radius, fill):
        """Draw a rounded rectangle."""
        x0, y0, x1, y1 = bbox
        # Draw the main rectangle
        draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
        draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
        
        # Draw the corners
        draw.ellipse([x0, y0, x0 + 2*radius, y0 + 2*radius], fill=fill)
        draw.ellipse([x1 - 2*radius, y0, x1, y0 + 2*radius], fill=fill)
        draw.ellipse([x0, y1 - 2*radius, x0 + 2*radius, y1], fill=fill)
        draw.ellipse([x1 - 2*radius, y1 - 2*radius, x1, y1], fill=fill)
    
    def generate_thumbnail_template(self, image_url: str, metadata: dict) -> str:
        """
        Generate thumbnail with the specified design pattern.
        Returns base64 encoded image.
        """
        # Download and prepare image
        image = self.download_image(image_url)
        image = image.resize((1280, 720), Image.Resampling.LANCZOS)
        
        # Create overlay for text contrast
        overlay = Image.new('RGBA', image.size, (0, 0, 0, int(255 * self.overlay_opacity)))
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        # Create drawing object
        draw = ImageDraw.Draw(image)
        
        # Extract metadata
        heading = metadata.get("heading", "").upper()  # Force uppercase
        subheading = metadata.get("subheading", "")
        label = metadata.get("label", "")
        date = metadata.get("date", "")
        
        # Calculate dynamic font sizes
        width, height = image.size
        heading_size = self.calculate_font_size(self.heading_size, width)
        subheading_size = self.calculate_font_size(self.subheading_size, width)
        label_size = self.calculate_font_size(self.label_size, width)
        date_size = self.calculate_font_size(self.date_size, width)
        
        # Get fonts
        heading_font = self.get_font(heading_size, bold=True)
        subheading_font = self.get_font(subheading_size, bold=False)
        label_font = self.get_font(label_size, bold=True)
        date_font = self.get_font(date_size, italic=True)
        
        # Calculate margins and spacing
        margin = int(width * 0.05)  # 5% margin
        top_margin = int(height * 0.08)  # 8% top margin
        bottom_margin = int(height * 0.05)  # 5% bottom margin
        
        # --- LOGO: Top-left corner ---
        logo = self.load_logo()
        if logo:
            # Position logo at top-left with some margin
            logo_x = margin
            logo_y = margin
            image.paste(logo, (logo_x, logo_y), logo)
        
        # --- HEADING: Top center, large, bold, all caps ---
        if heading:
            # Wrap heading if too long
            max_heading_width = width * 0.8  # 80% of image width
            heading_lines = self.wrap_text(heading, heading_font, max_heading_width)
            
            # Calculate total heading height
            total_heading_height = 0
            for line in heading_lines:
                bbox = draw.textbbox((0, 0), line, font=heading_font)
                total_heading_height += bbox[3] - bbox[1]
            
            # Position heading at top center
            heading_y = top_margin
            for line in heading_lines:
                bbox = draw.textbbox((0, 0), line, font=heading_font)
                line_width = bbox[2] - bbox[0]
                heading_x = (width - line_width) // 2
                
                # Draw heading with stroke
                self.draw_text_with_stroke(draw, (heading_x, heading_y), 
                                        line, heading_font, self.heading_color, self.shadow_color, stroke_width=4)
                
                heading_y += bbox[3] - bbox[1] + 10  # Add spacing between lines
        
        # --- SUBHEADING: Below heading, smaller ---
        if subheading:
            # Wrap subheading if too long
            max_subheading_width = width * 0.7  # 70% of image width
            subheading_lines = self.wrap_text(subheading, subheading_font, max_subheading_width)
            
            # Position subheading below heading
            subheading_y = heading_y + 20  # Add spacing after heading
            
            for line in subheading_lines:
                bbox = draw.textbbox((0, 0), line, font=subheading_font)
                line_width = bbox[2] - bbox[0]
                subheading_x = (width - line_width) // 2
                
                # Draw subheading with stroke
                self.draw_text_with_stroke(draw, (subheading_x, subheading_y), 
                                        line, subheading_font, self.subheading_color, self.shadow_color, stroke_width=2)
                
                subheading_y += bbox[3] - bbox[1] + 8  # Add spacing between lines
        
        # --- LABEL: Bottom-left badge ---
        if label:
            label_x = margin
            label_y = height - bottom_margin - 60  # Bottom-left position
            
            # Create label badge
            bbox = draw.textbbox((0, 0), label, font=label_font)
            label_width = bbox[2] - bbox[0]
            label_height = bbox[3] - bbox[1]
            
            # Draw rounded background
            padding = 12
            badge_width = label_width + 2 * padding
            badge_height = label_height + 2 * padding
            radius = min(badge_height // 2, 12)
            
            self.draw_rounded_rectangle(draw, 
                                      [label_x, label_y, label_x + badge_width, label_y + badge_height], 
                                      radius, self.label_bg)
            
            # Draw label text with stroke
            self.draw_text_with_stroke(draw, (label_x + padding, label_y + padding), 
                                    label, label_font, self.label_color, self.shadow_color, stroke_width=1)
        
        # --- DATE: Bottom-right with background ---
        if date:
            bbox = draw.textbbox((0, 0), date, font=date_font)
            date_width = bbox[2] - bbox[0]
            date_height = bbox[3] - bbox[1]
            
            # Add padding for background
            padding = 8
            bg_width = date_width + 2 * padding
            bg_height = date_height + 2 * padding
            
            date_x = width - bg_width - margin
            date_y = height - bg_height - bottom_margin
            
            # Draw semi-transparent background for date
            bg_rect = [date_x, date_y, date_x + bg_width, date_y + bg_height]
            draw.rectangle(bg_rect, fill=self.date_bg)
            
            # Draw date text
            self.draw_text_with_stroke(draw, (date_x + padding, date_y + padding), 
                                    date, date_font, self.date_color, self.shadow_color, stroke_width=1)
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def create_thumbnail(self, image_url: str, text_data: dict) -> str:
        """
        Legacy method for backward compatibility.
        Now calls the new generate_thumbnail_template method.
        """
        return self.generate_thumbnail_template(image_url, text_data)
