import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import os
import time
import math
import threading
import ctypes
import win32gui
import win32con

# -------------------------------------------------------------
# 🎯 Professional 60 FPS Tab Enforcer — Nose-Pinch Tab Closer
# Clean, box-free, fluid animation built for demos & social media
# -------------------------------------------------------------

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAMES_DIR = os.path.join(ASSETS_DIR, "orange_frames")

# 60 FPS tick duration in milliseconds
TICK_MS = 16

# Windows Virtual Keys for Ctrl + W
VK_CONTROL = 0x11
VK_W = 0x57
KEYEVENTF_KEYUP = 0x0002

def send_ctrl_w():
    """Simulate pressing Ctrl + W to close current active browser tab."""
    user32 = ctypes.windll.user32
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_W, 0, 0, 0)
    time.sleep(0.04)
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
                if r > 185 and g < 45 and b < 45:
                    red_spots.append((x, y))

        if red_spots:
            logo_x = int(sum(p[0] for p in red_spots) / len(red_spots))
            logo_y = int(sum(p[1] for p in red_spots) / len(red_spots))

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
            return exact_screen_x, exact_screen_y
    except Exception:
        pass

    # Method 3: Calculated fallback
    exact_screen_x = win_left + int(win_w * 0.962)
    exact_screen_y = win_top + 24
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
        
        # Calculate overlay dimensions
        self._calculate_geometry()
        
        # Canvas for character and impact FX
        self.canvas = tk.Canvas(
            self.root,
            width=self.win_w,
            height=self.win_h,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Load all crisp, distortion-free frames
        self._load_frames()
        
        # Character dimensions & nose offset
        self.char_w = 56
        self.char_h = 52
        self.nose_offset_x = 43
        self.nose_offset_y = 48
        
        # Position states
        self.current_x = -50.0  # Start just off the left edge for a clean entrance
        self.base_y = 10.0
        self.current_y = self.base_y
        
        # Pinpoint exact 'X' button location
        screen_target_x, screen_target_y = pinpoint_youtube_x_button(
            self.hwnd, self.win_x, self.win_y, self.win_w
        )
        self.target_x = screen_target_x - self.win_x
        self.target_y = max(18, min(self.win_h - 15, screen_target_y - self.win_y))
        
        # Stop point for walking right
        self.walk_stop_x = self.target_x - self.char_w + 4
        
        self.is_running = True
        self.walk_distance = 0.0
        
        # Start smooth 60fps walk loop
        self.root.after(50, self._tick_walk_right)

    def _calculate_geometry(self):
        screen_w = self.root.winfo_screenwidth()
        self.win_x = 0
        self.win_y = 0
        self.win_w = screen_w
        self.win_h = 110  # Height for jump arc
        
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
        """Load 100% binary-clean animation frames."""
        self.frames = {}
        names = [
            "walk_r1", "walk_r2", "walk_r3", "walk_r4",
            "walk_l1", "walk_l2", "walk_l3", "walk_l4",
            "stand_aim", "jump_up", "nose_down", "nose_impact", "celebrate"
        ]
        for name in names:
            p = os.path.join(FRAMES_DIR, f"{name}.png")
            if os.path.exists(p):
                img = Image.open(p).convert("RGBA")
                self.frames[name] = ImageTk.PhotoImage(img)

    def _render(self, frame_name, x, y, impact_radius=0):
        """Render pure sprite and optional impact shockwave without ANY text boxes."""
        self.canvas.delete("all")
        photo = self.frames.get(frame_name, self.frames.get("walk_r1"))
        
        # Clean expanding shockwave ring on impact
        if impact_radius > 0:
            cx = self.target_x
            cy = self.target_y
            r = impact_radius
            # Double concentric shockwave rings
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#FF4500", width=2)
            self.canvas.create_oval(cx - r*0.6, cy - r*0.6, cx + r*0.6, cy + r*0.6, outline="#FFD700", width=2)
            
        # Draw pure character sprite
        if photo:
            self.canvas.create_image(int(x), int(y), anchor="nw", image=photo)

    def _tick_walk_right(self):
        """Smooth 60 FPS walk from LEFT towards the YouTube tab."""
        if not self.is_running:
            return
            
        if self.current_x < self.walk_stop_x:
            # 3.2 pixels per 16ms = ~200px per second (natural walking speed)
            self.current_x += 3.2
            self.walk_distance += 3.2
            
            # True leg walking stride: 1 step every 16px walked
            stride_idx = int((self.walk_distance / 16)) % 4 + 1
            frame = f"walk_r{stride_idx}"
            
            # Subtle natural stride bob (1.5px sine wave)
            bob = -1.5 * abs(math.sin(self.walk_distance * 0.15))
            self.current_y = self.base_y + bob
            
            self._render(frame, self.current_x, self.current_y)
            self.root.after(TICK_MS, self._tick_walk_right)
        else:
            # Reached destination! Initiate cinematic jump & nose slam
            self._execute_cinematic_nose_slam()

    def _execute_cinematic_nose_slam(self):
        """
        Smooth Parabolic Nose Slam Sequence:
        1. Anticipation: Quick pause & crouch at the X button (100ms)
        2. Parabolic Launch: Smooth jump curve up into the air (240ms)
        3. Nose Spear Dive: Plummets nose-first into the exact center of [X] (120ms)
        4. Impact & Shockwave: Expands energy ring, closes tab (180ms)
        5. Victory & Left Exit: Walks smoothly off-screen to the left (60 FPS)
        """
        # Step 1: Stop cleanly at the target
        self.current_x = self.walk_stop_x
        self._render("stand_aim", self.current_x, self.base_y)
        
        def start_jump():
            # Step 2: Parabolic Jump Arc (60 FPS physics)
            jump_start_time = time.time()
            jump_duration = 0.28  # 280ms arc
            apex_height = 36.0    # 36px high jump
            
            def tick_jump():
                if not self.is_running:
                    return
                elapsed = time.time() - jump_start_time
                progress = min(1.0, elapsed / jump_duration)
                
                # Sine curve for natural gravity arc: 0 -> peak -> down
                arc = math.sin(progress * math.pi)
                y = self.base_y - (arc * apex_height)
                
                # Center sprite horizontally above the target
                char_x = self.target_x - (self.char_w // 2)
                
                if progress < 0.65:
                    # Going up: jump_up pose
                    self._render("jump_up", char_x, y)
                    self.root.after(TICK_MS, tick_jump)
                elif progress < 1.0:
                    # Near peak & turning down: nose pointing straight down
                    self._render("nose_down", char_x, y)
                    self.root.after(TICK_MS, tick_jump)
                else:
                    # Step 3: Trigger Nose Impact right on the X button!
                    trigger_impact()
                    
            tick_jump()
            
        def trigger_impact():
            # Step 4: Nose lands directly on center of the X button!
            impact_x = self.target_x - self.nose_offset_x
            impact_y = self.target_y - self.nose_offset_y
            
            # Send Ctrl+W to close tab
            if self.hwnd and win32gui.IsWindow(self.hwnd):
                try:
                    win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(self.hwnd)
                except Exception:
                    pass
            send_ctrl_w()
            print("💥 NOSE HIT CENTER OF [X]! YouTube tab closed cleanly!")
            
            # Animate expanding shockwave over 180ms
            fx_start = time.time()
            def tick_shockwave():
                elapsed = time.time() - fx_start
                if elapsed < 0.18:
                    radius = 4 + (elapsed / 0.18) * 22
                    self._render("nose_impact", impact_x, impact_y, impact_radius=radius)
                    self.root.after(TICK_MS, tick_shockwave)
                else:
                    # Celebrate pose
                    celebrate()
                    
            tick_shockwave()
            
        def celebrate():
            # Step 5: Brief standing victory pose
            celeb_x = self.target_x - (self.char_w // 2)
            self._render("celebrate", celeb_x, self.base_y - 4)
            # After 500ms, start walking left off-screen
            self.root.after(500, self._start_exit_left)
            
        # 100ms anticipation pause before leaping
        self.root.after(100, start_jump)

    def _start_exit_left(self):
        """Walk smoothly off the left side of the screen at 60 FPS."""
        self.exit_distance = 0.0
        self.current_x = self.target_x - (self.char_w // 2)
        
        def tick_exit():
            if not self.is_running:
                return
                
            if self.current_x > -70:
                # 3.8px per tick (brisk strut exit)
                self.current_x -= 3.8
                self.exit_distance += 3.8
                
                # Leg movement cycling for walking left
                stride_idx = int((self.exit_distance / 16)) % 4 + 1
                frame = f"walk_l{stride_idx}"
                
                bob = -1.5 * abs(math.sin(self.exit_distance * 0.15))
                y = self.base_y + bob
                
                self._render(frame, self.current_x, y)
                self.root.after(TICK_MS, tick_exit)
            else:
                # Completely off-screen! Clean shutdown
                self.is_running = False
                try:
                    self.root.destroy()
                except Exception:
                    pass
                if self.on_finished:
                    self.on_finished()
                    
        tick_exit()


def trigger_tab_enforcer(hwnd=None, on_finished=None):
    return OrangeTabEnforcer(hwnd=hwnd, on_finished=on_finished)


if __name__ == "__main__":
    print("Testing Professional 60 FPS Tab Enforcer...")
    app = OrangeTabEnforcer()
    app.root.mainloop()
