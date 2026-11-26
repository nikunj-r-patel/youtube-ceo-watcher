# 😤 YouTube CEO Watcher for Windows

> A hilarious desktop companion app for Windows. Whenever you open YouTube in your browser, an angry, funny cartoon CEO slides up from the corner of your screen, his eyes and face zoom into view in shock, and he yells at you in an authoritative male executive voice with funny lines like:
> *"YOUTUBE?! In MY company?! During MY time?! Are you SERIOUS right now?!"*

---

## 📸 How It Works

```
┌──────────────────────────────────────────────┐
│          Background YouTube Monitor          │
│   Scans open windows every 5s for YouTube    │
│   (Firefox, Chrome, Edge, Brave, Opera)      │
└──────────────────────┬───────────────────────┘
                       │ 🎯 YouTube Detected!
                       ▼
┌──────────────────────────────────────────────┐
│           Animated Desktop Overlay           │
│  - Borderless, transparent, always-on-top     │
│  - Slides smoothly up above Windows Taskbar  │
│  - Face & eyes zoom & pulse dynamically      │
└──────────────────────┬───────────────────────┘
                       │ 🔊 Synchronized
                       ▼
┌──────────────────────────────────────────────┐
│             Deep Male CEO Voice              │
│  - Plays high-definition angry CEO line      │
│  - Non-repeating shuffled line system        │
│  - Slides back down once speech finishes     │
└──────────────────────────────────────────────┘
```

---

## ✨ Features

- **🎯 Cross-Browser Detection**: Detects YouTube whether you're browsing the homepage or playing any full-screen / titled video across Mozilla Firefox, Google Chrome, Microsoft Edge, Brave, Opera, etc.
- **👁️ Dynamic Face & Eye Animation**: While speaking, the cartoon CEO's face pulses and zooms in, making his bulging eyes look huge and comedic.
- **🔊 Deep Male CEO Voice**: Pre-rendered high-quality authoritative male executive voice clips that play instantly with zero lag and 100% offline.
- **🏃 2-Strike Tab Enforcer (NEW!)**: After the CEO warns the user twice, on the 3rd infraction an orange character walks right across the browser's top tab bar, stomps the YouTube tab's **[X]** button, and cleanly closes the tab (`Ctrl+W`)!
- **🔀 Anti-Repeat Shuffled Deck**: Cycles through all hilarious lines without repeating any line twice until the entire deck has been used.
- **📐 Taskbar-Aware Positioning**: Automatically queries the Windows API (`SystemParametersInfoW`) to detect the taskbar height and rest right on top of it — no cutoffs!
- **👆 Click to Dismiss**: Need him to leave in a hurry? Just click on him!
- **⏱️ Smart Cooldown**: 10-second cooldown between detections prevents annoying pop-up spam.

---

## 🛠️ Software & Libraries Used

| Library / Tool | Purpose in Project |
|---|---|
| **Python 3.10+** | Core programming language |
| **Tkinter** (Built-in) | Lightweight, transparent, borderless overlay window |
| **win32gui / pywin32** | Windows User32 API integration to scan active browser windows |
| **Pillow (PIL)** | Image processing, transparency handling, and animated zoom frames |
| **ctypes / winmm.dll** | Direct Windows multimedia MCI interface to play audio with zero lag |
| **edge-tts** | High-definition neural text-to-speech engine used to generate the CEO voice lines |
| **psutil** | System process enumeration and management |
| **PyInstaller** | Bundles the script and assets into a standalone `.exe` |

---

## 📁 Project Structure

```
youtube-watcher/
├── assets/
│   ├── cartoon.png          # Transparent angry CEO character
│   ├── orange_character.png # Transparent orange tab enforcer character
│   ├── orange_frames/       # Walking, jumping, stomping animation frames
│   └── audio/               # Pre-rendered Male CEO voice MP3 clips
├── main.py                  # Main controller, detection & 2-strike escalation
├── overlay.py               # Tkinter CEO overlay & zoom animation
├── tab_enforcer.py          # Walking tab-bar overlay & tab closing logic
├── speech.py                # Audio playback & line shuffle logic
├── build_orange_sprites.py  # Generates walking frames for orange character
├── generate_audio.py        # Offline generator for voice clips
├── requirements.txt         # Python dependencies
└── README.md                # Documentation (this file)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Operating System**: Windows 10 or Windows 11
- **Python**: Python 3.10 or newer installed (make sure `Add Python to PATH` was checked during installation).

### 2. Installation
Open **PowerShell** or **Command Prompt** and navigate to the project directory:

```powershell
cd D:\funProjects\youtube-watcher
```

Install the required Python packages:

```powershell
python -m pip install -r requirements.txt
```

*(Optional)* If you ever want to re-generate the audio clips or add new lines:
```powershell
python generate_audio.py
```

---

## ▶️ Running the Application

In your terminal / PowerShell:

```powershell
cd D:\funProjects\youtube-watcher
python main.py
```

1. Keep the PowerShell window open (you can minimize it).
2. Open YouTube in any browser (Firefox, Chrome, Edge, etc.).
3. Within 5 seconds, watch the **bottom-right corner** above your taskbar! 😤
4. To stop the app at any time, press **`Ctrl + C`** in PowerShell.

---

## 📦 How to Package into a Standalone `.exe`

Want to run the app as a single clickable Windows program without needing Python open?

Run this PyInstaller command:

```powershell
cd D:\funProjects\youtube-watcher
pyinstaller --noconsole --onefile --add-data "assets;assets" main.py
```

Once built, you will find `main.exe` in the `dist/` folder. You can double-click it to run in the background!

---

## ⚙️ Customization

- **Change Cooldown**: In [main.py](file:///D:/funProjects/youtube-watcher/main.py#L11), change `COOLDOWN_SECONDS = 10` to any duration (e.g. `60` or `120`).
- **Add More Lines**: In [speech.py](file:///D:/funProjects/youtube-watcher/speech.py#L11), add your own quotes to the `FUNNY_LINES` list and run `python generate_audio.py` to bake them into voice clips.
- **Change Character**: Place any 300x400 transparent PNG image into `assets/cartoon.png`.
