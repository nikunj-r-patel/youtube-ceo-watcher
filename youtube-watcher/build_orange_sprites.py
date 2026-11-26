from PIL import Image
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
BASE_PATH = os.path.join(ASSETS_DIR, "orange_character.png")
OUTPUT_DIR = os.path.join(ASSETS_DIR, "orange_frames")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_frames():
    base = Image.open(BASE_PATH).convert("RGBA")
    
    # Standard height for browser tab bar
    target_h = 42
    target_w = int(base.width * (target_h / base.height))
    base_resized = base.resize((target_w, target_h), Image.LANCZOS)
    
    # Make sure we face left (direction of travel: right to left)
    face_left = base_resized.transpose(Image.FLIP_LEFT_RIGHT)
    
    # 1. Walk Frame 1 (neutral)
    face_left.save(os.path.join(OUTPUT_DIR, "walk_1.png"))
    
    # 2. Walk Frame 2 (tilt left / lean forward, bob up 2px)
    f2 = face_left.rotate(6, resample=Image.BICUBIC, expand=True)
    f2.save(os.path.join(OUTPUT_DIR, "walk_2.png"))
    
    # 3. Walk Frame 3 (neutral bob)
    face_left.save(os.path.join(OUTPUT_DIR, "walk_3.png"))
    
    # 4. Walk Frame 4 (tilt right / push off, bob down 2px)
    f4 = face_left.rotate(-6, resample=Image.BICUBIC, expand=True)
    f4.save(os.path.join(OUTPUT_DIR, "walk_4.png"))
    
    # 5. Jump / Preparation to stomp
    jump_w = int(target_w * 0.9)
    jump_h = int(target_h * 1.15)
    f_jump = face_left.resize((jump_w, jump_h), Image.LANCZOS)
    f_jump.save(os.path.join(OUTPUT_DIR, "stomp_jump.png"))
    
    # 6. Squash / Stomp down on the X button
    squash_w = int(target_w * 1.35)
    squash_h = int(target_h * 0.70)
    f_squash = face_left.resize((squash_w, squash_h), Image.LANCZOS)
    f_squash.save(os.path.join(OUTPUT_DIR, "stomp_squash.png"))
    
    # 7. Celebrate / Victory
    f_celeb = face_left.rotate(12, resample=Image.BICUBIC, expand=True)
    f_celeb.save(os.path.join(OUTPUT_DIR, "celebrate.png"))
    
    print(f"Generated {len(os.listdir(OUTPUT_DIR))} frames in {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_frames()
