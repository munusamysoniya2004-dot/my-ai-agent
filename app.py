import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import urllib.parse
from duckduckgo_search import DDGS
import PyPDF2
from gtts import gTTS
import os
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Suresh's Ultimate AI", page_icon="🤖", layout="wide")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    # 👇 UNGA API KEY INGA PODUNGA
    api_key = "AIzaSy_UNGA_ORIGINAL_KEY_INGA_IRUKKANUM"

genai.configure(api_key=api_key)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("🤖 Ultimate AI Agent")
    st.caption("Powered by Gemini 1.5 Flash ⚡")
    
    selected_mode = st.radio(
        "Choose Tool:",
        ["🏠 Home", "🎥 Video Analyst", "🌐 Internet Search", "📄 Chat with PDF", "🧠 Memory Chat", "📊 Data Analyst", "🎨 AI Artist"]
    )
    
    st.divider()
    personality = st.selectbox("Act like...", ["Helpful Assistant", "Strict Boss", "Funny Friend", "Tamil Poet"])
    voice_on = st.toggle("Enable Voice Response")

# --- HELPER FUNCTIONS ---
def speak(text):
    if voice_on:
        try:
            tts = gTTS(text=text, lang='en')
            tts.save("response.mp3")
            st.audio("response.mp3")
        except:
            pass

def get_system_prompt():
    if personality == "Strict Boss": return "You are a strict boss. Be brief."
    if personality == "Funny Friend": return "You are a funny friend. Use emojis."
    if personality == "Tamil Poet": return "You are a Tamil poet. Answer poetically."
    return "You are a helpful AI assistant."

# --- 3. MODES ---

# 🏠 HOME
if selected_mode == "🏠 Home":
    st.title("🚀 The Ultimate AI Dashboard")
    st.markdown("""
    **Update:** Now running on **Gemini 1.5 Flash** (Stable & Fast).
    
    **Capabilities:**
    Text 📝 | Voice 🗣️ | Vision 👁️ | Data 📊 | Internet 🌐 | Video 🎥
    """)

# 🎥 VIDEO ANALYST
elif selected_mode == "🎥 Video Analyst":
    st.header("🎥 AI Video Analyst")
    st.caption("Upload a short video (MP4) -> I will watch and explain it.")
    
    video_file = st.file_uploader("Upload MP4 Video", type=["mp4"])
    
    if video_file:
        st.video(video_file)
        
        user_query = st.text_input("Ask about the video:", placeholder="What is happening in this video?")
        
        if st.button("Analyze Video"):
            with st.spinner("Uploading & Watching video..."):
                try:
                    # 1. Save temp file locally
                    with open("temp_video.mp4", "wb") as f:
                        f.write(video_file.getbuffer())
                    
                    # 2. Upload to Google AI File Manager
                    myfile = genai.upload_file("temp_video.mp4")
                    
                    # 3. Wait for processing
                    while myfile.state.name == "PROCESSING":
                        time.sleep(2)
                        myfile = genai.get_file(myfile.name)
                        
                    # 4. Generate Content (FIXED MODEL)
                    # "gemini-1.5-flash" is standard and stable
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt = f"{get_system_prompt()}\nUser Question: {user_query}\nAnswer based on the video."
                    
                    response = model.generate_content([myfile, prompt])
                    
                    st.success("Analysis Complete!")
                    st.write(response.text)
                    speak(response.text)
                    
                except Exception as e:
                    st.error(f"Error: {e}")

# 🌐 INTERNET SEARCH
elif selected_mode == "🌐 Internet Search":
    st.header("🌐 Internet Search")
    q = st.text_input("Search Query:")
    if st.button("Search") and q:
        with st.spinner("Searching..."):
            try:
                res = DDGS().text(q, max_results=3)
                if res:
                    txt = "\n".join([f"{r['title']}: {r['body']}" for r in res])
                    # FIXED MODEL
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    ans = model.generate_content(f"{get_system_prompt()}\nContext: {txt}\nQ: {q}").text
                    st.write(ans)
                    speak(ans)
                else:
                    st.warning("No results found.")
            except Exception as e: st.error(f"Error: {e}")

# 📄 PDF CHAT
elif selected_mode == "📄 Chat with PDF":
    st.header("📄 PDF Chat")
    f = st.file_uploader("Upload PDF", type=["pdf"])
    if f:
        reader = PyPDF2.PdfReader(f)
        txt = "".join([p.extract_text() for p in reader.pages])
        q = st.text_input("Ask PDF:")
        if q:
            # FIXED MODEL
            model = genai.GenerativeModel("gemini-1.5-flash")
            ans = model.generate_content(f"{get_system_prompt()}\nPDF: {txt}\nQ: {q}").text
            st.write(ans)
            speak(ans)

# 🧠 MEMORY CHAT
elif selected_mode == "🧠 Memory Chat":
    st.header("🧠 Memory Chat")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).write(m["content"])
    if u := st.chat_input():
        st.session_state.messages.append({"role":"user","content":u})
        st.chat_message("user").write(u)
        
        # FIXED MODEL
        model = genai.GenerativeModel("gemini-1.5-flash")
        h = "\n".join([f"{m['role']}:{m['content']}" for m in st.session_state.messages])
        a = model.generate_content(f"{get_system_prompt()}\nHistory:{h}\nUser:{u}").text
        
        st.chat_message("assistant").write(a)
        st.session_state.messages.append({"role":"assistant","content":a})
        speak(a)

# 📊 DATA ANALYST
elif selected_mode == "📊 Data Analyst":
    st.header("📊 Data Analyst")
    f = st.file_uploader("Upload CSV", type=["csv"])
    if f:
        try: df = pd.read_csv(f, encoding='latin1')
        except: df = pd.read_csv(f)
        st.dataframe(df.head())
        q = st.text_input("Ask Data:")
        if q:
            # FIXED MODEL
            model = genai.GenerativeModel("gemini-1.5-flash")
            ans = model.generate_content(f"{get_system_prompt()}\nData:{df.head(10).to_string()}\nQ:{q}").text
            st.write(ans)
            speak(ans)

# 🎨 AI ARTIST
elif selected_mode == "🎨 AI Artist":
    st.header("🎨 AI Artist")
    p = st.text_area("Prompt:")
    if st.button("Generate") and p:
        # FIXED MODEL
        model = genai.GenerativeModel("gemini-1.5-flash")
        enhanced = model.generate_content(f"Enhance: {p}").text
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(enhanced)}"
        st.image(url)