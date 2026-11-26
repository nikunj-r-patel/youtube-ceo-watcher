from PIL import Image
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAMES_DIR = os.path.join(ASSETS_DIR, "orange_frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

def clean_binary_alpha(img, threshold=140):
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

def build_all_sprites():
    # Load clean base sprite
    master = Image.open(os.path.join(ASSETS_DIR, "orange_character_clean.png")).convert("RGBA")
    mw, mh = master.size
    
    # Scale to crisp 52px height for tab bar
    target_h = 52
    target_w = int(mw * (target_h / mh))
    base_r = clean_binary_alpha(master.resize((target_w, target_h), Image.LANCZOS))
    bw, bh = base_r.size
    
    # Separate body (top 68%) and legs (bottom 32%)
    leg_split = int(bh * 0.68)
    body_part = base_r.crop((0, 0, bw, leg_split))
    
    # Foot 1 (Back foot, x from 0 to 45% of width)
    split_x = int(bw * 0.46)
    foot1 = base_r.crop((0, leg_split, split_x, bh))
    # Foot 2 (Front foot, x from 45% to 80% of width)
    foot2 = base_r.crop((split_x, leg_split, bw, bh))
    
    def make_walk_frame(shift_f1_x, shift_f1_y, shift_f2_x, shift_f2_y, bob_body_y=0):
        # Canvas with generous size to avoid clipping
        canvas = Image.new("RGBA", (bw + 10, bh + 4), (255, 255, 255, 0))
        # Paste body
        canvas.paste(body_part, (5, 2 + bob_body_y), body_part)
        # Paste foot 1
        f1_x = 5 + shift_f1_x
        f1_y = 2 + leg_split + shift_f1_y
        canvas.paste(foot1, (f1_x, f1_y), foot1)
        # Paste foot 2
        f2_x = 5 + split_x + shift_f2_x
        f2_y = 2 + leg_split + shift_f2_y
        canvas.paste(foot2, (f2_x, f2_y), foot2)
        return clean_binary_alpha(canvas)

    # 1. Walk RIGHT frames (legs actively stepping!)
    # Frame 1: Neutral stride
    r1 = make_walk_frame(0, 0, 0, 0, bob_body_y=0)
    # Frame 2: Front foot stepping forward & up (+3px, -3px), back foot back (-3px)
    r2 = make_walk_frame(-3, 0, 3, -3, bob_body_y=-2)
    # Frame 3: Neutral stride
    r3 = make_walk_frame(0, 0, 0, 0, bob_body_y=0)
    # Frame 4: Back foot stepping forward & up (+3px, -3px), front foot back (-3px)
    r4 = make_walk_frame(3, -3, -3, 0, bob_body_y=-2)

    r1.save(os.path.join(FRAMES_DIR, "walk_r1.png"))
    r2.save(os.path.join(FRAMES_DIR, "walk_r2.png"))
    r3.save(os.path.join(FRAMES_DIR, "walk_r3.png"))
    r4.save(os.path.join(FRAMES_DIR, "walk_r4.png"))

    # Also keep walk_1..4 pointing to walk_r1..4 for compatibility
    r1.save(os.path.join(FRAMES_DIR, "walk_1.png"))
    r2.save(os.path.join(FRAMES_DIR, "walk_2.png"))
    r3.save(os.path.join(FRAMES_DIR, "walk_3.png"))
    r4.save(os.path.join(FRAMES_DIR, "walk_4.png"))

    # 2. Walk LEFT frames (horizontally flipped for walking back to the left!)
    l1 = clean_binary_alpha(r1.transpose(Image.FLIP_LEFT_RIGHT))
    l2 = clean_binary_alpha(r2.transpose(Image.FLIP_LEFT_RIGHT))
    l3 = clean_binary_alpha(r3.transpose(Image.FLIP_LEFT_RIGHT))
    l4 = clean_binary_alpha(r4.transpose(Image.FLIP_LEFT_RIGHT))

    l1.save(os.path.join(FRAMES_DIR, "walk_l1.png"))
    l2.save(os.path.join(FRAMES_DIR, "walk_l2.png"))
    l3.save(os.path.join(FRAMES_DIR, "walk_l3.png"))
    l4.save(os.path.join(FRAMES_DIR, "walk_l4.png"))

    # 3. Action frames (aim, jump, nose-down, nose-impact, celebrate)
    stand_aim = r1
    stand_aim.save(os.path.join(FRAMES_DIR, "stand_aim.png"))

    jump_up = clean_binary_alpha(base_r.resize((int(bw * 0.95), int(bh * 1.15)), Image.LANCZOS))
    jump_up.save(os.path.join(FRAMES_DIR, "jump_up.png"))

    # Rotate 85 degrees so nose points straight down
    nose_down = clean_binary_alpha(base_r.rotate(-85, resample=Image.NEAREST, expand=True))
    nose_down.save(os.path.join(FRAMES_DIR, "nose_down.png"))

    nd_w, nd_h = nose_down.size
    nose_impact = clean_binary_alpha(nose_down.resize((int(nd_w * 1.25), int(nd_h * 0.85)), Image.LANCZOS))
    nose_impact.save(os.path.join(FRAMES_DIR, "nose_impact.png"))

    celeb = clean_binary_alpha(base_r.rotate(-15, resample=Image.NEAREST, expand=True))
    celeb.save(os.path.join(FRAMES_DIR, "celebrate.png"))

    print("✅ All leg-animated walk frames (Right & Left) and action frames generated successfully!")

if __name__ == "__main__":
    build_all_sprites()
