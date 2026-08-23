import streamlit as st
import asyncio
import os
from video_engine import get_script_and_keywords, generate_voiceover, download_pexels_videos, assemble_video

st.set_page_config(page_title="Pro AI Shorts Builder", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: 800; color: #FF4B4B; margin-bottom: 0px;}
    .sub-title { font-size: 1.2rem; color: #888; margin-bottom: 2rem;}
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #FF4B4B; color: white;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">⚡ AutoShorts AI Pro (Hindi Version)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Fully Automated Faceless Video Pipeline (Script -> Voice -> Render)</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Engine Configuration")
    st.subheader("1. API Keys (Required)")
    gemini_key = st.text_input("Google Gemini API Key", type="password")
    pexels_key = st.text_input("Pexels Video API Key", type="password")
    
    st.markdown("---")
    st.subheader("2. Video Settings")
    video_length = st.select_slider("Target Duration", options=["15 Sec", "30 Sec", "60 Sec"], value="30 Sec")
    
    # 🔴 CHANGED TO HINDI VOICES 🔴
    voice_type = st.selectbox("AI Voice Actor", ["Male (Hindi)", "Female (Hindi)"]) 
    
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎬 Create New Project")
    topic = st.text_area("What should the video be about?", placeholder="e.g., Explain Quantum Physics in simple terms...", height=100)
    generate_btn = st.button("🚀 Initialize AI Pipeline")

with col2:
    st.subheader("📊 Output Console")
    status_box = st.empty()
    status_box.info("Waiting for project details...")

if generate_btn:
    if not gemini_key or not pexels_key or not topic:
        status_box.error("⚠️ Missing Configuration! Please check API keys and Topic.")
    else:
        # 🔴 ASSIGNING MICROSOFT HINDI NEURAL VOICES 🔴
        voice_str = "hi-IN-MadhurNeural" if voice_type == "Male (Hindi)" else "hi-IN-SwaraNeural"
        
        try:
            progress_bar = st.progress(0)
            status_box.info("🤖 AI is thinking... (Step 1/4)")
            
            data = get_script_and_keywords(gemini_key, topic)
            progress_bar.progress(25)
            with st.expander("📝 View AI Generated Script", expanded=True):
                st.write(data['script'])
                st.caption(f"Tags: {', '.join(data['keywords'])}")
            
            status_box.info("🎙️ Synthesizing Neural Voice... (Step 2/4)")
            # 🔴 PASSING THE HINDI VOICE TO ENGINE 🔴
            asyncio.run(generate_voiceover(data['script'], voice_str, "voice.mp3")) 
            progress_bar.progress(50)
            
            status_box.info("🎥 Hunting for HD B-Rolls... (Step 3/4)")
            video_paths = download_pexels_videos(pexels_key, data['keywords'])
            progress_bar.progress(75)
            
            status_box.warning("⏳ Rendering Video Engine... Please don't close tab (Step 4/4)")
            final_file = assemble_video("voice.mp3", video_paths)
            progress_bar.progress(100)
            
            status_box.success("✅ Render Complete!")
            st.markdown("---")
            st.subheader("📺 Final Export")
            st.video(final_file)
            
            with open(final_file, "rb") as file:
                btn = st.download_button(label="⬇️ Download Ultra HD Short", data=file, file_name="AutoShort_AI.mp4", mime="video/mp4")
                
        except Exception as e:
            status_box.error(f"❌ Pipeline Failure: {str(e)}")