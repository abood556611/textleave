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
        """Generate realistic article text for background"""
        words = [
            "technology", "innovation", "security", "digital", "modern", "industry",
            "development", "research", "analysis", "systems", "protocols", "networks",
            "enhanced", "protocols", "data", "patterns", "tracking", "solutions",
            "comprehensive", "emerging", "strategic", "impact", "progress", "evolution",
            "fundamental", "principles", "integration", "framework", "methodology", "standards",
            "infrastructure", "implementation", "optimization", "efficiency", "capabilities",
            "transforming", "revolutionizing", "advancing", "establishing", "enabling"
        ]
        
        # Generate full paragraphs that fill the page
        paragraphs = []
        for _ in range(8):  # More paragraphs
            sentences = []
            for _ in range(random.randint(3, 5)):  # Multiple sentences per paragraph
                sentence_length = random.randint(8, 15)
                sentence = ' '.join(random.choice(words) for _ in range(sentence_length))
                sentence = sentence.capitalize() + '.'
                sentences.append(sentence)
            paragraphs.append(' '.join(sentences))
        
        return paragraphs
    
    def generate_page(self, main_text, page_number, add_watermark=True):
        """Generate a single page with main text and random variations"""
        
        # Select random background
        bg_path = random.choice(self.backgrounds)
        img = Image.open(bg_path).resize((self.width, self.height))
        
        # Create drawing context
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Generate full article text that fills the page
        paragraphs = self._generate_filler_text()
        
        # Draw article text across the entire page
        margin_x = 80
        margin_y = 100
        line_height = 45
        max_width = self.width - (margin_x * 2)
        
        y_offset = margin_y
        main_text_position = None
        
        # Choose random position for main text (middle area)
        target_y = random.randint(self.height // 3, 2 * self.height // 3)
        
        for para_idx, paragraph in enumerate(paragraphs):
            # Word wrap the paragraph
            words = paragraph.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=self.filler_font)
                if bbox[2] - bbox[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw each line
            for line in lines:
                # Check if this is where we should place the main text
                if main_text_position is None and y_offset >= target_y and y_offset < target_y + 200:
                    # Replace part of this line with main text
                    words_in_line = line.split()
                    if len(words_in_line) > 3:
                        # Insert main text in the middle of the line
                        insert_pos = len(words_in_line) // 2
                        before_text = ' '.join(words_in_line[:insert_pos])
                        after_text = ' '.join(words_in_line[insert_pos + len(main_text.split()):])
                        
                        # Draw text before
                        if before_text:
                            draw.text((margin_x, y_offset), before_text, font=self.filler_font, fill=(40, 40, 40))
                            bbox_before = draw.textbbox((0, 0), before_text, font=self.filler_font)
                            x_offset = margin_x + (bbox_before[2] - bbox_before[0]) + 10
                        else:
                            x_offset = margin_x
                        
                        # Save main text position for highlighting
                        main_text_position = (x_offset, y_offset)
                        
                        # Draw main text
                        bbox_main = draw.textbbox((0, 0), main_text, font=self.font)
                        main_text_width = bbox_main[2] - bbox_main[0]
                        main_text_height = bbox_main[3] - bbox_main[1]
                        
                        # Draw highlighter BEHIND main text (transparent yellow)
                        padding = 15
                        highlighter_bbox = (
                            x_offset - padding,
                            y_offset - padding,
                            x_offset + main_text_width + padding,
                            y_offset + main_text_height + padding
                        )
                        self._draw_shaky_rectangle(draw, highlighter_bbox, (255, 255, 0, 100))  # More transparent
                        
                        # Draw main text on top (darker, bold)
                        draw.text((x_offset, y_offset), main_text, font=self.font, fill=(0, 0, 0))  # Pure black
                        
                        # Draw text after
                        if after_text:
                            x_after = x_offset + main_text_width + 10
                            draw.text((x_after, y_offset), after_text, font=self.filler_font, fill=(40, 40, 40))
                        
                        y_offset += line_height
                        continue
                
                # Draw normal line
                draw.text((margin_x, y_offset), line, font=self.filler_font, fill=(40, 40, 40))
                y_offset += line_height
                
                if y_offset > self.height - margin_y:
                    break
            
            # Paragraph spacing
            y_offset += 25
            
            if y_offset > self.height - margin_y:
                break
        
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
