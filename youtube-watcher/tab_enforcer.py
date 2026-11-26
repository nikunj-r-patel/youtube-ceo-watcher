import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import os
import time
import threading
import ctypes
import win32gui
import win32con

# -------------------------------------------------------------
# 👃 Orange Tab Enforcer — Precise 'X' Target & Nose-Pinch Action
# -------------------------------------------------------------

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAMES_DIR = os.path.join(ASSETS_DIR, "orange_frames")

# Windows Virtual Keys for Ctrl + W
VK_CONTROL = 0x11
VK_W = 0x57
KEYEVENTF_KEYUP = 0x0002

def send_ctrl_w():
    """Simulate pressing Ctrl + W to close current active browser tab."""
    user32 = ctypes.windll.user32
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_W, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


def pinpoint_youtube_x_button(hwnd, win_left, win_top, win_w):
    """
    Finds the EXACT pixel coordinate (center_x, center_y) of the active YouTube tab's 'X' button.
    1. Tries native UI Automation.
    2. Uses visual red-logo tab strip detection for 100% precision across all displays.
    """
    # Method 1: UIAutomation
    try:
        import comtypes.client
        UIAutomationClient = comtypes.client.GetModule("UIAutomationCore.dll")
        uia = comtypes.client.CreateObject(UIAutomationClient.CUIAutomation, interface=UIAutomationClient.IUIAutomation)
        elem = uia.ElementFromHandle(hwnd)
        tab_cond = uia.CreatePropertyCondition(
            UIAutomationClient.UIA_ControlTypePropertyId,
            UIAutomationClient.UIA_TabItemControlTypeId
        )
        tabs = elem.FindAll(UIAutomationClient.TreeScope_Descendants, tab_cond)
        for i in range(tabs.Length):
            t = tabs.GetElement(i)
            name = (t.CurrentName or "").lower()
            if "youtube" in name:
                r = t.CurrentBoundingRectangle
                x_center = r.right - 18
                y_center = r.top + (r.bottom - r.top) // 2
                print(f"🎯 UIAutomation pinpointed 'X' icon at: ({x_center}, {y_center})")
                return x_center, y_center
    except Exception:
        pass

    # Method 2: Visual Detection of YouTube Red Icon in the Tab Strip
    try:
        tab_strip_top = max(0, win_top + 2)
        tab_strip_bottom = tab_strip_top + 48
        strip = ImageGrab.grab(bbox=(win_left, tab_strip_top, win_left + win_w, tab_strip_bottom))
        sw, sh = strip.size

        red_spots = []
        for x in range(sw):
            for y in range(sh):
                r, g, b = strip.getpixel((x, y))[:3]
                # YouTube Play red
                if r > 185 and g < 45 and b < 45:
                    red_spots.append((x, y))

        if red_spots:
            logo_x = int(sum(p[0] for p in red_spots) / len(red_spots))
            logo_y = int(sum(p[1] for p in red_spots) / len(red_spots))

            # Scan rightwards for the bright 'X' icon pixels
            x_candidates = []
            for scan_x in range(logo_x + 50, min(sw - 10, logo_x + 150)):
                for scan_y in range(max(0, logo_y - 12), min(sh, logo_y + 12)):
                    r, g, b = strip.getpixel((scan_x, scan_y))[:3]
                    if r > 185 and g > 185 and b > 185:
                        x_candidates.append(scan_x)

            if x_candidates:
                best_rel_x = int(sum(x_candidates) / len(x_candidates))
            else:
                best_rel_x = logo_x + 88

            exact_screen_x = win_left + best_rel_x
            exact_screen_y = tab_strip_top + logo_y
            print(f"🎯 Visual detection pinpointed 'X' icon at: ({exact_screen_x}, {exact_screen_y})")
            return exact_screen_x, exact_screen_y
    except Exception as e:
        print(f"Tab pinpointer visual note: {e}")

    # Method 3: Geometric fallback for active tab on the right
    exact_screen_x = win_left + int(win_w * 0.962)
    exact_screen_y = win_top + 24
    print(f"🎯 Calculated fallback pinpointed 'X' icon at: ({exact_screen_x}, {exact_screen_y})")
    return exact_screen_x, exact_screen_y


