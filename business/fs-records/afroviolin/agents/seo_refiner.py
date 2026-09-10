import json
from datetime import datetime

def refine_track_seo(track):
    audio = track.get("audio_features", {})
    generated = track.get("generated_metadata", {})
    suno = track.get("suno_metadata", {})
    
    bpm = audio.get("bpm", 100)
    key = audio.get("key", "C")
    mood = audio.get("mood_tag", "chill")
    genre = "afro-highlife"
    
    # 1. Title (Max 100 chars for discoverability)
    base_title = generated.get("clean_title", "Afroviolin Instrumental")
    refined_title = f"{base_title} | Uplifting {genre.title()} Violin | African Instrumental 2026"
    
    # 2. Description (SEO structured)
    description = f"""Afroviolin presents "{base_title}" — a soulful {genre} violin instrumental perfect for focus, worship, study, and relaxation.

{bpm} BPM | Key of {key} | {mood.title()} energy
Crafted for deep listening, prayer, meditation, and creative flow.

🎵 Stream Afroviolin: [Link]
🔔 Subscribe for weekly Afro violin instrumentals
🎨 Visuals powered by Kling AI

— Timestamps —
00:00 Intro
03:25 Full track

— Why this track? —
Uplifting African guitar grooves meet expressive violin — ideal for peace, motivation, and spiritual moments.

#Afroviolin #Afrobeat #ViolinInstrumental #{genre.replace('-', '')} #AfricanMusic #FocusMusic #WorshipInstrumental #StudyBeats

Track Details:
• BPM: {bpm}
• Key: {key}
• Duration: {audio.get("duration_formatted", "3:25")}
• Mood: {mood.title()}
"""
    
    # 3. Tags (mix of broad + long-tail)
    tags = [
        "Afroviolin", "Afrobeat Violin", "African Violin", "Violin Instrumental",
        f"{genre} instrumental", f"{mood} afrobeat", "African music 2026",
        "focus music", "worship music", "study beats", "meditation music",
        "instrumental worship", "afro highlife", "uplifting african music",
        "violin afrobeat", "healing music"
    ]
    
    track["generated_metadata"].update({
        "seo_title": refined_title,
        "seo_description": description.strip(),
        "seo_tags": tags,
        "seo_optimized_at": datetime.utcnow().isoformat() + "Z",
        "seo_version": "v2"
    })
    
    return track

# Load state
with open("artifacts/afroviolin_state.json") as f:
    state = json.load(f)

# Refine Track 1
track1 = state["tracks"]["374a9a2f-6fc1-446c-9e13-7c886d7c9eb6"]
refined = refine_track_seo(track1)

# Save updated state
with open("artifacts/afroviolin_state.json", "w") as f:
    json.dump(state, f, indent=2)

print("✅ SEO Refinement complete for Track #1 (All Is Mind)")
print(f"New Title: {refined['generated_metadata']['seo_title']}")
