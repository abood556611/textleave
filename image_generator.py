import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import Config


class ImageGenerator:
    """Generates magazine-style pages with text overlays"""
    
    def __init__(self, resolution='9:16'):
        """Initialize image generator with resolution"""
        self.width, self.height = Config.RESOLUTIONS.get(resolution, Config.RESOLUTIONS['9:16'])
        self.backgrounds = self._load_backgrounds()
        self.font = self._load_font()
        self.filler_font = self._load_font(size=Config.FILLER_TEXT_FONT_SIZE)
        
    def _load_backgrounds(self):
        """Load background images from static folder"""
        bg_folder = os.path.join(os.path.dirname(__file__), 'static', 'backgrounds')
        backgrounds = []
        
        if os.path.exists(bg_folder):
            for file in os.listdir(bg_folder):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    backgrounds.append(os.path.join(bg_folder, file))
        
        # If no backgrounds found, create default ones
        if not backgrounds:
            backgrounds = self._create_default_backgrounds()
        
        return backgrounds
    
    def _create_default_backgrounds(self):
        """Create default paper texture backgrounds"""
        bg_folder = os.path.join(os.path.dirname(__file__), 'static', 'backgrounds')
        os.makedirs(bg_folder, exist_ok=True)
        
        backgrounds = []
        colors = [
            (245, 245, 220),  # Beige
            (255, 253, 208),  # Cream
            (240, 234, 214),  # Light beige
            (255, 250, 240),  # Floral white
            (250, 240, 230),  # Linen
        ]
        
        for i, color in enumerate(colors):
            bg_path = os.path.join(bg_folder, f'paper_{i+1}.png')
            if not os.path.exists(bg_path):
                img = Image.new('RGB', (self.width, self.height), color)
                # Add noise for paper texture
                pixels = img.load()
                for x in range(self.width):
                    for y in range(self.height):
                        noise = random.randint(-10, 10)
                        r, g, b = pixels[x, y]
                        pixels[x, y] = (
                            max(0, min(255, r + noise)),
                            max(0, min(255, g + noise)),
                            max(0, min(255, b + noise))
                        )
                img.save(bg_path)
            backgrounds.append(bg_path)
        
        return backgrounds
    
    def _load_font(self, size=None):
        """Load font for text rendering"""
        if size is None:
            size = Config.MAIN_TEXT_FONT_SIZE
        
        # Try to load custom fonts
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            'C:\\Windows\\Fonts\\Arial.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def _draw_shaky_rectangle(self, draw, bbox, fill_color):
        """Draw a rectangle with shaky edges for highlighter effect"""
        x1, y1, x2, y2 = bbox
        
        # Add random shakiness to edges
        points = []
        num_points = 20
        
        # Top edge
        for i in range(num_points):
            x = x1 + (x2 - x1) * i / num_points
            y = y1 + random.randint(-3, 3)
            points.append((x, y))
        
        # Right edge
        for i in range(num_points):
            x = x2 + random.randint(-3, 3)
            y = y1 + (y2 - y1) * i / num_points
            points.append((x, y))
        
        # Bottom edge
        for i in range(num_points):
            x = x2 - (x2 - x1) * i / num_points
            y = y2 + random.randint(-3, 3)
            points.append((x, y))
        
        # Left edge
        for i in range(num_points):
            x = x1 + random.randint(-3, 3)
            y = y2 - (y2 - y1) * i / num_points
            points.append((x, y))
        
        draw.polygon(points, fill=fill_color)
    
    def _generate_filler_text(self):
        """Generate random filler text for background"""
        words = [
            "Lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
            "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
            "incididunt", "ut", "labore", "et", "dolore", "magna",
            "aliqua", "Ut", "enim", "ad", "minim", "veniam"
        ]
        
        lines = []
        for _ in range(15):
            line = ' '.join(random.choice(words) for _ in range(random.randint(5, 12)))
            lines.append(line)
        
        return lines
    
    def generate_page(self, main_text, page_number, add_watermark=True):
        """Generate a single page with main text and random variations"""
        
        # Select random background
        bg_path = random.choice(self.backgrounds)
        img = Image.open(bg_path).resize((self.width, self.height))
        
        # Create drawing context
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Generate and draw filler text (blurred)
        filler_lines = self._generate_filler_text()
        y_offset = 50
        for line in filler_lines:
            x = random.randint(50, self.width // 4)
            draw.text((x, y_offset), line, font=self.filler_font, fill=(180, 180, 180, 100))
            y_offset += 40
        
        # Apply slight blur to filler text
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Calculate main text position with random offset
        bbox = draw.textbbox((0, 0), main_text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center position with random offset
        base_x = (self.width - text_width) // 2
        base_y = (self.height - text_height) // 2
        
        # Apply random offset for realism
        offset_x = random.randint(-Config.POSITION_VARIANCE, Config.POSITION_VARIANCE)
        offset_y = random.randint(-Config.POSITION_VARIANCE, Config.POSITION_VARIANCE)
        
        x = base_x + offset_x
        y = base_y + offset_y
        
        # Draw highlighter rectangle
        padding = 20
        highlighter_bbox = (
            x - padding,
            y - padding,
            x + text_width + padding,
            y + text_height + padding
        )
        self._draw_shaky_rectangle(draw, highlighter_bbox, Config.HIGHLIGHTER_COLOR)
        
        # Draw main text
        draw.text((x, y), main_text, font=self.font, fill=Config.TEXT_COLOR)
        
        # Add watermark if required
        if add_watermark:
            watermark_font = self._load_font(size=Config.WATERMARK_FONT_SIZE)
            watermark_bbox = draw.textbbox((0, 0), Config.WATERMARK_TEXT, font=watermark_font)
            wm_width = watermark_bbox[2] - watermark_bbox[0]
            wm_x = self.width - wm_width - 20
            wm_y = self.height - 60
            draw.text(
                (wm_x, wm_y),
                Config.WATERMARK_TEXT,
                font=watermark_font,
                fill=(128, 128, 128, Config.WATERMARK_OPACITY)
            )
        
        return img
    
    def generate_pages(self, main_text, num_pages, add_watermark=True):
        """Generate multiple pages"""
        pages = []
        for i in range(num_pages):
            page = self.generate_page(main_text, i, add_watermark)
            pages.append(page)
        
        return pages
