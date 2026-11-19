import asyncio
import edge_tts
import os
import hashlib

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE = "en-US-ChristopherNeural"  # Authoritative deep male CEO voice

LINES = [
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
]

def get_filename_for_line(text):
    h = hashlib.md5(text.encode("utf-8")).hexdigest()[:10]
    return os.path.join(AUDIO_DIR, f"line_{h}.mp3")

async def generate_all():
    print(f"🎙️ Generating {len(LINES)} realistic Male CEO voice clips...")
    for i, line in enumerate(LINES):
        out_file = get_filename_for_line(line)
        if not os.path.exists(out_file):
            print(f"[{i+1}/{len(LINES)}] Generating: {line[:40]}...")
            communicate = edge_tts.Communicate(
                line,
                voice=VOICE,
                rate="+12%",
                pitch="-4Hz"
            )
            await communicate.save(out_file)
        else:
            print(f"[{i+1}/{len(LINES)}] Exists: {line[:40]}...")
    print("✅ All Male CEO voice lines generated successfully!")

if __name__ == "__main__":
    asyncio.run(generate_all())
