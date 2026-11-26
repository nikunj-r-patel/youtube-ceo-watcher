import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import threading
import ctypes
import win32gui
import win32con

# -------------------------------------------------------------
# 👃 Orange Tab Enforcer — Left-to-Right Walk & Nose-Pinch Tab Closer
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
                # Close 'X' button is ~18px from the right edge of the tab
                target_screen_x = rect.right - 18
                print(f"🎯 UIAutomation found YouTube Tab '{name[:30]}' at X={target_screen_x}")
                return target_screen_x
    except Exception as e:
        pass
        
    # Smart Fallback: in typical multi-tab sessions, active tab is in the right 75-80% zone
    # Tab 'X' is roughly 240px from the right edge of the window
    target_screen_x = win_left + max(200, win_w - 240)
    print(f"🎯 Using calculated YouTube Tab 'X' position: X={target_screen_x}")
    return target_screen_x


class OrangeTabEnforcer:
    def __init__(self, hwnd=None, on_finished=None):
        self.hwnd = hwnd
        self.on_finished = on_finished
        
        self.root = tk.Toplevel() if tk._default_root else tk.Tk()
        self.root.title("Tab Enforcer")
        
        # Completely transparent, borderless, always on top
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "white")
        self.root.config(bg="white")
        
        # Calculate window and tab bar positions
        self._calculate_geometry()
        
        # Canvas for sprite, impact star, and speech bubble
        self.canvas = tk.Canvas(
            self.root,
            width=self.win_w,
            height=self.win_h,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Load crisp animation frames
        self._load_frames()
        
        # Character dimensions (approx 56x52px)
        self.char_w = 56
        self.char_h = 52
        
        # START ON THE LEFT SIDE of the tab bar!
        self.current_x = 10
        self.base_y = 10   # Natural height right along the tab line
        self.current_y = self.base_y
        
        # TARGET: Where the nose tip should pinch the 'X' button!
        # The nose is on the RIGHT side of the sprite (+char_w)
        # So character stops when (current_x + char_w - 4) reaches target_x
        target_screen_x = locate_youtube_tab_x(self.hwnd, self.win_x, self.win_w)
        # Convert screen X to overlay-relative X
        self.target_x = max(80, target_screen_x - self.win_x - self.char_w + 6)
        
        self.walk_step = 0
        self.is_running = True
        
        # Start walking animation loop after small initial pause
        self.root.after(150, self._start_walk)

    def _calculate_geometry(self):
        screen_w = self.root.winfo_screenwidth()
        self.win_x = 0
        self.win_y = 0
        self.win_w = screen_w
        self.win_h = 90  # Generous height covering tab strip and jump room
        
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
        """Load crisp frames with anti-aliasing."""
        self.frames = {}
        frame_names = [
            "walk_1", "walk_2", "walk_3", "walk_4", 
            "jump_aim", "nose_dive", "nose_pinch", "celebrate"
        ]
        for name in frame_names:
            path = os.path.join(FRAMES_DIR, f"{name}.png")
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                self.frames[name] = ImageTk.PhotoImage(img)
            else:
                base_path = os.path.join(ASSETS_DIR, "orange_character_clean.png")
                img = Image.open(base_path).convert("RGBA").resize((56, 52), Image.LANCZOS)
                self.frames[name] = ImageTk.PhotoImage(img)

    def _draw_frame(self, frame_name, x, y, bubble_text="", impact=False):
        """Render sprite, optional comic speech bubble, and impact star."""
        self.canvas.delete("all")
        photo = self.frames.get(frame_name, self.frames.get("walk_1"))
        
        # 1. Comic Speech Bubble
        if bubble_text:
            bx = x + 35
            by = max(14, y - 6)
            self.canvas.create_rectangle(
                bx - 35, by - 14, bx + 50, by + 4,
                fill="#FF4500", outline="#8B0000", width=1.5
            )
            self.canvas.create_text(
                bx + 7, by - 5,
                text=bubble_text,
                fill="white",
                font=("Arial", 8, "bold")
            )
            
        # 2. Impact star right at the nose tip!
        if impact:
            nose_x = x + self.char_w - 2
            nose_y = y + self.char_h - 10
            # Bright yellow/orange impact star
            points = [
                nose_x, nose_y - 12,
                nose_x + 4, nose_y - 4,
                nose_x + 14, nose_y - 6,
                nose_x + 6, nose_y + 2,
                nose_x + 12, nose_y + 10,
                nose_x + 2, nose_y + 6,
                nose_x - 4, nose_y + 14,
                nose_x - 3, nose_y + 4,
                nose_x - 14, nose_y + 6,
                nose_x - 5, nose_y - 2,
                nose_x - 10, nose_y - 8,
                nose_x - 2, nose_y - 4,
            ]
            self.canvas.create_polygon(points, fill="#FFFF00", outline="#FF4500", width=2)
            self.canvas.create_text(nose_x, nose_y - 16, text="PINCH! 💥", fill="#D00000", font=("Arial", 9, "bold"))
            
        # 3. Draw Character Sprite
        self.canvas.create_image(x, y, anchor="nw", image=photo)

    def _start_walk(self):
        """Walk smoothly from LEFT to RIGHT towards the YouTube tab."""
        if not self.is_running:
            return
            
        if self.current_x < self.target_x:
            # Walk speed: 6 pixels per tick
            self.current_x += 6
            self.walk_step += 1
            
            # Cycle through walk frames 1 -> 2 -> 3 -> 4
            walk_frame = f"walk_{(self.walk_step % 4) + 1}"
            
            # Gentle natural bobbing up and down
            bob = -3 if (self.walk_step % 2 == 1) else 0
            self.current_y = self.base_y + bob
            
            # Cute walking message
            msg = "Here I come! 👃" if (self.walk_step % 8 < 4) else "Closing YouTube..."
            self._draw_frame(walk_frame, self.current_x, self.current_y, msg)
            
            # Continue walk loop (35ms ≈ ~30fps)
            self.root.after(35, self._start_walk)
        else:
            # Arrived right at the 'X' button! Initiate the nose-pinch jump!
            self._perform_nose_pinch()

    def _perform_nose_pinch(self):
        """
        Nose-Pinch Sequence:
        1. Pause & Aim directly at the [X]
        2. Jump up into the air (jump_aim)
        3. Dive down head-first with nose pointing at [X] (nose_dive)
        4. SLAM nose tip directly onto [X] button with impact effect (nose_pinch)
        5. Close tab via Ctrl+W!
        6. Victory celebration
        """
        # Step 1: Pause & Aim
        self._draw_frame("walk_1", self.target_x, self.base_y, "TARGET LOCKED! 🎯")
        
        def jump_up():
            # Step 2: Leap up into the air
            self._draw_frame("jump_aim", self.target_x, self.base_y - 18, "JUMPING! 🚀")
            self.root.after(160, dive_down)
            
        def dive_down():
            # Step 3: Dive nose-first towards the [X]
            self._draw_frame("nose_dive", self.target_x + 4, self.base_y - 6, "NOSE DIVE! 👃")
            self.root.after(140, pinch_slam)
            
        def pinch_slam():
            # Step 4: Slam nose directly onto the [X] button!
            self._draw_frame("nose_pinch", self.target_x + 8, self.base_y + 2, impact=True)
            
            # Activate browser window and send Ctrl+W to close tab
            if self.hwnd and win32gui.IsWindow(self.hwnd):
                try:
                    win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(self.hwnd)
                except Exception:
                    pass
                    
            time.sleep(0.06)
            send_ctrl_w()
            print("💥 NOSE PINCH SUCCESSFUL! Tab closed!")
            
            # Step 5: Celebrate
            self.root.after(300, celebrate)
            
        def celebrate():
            # Step 6: Victory pose
            self._draw_frame("celebrate", self.target_x, self.base_y - 6, "PINCHED & CLOSED! 🎉")
            self.root.after(1400, finish)
            
        def finish():
            self.is_running = False
            try:
                self.root.destroy()
            except Exception:
                pass
            if self.on_finished:
                self.on_finished()
                
        self.root.after(200, jump_up)


def trigger_tab_enforcer(hwnd=None, on_finished=None):
    return OrangeTabEnforcer(hwnd=hwnd, on_finished=on_finished)


if __name__ == "__main__":
    print("👃 Testing Left-to-Right Walk & Nose-Pinch Tab Enforcer...")
    app = OrangeTabEnforcer()
    app.root.mainloop()
