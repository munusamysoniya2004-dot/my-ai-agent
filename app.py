import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import urllib.parse
from duckduckgo_search import DDGS
import PyPDF2
from gtts import gTTS
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Suresh's Ultimate AI", page_icon="🤖", layout="wide")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    # 👇 UNGA API KEY INGA PODUNGA
    api_key = "AIzaSyBG9FHTRxsUMSshxx6IPoz3SBoDZijKE9E"

genai.configure(api_key=api_key)

# --- 2. SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.title("🤖 Ultimate AI Agent")
    st.caption("Built by Suresh | Hour 35")
    
    # Navigation
    selected_mode = st.radio(
        "Choose Tool:",
        ["🏠 Home", "🌐 Internet Search", "📄 Chat with PDF", "🧠 Memory Chat", "📊 Data Analyst", "🎨 AI Artist"]
    )
    
    st.divider()
    
    # Hour 34: Custom Personality 🎭
    st.subheader("⚙️ AI Personality")
    personality = st.selectbox("Act like...", ["Helpful Assistant", "Strict Boss", "Funny Friend", "Tamil Poet"])
    
    # Hour 33: Voice Toggle 🗣️
    voice_on = st.toggle("Enable Voice Response")

# --- HELPER: TEXT TO SPEECH ---
def speak(text):
    if voice_on:
        try:
            tts = gTTS(text=text, lang='en')
            tts.save("response.mp3")
            st.audio("response.mp3")
        except:
            st.warning("Audio generation failed.")

# --- HELPER: SYSTEM PROMPT ---
def get_system_prompt():
    if personality == "Strict Boss":
        return "You are a strict corporate boss. Be brief, professional, and slightly demanding."
    elif personality == "Funny Friend":
        return "You are a funny friend. Use emojis, jokes, and casual slang (Thanglish allowed)."
    elif personality == "Tamil Poet":
        return "You are a Tamil poet. Answer poetically, preferably in Tamil or poetic English."
    else:
        return "You are a helpful AI assistant."

# --- 3. MODES ---

# 🏠 HOME
if selected_mode == "🏠 Home":
    st.title("🚀 The Ultimate AI Dashboard")
    st.markdown(f"""
    Welcome! I am running in **{personality}** mode.
    
    **New Features Added:**
    * 📄 **PDF RAG:** I can read your documents.
    * 🗣️ **Voice:** I can speak back to you.
    * 🎭 **Persona:** I can change my character.
    """)

# 🌐 INTERNET SEARCH
elif selected_mode == "🌐 Internet Search":
    st.header("🌐 Live Internet Search")
    query = st.text_input("What's happening in the world?")
    if st.button("🔍 Search"):
        if query:
            with st.spinner("Searching..."):
                try:
                    results = DDGS().text(query, max_results=4)
                    search_data = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                    
                    model = genai.GenerativeModel("models/gemini-flash-latest")
                    prompt = f"{get_system_prompt()}\nUser asked: {query}\nWeb Results: {search_data}\nSummarize this."
                    
                    response = model.generate_content(prompt).text
                    st.write(response)
                    speak(response) # Voice Output
                except Exception as e:
                    st.error(f"Error: {e}")

# 📄 CHAT WITH PDF (New Integration!)
elif selected_mode == "📄 Chat with PDF":
    st.header("📄 Chat with Documents")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    
    if pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()
            
        st.success("PDF Loaded! Ask questions below.")
        
        question = st.text_input("Ask about the PDF:")
        if question:
            model = genai.GenerativeModel("models/gemini-flash-latest")
            prompt = f"{get_system_prompt()}\nContext from PDF:\n{pdf_text}\n\nQuestion: {question}"
            response = model.generate_content(prompt).text
            st.write(response)
            speak(response)

# 🧠 MEMORY CHAT
elif selected_mode == "🧠 Memory Chat":
    st.header(f"🧠 Chat ({personality} Mode)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Type something..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Context Logic
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        prompt = f"{get_system_prompt()}\nHistory:\n{history_text}\nUser: {user_input}"
        
        model = genai.GenerativeModel("models/gemini-flash-latest")
        response = model.generate_content(prompt).text
        
        with st.chat_message("assistant"):
            st.write(response)
            speak(response) # Voice Output
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# 📊 DATA ANALYST
elif selected_mode == "📊 Data Analyst":
    st.header("📊 AI Data Analyst")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file, encoding='latin1')
        st.dataframe(df.head())
        q = st.text_input("Ask about data:")
        if q:
            model = genai.GenerativeModel("models/gemini-flash-latest")
            prompt = f"{get_system_prompt()}\nData: {df.head(20).to_string()}\nQuestion: {q}"
            res = model.generate_content(prompt).text
            st.write(res)
            speak(res)

# 🎨 AI ARTIST
elif selected_mode == "🎨 AI Artist":
    st.header("🎨 AI Artist")
    prompt = st.text_area("Describe image:")
    if st.button("Generate"):
        model = genai.GenerativeModel("models/gemini-flash-latest")
        enhanced = model.generate_content(f"Enhance prompt: {prompt}").text
        st.caption(f"Enhanced: {enhanced}")
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(enhanced)}"
        st.image(url)