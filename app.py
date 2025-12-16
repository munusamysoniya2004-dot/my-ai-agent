import streamlit as st
import google.generativeai as genai
import random 

# --- 1. SETUP ---
api_key = st.secrets["GEMINI_API_KEY"] 
genai.configure(api_key=api_key)

st.set_page_config(page_title="My Super AI Agent", page_icon="🤖")
st.title("🤖 Tamil Super Agent")
st.caption("Capabilities: 🌦️ Weather | 🏏 Cricket Scores")

# --- 2. THE TOOLS (Functions) ---

# Tool 1: Weather
def get_weather(city: str):
    """Returns weather for a city."""
    city = city.lower().strip()
    if "chennai" in city: return "Sunny, 32°C ☀️"
    elif "coimbatore" in city: return "Pleasant, 28°C 🌤️"
    elif "london" in city: return "Rainy, 15°C 🌧️"
    elif "mumbai" in city: return "Humid, 30°C ☁️"
    else: return "Unknown city data."

# Tool 2: Cricket Score (NEW!)
def get_cricket_score(team: str):
    """Returns the latest cricket score for a given team or match."""
    # Real app-la Cricbuzz API use pannuvom. Ippo Fake Data.
    team = team.lower()
    
    if "csk" in team or "chennai" in team:
        return "🏏 Match Update: CSK vs RCB. CSK won by 6 wickets! (Dhoni 25* off 10 balls)"
    elif "india" in team:
        return "🏏 Live: IND vs AUS. India 250/3 (45 Overs). Kohli batting on 95*."
    elif "mi" in team or "mumbai" in team:
        return "🏏 Result: MI lost to KKR by 15 runs."
    else:
        return "No live match found for this team."

# Tool List-la rendayum serkurom!
my_tools = [get_weather, get_cricket_score]

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 4. CHAT LOGIC ---
user_input = st.chat_input("Ask: 'CSK score?' or 'Chennai Weather?'")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    try:
        # Gemini with Tools
        model = genai.GenerativeModel('models/gemini-flash-latest', tools=my_tools)
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        with st.spinner("🤖 Thinking & Checking Tools..."):
            response = chat.send_message(user_input)
        
        bot_reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)
            
    except Exception as e:
        st.error(f"Error: {e}")