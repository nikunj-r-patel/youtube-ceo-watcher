import os
import random
import threading
import ctypes
import hashlib
import time

# -----------------------------------------------
# 😤 CEO Boss Funny Lines
# -----------------------------------------------
FUNNY_LINES = [
    "HEY! What do you think you are doing?! Is this what I pay you for?!",
    "YOUTUBE?! In MY company?! During MY time?! Are you SERIOUS right now?!",
    "I did not build this company from ZERO to watch you watch cat videos!!",
    "Put that YouTube DOWN! You are supposed to be working! RIGHT NOW!!",
    "Do you know what I was doing at your age?! NOT watching YouTube, I tell you!!",
    "UNBELIEVABLE! I leave for five minutes and THIS is what happens?!",
    "My GRANDMOTHER works harder than you and she is NINETY THREE years old!!",
    "You are lucky I am in a good mood today! Close that YouTube! NOW!!",
    "I can SEE you! Yes, YOU! Sitting there watching YouTube like you own the place!!",
    "This is coming OUT of your salary! YouTube subscription? No no no! MY subscription!",
    "Get back to work before I make you watch only spreadsheets for the rest of your life!!",
    "CAUGHT! Red handed! YouTube open, brain closed! Back to work! IMMEDIATELY!",
    "Every second you spend on YouTube is a second I am losing MONEY! CLOSE IT!",
    "Do you think this company runs on YouTube views?! GET BACK TO WORK!",
    "I am calling your mother! She will hear about this YouTube business!",
    "ANOTHER YouTube tab?! Are you SERIOUS?! I saw that second tab! Close it NOW!!",
    "THAT IS IT! I warned you TWICE! Tab CLOSED!",
    "THAT IS IT! I warned you! Tab CLOSED!",
]

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")

# Shuffled queue so NO line repeats until all 15 are used!
_deck = []

def get_random_line():
    """Returns a unique line every time. Reshuffles only after all are used."""
    global _deck
    if not _deck:
        _deck = FUNNY_LINES.copy()
        random.shuffle(_deck)
    return _deck.pop()

def get_audio_path_for_line(text):
    """Find matching pre-generated male voice MP3."""
    h = hashlib.md5(text.encode("utf-8")).hexdigest()[:10]
    p = os.path.join(AUDIO_DIR, f"line_{h}.mp3")
    if os.path.exists(p):
        return p
    return None

def stop_speech():
    """Immediately halt all audio playback."""
    try:
        mci = ctypes.windll.winmm.mciSendStringW
        mci("close all", None, 0, 0)
    except Exception:
        pass

def play_audio_file(file_path):
    """Play MP3 file via Windows MCI (built into winmm.dll, 100% offline, zero lag)."""
    try:
        mci = ctypes.windll.winmm.mciSendStringW
        alias = f"ceo_{int(time.time()*1000)}"
        abs_path = os.path.abspath(file_path)

        # Open and play
        mci(f'open "{abs_path}" type mpegvideo alias {alias}', None, 0, 0)
        mci(f'play {alias} wait', None, 0, 0)
        mci(f'close {alias}', None, 0, 0)
        return True
    except Exception as e:
        print(f"MCI playback error: {e}")
        return False

def speak(text):
    """
    Play the deep male CEO voice clip.
    Blocks the calling thread until audio finishes.
    """
    audio_path = get_audio_path_for_line(text)
    if audio_path:
        play_audio_file(audio_path)
    else:
        # Fallback to pyttsx3 if file not found
        try:
            import pyttsx3
            import pythoncom
            pythoncom.CoInitialize()
            engine = pyttsx3.init()
            engine.setProperty('rate', 130)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            pythoncom.CoUninitialize()
        except Exception as e:
            print(f"TTS error: {e}")

def speak_character_closed_bye():
    """Play cute cartoon character voice saying 'Closed! Bye bye!' asynchronously."""
    p = os.path.join(AUDIO_DIR, "character_closed_bye.mp3")
    if os.path.exists(p):
        threading.Thread(target=lambda: play_audio_file(p), daemon=True).start()

def setup():
    """Ensure audio directory exists."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print(f"🎙️ Deep Male CEO Voice initialized ({len(FUNNY_LINES)} audio clips ready)!")

if __name__ == "__main__":
    setup()
    line = get_random_line()
    print(f"Testing line: {line}")
    speak(line)
