# 😤 YouTube CEO Watcher & 3D Tab Enforcer for Windows

> A hilarious desktop companion app for Windows. Whenever you open YouTube in your browser, an angry, funny cartoon CEO slides up from the corner of your screen, his eyes and face zoom into view in shock, and he yells at you in an authoritative male executive voice with funny lines like:
> *"YOUTUBE?! In MY company?! During MY time?! Are you SERIOUS right now?!"*
>
> If you don't close it, a 3D cartoon enforcer walks right across your browser's top tab bar, leaps into the air, dives nose-first right onto the tab's **[X]** close button to close it, yells *"Closed! Bye bye!"*, and struts off-screen!

---

## 🎬 How It Works

```
┌──────────────────────────────────────────────┐
│          Background YouTube Monitor          │
│   Scans open windows every 3s for YouTube    │
│   (Firefox, Chrome, Edge, Brave, Opera)      │
└──────────────────────┬───────────────────────┘
                       │ 🎯 YouTube Detected!
                       ▼
┌──────────────────────────────────────────────┐
│         Step 1: CEO Warning Overlay          │
│  - Borderless, transparent, always-on-top    │
│  - Slides up above Windows Taskbar           │
│  - Face & eyes zoom & pulse dynamically      │
│  - Plays authoritative deep male CEO voice   │
│  - Slides back down once speech finishes     │
└──────────────────────┬───────────────────────┘
                       │ 💨 Once CEO Leaves:
                       ▼
┌──────────────────────────────────────────────┐
│       Step 2: 3D Tab Enforcer Sequence       │
│  - CEO is completely hidden and silent       │
│  - 3D cartoon character walks along tab bar  │
│  - Real puppet-rigged leg-stepping animation │
│  - Parabolic jump & precision nose-dive slam │
│  - Lands on active YouTube tab's [X] button  │
│  - Sends Ctrl+W, shockwave explodes, closes  │
│  - Character shouts "Closed! Bye bye!"       │
│  - Struts off-screen to the left             │
└──────────────────────┬───────────────────────┘
                       │ 🚨 If 2nd Tab Exists:
                       ▼
┌──────────────────────────────────────────────┐
│        Step 3: Multi-Tab CEO Reaction        │
│  - CEO immediately slides up in shock:       │
│    "ANOTHER YouTube tab?! Are you SERIOUS?!  │
│     I saw that second tab! Close it NOW!!"   │
│  - Enforcer returns to close the 2nd tab too │
└──────────────────────────────────────────────┘
```

---

## ✨ Features

- **🎯 Cross-Browser Detection**: Detects YouTube whether you're browsing the homepage or playing any video across Mozilla Firefox, Google Chrome, Microsoft Edge, Brave, Opera, etc.
- **👁️ Dynamic Face & Eye Animation**: While speaking, the cartoon CEO's face pulses and zooms in with solid white sclera and visible pupils.
- **🔊 Deep Male CEO Voice**: Pre-rendered high-definition authoritative male executive voice clips that play instantly with zero lag via native Windows MCI (`winmm.dll`).
- **🏃 3D Puppet-Rigged Tab Enforcer**: A custom-rigged 3D cartoon character with dynamic alternating leg stride animation, ground contact shadows, and zero body slicing.
- **🎯 Exact [X] Button Pinpointer**: Uses visual tab strip detection and UI Automation to find the exact center of the active YouTube tab's close button across all DPI displays.
- **🗣️ Character Voice ("Closed! Bye bye!")**: When the nose hits the **[X]** and the tab closes, the character celebrates and cheerfully says *"Closed! Bye bye!"*.
- **⚡ Multi-Tab Intelligence**: If multiple YouTube tabs are open, the character closes the first tab, and the CEO immediately appears in disbelief to confront the user about the second tab.
- **📐 Taskbar-Aware Positioning**: Automatically queries the Windows API (`SystemParametersInfoW`) to detect the taskbar work area and sit right above it.
- **✨ Crisp 1-Bit Binary Alpha**: All graphics are processed with protected whites so Tkinter's colorkey transparency produces zero edge halos or distorted borders on dark and light themes alike.

---

## 🛠️ Software & Libraries Used

| Library / Tool | Purpose in Project |
|---|---|
| **Python 3.10+** | Core programming language |
| **Tkinter** (Built-in) | Transparent, borderless desktop overlays |
| **win32gui / pywin32** | Windows User32 API integration to scan active browser windows and input simulated keystrokes |
| **Pillow (PIL)** | Image processing, limb rotation, perspective scaling, and sprite generation |
| **ctypes / winmm.dll** | Direct Windows multimedia MCI interface to play audio with zero lag |
| **edge-tts** | High-definition neural text-to-speech engine used to generate the voice lines |

---

## 📁 Project Structure

```
youtube-watcher/
├── assets/
│   ├── cartoon.png          # Master clean transparent CEO character
│   ├── character_3d.png     # Master clean 3D enforcer character
│   ├── orange_frames/       # 60 FPS walking, jumping, diving, and celebrate frames
│   └── audio/               # Pre-rendered CEO and character voice MP3 clips
├── main.py                  # Main controller, window monitor & choreography
├── overlay.py               # Tkinter CEO overlay & zoom animation
├── tab_enforcer.py          # 60 FPS walking tab-bar overlay & tab closing logic
├── speech.py                # Audio playback & line shuffle logic
├── build_3d_walk_sprites.py # Generates puppet-rigged walking sprites
├── generate_audio.py        # Offline generator for voice clips
├── requirements.txt         # Python dependencies
└── README.md                # Documentation (this file)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Operating System**: Windows 10 or Windows 11
- **Python**: Python 3.10 or newer installed (ensure Python is in PATH).

### 2. Installation
Open **PowerShell** or **Command Prompt** and navigate to the project directory:

```powershell
cd D:\funProjects\youtube-watcher
```

Install the required Python packages:

```powershell
pip install -r requirements.txt
```

### 3. Running the App

```powershell
python main.py
```

Now open YouTube in any browser and watch the companion in action!
- Press `Ctrl + C` in the terminal to stop the watcher.
