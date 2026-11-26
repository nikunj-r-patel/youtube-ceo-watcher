import time
import threading
import win32gui
import sys
from tab_enforcer import OrangeTabEnforcer

# -----------------------------------------------
# 🕵️ YouTube Watcher — Main Controller
# -----------------------------------------------

CHECK_INTERVAL   = 5    # seconds between checks
COOLDOWN_SECONDS = 10   # 10s cooldown between appearances

# Browser suffixes in window titles
BROWSER_SUFFIXES = [
    "mozilla firefox",
    "google chrome",
    "microsoft edge",
    "opera",
    "brave",
]

def find_youtube_window():
    """
    Search for open browser windows containing 'YouTube'.
    Returns (found_boolean, hwnd, window_title).
    """
    found = [False, None, ""]
    
    def callback(hwnd, _):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and title.strip():
                    t_lower = title.lower()
                    if "youtube" in t_lower:
                        is_browser = any(b in t_lower for b in BROWSER_SUFFIXES)
                        if is_browser:
                            found[0] = True
                            found[1] = hwnd
                            found[2] = title
        except Exception:
            pass

    try:
        win32gui.EnumWindows(callback, None)
    except Exception as e:
        print(f"  ⚠️ EnumWindows error: {e}")
        
    return found[0], found[1], found[2]


# -----------------------------------------------
# 🎮 Watcher Controller (with 2-Strike Escalation)
# -----------------------------------------------
class YouTubeWatcher:
    def __init__(self, overlay, speak_fn, get_line_fn):
        self.overlay         = overlay
        self.speak_fn        = speak_fn
        self.get_line_fn     = get_line_fn
        self.last_trigger    = 0
        self.running         = False
        self._thread         = None
        self.warning_count   = 0     # Track number of warnings
        self.tab_just_closed = False # Flags if character just closed a tab

    def _check_loop(self):
        print(f"\n🔍 YouTube Watcher is ACTIVE!")
        print(f"   Checking every {CHECK_INTERVAL} seconds...")
        print(f"   Cooldown: {COOLDOWN_SECONDS}s")
        print(f"   Logic: CEO warns once. Next infraction: 3D character closes tab (CEO voice OFF).")
        print(f"   If 2nd tab exists: CEO voice turns ON to confront the 2nd tab!\n")

        while self.running:
            now           = time.time()
            cooldown_left = COOLDOWN_SECONDS - (now - self.last_trigger)

            if cooldown_left > 0:
                print(f"⏳ Cooldown: {int(cooldown_left)}s left...")
            else:
                print(f"👁️  Checking for YouTube...")
                try:
                    is_open, hwnd, title = find_youtube_window()
                    if is_open:
                        self.last_trigger = time.time()
                        print(f"  🎯 YouTube detected: '{title[:60]}'")
                        
                        if self.tab_just_closed:
                            # 2nd YouTube tab is open after 1st was closed!
                            # CEO voice is ON specifically for the 2nd tab!
                            print(f"\n🚨 2ND YOUTUBE TAB DETECTED! CEO voice is ON!")
                            second_tab_line = "ANOTHER YouTube tab?! Are you SERIOUS?! I saw that second tab! Close it NOW!!"
                            self._trigger_ceo(line=second_tab_line)
                            self.tab_just_closed = False
                            self.warning_count = 1
                        elif self.warning_count == 0:
                            # Warning 1: Standard CEO warning (Voice ON)
                            self.warning_count = 1
                            print(f"\n⚠️ WARNING 1: CEO is coming to warn you! (Voice ON)")
                            self._trigger_ceo()
                        else:
                            # Warning 2: 3D Character comes to close tab (CEO voice OFF!)
                            print(f"\n🏃 3D Character ACTIVATED to close the YouTube tab! (CEO voice OFF)")
                            self._trigger_tab_enforcer(hwnd)
                            self.warning_count = 0
                    else:
                        print(f"   ✅ No YouTube open.\n")
                        self.tab_just_closed = False
                except Exception as e:
                    print(f"   ⚠️  Check error: {e}")

            time.sleep(CHECK_INTERVAL)

    def _trigger_ceo(self, line=None):
        """Show CEO cartoon and speak funny line (Voice ON)."""
        if line is None:
            line = self.get_line_fn()
        print(f"😤 CEO says: {line}\n")
        self.overlay.root.after(0, lambda: self.overlay.show_with_voice(line, self.speak_fn))

    def _trigger_tab_enforcer(self, hwnd):
        """Trigger 3D character walking on tab bar to close YouTube tab. (CEO voice is OFF!)"""
        def on_closed():
            self.tab_just_closed = True
            
        def launch():
            # CEO voice is strictly OFF while character is coming!
            OrangeTabEnforcer(hwnd=hwnd, on_finished=on_closed)

        self.overlay.root.after(0, launch)

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False


# -----------------------------------------------
# 🚀 Main Entry Point
# -----------------------------------------------
def main():
    print("=" * 50)
    print("  😤 YouTube CEO Watcher & Tab Enforcer  ")
    print("=" * 50)
    print("Starting up...\n")

    from overlay import CEOOverlay
    from speech  import speak, get_random_line, setup

    setup()

    overlay = CEOOverlay()
    watcher = YouTubeWatcher(
        overlay     = overlay,
        speak_fn    = speak,
        get_line_fn = get_random_line
    )

    watcher.start()

    print("💡 Status:")
    print("   1. Open YouTube → Warning 1 (CEO yells)")
    print("   2. YouTube still open → Warning 2 (CEO yells again)")
    print("   3. YouTube still open → Orange Enforcer WALKS on tab bar & CLOSES it!")
    print("💡 Press Ctrl+C to quit\n")

    try:
        overlay.run()
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop()
        print("\n👋 YouTube Watcher stopped. Goodbye!")


if __name__ == "__main__":
    main()
