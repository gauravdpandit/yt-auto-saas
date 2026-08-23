import streamlit as st
import asyncio
from video_engine import get_script_and_keywords, generate_voiceover, download_pexels_videos, assemble_video

st.set_page_config(page_title="AI Shorts Pro", layout="centered")
st.title("🚀 AI YouTube Shorts Generator")
st.write("Generate a complete faceless video with AI script, voiceover, and stock footage!")

with st.sidebar:
    st.header("🔑 API Setup")
    gemini_key = st.text_input("Gemini API Key", type="password")
    pexels_key = st.text_input("Pexels API Key", type="password")
    st.markdown("[Get Free Gemini Key](https://aistudio.google.com/)")
    st.markdown("[Get Free Pexels Key](https://www.pexels.com/api/)")

topic = st.text_input("Enter Video Topic", placeholder="e.g., Top 3 Mysteries of Ancient Egypt")

if st.button("Generate Short 🎬"):
    if not gemini_key or not pexels_key or not topic:
        st.error("Please enter your API keys in the sidebar and a video topic!")
    else:
        try:
            with st.spinner("1/4: AI Writing Script & Extracting Keywords..."):
                data = get_script_and_keywords(gemini_key, topic)
                st.success(f"Keywords Found: {', '.join(data['keywords'])}")
                st.text_area("Generated Script", data['script'], height=120)
                
            with st.spinner("2/4: Generating Neural Voiceover..."):
                asyncio.run(generate_voiceover(data['script']))
                
            with st.spinner("3/4: Downloading B-Rolls from Pexels..."):
                video_paths = download_pexels_videos(pexels_key, data['keywords'])
                st.success(f"Downloaded {len(video_paths)} background clips!")
                
            with st.spinner("4/4: Stitching & Rendering Video (This takes 1-2 minutes)..."):
                final_file = assemble_video("voice.mp3", video_paths)
                
            st.success("🎉 Video Ready to Upload!")
            st.video(final_file)
            
        except Exception as e:
            st.error(f"An error occurred during generation: {e}")