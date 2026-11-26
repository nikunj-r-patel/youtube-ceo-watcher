import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import threading
import ctypes
import win32gui
import win32con

# -------------------------------------------------------------
# 👃 Orange Tab Enforcer — Left-to-Right Walk, Nose-Pinch & Left Exit
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


def locate_youtube_tab_x(hwnd, win_left, win_w):
    """
    Find the exact screen X coordinate of the YouTube tab's 'X' close button.
    Tries native UI Automation first; falls back to active tab geometry.
    """
    try:
        import comtypes.client
        UIAutomationClient = comtypes.client.GetModule("UIAutomationCore.dll")
        uia = comtypes.client.CreateObject(UIAutomationClient.CUIAutomation, interface=UIAutomationClient.IUIAutomation)
        element = uia.ElementFromHandle(hwnd)
        
        tab_cond = uia.CreatePropertyCondition(
            UIAutomationClient.UIA_ControlTypePropertyId, 
            UIAutomationClient.UIA_TabItemControlTypeId
        )
        tabs = element.FindAll(UIAutomationClient.TreeScope_Descendants, tab_cond)
        
        for i in range(tabs.Length):
            t = tabs.GetElement(i)
            name = t.CurrentName or ""
            if "youtube" in name.lower():
                rect = t.CurrentBoundingRectangle
                target_screen_x = rect.right - 18
                print(f"🎯 UIAutomation found YouTube Tab '{name[:30]}' at X={target_screen_x}")
                return target_screen_x
    except Exception:
        pass
        
    # Standard multi-tab layout fallback (YouTube tab around ~78% of width)
    target_screen_x = win_left + max(200, win_w - 240)
    print(f"🎯 Using calculated YouTube Tab 'X' position: X={target_screen_x}")
    return target_screen_x


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
        
        # Load crisp leg-animated frames (clean 1-bit transparency, zero halos)
        self._load_frames()
        
        # Sprite dimensions
        self.char_w = 56
        self.char_h = 52
        
        # Start on the LEFT side of the tab strip
        self.current_x = 10
        self.base_y = 12
        self.current_y = self.base_y
        
        # Calculate destination right at the YouTube tab X button
        target_screen_x = locate_youtube_tab_x(self.hwnd, self.win_x, self.win_w)
        self.target_x = max(80, target_screen_x - self.win_x - self.char_w + 10)
        
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
        self.win_h = 100
        
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
        """Render sprite and optional impact / bubble without any artifacts."""
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
            
        # 2. Comic impact star when nose slams into the X button!
        if impact:
            ix = x + 24
            iy = y + self.char_h - 6
            points = [
                ix, iy - 14,
                ix + 5, iy - 5,
                ix + 16, iy - 7,
                ix + 7, iy + 2,
                ix + 14, iy + 12,
                ix + 2, iy + 7,
                ix - 5, iy + 16,
                ix - 4, iy + 5,
                ix - 16, iy + 7,
                ix - 6, iy - 2,
                ix - 12, iy - 9,
                ix - 2, iy - 5,
            ]
            self.canvas.create_polygon(points, fill="#FFFF00", outline="#FF4500", width=2)
            self.canvas.create_text(ix, iy - 18, text="SLAM! 💥", fill="#D00000", font=("Arial", 10, "bold"))
            
        # 3. Draw Character Sprite
        if photo:
            self.canvas.create_image(x, y, anchor="nw", image=photo)

    def _start_walk_right(self):
        """Walk smoothly from LEFT to RIGHT towards the YouTube tab with leg animation."""
        if not self.is_running:
            return
            
        if self.current_x < self.target_x:
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
            # Reached exact position! Stop, jump, land on nose!
            self._stop_jump_and_land_on_nose()

    def _stop_jump_and_land_on_nose(self):
        """
        1. STOPS directly at the X icon (clear pause).
        2. JUMPS high up into the air above the X icon.
        3. Flips and LANDS ON ITS NOSE directly on the X icon!
        4. Fires Ctrl+W to close tab.
        5. Celebrates briefly.
        6. Turns around and WALKS ALL THE WAY TO THE LEFT OUT OF SCREEN!
        """
        # Step 1: STOP at the X icon
        self._draw_frame("stand_aim", self.target_x, self.base_y, "STOPPING AT [X]! 🛑")
        
        def do_jump():
            # Step 2: JUMP high up into the air
            self._draw_frame("jump_up", self.target_x, self.base_y - 28, "JUMPING! 🚀")
            self.root.after(220, do_land_on_nose)
            
        def do_land_on_nose():
            # Step 3: LAND ON NOSE directly onto the X icon (nose pointing straight down)
            self._draw_frame("nose_impact", self.target_x - 4, self.base_y + 2, impact=True)
            
            # Step 4: Focus browser window and send Ctrl+W to close YouTube tab!
            if self.hwnd and win32gui.IsWindow(self.hwnd):
                try:
                    win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(self.hwnd)
                except Exception:
                    pass
                    
            time.sleep(0.06)
            send_ctrl_w()
            print("💥 NOSE LANDED ON [X] BUTTON! YouTube tab closed!")
            
            # Step 5: Celebrate briefly
            self.root.after(350, do_celebrate)
            
        def do_celebrate():
            self._draw_frame("celebrate", self.target_x, self.base_y - 6, "CLOSED WITH NOSE! 👃🎉")
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
    print("Testing Tab Enforcer with left exit...")
    app = OrangeTabEnforcer()
    app.root.mainloop()
