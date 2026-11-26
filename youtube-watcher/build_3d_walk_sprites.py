from PIL import Image, ImageDraw
import os
import math

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAMES_DIR = os.path.join(ASSETS_DIR, "orange_frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

def clean_binary_alpha(img, threshold=120):
    """Ensure crisp 1-bit alpha for Tkinter transparency without edge distortion."""
    img = img.convert("RGBA")
    w, h = img.size
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < threshold:
                pixels[x, y] = (255, 255, 255, 0)
            else:
                # Protect near-white pixels from Tkinter's colorkey
                if r >= 254 and g >= 254 and b >= 254:
                    pixels[x, y] = (254, 254, 254, 255)
                else:
                    pixels[x, y] = (r, g, b, 255)
    return img

def build_3d_sprites():
    src_path = os.path.join(ASSETS_DIR, "character_3d.png")
    master = Image.open(src_path).convert("RGBA")
    mw, mh = master.size

    # Target height on browser tab bar: 54px
    target_h = 54
    target_w = int(mw * (target_h / mh))
    base = clean_binary_alpha(master.resize((target_w, target_h), Image.LANCZOS))
    bw, bh = base.size

    canvas_w = bw + 14
    canvas_h = bh + 14

    def make_3d_frame(scale_x, scale_y, rotate_deg, offset_x=0, offset_y=0, shadow_scale=1.0):
        # 1. Scale character
        fw = int(bw * scale_x)
        fh = int(bh * scale_y)
        scaled = base.resize((fw, fh), Image.LANCZOS)

        # 2. 3D perspective rotation
        if rotate_deg != 0:
            rotated = scaled.rotate(rotate_deg, resample=Image.BICUBIC, expand=True)
        else:
            rotated = scaled

        rw, rh = rotated.size

        # 3. Canvas with 3D drop shadow
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(canvas)

        # 3D contact shadow (dark ellipse on the ground beneath feet)
        sw = int(bw * 0.70 * shadow_scale)
        sh = max(2, int(6 * shadow_scale))
        sx = (canvas_w - sw) // 2 + offset_x
        sy = canvas_h - 7
        # Render a crisp dark shadow ellipse
        draw.ellipse([sx, sy, sx + sw, sy + sh], fill=(35, 25, 20, 255))

        # 4. Paste character on top of ground shadow
        px = max(0, (canvas_w - rw) // 2 + offset_x)
        py = max(0, canvas_h - rh - 5 + offset_y)
        canvas.paste(rotated, (px, py), rotated)

        return clean_binary_alpha(canvas)

    # 1. Walk RIGHT frames (4-phase 3D walk cycle)
    # Phase 1: Right foot stride forward, forward lean (-4 deg)
    r1 = make_3d_frame(1.02, 0.98, -4, offset_x=1, offset_y=1, shadow_scale=1.0)
    # Phase 2: Passing buoyant lift (+3px up), shadow contracts (0.85)
    r2 = make_3d_frame(0.98, 1.02, 0, offset_x=0, offset_y=-3, shadow_scale=0.85)
    # Phase 3: Left foot push-off, backward shift (+4 deg)
    r3 = make_3d_frame(1.02, 0.98, 4, offset_x=-1, offset_y=1, shadow_scale=1.0)
    # Phase 4: Passing buoyant lift (+3px up), shadow contracts (0.85)
    r4 = make_3d_frame(0.99, 1.01, 0, offset_x=0, offset_y=-3, shadow_scale=0.85)

    r1.save(os.path.join(FRAMES_DIR, "walk_r1.png"))
    r2.save(os.path.join(FRAMES_DIR, "walk_r2.png"))
    r3.save(os.path.join(FRAMES_DIR, "walk_r3.png"))
    r4.save(os.path.join(FRAMES_DIR, "walk_r4.png"))

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

    # 3. Action frames (stand, jump, nose-down, nose-impact, celebrate)
    stand = make_3d_frame(1.0, 1.0, 0, shadow_scale=1.0)
    stand.save(os.path.join(FRAMES_DIR, "stand_aim.png"))

    # High jump: character airborne, shadow shrinks (0.5)
    jump = make_3d_frame(0.92, 1.12, 0, offset_y=-6, shadow_scale=0.55)
    jump.save(os.path.join(FRAMES_DIR, "jump_up.png"))

    # Nose pointing straight down (85 deg clockwise)
    nose_rot = base.rotate(-85, resample=Image.BICUBIC, expand=True)
    nr_w, nr_h = nose_rot.size
    nd_can = Image.new("RGBA", (nr_w + 10, nr_h + 10), (255, 255, 255, 0))
    nd_can.paste(nose_rot, (5, 5), nose_rot)
    nose_down = clean_binary_alpha(nd_can)
    nose_down.save(os.path.join(FRAMES_DIR, "nose_down.png"))

    # Nose impact: squashed slightly on X button
    ni_w, ni_h = nose_down.size
    nose_impact = clean_binary_alpha(nose_down.resize((int(ni_w * 1.25), int(ni_h * 0.85)), Image.LANCZOS))
    nose_impact.save(os.path.join(FRAMES_DIR, "nose_impact.png"))

    # Celebrate: victory bounce
    celeb = make_3d_frame(1.05, 1.02, -12, shadow_scale=1.05)
    celeb.save(os.path.join(FRAMES_DIR, "celebrate.png"))

    print("✅ Generated 3D-feel walking sprites with dynamic ground shadow & action frames!")

if __name__ == "__main__":
    build_3d_sprites()
