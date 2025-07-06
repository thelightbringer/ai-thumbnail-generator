import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os

class ThumbnailGenerator:
    def __init__(self):
        # Fixed font sizes for 1920x1080
        self.heading_size = 180
        self.subheading_size = 100
        self.label_size = 60
        self.date_size = 60
        self.line_spacing = 25

        # Colors
        self.heading_color = (255, 255, 255)
        self.subheading_color = (255, 255, 255)
        self.label_color = (255, 255, 255)
        self.date_color = (255, 255, 255)

        # Background colors
        self.label_bg = (220, 38, 38)
        self.date_bg = (0, 0, 0, 180)

        # Stroke/shadow
        self.shadow_color = (0, 0, 0)

        # Overlay opacity
        self.overlay_opacity = 0.3

        # Logo
        self.logo_path = "../frontend/src/assets/Logo.png"
        self.logo_size = (180, 180)

    def load_logo(self):
        try:
            if os.path.exists(self.logo_path):
                print(f"✅ Found logo at {self.logo_path}")
                logo = Image.open(self.logo_path).convert('RGBA')
                return logo.resize(self.logo_size, Image.Resampling.LANCZOS)
            else:
                print(f"⚠️ Logo not found at: {self.logo_path}")
        except Exception as e:
            print(f"❌ Error loading logo: {e}")
        return None

    def download_image(self, url: str) -> Image.Image:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content)).convert('RGB')
        except Exception as e:
            print(f"Error downloading image: {e}")
            return Image.new('RGB', (1920, 1080), (50, 50, 50))

    def get_font(self, size, bold=False, italic=False):
        try:
            if bold:
                return ImageFont.truetype("Montserrat-Bold.ttf", size)
            elif italic:
                return ImageFont.truetype("Montserrat-Italic.ttf", size)
            return ImageFont.truetype("Montserrat-Regular.ttf", size)
        except:
            try:
                return ImageFont.truetype("arialbd.ttf" if bold else "ariali.ttf" if italic else "arial.ttf", size)
            except:
                return ImageFont.load_default()

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines, current = [], []
        for word in words:
            test_line = ' '.join(current + [word])
            test_width = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)[2]
            if test_width <= max_width:
                current.append(word)
            else:
                lines.append(' '.join(current))
                current = [word]
        if current:
            lines.append(' '.join(current))
        return lines or [text]

    def draw_text_with_stroke(self, draw, xy, text, font, text_color, stroke_color, stroke_width=3):
        x, y = xy
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx*dx + dy*dy <= stroke_width*stroke_width:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
        draw.text((x, y), text, font=font, fill=text_color)

    def draw_rounded_rectangle(self, draw, bbox, radius, fill):
        x0, y0, x1, y1 = bbox
        draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
        draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
        draw.ellipse([x0, y0, x0 + 2*radius, y0 + 2*radius], fill=fill)
        draw.ellipse([x1 - 2*radius, y0, x1, y0 + 2*radius], fill=fill)
        draw.ellipse([x0, y1 - 2*radius, x0 + 2*radius, y1], fill=fill)
        draw.ellipse([x1 - 2*radius, y1 - 2*radius, x1, y1], fill=fill)

    def generate_thumbnail_template(self, image_url: str, metadata: dict) -> str:
        image = self.download_image(image_url).resize((1920, 1080), Image.Resampling.LANCZOS)
        overlay = Image.new('RGBA', image.size, (0, 0, 0, int(255 * self.overlay_opacity)))
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(image)

        heading = metadata.get("heading", "").upper()
        subheading = metadata.get("subheading", "")
        label = metadata.get("label", "")
        date = metadata.get("date", "")

        width, height = image.size
        heading_font = self.get_font(self.heading_size, bold=True)
        subheading_font = self.get_font(self.subheading_size)
        label_font = self.get_font(self.label_size, bold=True)
        date_font = self.get_font(self.date_size, italic=True)

        margin = int(width * 0.08)
        top_margin = int(height * 0.10)
        bottom_margin = int(height * 0.06)

        # Logo
        logo = self.load_logo()
        if logo:
            image.paste(logo, (margin, top_margin), logo)

        # Heading
        heading_lines = self.wrap_text(heading, heading_font, width * 0.85)
        y = top_margin + (self.logo_size[1] if logo else 0) + 30
        for line in heading_lines:
            bbox = draw.textbbox((0, 0), line, font=heading_font)
            x = (width - bbox[2]) // 2
            self.draw_text_with_stroke(draw, (x, y), line, heading_font, self.heading_color, self.shadow_color, stroke_width=6)
            y += bbox[3] - bbox[1] + self.line_spacing

        # Subheading
        if subheading:
            subheading_lines = self.wrap_text(subheading, subheading_font, width * 0.75)
            for line in subheading_lines:
                bbox = draw.textbbox((0, 0), line, font=subheading_font)
                x = (width - bbox[2]) // 2
                self.draw_text_with_stroke(draw, (x, y), line, subheading_font, self.subheading_color, self.shadow_color, stroke_width=3)
                y += bbox[3] - bbox[1] + self.line_spacing

        # Label
        if label:
            bbox = draw.textbbox((0, 0), label, font=label_font)
            lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            padding = 12
            self.draw_rounded_rectangle(draw, [margin, height - lh - padding*2 - bottom_margin, margin + lw + padding*2, height - bottom_margin], 16, self.label_bg)
            self.draw_text_with_stroke(draw, (margin + padding, height - lh - padding - bottom_margin), label, label_font, self.label_color, self.shadow_color, stroke_width=2)

        # Date
        if date:
            bbox = draw.textbbox((0, 0), date, font=date_font)
            dw, dh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            padding = 10
            x = width - dw - padding*2 - margin
            y_date = height - dh - padding*2 - bottom_margin
            draw.rectangle([x, y_date, x + dw + padding*2, y_date + dh + padding*2], fill=self.date_bg)
            self.draw_text_with_stroke(draw, (x + padding, y_date + padding), date, date_font, self.date_color, self.shadow_color, stroke_width=2)

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    def create_thumbnail(self, image_url: str, text_data: dict) -> str:
        return self.generate_thumbnail_template(image_url, text_data)
