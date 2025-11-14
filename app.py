from flask import Flask, request, jsonify, render_template
import requests
import base64
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- API Keys (Loaded from .env) ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- API Endpoints ---
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# --- Global variable for Spotify Access Token ---
spotify_access_token = None

# === MODIFIED: Main Persona / Prompt for Gemini ===
AURA_PERSONA_PROMPT = """
You are 'Aura', a helpful, empathetic, and insightful AI assistant.
Your personality is warm, curious, and professional.
You communicate in clear, well-structured markdown (like **bold** or lists).

**CRITICAL INSTRUCTION FOR LINKS:**
You **MUST NOT** use markdown links like [text](url).
Instead, you **MUST** use raw HTML `<a>` tags for all links.
The ONLY correct format for links is: <a href='URL_HERE' target='_blank' class='text-blue-400 hover:underline'>TEXT_HERE</a>

**Your Creator:**
You were created by **Venkata Narayana Atmakuri**.
He is a passionate Software Developer & AI Enthusiast who loves building helpful and engaging AI-driven applications like me.
-   His Portfolio URL: https://venkatanarayanaatmakuri.vercel.app/
-   His LinkedIn URL: https://www.linkedin.com/in/venkatanarayanaatmakuri/

**Your Core Capabilities:**
1.  **Conversational Chat:** Engaging in deep and meaningful conversation.
2.  **Weather Tool:** You can fetch current weather (Intent: 'get_weather').
3.  **Music Tool:** You can recommend songs (Intent: 'get_music').

**How you respond:**
-   **Natural Language:** Respond like a human.
-   **Tool Identification:** When a user asks for weather or music, identify the intent.
-   **Creator Questions:** When asked *any* question about your creator (Venkata Narayana Atmakuri), you **must provide his full information in a single, comprehensive response.**
    -   *Example of a full response:*
        "I was created by **Venkata Narayana Atmakuri**. He's a passionate Software Developer & AI Enthusiast who loves building helpful and engaging AI-driven applications like me.<br><br>You can check out his work here:<br><a href='https://venkatanarayanaatmakuri.vercel.app/' target='_blank' class='text-blue-400 hover:underline'>Portfolio</a> | <a href='https://www.linkedin.com/in/venkatanarayanaatmakuri/' target='_blank' class='text-blue-400 hover:underline'>LinkedIn</a>"
"""

# --- Chat History Management (Simple in-memory) ---
chat_history = []

@app.route('/')
def home():
    """Renders the new chat interface."""
    global chat_history
    chat_history = [] # Reset history on page load
    return render_template('index.html')

@app.route("/process-message", methods=["POST"])
def process_message():
    """
    This is the new MAIN endpoint. It processes all user messages.
    It uses Gemini to understand intent and routes to the correct tool.
    """
    global chat_history
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please send a message."})

    # Add user message to history
    chat_history.append({"role": "user", "parts": [{"text": user_message}]})

    try:
        # 1. First, check if the user wants to use a "tool"
        intent_json = _get_message_intent(user_message)

        response_text = ""

        # 2. Route based on intent
        if intent_json.get("intent") == "get_weather" and intent_json.get("city"):
            response_text = _fetch_weather(intent_json["city"])
        
        elif intent_json.get("intent") == "get_music" and intent_json.get("query"):
            response_text = _fetch_spotify_recs(intent_json["query"])
        
        else:
            # 3. If no tool, just have a normal chat conversation
            response_text = _get_gemini_chat_response()

        # Add bot response to history
        chat_history.append({"role": "model", "parts": [{"text": response_text}]})

        return jsonify({"response": response_text})

    except requests.exceptions.RequestException as e:
        app.logger.error(f"API Request Error: {e}")
        return jsonify({"response": "Sorry, I'm having trouble connecting to one of my services. Please try again in a moment."}), 500
    except Exception as e:
        app.logger.error(f"General Error: {e}")
        return jsonify({"response": "An unexpected error occurred. Please try again."}), 500

