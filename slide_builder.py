from PIL import Image, ImageDraw, ImageFont
from config import SLIDE_DIR, VIDEO_SIZE
import os

os.makedirs(SLIDE_DIR, exist_ok=True)

def build_slide(image_path, heading, subheading, idx):
    # White background
    base = Image.new("RGB", VIDEO_SIZE, (255, 255, 255))
    draw = ImageDraw.Draw(base)

    # Load image with error handling
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"⚠️ Error loading image {image_path}: {e}")
        print(f"🧱 Creating placeholder image for slide {idx}")
        # Create a placeholder image
        img = Image.new("RGB", (800, 450), (200, 200, 200))
        placeholder_draw = ImageDraw.Draw(img)
        placeholder_draw.text((400, 225), "Image Not Available", fill=(100, 100, 100), anchor="mm")

    # -------------------------
    # RESIZE: fixed height, auto width
    # -------------------------
    target_height = 450
    w, h = img.size
    scale = target_height / h
    new_width = int(w * scale)

    img = img.resize((new_width, target_height), Image.LANCZOS)

    # Center image horizontally
    x = (VIDEO_SIZE[0] - new_width) // 2
    y = 160
    base.paste(img, (x, y))

    # -------------------------
    # Fonts (safe fallback)
    # -------------------------
    try:
        font_h = ImageFont.truetype("arial.ttf", 48)
        font_s = ImageFont.truetype("arial.ttf", 32)
    except:
        font_h = ImageFont.load_default()
        font_s = ImageFont.load_default()

    # Dark text colors
    heading_color = (20, 20, 20)
    subheading_color = (90, 90, 90)

    # Title
    draw.text(
        (VIDEO_SIZE[0] // 2, 50),
        heading,
        fill=heading_color,
        anchor="mm",
        font=font_h
    )

    # Subtitle
    draw.text(
        (VIDEO_SIZE[0] // 2, 110),
        subheading,
        fill=subheading_color,
        anchor="mm",
        font=font_s
    )

    path = f"{SLIDE_DIR}/slide_{idx}.png"
    base.save(path)
    return path
