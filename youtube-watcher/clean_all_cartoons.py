from PIL import Image
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAMES_DIR = os.path.join(ASSETS_DIR, "orange_frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

def clean_binary_alpha(img, threshold=160):
    """Ensure image has razor-sharp 1-bit alpha (0 or 255). No semi-transparent halos in Tkinter!"""
    img = img.convert("RGBA")
    w, h = img.size
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < threshold or (r > 240 and g > 240 and b > 240):
                pixels[x, y] = (255, 255, 255, 0)
            else:
                pixels[x, y] = (r, g, b, 255)
    return img

def process_ceo_cartoon():
    """Clean CEO cartoon of any edge fringe or distorted borders."""
    ceo_path = os.path.join(ASSETS_DIR, "cartoon.png")
    if os.path.exists(ceo_path):
        img = Image.open(ceo_path)
        cleaned = clean_binary_alpha(img, threshold=150)
        cleaned.save(ceo_path, "PNG")
        print("✅ CEO cartoon.png cleaned and made razor-sharp!")

def process_orange_character():
    """Generate crisp, distortion-free animation frames for orange character."""
    raw_path = os.path.join(ASSETS_DIR, "image_7b09e998.jpg")
    raw = Image.open(raw_path).convert("RGBA")
    w, h = raw.size
    pixels = raw.load()

    min_x, min_y, max_x, max_y = w, h, 0, 0
    # Clean chroma keying - remove green background completely
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # Green screen check
            if g > 75 and g > r * 1.05 and g > b * 1.05:
                pixels[x, y] = (255, 255, 255, 0)
            else:
                pixels[x, y] = (r, g, b, 255)
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y

    pad = 2
    crop_box = (
        max(0, min_x - pad),
        max(0, min_y - pad),
        min(w, max_x + 1 + pad),
        min(h, max_y + 1 + pad)
    )
    cropped = raw.crop(crop_box)
    
    # Scale to crisp 52px height for tab bar
    target_h = 52
    target_w = int(cropped.width * (target_h / cropped.height))
    base = cropped.resize((target_w, target_h), Image.LANCZOS)
    base = clean_binary_alpha(base)

    # 1. Walk frames (facing right naturally)
    walk_1 = base
    walk_2 = clean_binary_alpha(base.rotate(-6, resample=Image.NEAREST, expand=True))
    walk_3 = base
    walk_4 = clean_binary_alpha(base.rotate(6, resample=Image.NEAREST, expand=True))

    walk_1.save(os.path.join(FRAMES_DIR, "walk_1.png"))
    walk_2.save(os.path.join(FRAMES_DIR, "walk_2.png"))
    walk_3.save(os.path.join(FRAMES_DIR, "walk_3.png"))
    walk_4.save(os.path.join(FRAMES_DIR, "walk_4.png"))

    # 2. Stand & Lock-on pose at the X icon
    stand = base
    stand.save(os.path.join(FRAMES_DIR, "stand_aim.png"))

    # 3. Jump high into the air
    jump = clean_binary_alpha(base.resize((int(target_w * 0.95), int(target_h * 1.15)), Image.LANCZOS))
    jump.save(os.path.join(FRAMES_DIR, "jump_up.png"))

    # 4. Rotate 85 degrees clockwise so NOSE POINTS STRAIGHT DOWN at the X icon!
    # In original, nose points right (at x=max, y=mid).
    # Rotating 85 degrees clockwise points the long nose straight DOWN!
    nose_down = clean_binary_alpha(base.rotate(-85, resample=Image.NEAREST, expand=True))
    nose_down.save(os.path.join(FRAMES_DIR, "nose_down.png"))

    # 5. Nose impact (squashed slightly on landing on the X icon)
    nd_w, nd_h = nose_down.size
    nose_impact = clean_binary_alpha(nose_down.resize((int(nd_w * 1.25), int(nd_h * 0.85)), Image.LANCZOS))
    nose_impact.save(os.path.join(FRAMES_DIR, "nose_impact.png"))

    # 6. Celebrate
    celeb = clean_binary_alpha(base.rotate(-15, resample=Image.NEAREST, expand=True))
    celeb.save(os.path.join(FRAMES_DIR, "celebrate.png"))

    print(f"✅ Generated 8 razor-sharp, zero-distortion frames in {FRAMES_DIR}")

if __name__ == "__main__":
    process_ceo_cartoon()
    process_orange_character()