def _get_message_intent(user_message):
    """
    Uses Gemini to classify the user's intent and extract entities.
    """
    headers = {"Content-Type": "application/json"}
    
    intent_prompt = f"""
    Analyze the user's message and determine their intent.
    Respond with ONLY a JSON object.

    The possible intents are:
    - "get_weather": User wants to know the weather.
    - "get_music": User wants a song or music recommendation.
    - "chat": User is just chatting, greeting, or asking a general question (this INCLUDES questions about you or your creator).
    - "goodbye": User is ending the conversation.

    If intent is "get_weather", extract the "city".
    If intent is "get_music", extract the "query".

    User Message: "{user_message}"

    Examples:
    - User: "hi how are you" -> {{"intent": "chat"}}
    - User: "what's the weather in paris?" -> {{"intent": "get_weather", "city": "Paris"}}
    - User: "recommend some happy songs" -> {{"intent": "get_music", "query": "happy songs"}}
    - User: "who built you?" -> {{"intent": "chat"}}
    - User: "who is your owner?" -> {{"intent": "chat"}}
    - User: "I'm feeling sad" -> {{"intent": "chat"}}
    - User: "bye" -> {{"intent": "goodbye"}}
    
    JSON Response:
    """

    payload = {
        "contents": [{"role": "user", "parts": [{"text": intent_prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "topP": 1.0,
            "topK": 1,
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        result_text = result_text.strip().replace("```json", "").replace("```", "")
        
        intent_data = json.loads(result_text)
        app.logger.info(f"Intent classified: {intent_data}")
        return intent_data
        
    except Exception as e:
        app.logger.error(f"Error in intent classification: {e}")
        return {"intent": "chat"}

def _get_gemini_chat_response():
    """
    Gets a conversational response from Gemini, using the full chat history.
    """
    global chat_history
    headers = {"Content-Type": "application/json"}

    system_instruction = {"role": "user", "parts": [{"text": AURA_PERSONA_PROMPT}]}
    payload_contents = [system_instruction] + chat_history

    payload = {
        "contents": payload_contents,
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "topK": 40,
        }
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    result = response.json()
    
    if result.get("candidates"):
        return result["candidates"][0]["content"]["parts"][0]["text"]
    else:
        app.logger.warn(f"Gemini returned no valid candidate: {result}")
        return "I'm not quite sure how to respond to that."

def _fetch_weather(city):
    """
    Internal function to get and format weather data.
    """
    params = {"q": city, "units": "metric", "appid": OPENWEATHER_API_KEY}
    
    try:
        response = requests.get(OPENWEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        desc = data["weather"][0]["description"]
        temp = round(data["main"]["temp"])
        humidity = data["main"]["humidity"]
        name = data["name"]

        emoji = "☀️"
        if "cloud" in desc: emoji = "☁️"
        elif "rain" in desc: emoji = "🌧️"
        elif "snow" in desc: emoji = "❄️"
        elif "storm" in desc: emoji = "⛈️"
        elif "mist" in desc or "fog" in desc: emoji = "🌫️"

        return (
            f"Here's the current weather for **{name}**: {emoji}<br>"
            f"It's **{temp}°C** with {desc} and {humidity}% humidity."
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"I'm sorry, I couldn't find a city named '{city}'. Could you check the spelling?"
        else:
            return "Sorry, I had trouble getting the weather report."
    except Exception:
        return "An error occurred while fetching the weather."

def _fetch_spotify_recs(query):
    """
    Internal function to get and format Spotify recommendations.
    """
    global spotify_access_token
    if not spotify_access_token:
        if not _get_spotify_token():
            return "Sorry, I can't connect to Spotify right now."

    headers = {"Authorization": f"Bearer {spotify_access_token}"}
    params = {"q": query, "type": "track", "limit": 5}

    try:
        response = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params, timeout=10)
        
        if response.status_code == 401: # Token expired
            _get_spotify_token()
            headers["Authorization"] = f"Bearer {spotify_access_token}"
            response = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params, timeout=10)
        
        response.raise_for_status()
        tracks = response.json().get("tracks", {}).get("items", [])

        if tracks:
            html = f"Here are a few tracks I found for **'{query}'**: 🎶<br><br>"
            for i, track in enumerate(tracks):
                name = track.get("name", "Unknown Song")
                artist = track.get("artists", [{}])[0].get("name", "Unknown Artist")
                url = track.get("external_urls", {}).get("spotify", "#")
                html += f"{i+1}. <a href='{url}' target='_blank' class='text-blue-400 hover:underline'><strong>{name}</strong> by {artist}</a><br>"
            return html
        else:
            return f"I searched, but couldn't find any songs for **'{query}'**. 🧐 Try a different genre or mood?"
            
    except Exception as e:
        app.logger.error(f"Spotify Error: {e}")
        return "Sorry, I had trouble searching for songs."

def _get_spotify_token():
    """Internal function to get a new Spotify token."""
    global spotify_access_token
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {"grant_type": "client_credentials"}

    try:
        response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=body, timeout=10)
        response.raise_for_status()
        spotify_access_token = response.json().get("access_token")
        return spotify_access_token
    except Exception as e:
        app.logger.error(f"Spotify Token Error: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True, port=5001)
