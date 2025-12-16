import streamlit as st
import google.generativeai as genai
from PIL import Image
import io  # <-- Puthusa add pannirukom (For safety)

# --- 1. SETUP ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    # GitHub la podum pothu ithai delete pannanum!
    api_key = "AIzaSy_INGA_UNGA_KEY_IRUKKANUM" 

genai.configure(api_key=api_key)

st.set_page_config(page_title="Super AI Agent", page_icon="👁️")
st.title("👁️ AI with Vision")
st.caption("Chat with me OR Upload an image to ask questions!")

# --- 2. IMAGE UPLOADER (Fixed Version) ---
with st.sidebar:
    st.header("📸 Give me Sight")
    uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
    
    image = None
    if uploaded_file:
        try:
            # FIX: File-a direct-a open pannama, bytes-a maathi open panrom
            image_bytes = uploaded_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, caption="Uploaded Image", use_column_width=True)
        except Exception as e:
            st.error(f"❌ Image Error: Antha file sari illa. Vera photo try pannunga. ({e})")

# --- 3. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask about the image or anything else...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    try:
        with st.spinner("🤖 Analyzing..."):
            if image:
                # Vision Model
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                response = model.generate_content([user_input, image])
            else:
                # Text Only Model
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                response = model.generate_content(user_input)
        
        bot_reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)
            
    except Exception as e:
        st.error(f"Error: {e}")