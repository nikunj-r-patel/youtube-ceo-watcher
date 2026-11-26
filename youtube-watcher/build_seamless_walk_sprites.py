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
            if a < threshold:
                pixels[x, y] = (255, 255, 255, 0)
            else:
                if r >= 254 and g >= 254 and b >= 254:
                    pixels[x, y] = (254, 254, 254, 255)
                else:
                    pixels[x, y] = (r, g, b, 255)
    return img

def build_seamless_sprites():
    # Load clean un-sliced master character
    master = Image.open(os.path.join(ASSETS_DIR, "orange_character_clean.png")).convert("RGBA")
    mw, mh = master.size
    
    # Scale to crisp 50px height for tab bar
    target_h = 50
    target_w = int(mw * (target_h / mh))
    base = clean_binary_alpha(master.resize((target_w, target_h), Image.LANCZOS))
    bw, bh = base.size
    
    # Pad canvas size so rotations and squash/stretch never clip
    canvas_w = bw + 8
    canvas_h = bh + 8
    
    def create_seamless_frame(scale_x, scale_y, rotate_deg, offset_x=0, offset_y=0):
        # 100% INTACT BODY - NO HORIZONTAL CUTS!
        fw = int(bw * scale_x)
        fh = int(bh * scale_y)
        scaled = base.resize((fw, fh), Image.LANCZOS)
        
        if rotate_deg != 0:
            rotated = scaled.rotate(rotate_deg, resample=Image.BICUBIC, expand=True)
        else:
            rotated = scaled
            
        rw, rh = rotated.size
        # Paste onto clean transparent canvas
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 0))
        px = max(0, (canvas_w - rw) // 2 + offset_x)
        py = max(0, (canvas_h - rh) // 2 + offset_y)
        canvas.paste(rotated, (px, py), rotated)
        return clean_binary_alpha(canvas)

    # 1. Walk RIGHT frames (smooth, squash-and-stretch cartoon walking - zero cuts!)
    # Frame 1: Stride forward, slight forward lean (-4 deg)
    r1 = create_seamless_frame(1.02, 0.98, -4, offset_x=1, offset_y=1)
    # Frame 2: Passing step / buoyant upward bob
    r2 = create_seamless_frame(0.98, 1.02, 0, offset_x=0, offset_y=-2)
    # Frame 3: Stride back push-off, slight backward tilt (+4 deg)
    r3 = create_seamless_frame(1.02, 0.98, 4, offset_x=-1, offset_y=1)
    # Frame 4: Neutral step / upward bob
    r4 = create_seamless_frame(0.99, 1.01, 0, offset_x=0, offset_y=-2)

    r1.save(os.path.join(FRAMES_DIR, "walk_r1.png"))
    r2.save(os.path.join(FRAMES_DIR, "walk_r2.png"))
    r3.save(os.path.join(FRAMES_DIR, "walk_r3.png"))
    r4.save(os.path.join(FRAMES_DIR, "walk_r4.png"))

    # Also keep walk_1..4 for fallback
    r1.save(os.path.join(FRAMES_DIR, "walk_1.png"))
    r2.save(os.path.join(FRAMES_DIR, "walk_2.png"))
    r3.save(os.path.join(FRAMES_DIR, "walk_3.png"))
    r4.save(os.path.join(FRAMES_DIR, "walk_4.png"))

    # 2. Walk LEFT frames (horizontally flipped for clean left exit)
    l1 = clean_binary_alpha(r1.transpose(Image.FLIP_LEFT_RIGHT))
    l2 = clean_binary_alpha(r2.transpose(Image.FLIP_LEFT_RIGHT))
    l3 = clean_binary_alpha(r3.transpose(Image.FLIP_LEFT_RIGHT))
    l4 = clean_binary_alpha(r4.transpose(Image.FLIP_LEFT_RIGHT))

    l1.save(os.path.join(FRAMES_DIR, "walk_l1.png"))
    l2.save(os.path.join(FRAMES_DIR, "walk_l2.png"))
    l3.save(os.path.join(FRAMES_DIR, "walk_l3.png"))
    l4.save(os.path.join(FRAMES_DIR, "walk_l4.png"))

    # 3. Action frames (intact body, zero cuts!)
    # Standing aim pose at the X icon
    stand = create_seamless_frame(1.0, 1.0, 0)
    stand.save(os.path.join(FRAMES_DIR, "stand_aim.png"))

    # High jump up into air (stretched vertically)
    jump = create_seamless_frame(0.92, 1.15, 0)
    jump.save(os.path.join(FRAMES_DIR, "jump_up.png"))

    # Rotated 85 degrees clockwise so nose points straight down
    # Rotate clean intact body
    nose_down_rot = base.rotate(-85, resample=Image.BICUBIC, expand=True)
    nd_w, nd_h = nose_down_rot.size
    nd_canvas = Image.new("RGBA", (nd_w + 6, nd_h + 6), (255, 255, 255, 0))
    nd_canvas.paste(nose_down_rot, (3, 3), nose_down_rot)
    nose_down = clean_binary_alpha(nd_canvas)
    nose_down.save(os.path.join(FRAMES_DIR, "nose_down.png"))

    # Nose impact: squashed on the X button
    ni_w, ni_h = nose_down.size
    nose_impact = clean_binary_alpha(nose_down.resize((int(ni_w * 1.25), int(ni_h * 0.82)), Image.LANCZOS))
    nose_impact.save(os.path.join(FRAMES_DIR, "nose_impact.png"))

    # Victory celebration pose
    celeb = create_seamless_frame(1.05, 1.02, -12)
    celeb.save(os.path.join(FRAMES_DIR, "celebrate.png"))

    print("✅ Seamless, 100% uncut walking frames & action sprites generated successfully!")

if __name__ == "__main__":
    build_seamless_sprites()
