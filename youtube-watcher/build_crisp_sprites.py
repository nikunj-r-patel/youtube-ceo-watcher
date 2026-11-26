from PIL import Image, ImageFilter
import os
import math

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
RAW_PATH = os.path.join(ASSETS_DIR, "image_7b09e998.jpg")
FRAMES_DIR = os.path.join(ASSETS_DIR, "orange_frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

def create_crisp_sprite():
    raw = Image.open(RAW_PATH).convert("RGBA")
    w, h = raw.size
    pixels = raw.load()

    # High-quality chroma keying with green despill
    min_x, min_y, max_x, max_y = w, h, 0, 0

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            
            # Check for green background
            # If green is dominant over red and blue
            if g > 75 and g > r * 1.08 and g > b * 1.08:
                # Fully transparent background
                pixels[x, y] = (0, 0, 0, 0)
            elif g > r and g > b:
                # Green edge / fringe pixel -> despill: neutralize green to match orange/skin
                new_g = int((r + b) * 0.45)
                # Soft alpha falloff for smooth anti-aliased edge
                alpha = max(0, min(255, int(255 - (g - r) * 2.5)))
                pixels[x, y] = (r, new_g, b, alpha)
                if alpha > 40:
                    if x < min_x: min_x = x
                    if y < min_y: min_y = y
                    if x > max_x: max_x = x
                    if y > max_y: max_y = y
            else:
                # Solid character pixel
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y

    # Crop tightly to character bounds
    pad = 4
    crop_box = (
        max(0, min_x - pad),
        max(0, min_y - pad),
        min(w, max_x + 1 + pad),
        min(h, max_y + 1 + pad)
    )
    cropped = raw.crop(crop_box)
    
    # Save master high-res transparent character
    master_path = os.path.join(ASSETS_DIR, "orange_character_clean.png")
    cropped.save(master_path, "PNG")
    print(f"Master clean sprite saved: {cropped.size}")
    
    # Target height for clear, visible display on tab bar: 52px tall!
    target_h = 52
    target_w = int(cropped.width * (target_h / cropped.height))
    base_sprite = cropped.resize((target_w, target_h), Image.LANCZOS)
    
    # Note: Character is NATURALLY FACING RIGHT with its nose pointing right!
    # No horizontal flip needed — it naturally walks from left to right!
    
    # 1. Walk Frame 1 (neutral upright stride)
    base_sprite.save(os.path.join(FRAMES_DIR, "walk_1.png"))
    
    # 2. Walk Frame 2 (lean forward, bob up 2px, nose tilts slightly up)
    f2 = base_sprite.rotate(-5, resample=Image.BICUBIC, expand=True)
    f2.save(os.path.join(FRAMES_DIR, "walk_2.png"))
    
    # 3. Walk Frame 3 (stride midpoint)
    base_sprite.save(os.path.join(FRAMES_DIR, "walk_3.png"))
    
    # 4. Walk Frame 4 (push off, bob down 2px, nose tilts forward)
    f4 = base_sprite.rotate(5, resample=Image.BICUBIC, expand=True)
    f4.save(os.path.join(FRAMES_DIR, "walk_4.png"))
    
    # 5. Jump & Aim: Character leaps up into the air, nose pointing toward the X
    jump_w = int(target_w * 0.95)
    jump_h = int(target_h * 1.15)
    f_jump = base_sprite.resize((jump_w, jump_h), Image.LANCZOS).rotate(15, resample=Image.BICUBIC, expand=True)
    f_jump.save(os.path.join(FRAMES_DIR, "jump_aim.png"))
    
    # 6. Nose Dive: Diving down nose-first at 45 degrees towards the X button
    f_dive = base_sprite.rotate(35, resample=Image.BICUBIC, expand=True)
    f_dive.save(os.path.join(FRAMES_DIR, "nose_dive.png"))
    
    # 7. Nose Pinch / Impact: Nose slammed down on the X button, squashed on impact!
    squash_w = int(target_w * 1.25)
    squash_h = int(target_h * 0.75)
    f_pinch = base_sprite.resize((squash_w, squash_h), Image.LANCZOS).rotate(45, resample=Image.BICUBIC, expand=True)
    f_pinch.save(os.path.join(FRAMES_DIR, "nose_pinch.png"))
    
    # 8. Celebrate: Victory pose after closing tab!
    f_celeb = base_sprite.rotate(-12, resample=Image.BICUBIC, expand=True)
    f_celeb.save(os.path.join(FRAMES_DIR, "celebrate.png"))
    
    print(f"Generated 8 crisp right-facing frames (height={target_h}px) in {FRAMES_DIR}")

if __name__ == "__main__":
    create_crisp_sprite()
