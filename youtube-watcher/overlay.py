import tkinter as tk
from PIL import Image, ImageTk
import os
import threading
import signal
import sys
import math
import ctypes
import ctypes.wintypes

# -----------------------------------------------
# 🪟 CEO Cartoon Overlay — with Taskbar Detection
# -----------------------------------------------

ASSETS_DIR    = os.path.join(os.path.dirname(__file__), "assets")
CARTOON_PATH  = os.path.join(ASSETS_DIR, "cartoon.png")

WINDOW_WIDTH  = 340
WINDOW_HEIGHT = 440
SLIDE_SPEED   = 18

def get_work_area():
    """Get the usable desktop area excluding the Windows taskbar."""
    try:
        rect = ctypes.wintypes.RECT()
        # SPI_GETWORKAREA = 0x0030
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
        return rect.left, rect.top, rect.right, rect.bottom
    except Exception:
        # Fallback to standard 1080p if failed
        return 0, 0, 1920, 1040


class CEOOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CEO Watcher")

        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "white")
        self.root.config(bg="white")

        signal.signal(signal.SIGINT, self._on_exit)
        signal.signal(signal.SIGTERM, self._on_exit)

        self.is_visible   = False
        self.is_animating = False
        self.is_speaking  = False
        self._anim_id     = None
        self._anim_step   = 0

        # Calculate exact position to sit right ABOVE the Windows Taskbar
        _, _, work_w, work_h = get_work_area()
        screen_h = self.root.winfo_screenheight()

        self.hidden_y = screen_h + 50
        # Position bottom of window 4 pixels above the taskbar
        self.shown_y  = work_h - WINDOW_HEIGHT - 4
        self.pos_x    = work_w - WINDOW_WIDTH - 10

        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{self.pos_x}+{self.hidden_y}")
        self.canvas_height = 360  # leaves 80px for speech bubble

        # Pre-load base cartoon image
        try:
            raw = Image.open(CARTOON_PATH).convert("RGBA")
            self.base_img = raw.resize((WINDOW_WIDTH, self.canvas_height), Image.LANCZOS)
            self._frames = self._build_zoom_frames()
        except Exception as e:
            print(f"Image load error: {e}")
            self.base_img = None
            self._frames  = []

        self._load_ui()
        self._poll_signal()

    def _build_zoom_frames(self):
        """Pre-build animation frames for face zoom pulse."""
        frames = []
        steps  = 20
        img_w, img_h = self.base_img.size
        face_bottom  = int(img_h * 0.65)

        for i in range(steps):
            t      = i / steps
            zoom   = 0.30 * math.sin(t * math.pi)

            margin_x = int(img_w * zoom * 0.15)
            margin_y = int(face_bottom * zoom * 0.10)

            crop_box = (
                margin_x,
                margin_y,
                img_w - margin_x,
                face_bottom - margin_y
            )
            cropped  = self.base_img.crop(crop_box)
            resized  = cropped.resize((img_w, self.canvas_height), Image.LANCZOS)
            frames.append(resized)

        return frames

    def _poll_signal(self):
        self.root.after(500, self._poll_signal)

    def _on_exit(self, *args):
        print("\n👋 CEO is leaving... Goodbye!")
        self.root.quit()
        sys.exit(0)

    def _load_ui(self):
        """Build canvas + speech bubble."""
        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=self.canvas_height,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(fill="x", expand=False)
        self.canvas.bind("<Button-1>", lambda e: self.slide_out())

        # Draw static image initially
        self._draw_frame(self.base_img)

        # Container for the speech bubble with border
        bubble_frame = tk.Frame(
            self.root,
            bg="#8B0000",   # Dark red border
            padx=2, pady=2
        )
        bubble_frame.pack(fill="x", padx=4, pady=(2, 0))

        # Yellow speech bubble
        self.text_label = tk.Label(
            bubble_frame,
            text="",
            bg="#FFD700",
            fg="#8B0000",
            font=("Arial", 9, "bold"),
            wraplength=310,
            justify="center",
            pady=8,
            padx=6
        )
        self.text_label.pack(fill="both", expand=True)
        self.text_label.bind("<Button-1>", lambda e: self.slide_out())
        bubble_frame.bind("<Button-1>", lambda e: self.slide_out())

    def _draw_frame(self, img):
        """Draw PIL image on canvas."""
        if img is None:
            return
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

    def _animate_speaking(self):
        """Face zoom pulse while speaking."""
        if not self.is_speaking:
            self._draw_frame(self.base_img)
            return

        if self._frames:
            frame_idx = self._anim_step % len(self._frames)
            self._draw_frame(self._frames[frame_idx])

        self._anim_step += 1
        self._anim_id = self.root.after(50, self._animate_speaking)

    def start_animation(self):
        self.is_speaking  = True
        self._anim_step   = 0
        self._animate_speaking()

    def stop_animation(self):
        self.is_speaking = False
        if self._anim_id:
            self.root.after_cancel(self._anim_id)
            self._anim_id = None
        self._draw_frame(self.base_img)

    def set_speech_text(self, text):
        short = text[:95] + "..." if len(text) > 95 else text
        self.text_label.config(text=f'"{short}"')

    def slide_in(self, speech_text="", on_complete=None):
        if self.is_animating or self.is_visible:
            return
        self.is_animating = True
        self.set_speech_text(speech_text)
        current_y = [self.hidden_y]

        def animate():
            if current_y[0] > self.shown_y:
                current_y[0] -= SLIDE_SPEED
                self.root.geometry(
                    f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{self.pos_x}+{current_y[0]}")
                self.root.after(10, animate)
            else:
                self.root.geometry(
                    f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{self.pos_x}+{self.shown_y}")
                self.is_visible   = True
                self.is_animating = False
                if on_complete:
                    on_complete()

        animate()

    def slide_out(self):
        self.stop_animation()
        if self.is_animating or not self.is_visible:
            return
        self.is_animating = True
        current_y = [self.shown_y]

        def animate():
            if current_y[0] < self.hidden_y:
                current_y[0] += SLIDE_SPEED
                self.root.geometry(
                    f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{self.pos_x}+{current_y[0]}")
                self.root.after(10, animate)
            else:
                self.root.geometry(
                    f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{self.pos_x}+{self.hidden_y}")
                self.is_visible   = False
                self.is_animating = False

        animate()

    def show_with_voice(self, speech_text, speak_fn):
        def after_slide_in():
            self.start_animation()

            def speak_then_slideout():
                speak_fn(speech_text)
                self.root.after(0, self.stop_animation)
                self.root.after(800, self.slide_out)

            thread = threading.Thread(target=speak_then_slideout, daemon=True)
            thread.start()

        self.slide_in(speech_text, on_complete=after_slide_in)

    def run(self):
        self.root.mainloop()

    def stop(self):
        self.root.quit()


if __name__ == "__main__":
    from speech import speak, get_random_line

    overlay = CEOOverlay()

    def trigger():
        line = get_random_line()
        print(f"\n😤 CEO says: {line}")
        overlay.show_with_voice(line, speak)

    overlay.root.after(1000, trigger)
    print("Testing taskbar positioning...")
    overlay.run()
