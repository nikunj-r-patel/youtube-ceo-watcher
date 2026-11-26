import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import threading
import ctypes
import win32gui
import win32con

# -------------------------------------------------------------
# 🏃 Orange Tab Enforcer — Walks across tab bar & closes YouTube
# -------------------------------------------------------------

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAMES_DIR = os.path.join(ASSETS_DIR, "orange_frames")

# Windows Virtual Keys for Ctrl + W
VK_CONTROL = 0x11
VK_W = 0x57
KEYEVENTF_KEYUP = 0x0002

def send_ctrl_w():
    """Simulate pressing Ctrl + W to close current browser tab."""
    user32 = ctypes.windll.user32
    # Key down
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_W, 0, 0, 0)
    time.sleep(0.05)
    # Key up
    user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


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
        
        # Get browser window geometry
        self._calculate_geometry()
        
        # Canvas for sprite and speech bubble
        self.canvas = tk.Canvas(
            self.root,
            width=self.win_w,
            height=self.win_h,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Load sprite animation frames
        self._load_frames()
        
        # Walk state
        # Starts on far right of the tab bar
        self.current_x = self.win_w - 70
        # In typical browsers with tabs open, active YouTube tab is near the right section
        # We walk towards YouTube tab close button (approx 220px to 320px from right)
        self.target_x = max(180, self.win_w - 260)
        self.base_y = 12   # Height aligned on top of the tab strip
        self.current_y = self.base_y
        
        self.walk_step = 0
        self.is_running = True
        
        # Character canvas items
        self.char_item = None
        self.bubble_item = None
        self.text_item = None
        
        # Start walking animation loop after small delay
        self.root.after(200, self._start_walk)

    def _calculate_geometry(self):
        """Align overlay to top of the browser window or top of screen."""
        screen_w = self.root.winfo_screenwidth()
        
        self.win_x = 0
        self.win_y = 0
        self.win_w = screen_w
        self.win_h = 75  # Height covering tab strip area
        
        if self.hwnd and win32gui.IsWindow(self.hwnd):
            try:
                rect = win32gui.GetWindowRect(self.hwnd)
                left, top, right, bottom = rect
                if right > left and bottom > top and top >= -10:
                    self.win_x = max(0, left)
                    self.win_y = max(0, top)
                    self.win_w = right - left
            except Exception as e:
                print(f"Geometry error: {e}")
                
        self.root.geometry(f"{self.win_w}x{self.win_h}+{self.win_x}+{self.win_y}")

    def _load_frames(self):
        """Load pre-generated frames for the orange character."""
        self.frames = {}
        for name in ["walk_1", "walk_2", "walk_3", "walk_4", "stomp_jump", "stomp_squash", "celebrate"]:
            path = os.path.join(FRAMES_DIR, f"{name}.png")
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                self.frames[name] = ImageTk.PhotoImage(img)
            else:
                # Fallback to base character if frame missing
                base_path = os.path.join(ASSETS_DIR, "orange_character.png")
                img = Image.open(base_path).convert("RGBA").resize((42, 40), Image.LANCZOS)
                self.frames[name] = ImageTk.PhotoImage(img)

    def _draw_character(self, frame_name, x, y, bubble_text=""):
        """Draw character sprite and optional speech bubble."""
        self.canvas.delete("all")
        photo = self.frames.get(frame_name, self.frames.get("walk_1"))
        
        # Draw speech bubble if provided
        if bubble_text:
            bx = x - 25
            by = max(4, y - 2)
            self.canvas.create_rectangle(
                bx - 40, by - 12, bx + 45, by + 4,
                fill="#FF4500", outline="#8B0000", width=1.5
            )
            self.canvas.create_text(
                bx + 2, by - 4,
                text=bubble_text,
                fill="white",
                font=("Arial", 7, "bold")
            )
            
        # Draw character
        self.canvas.create_image(x, y, anchor="nw", image=photo)

    def _start_walk(self):
        """Walk leftwards from current_x to target_x."""
        if not self.is_running:
            return
            
        if self.current_x > self.target_x:
            # Still walking towards the tab
            self.current_x -= 5  # Walk speed (pixels per tick)
            self.walk_step += 1
            
            # Cycle through walk frames: 1 -> 2 -> 3 -> 4
            walk_frame = f"walk_{(self.walk_step % 4) + 1}"
            
            # Subtle bobbing up and down
            bob = -2 if (self.walk_step % 2 == 0) else 0
            self.current_y = self.base_y + bob
            
            # Show walking message
            msg = "Caught ya! 🛑" if self.walk_step > 8 else "On my way..."
            self._draw_character(walk_frame, self.current_x, self.current_y, msg)
            
            # Next step in 35ms (approx 30fps)
            self.root.after(35, self._start_walk)
        else:
            # Arrived at the tab! Perform the stomp/close action
            self._perform_stomp()

    def _perform_stomp(self):
        """Jump up and slam down on the X button, then close tab."""
        # Step 1: Jump up
        self._draw_character("stomp_jump", self.target_x, self.base_y - 12, "CLICKING [X]!")
        
        def slam_down():
            # Step 2: Slam down onto the X button
            self._draw_character("stomp_squash", self.target_x, self.base_y + 4, "STOMP!! 💥")
            
            # Step 3: Bring window to foreground and close active tab with Ctrl+W
            if self.hwnd and win32gui.IsWindow(self.hwnd):
                try:
                    win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(self.hwnd)
                except Exception:
                    pass
            
            time.sleep(0.08)
            send_ctrl_w()
            print("💥 Orange character stomped the 'X' button! YouTube tab closed!")
            
            # Step 4: Celebrate
            self.root.after(250, self._celebrate)
            
        self.root.after(180, slam_down)

    def _celebrate(self):
        """Victory pose and cleanup."""
        self._draw_character("celebrate", self.target_x, self.base_y - 4, "TAB CLOSED! 🎉")
        
        def finish():
            self.is_running = False
            try:
                self.root.destroy()
            except Exception:
                pass
            if self.on_finished:
                self.on_finished()
                
        # Stay on screen celebrating for 1.2s then finish
        self.root.after(1200, finish)


def trigger_tab_enforcer(hwnd=None, on_finished=None):
    """Convenience function to trigger the enforcer."""
    enforcer = OrangeTabEnforcer(hwnd=hwnd, on_finished=on_finished)
    return enforcer


# -----------------------------------------------
# Quick standalone test
# -----------------------------------------------
if __name__ == "__main__":
    print("🏃 Testing Orange Tab Enforcer...")
    print("👀 Watch the top of your screen for the walking character!")
    app = OrangeTabEnforcer()
    app.root.mainloop()