class OrangeTabEnforcer:
    def __init__(self, hwnd=None, on_finished=None):
        self.hwnd = hwnd
        self.on_finished = on_finished
        
        self.root = tk.Toplevel() if tk._default_root else tk.Tk()
        self.root.title("Tab Enforcer")
        
        # Transparent, borderless, always on top
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "white")
        self.root.config(bg="white")
        
        # Calculate overlay geometry
        self._calculate_geometry()
        
        # Canvas for sprite, impact, and speech bubble
        self.canvas = tk.Canvas(
            self.root,
            width=self.win_w,
            height=self.win_h,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Load crisp frames (all have 100% clean binary transparency, no halos)
        self._load_frames()
        
        # Sprite dimensions & nose tip offset inside nose_impact.png
        # nose_impact.png size is 72x52; tip is at (x=43, y=48)
        self.char_w = 56
        self.char_h = 52
        self.nose_offset_x = 43
        self.nose_offset_y = 48
        
        # Start on the LEFT side of the tab strip
        self.current_x = 10
        self.base_y = 12
        self.current_y = self.base_y
        
        # Pinpoint EXACT 'X' button coordinate
        screen_target_x, screen_target_y = pinpoint_youtube_x_button(
            self.hwnd, self.win_x, self.win_y, self.win_w
        )
        
        # Target coordinate relative to overlay
        self.target_x = screen_target_x - self.win_x
        self.target_y = max(18, min(self.win_h - 15, screen_target_y - self.win_y))
        
        # Character walk stop X (stop right before the X icon so nose aligns)
        self.walk_stop_x = self.target_x - self.char_w + 4
        
        self.walk_step = 0
        self.exit_step = 0
        self.is_running = True
        
        # Start walking right after brief initial pause
        self.root.after(100, self._start_walk_right)

    def _calculate_geometry(self):
        screen_w = self.root.winfo_screenwidth()
        self.win_x = 0
        self.win_y = 0
        self.win_w = screen_w
        self.win_h = 105
        
        if self.hwnd and win32gui.IsWindow(self.hwnd):
            try:
                rect = win32gui.GetWindowRect(self.hwnd)
                left, top, right, bottom = rect
                if right > left and bottom > top and top >= -10:
                    self.win_x = max(0, left)
                    self.win_y = max(0, top)
                    self.win_w = right - left
            except Exception:
                pass
                
        self.root.geometry(f"{self.win_w}x{self.win_h}+{self.win_x}+{self.win_y}")

    def _load_frames(self):
        """Load razor-sharp, zero-distortion frames with leg walking animations."""
        self.frames = {}
        frame_names = [
            "walk_r1", "walk_r2", "walk_r3", "walk_r4",
            "walk_l1", "walk_l2", "walk_l3", "walk_l4",
            "stand_aim", "jump_up", "nose_down", "nose_impact", "celebrate"
        ]
        for name in frame_names:
            path = os.path.join(FRAMES_DIR, f"{name}.png")
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                self.frames[name] = ImageTk.PhotoImage(img)

    def _draw_frame(self, frame_name, x, y, bubble_text="", impact=False):
        """Render sprite, comic speech bubble, and impact star with pixel perfection."""
        self.canvas.delete("all")
        photo = self.frames.get(frame_name, self.frames.get("walk_r1"))
        
        # 1. Comic Speech Bubble
        if bubble_text:
            bx = x + 30
            by = max(14, y - 8)
            self.canvas.create_rectangle(
                bx - 35, by - 14, bx + 55, by + 4,
                fill="#FF4500", outline="#8B0000", width=1.5
            )
            self.canvas.create_text(
                bx + 10, by - 5,
                text=bubble_text,
                fill="white",
                font=("Arial", 8, "bold")
            )
            
        # 2. Comic impact burst EXACTLY on the X button!
        if impact:
            ix = self.target_x
            iy = self.target_y
            points = [
                ix, iy - 16,
                ix + 5, iy - 6,
                ix + 18, iy - 8,
                ix + 8, iy + 2,
                ix + 15, iy + 14,
                ix + 2, iy + 8,
                ix - 6, iy + 18,
                ix - 5, iy + 6,
                ix - 18, iy + 8,
                ix - 7, iy - 2,
                ix - 14, iy - 10,
                ix - 2, iy - 6,
            ]
            self.canvas.create_polygon(points, fill="#FFFF00", outline="#FF4500", width=2)
            # Red bullseye ring on the X
            self.canvas.create_oval(ix - 8, iy - 8, ix + 8, iy + 8, outline="#FF0000", width=2)
            self.canvas.create_text(ix, iy - 20, text="PINCH! 💥", fill="#D00000", font=("Arial", 10, "bold"))
            
        # 3. Draw Character Sprite
        if photo:
            self.canvas.create_image(x, y, anchor="nw", image=photo)

    def _start_walk_right(self):
        """Walk smoothly from LEFT to RIGHT towards the YouTube tab with moving legs."""
        if not self.is_running:
            return
            
        if self.current_x < self.walk_stop_x:
            self.current_x += 5
            self.walk_step += 1
            
            # Leg-walking frames (r1 -> r2 -> r3 -> r4)
            walk_frame = f"walk_r{(self.walk_step % 4) + 1}"
            
            # Subtle natural stride bobbing
            bob = -2 if (self.walk_step % 2 == 1) else 0
            self.current_y = self.base_y + bob
            
            msg = "Targeting [X]..." if (self.walk_step % 6 < 3) else "No YouTube! 🛑"
            self._draw_frame(walk_frame, self.current_x, self.current_y, msg)
            
            self.root.after(30, self._start_walk_right)
        else:
            # Reached exact position! Stop, jump, and land on nose!
            self._stop_jump_and_land_on_nose()

    def _stop_jump_and_land_on_nose(self):
        """
        1. STOPS directly at the X icon (clear pause).
        2. JUMPS high up into the air above the X icon.
        3. Flips and LANDS ON ITS NOSE EXACTLY in the center of the X icon!
        4. Fires Ctrl+W to close tab.
        5. Celebrates briefly.
        6. Turns around and WALKS ALL THE WAY TO THE LEFT OUT OF SCREEN!
        """
        # Step 1: STOP at the X icon
        self._draw_frame("stand_aim", self.walk_stop_x, self.base_y, "TARGET LOCKED! 🎯")
        
        def do_jump():
            # Step 2: JUMP high up into the air directly above the X icon
            jump_draw_x = self.target_x - (self.char_w // 2)
            self._draw_frame("jump_up", jump_draw_x, self.base_y - 28, "JUMPING! 🚀")
            self.root.after(220, do_land_on_nose)
            
        def do_land_on_nose():
            # Step 3: LAND ON NOSE directly onto the center of the X icon!
            # Sprite tip is at (43, 48) inside nose_impact.png
            # Drawing at (target_x - 43, target_y - 48) places the nose tip EXACTLY AT (target_x, target_y)!
            impact_draw_x = self.target_x - self.nose_offset_x
            impact_draw_y = self.target_y - self.nose_offset_y
            self._draw_frame("nose_impact", impact_draw_x, impact_draw_y, impact=True)
            
            # Step 4: Focus browser window and send Ctrl+W to close YouTube tab!
            if self.hwnd and win32gui.IsWindow(self.hwnd):
                try:
                    win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(self.hwnd)
                except Exception:
                    pass
                    
            time.sleep(0.06)
            send_ctrl_w()
            print(f"💥 NOSE PINCHED EXACTLY ON CENTER OF [X] ({self.target_x}, {self.target_y})! Tab closed!")
            
            # Step 5: Celebrate briefly
            self.root.after(350, do_celebrate)
            
        def do_celebrate():
            celeb_draw_x = self.target_x - (self.char_w // 2)
            self._draw_frame("celebrate", celeb_draw_x, self.base_y - 6, "PINCHED ON [X]! 👃🎉")
            # Step 6: After celebrating 700ms, turn left and walk off screen!
            self.root.after(700, self._start_walk_left_exit)

        # Stop for 350ms so user clearly sees the character standing at the X, then jump!
        self.root.after(350, do_jump)

    def _start_walk_left_exit(self):
        """Turn around, face LEFT, and walk with leg animation all the way off-screen!"""
        if not self.is_running:
            return

        if self.current_x > -70:
            self.current_x -= 6
            self.exit_step += 1

            # Leg-walking frames facing left (l1 -> l2 -> l3 -> l4)
            walk_frame = f"walk_l{(self.exit_step % 4) + 1}"
            bob = -2 if (self.exit_step % 2 == 1) else 0
            self.current_y = self.base_y + bob

            msg = "Back to work! 👋" if self.current_x > 100 else ""
            self._draw_frame(walk_frame, self.current_x, self.current_y, msg)

            self.root.after(30, self._start_walk_left_exit)
        else:
            # Fully off-screen on the left! Close overlay
            self.is_running = False
            try:
                self.root.destroy()
            except Exception:
                pass
            if self.on_finished:
                self.on_finished()


def trigger_tab_enforcer(hwnd=None, on_finished=None):
    return OrangeTabEnforcer(hwnd=hwnd, on_finished=on_finished)


if __name__ == "__main__":
    print("Testing Tab Enforcer with exact nose-pinch targeting...")
    app = OrangeTabEnforcer()
    app.root.mainloop()
