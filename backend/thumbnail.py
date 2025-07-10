import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os

class ThumbnailGenerator:
    def __init__(self):
        self.canvas_size = (1280, 720)  # YouTube thumbnail size

        # Fonts sized for 1280x720 canvas
        self.heading_size = 100
        self.subheading_size = 60
        self.label_size = 40
        self.date_size = 38
        self.line_spacing = 18

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
        self.overlay_opacity = 0.35

        # Logo
        self.logo_size = (100, 100)
        self.logo_path = os.path.join(os.path.dirname(__file__), "static", "Logo.png")

        # Font paths
        static_dir = os.path.join(os.path.dirname(__file__), "static", "fonts")
        self.font_regular = os.path.join(static_dir, "Montserrat-Regular.ttf")
        self.font_bold = os.path.join(static_dir, "Montserrat-Bold.ttf")
        self.font_italic = os.path.join(static_dir, "Montserrat-Italic.ttf")

    def download_image(self, url: str) -> Image.Image:
        try:
            response = requests.get(url)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert('RGB')
            return image.resize(self.canvas_size, Image.Resampling.LANCZOS)
        except:
            return Image.new('RGB', self.canvas_size, (40, 40, 40))

    def load_logo(self):
        try:
            if os.path.exists(self.logo_path):
                logo = Image.open(self.logo_path).convert("RGBA")
                return logo.resize(self.logo_size, Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"⚠️ Failed to load logo: {e}")
        return None

    def get_font(self, size, bold=False, italic=False):
        try:
            if bold and os.path.exists(self.font_bold):
                return ImageFont.truetype(self.font_bold, size)
            if italic and os.path.exists(self.font_italic):
                return ImageFont.truetype(self.font_italic, size)
            if os.path.exists(self.font_regular):
                return ImageFont.truetype(self.font_regular, size)
        except:
            pass
        # Fallback to system
        try:
            return ImageFont.truetype("arialbd.ttf" if bold else "ariali.ttf" if italic else "arial.ttf", size)
        except:
            return ImageFont.load_default()

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines, current = [], []
        for word in words:
            test_line = ' '.join(current + [word])
            test_width = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test_line, font=font)[2]
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
                if dx**2 + dy**2 <= stroke_width**2:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
        draw.text((x, y), text, font=font, fill=text_color)

    def draw_rounded_rectangle(self, draw, bbox, radius, fill):
        x0, y0, x1, y1 = bbox
        draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
        draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
        draw.ellipse([x0, y0, x0 + 2 * radius, y0 + 2 * radius], fill=fill)
        draw.ellipse([x1 - 2 * radius, y0, x1, y0 + 2 * radius], fill=fill)
        draw.ellipse([x0, y1 - 2 * radius, x0 + 2 * radius, y1], fill=fill)
        draw.ellipse([x1 - 2 * radius, y1 - 2 * radius, x1, y1], fill=fill)

    def generate_thumbnail_template(self, image_url: str, metadata: dict) -> str:
        image = self.download_image(image_url)
        overlay = Image.new("RGBA", self.canvas_size, (0, 0, 0, int(255 * self.overlay_opacity)))
        image = Image.alpha_composite(image.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(image)

        heading = metadata.get("heading", "").upper()
        subheading = metadata.get("subheading", "")
        label = metadata.get("label", "")
        date = metadata.get("date", "")

        width, height = self.canvas_size
        margin = 60
        bottom_margin = 40
        y = margin

        # Logo
        logo = self.load_logo()
        if logo:
            image.paste(logo, (margin, margin), logo)
            y += self.logo_size[1]

        # Heading
        heading_font = self.get_font(self.heading_size, bold=True)
        for line in self.wrap_text(heading, heading_font, width * 0.85):
            bbox = draw.textbbox((0, 0), line, font=heading_font)
            x = (width - bbox[2]) // 2
            self.draw_text_with_stroke(draw, (x, y), line, heading_font, self.heading_color, self.shadow_color, 6)
            y += bbox[3] - bbox[1] + self.line_spacing

        # Add extra space between heading and subheading
        y += 30

        # Subheading
        if subheading:
            sub_font = self.get_font(self.subheading_size)
            for line in self.wrap_text(subheading, sub_font, width * 0.75):
                bbox = draw.textbbox((0, 0), line, font=sub_font)
                x = (width - bbox[2]) // 2
                self.draw_text_with_stroke(draw, (x, y), line, sub_font, self.subheading_color, self.shadow_color, 3)
                y += bbox[3] - bbox[1] + self.line_spacing

        # Label
        if label:
            label_font = self.get_font(self.label_size, bold=True)
            bbox = draw.textbbox((0, 0), label, font=label_font)
            lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            padding = 14
            rect_left = margin
            rect_top = height - lh - padding * 2 - bottom_margin
            rect_right = margin + lw + padding * 2
            rect_bottom = height - bottom_margin
            rect = [rect_left, rect_top, rect_right, rect_bottom]
            self.draw_rounded_rectangle(draw, rect, 12, self.label_bg)
            # Center label horizontally and vertically in the rectangle, correcting for bbox[1] offset
            label_x = rect_left + (rect_right - rect_left - lw) // 2
            label_y = rect_top + (rect_bottom - rect_top - lh) // 2 - bbox[1]
            self.draw_text_with_stroke(draw, (label_x, label_y), label, label_font, self.label_color, self.shadow_color, 2)

        # Date
        if date:
            date_font = self.get_font(self.date_size, italic=True)
            bbox = draw.textbbox((0, 0), date, font=date_font)
            dw, dh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            padding = 10
            # Keep the date rectangle right-aligned at the bottom
            rect_left = width - dw - padding * 2 - margin
            rect_top = height - dh - padding * 2 - bottom_margin
            rect_right = rect_left + dw + padding * 2
            rect_bottom = rect_top + dh + padding * 2
            draw.rectangle([rect_left, rect_top, rect_right, rect_bottom], fill=self.date_bg)
            # Center the date text within the rectangle, correcting for bbox offset
            date_x = rect_left + ((rect_right - rect_left) - dw) // 2 - bbox[0]
            date_y = rect_top + ((rect_bottom - rect_top) - dh) // 2 - bbox[1]
            self.draw_text_with_stroke(draw, (date_x, date_y), date, date_font, self.date_color, self.shadow_color, 2)

        # Export to base64
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    def create_thumbnail(self, image_url: str, text_data: dict) -> str:
        return self.generate_thumbnail_template(image_url, text_data)
