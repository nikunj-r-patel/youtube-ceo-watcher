import time
import threading
import win32gui
import sys
from tab_enforcer import OrangeTabEnforcer

# -----------------------------------------------
# 🕵️ YouTube Watcher — Main Controller
# -----------------------------------------------

CHECK_INTERVAL   = 3    # seconds between checks
COOLDOWN_SECONDS = 10   # seconds cooldown between appearances

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
# 🎮 Watcher Controller
# -----------------------------------------------
class YouTubeWatcher:
    def __init__(self, overlay, speak_fn, get_line_fn):
        self.overlay         = overlay
        self.speak_fn        = speak_fn
        self.get_line_fn     = get_line_fn
        self.running         = False
        self._thread         = None
        self.is_busy         = False      # True while sequence is active
        self.tab_just_closed = False      # True when character just closed a tab

    def _check_loop(self):
        print(f"\n🔍 YouTube Watcher is ACTIVE!")
        print(f"   Checking every {CHECK_INTERVAL} seconds...")
        print(f"   Flow: 1. YouTube detected → CEO displays ONCE and warns with voice.")
        print(f"         2. AFTER CEO leaves → 3D Character comes, jumps on [X], closes tab, and says 'Closed! Bye bye!'.")
        print(f"         3. If 2nd tab remains open → CEO immediately displays for 2nd tab!\n")

        while self.running:
            if self.is_busy:
                time.sleep(1)
                continue

            try:
                is_open, hwnd, title = find_youtube_window()
                if is_open:
                    print(f"  🎯 YouTube detected: '{title[:60]}'")
                    self.is_busy = True

                    if self.tab_just_closed:
                        # 2nd YouTube tab is open after 1st was closed!
                        # CEO voice and display are ON specifically for the 2nd tab!
                        print(f"\n🚨 2ND YOUTUBE TAB DETECTED! CEO voice is ON!")
                        second_tab_line = "ANOTHER YouTube tab?! Are you SERIOUS?! I saw that second tab! Close it NOW!!"
                        self._trigger_ceo_then_enforcer(hwnd, line=second_tab_line)
                        self.tab_just_closed = False
                    else:
                        # Standard first detection:
                        # Step 1: CEO displays once with funny line.
                        # Step 2: Only after CEO goes, the 3D character comes!
                        print(f"\n😤 STEP 1: CEO displays once to warn you!")
                        self._trigger_ceo_then_enforcer(hwnd)
                else:
                    self.tab_just_closed = False
            except Exception as e:
                print(f"   ⚠️ Check error: {e}")

            time.sleep(CHECK_INTERVAL)

    def _trigger_ceo_then_enforcer(self, hwnd, line=None):
        """Show CEO once. AFTER CEO leaves, the 3D character comes to close the tab!"""
        if line is None:
            line = self.get_line_fn()
        print(f"😤 CEO says: {line}\n")

        def after_ceo_goes():
            # Check if YouTube is STILL open after the CEO left
            is_open, current_hwnd, _ = find_youtube_window()
            if is_open:
                target_hwnd = current_hwnd if current_hwnd else hwnd
                print(f"🏃 STEP 2: CEO is gone! 3D Character ACTIVATED to close the tab!")
                self._trigger_tab_enforcer(target_hwnd)
            else:
                print(f"✅ User closed YouTube while CEO was speaking. Enforcer not needed.")
                self.is_busy = False

        self.overlay.root.after(0, lambda: self.overlay.show_with_voice(line, self.speak_fn, on_finished=after_ceo_goes))

    def _trigger_tab_enforcer(self, hwnd):
        """Trigger 3D character walking on tab bar to close YouTube tab."""
        def on_closed_and_exited():
            print("🏁 Character closed tab and exited off-screen!")
            self.tab_just_closed = True
            self.is_busy = False

        def launch():
            # Guarantee CEO is completely hidden and audio is silent while character comes
            self.overlay.hide_immediately()
            OrangeTabEnforcer(hwnd=hwnd, on_finished=on_closed_and_exited)

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

    print("💡 Flow:")
    print("   1. Open YouTube → CEO displays ONCE and warns with voice.")
    print("   2. After CEO leaves → 3D Character comes, jumps on [X], closes tab, and says 'Closed! Bye bye!'.")
    print("   3. If 2nd YouTube tab is open → CEO displays again for the 2nd tab!")
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
