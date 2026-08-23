import os
import json
import asyncio
import requests
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

# 1. Generate Script (In Hindi) & Keywords (In English) - DIRECT API CALL TO GEMINI-PRO
def get_script_and_keywords(gemini_key: str, topic: str):
    # Using 'gemini-pro' as it is the most stable universally supported model right now
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_key}"
    
    prompt = f"""
    Write a highly engaging 30-second YouTube shorts script about '{topic}'.
    IMPORTANT: The spoken script MUST be in Hindi (Devanagari script). 
    However, provide 3 one-word search keywords in ENGLISH representing the visual themes to download background videos.
    Output ONLY valid JSON in this exact format, with no extra text or markdown formatting:
    {{"script": "your hindi spoken script here", "keywords": ["english_keyword1", "english_keyword2", "english_keyword3"]}}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7}
    }
    
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
         raise Exception(f"API Error {response.status_code}: {response.text}")

    # Extracting the text from the response structure
    raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
    # Clean up any potential markdown formatting
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw_text)

# 2. Generate Neural Voiceover (Receives Hindi Voice String)
async def generate_voiceover(script: str, voice_model: str, audio_path: str = "voice.mp3"):
    communicate = edge_tts.Communicate(script, voice_model)
    await communicate.save(audio_path)

# 3. Fetch Vertical Videos from Pexels
def download_pexels_videos(pexels_key: str, keywords: list):
    headers = {"Authorization": pexels_key}
    video_paths = []
    
    for i, kw in enumerate(keywords):
        url = f"https://api.pexels.com/videos/search?query={kw}&orientation=portrait&per_page=1"
        resp = requests.get(url, headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('videos'):
                link = data['videos'][0]['video_files'][0]['link']
                vid_resp = requests.get(link, stream=True)
                vid_name = f"clip_{i}.mp4"
                with open(vid_name, 'wb') as f:
                    for chunk in vid_resp.iter_content(chunk_size=1024):
                        if chunk: f.write(chunk)
                video_paths.append(vid_name)
                
    return video_paths

# 4. Concatenate and Render the Final Video
def assemble_video(audio_path: str, video_paths: list, output_path: str = "final_short.mp4"):
    if not video_paths:
        raise ValueError("Could not find relevant videos from Pexels.")
    
    audio = AudioFileClip(audio_path)
    clip_duration = audio.duration / len(video_paths)
    
    clips = []
    for vp in video_paths:
        clip = VideoFileClip(vp)
        duration_to_use = min(clip_duration, clip.duration)
        clip = clip.subclip(0, duration_to_use)
        
        clip = clip.resize(height=1920)
        clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=1080, height=1920)
        clips.append(clip)
        
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio)
    
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast", threads=4)
    
    for vp in video_paths:
        os.remove(vp)
        
    return output_path