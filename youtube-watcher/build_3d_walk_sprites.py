from PIL import Image, ImageDraw
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAMES_DIR = os.path.join(ASSETS_DIR, "orange_frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

def clean_binary_alpha(img, threshold=110):
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
    pix = master.load()

    # 1. Decompose character cleanly into:
    # - body: intact round torso, face, long nose, and cheeks (down to y=555)
    # - leg_l: left leg (y >= 520, x < 280) with hip anchor meat inside the belly
    # - leg_r: right leg (y >= 520, x >= 280) with hip anchor meat inside the belly
    body = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
    leg_l = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
    leg_r = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))

    hip_l = (215, 545)
    hip_r = (355, 545)

    for y in range(mh):
        for x in range(mw):
            r, g, b, a = pix[x, y]
            if a < 80:
                continue
            p = (r, g, b, 255)
            # Full round belly and torso
            if y < 555:
                body.putpixel((x, y), p)
            # Legs with hip joint overlap from y=520
            if y >= 520:
                if x < 280:
                    leg_l.putpixel((x, y), p)
                elif x <= 560:
                    leg_r.putpixel((x, y), p)

    # Tight crop limbs
    bb_l = leg_l.getbbox()
    leg_l_c = leg_l.crop(bb_l)
    p_l = (hip_l[0] - bb_l[0], hip_l[1] - bb_l[1])

    bb_r = leg_r.getbbox()
    leg_r_c = leg_r.crop(bb_r)
    p_r = (hip_r[0] - bb_r[0], hip_r[1] - bb_r[1])

    def rotate_limb(limb_img, pivot, angle, scale_y=1.0, dy=0):
        px, py = pivot
        lw, lh = limb_img.size
        if scale_y != 1.0:
            new_lh = max(10, int(lh * scale_y))
            limb_img = limb_img.resize((lw, new_lh), Image.LANCZOS)
            py = int(py * scale_y)
            lw, lh = limb_img.size
        radius = int(max(px, lw - px, py, lh - py)) + 40
        c_size = radius * 2
        canvas = Image.new("RGBA", (c_size, c_size), (0, 0, 0, 0))
        canvas.paste(limb_img, (radius - px, radius - py))
        rotated = canvas.rotate(angle, resample=Image.BICUBIC)
        return rotated, radius, dy

    pad_x, pad_y = 120, 80
    cw, ch = mw + pad_x * 2, mh + pad_y * 2
    ground_y = 830 + pad_y

    def render_hi_res_frame(rot_l, sc_l, dy_l, rot_r, sc_r, dy_r, bob, shadow_spread=1.0):
        frame = Image.new("RGBA", (cw, ch), (255, 255, 255, 0))
        draw = ImageDraw.Draw(frame)

        # 1. 3D contact ground shadow
        sw = int(320 * shadow_spread)
        sh = int(36 * shadow_spread)
        sx = (cw - sw) // 2 - 20
        draw.ellipse([sx, ground_y - sh // 2, sx + sw, ground_y + sh // 2], fill=(35, 22, 18, 255))

        # 2. Back leg (Left)
        r_l, rad_l, dyl = rotate_limb(leg_l_c, p_l, rot_l, sc_l, dy_l)
        hl_x = hip_l[0] + pad_x
        hl_y = hip_l[1] + pad_y + bob + dyl
        frame.paste(r_l, (hl_x - rad_l, hl_y - rad_l), r_l)

        # 3. Front leg (Right)
        r_r, rad_r, dyr = rotate_limb(leg_r_c, p_r, rot_r, sc_r, dy_r)
        hr_x = hip_r[0] + pad_x
        hr_y = hip_r[1] + pad_y + bob + dyr
        frame.paste(r_r, (hr_x - rad_r, hr_y - rad_r), r_r)

        # 4. Intact round body pasted ON TOP of hips -> 0% cut, 100% seamless!
        frame.paste(body, (pad_x, pad_y + bob), body)

        # Crop to standard canvas
        crop_box = (pad_x - 40, pad_y - 30, pad_x + mw + 40, pad_y + mh + 50)
        return frame.crop(crop_box)

    # Key poses of true organic walking:
    # Frame 1: Contact (Right leg forward +18°, Left leg back -18°, both on ground)
    # Frame 2: Passing (Right leg plants 0°, Left leg bends +8° and lifts -25px, body bobs up -16px)
    # Frame 3: Contact (Left leg forward +18°, Right leg back -18°, both on ground)
    # Frame 4: Passing (Left leg plants 0°, Right leg bends +8° and lifts -25px, body bobs up -16px)
    walk_configs = [
        (-18, 0.98,   0,  18, 1.02,   0,   0, 1.05),
        (  8, 0.88, -25,   0, 1.00,   0, -16, 0.88),
        ( 18, 1.02,   0, -18, 0.98,   0,   0, 1.05),
        (  0, 1.00,   0,   8, 0.88, -25, -16, 0.88),
    ]

    target_h = 54
    hi_frames = [render_hi_res_frame(*cfg) for cfg in walk_configs]
    
    # Scale each frame to 54px target height with Lanczos antialiasing then clean binary alpha
    scaled_frames_r = []
    for hf in hi_frames:
        fw, fh = hf.size
        sw = int(fw * (target_h / fh))
        sc = hf.resize((sw, target_h), Image.LANCZOS)
        scaled_frames_r.append(clean_binary_alpha(sc))

    # Save Walk Right frames
    for i, sf in enumerate(scaled_frames_r):
        sf.save(os.path.join(FRAMES_DIR, f"walk_r{i+1}.png"))
        sf.save(os.path.join(FRAMES_DIR, f"walk_{i+1}.png"))

    # Save Walk Left frames (horizontally flipped for walking left out of screen)
    for i, sf in enumerate(scaled_frames_r):
        flipped = clean_binary_alpha(sf.transpose(Image.FLIP_LEFT_RIGHT))
        flipped.save(os.path.join(FRAMES_DIR, f"walk_l{i+1}.png"))

    # Action frames
    # 1. Stand aim: neutral standing pose
    stand_hi = render_hi_res_frame(0, 1.0, 0, 0, 1.0, 0, 0, 1.0)
    sw = int(stand_hi.width * (target_h / stand_hi.height))
    stand = clean_binary_alpha(stand_hi.resize((sw, target_h), Image.LANCZOS))
    stand.save(os.path.join(FRAMES_DIR, "stand_aim.png"))

    # 2. Jump up: airborne pose with contracted ground shadow
    jump_hi = render_hi_res_frame(-8, 0.92, -15, 8, 0.92, -15, -45, 0.55)
    jw = int(jump_hi.width * (target_h / jump_hi.height))
    jump = clean_binary_alpha(jump_hi.resize((jw, target_h), Image.LANCZOS))
    jump.save(os.path.join(FRAMES_DIR, "jump_up.png"))

    # 3. Nose down: rotate so nose points straight down
    # Master base for rotation
    bw = int(mw * (target_h / mh))
    base_clean = clean_binary_alpha(master.resize((bw, target_h), Image.LANCZOS))
    nose_rot = base_clean.rotate(-85, resample=Image.BICUBIC, expand=True)
    nr_w, nr_h = nose_rot.size
    nd_can = Image.new("RGBA", (nr_w + 10, nr_h + 10), (255, 255, 255, 0))
    nd_can.paste(nose_rot, (5, 5), nose_rot)
    nose_down = clean_binary_alpha(nd_can)
    nose_down.save(os.path.join(FRAMES_DIR, "nose_down.png"))

    # 4. Nose impact: squashed on the X button
    ni_w, ni_h = nose_down.size
    nose_impact = clean_binary_alpha(nose_down.resize((int(ni_w * 1.25), int(ni_h * 0.85)), Image.LANCZOS))
    nose_impact.save(os.path.join(FRAMES_DIR, "nose_impact.png"))

    # 5. Celebrate: victory bounce
    celeb_hi = render_hi_res_frame(-15, 1.02, 0, 15, 1.02, 0, -10, 1.05)
    cw_celeb = int(celeb_hi.width * (target_h / celeb_hi.height))
    celeb = clean_binary_alpha(celeb_hi.resize((cw_celeb, target_h), Image.LANCZOS))
    celeb.save(os.path.join(FRAMES_DIR, "celebrate.png"))

    print("✅ Successfully generated 100% seamless, true walking-legged 3D cartoon sprites!")

if __name__ == "__main__":
    build_3d_sprites()
