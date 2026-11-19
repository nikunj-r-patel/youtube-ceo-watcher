import time
import threading
import win32gui
import sys

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

def get_all_window_titles():
    """Get all visible window titles using win32gui."""
    titles = []
    def callback(hwnd, _):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and title.strip():
                    titles.append(title)
        except:
            pass
    try:
        win32gui.EnumWindows(callback, None)
    except Exception as e:
        print(f"  ⚠️  EnumWindows error: {e}")
    return titles


def is_youtube_open():
    """
    Returns True if any browser window title contains 'YouTube'.

    Firefox example: "(7347) Best of Atif Aslam - YouTube — Mozilla Firefox"
    Chrome example:  "YouTube - Google Chrome"
    Both contain 'youtube' in lowercase — detected!
    """
    titles = get_all_window_titles()

    for title in titles:
        t_lower = title.lower()

        # Must contain 'youtube'
        if "youtube" not in t_lower:
            continue

        # Must be a browser window
        is_browser = any(browser in t_lower for browser in BROWSER_SUFFIXES)
        if is_browser:
            print(f"  🎯 YouTube detected: '{title[:70]}'")
            return True

    return False


# -----------------------------------------------
# 🎮 Watcher Controller
# -----------------------------------------------
class YouTubeWatcher:
    def __init__(self, overlay, speak_fn, get_line_fn):
        self.overlay      = overlay
        self.speak_fn     = speak_fn
        self.get_line_fn  = get_line_fn
        self.last_trigger = 0
        self.running      = False
        self._thread      = None

    def _check_loop(self):
        print(f"\n🔍 YouTube Watcher is ACTIVE!")
        print(f"   Checking every {CHECK_INTERVAL} seconds...")
        print(f"   Cooldown: {COOLDOWN_SECONDS}s (testing mode)\n")

        while self.running:
            now           = time.time()
            cooldown_left = COOLDOWN_SECONDS - (now - self.last_trigger)

            if cooldown_left > 0:
                print(f"⏳ Cooldown: {int(cooldown_left)}s left...")
            else:
                print(f"👁️  Checking for YouTube...")
                try:
                    if is_youtube_open():
                        self.last_trigger = time.time()
                        self._trigger_ceo()
                    else:
                        print(f"   ✅ No YouTube open.\n")
                except Exception as e:
                    print(f"   ⚠️  Check error: {e}")

            time.sleep(CHECK_INTERVAL)

    def _trigger_ceo(self):
        line = self.get_line_fn()
        print(f"\n🚨 YOUTUBE DETECTED! CEO incoming!")
        print(f"😤 CEO says: {line}\n")
        # Schedule on main UI thread
        self.overlay.root.after(0, lambda: self.overlay.show_with_voice(line, self.speak_fn))

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
    print("  😤 YouTube CEO Watcher  ")
    print("=" * 50)
    print("Starting up...\n")

    from overlay import CEOOverlay
    from speech  import speak, get_random_line, setup

    # Initialize voice and unlock male voices if possible
    setup()

    overlay = CEOOverlay()
    watcher = YouTubeWatcher(
        overlay     = overlay,
        speak_fn    = speak,
        get_line_fn = get_random_line
    )

    watcher.start()

    print("💡 YouTube is already open — CEO should appear in ~5 seconds!")
    print("💡 Press Ctrl+C to quit\n")

    try:
        overlay.run()
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop()
        print("\n👋 CEO Watcher stopped. Goodbye!")


if __name__ == "__main__":
    main()
