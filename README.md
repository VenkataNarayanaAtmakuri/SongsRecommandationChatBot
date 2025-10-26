# SongsRecommandationChatBot
-----

# Aura - AI Song Recommendation Chatbot

A full-stack AI chatbot named Aura, built with a Python (Flask) backend and a modern "glassmorphism" UI. Uses Google Gemini for natural language intent classification to provide weather (OpenWeatherMap) and song recommendations (Spotify).

<img width="1918" height="870" alt="image" src="https://github.com/user-attachments/assets/124e3f2b-72f2-422e-9e88-9523cb77fcb5" />


## ✨ Core Features

  * **Natural Language Understanding:** Aura uses Google Gemini to understand *what* a user means, not just what they type. It can differentiate between a general chat, a request for weather, and a request for music.
  * **AI-Driven Conversation:** The bot can hold natural conversations, answer general knowledge questions, and remember the chat history to handle follow-up questions.
  * **Real-Time Weather:** Connects to the **OpenWeatherMap API** to fetch and display current weather data for any city.
  * **Music Recommendations:** Connects to the **Spotify API** to provide song recommendations based on mood, genre, or artist.
  * **Personalized Creator Info:** The bot is programmed to know who its creator is and can provide your professional portfolio and LinkedIn links when asked.
  * **Polished UI/UX:**
      * A full-screen, responsive "frosted glass" (glassmorphism) UI.
      * An animated gradient background.
      * A dynamic welcome screen with clickable example prompts.
      * A "Clear Chat" confirmation modal to prevent accidental deletion.
  * **Markdown Rendering:** Bot responses are correctly parsed from markdown to display **bold text**, lists, and clean HTML links.

## 🛠️ Tech Stack

  * **Backend:** Python 3, Flask
  * **AI & Language Model:** Google Gemini
  * **APIs:** OpenWeatherMap (Weather), Spotify (Music)
  * **Frontend:** HTML5, Tailwind CSS, JavaScript
  * **Deployment:** Render (using Gunicorn)

## 🚀 Getting Started

To run this project locally, you will need to have Python 3 installed.

### 1\. Clone the Repository

```bash
git clone https://github.com/VenkataNarayanaAtmakuri/SongsRecommandationChatBot.git
cd SongsRecommandationChatBot
```

### 2\. Create a Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4\. Set Up Environment Variables

Create a file named `.env` in the root of the project folder. This file holds all your secret API keys.

```.env
GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
OPENWEATHER_API_KEY=YOUR_OPENWEATHER_KEY_HERE
SPOTIFY_CLIENT_ID=YOUR_SPOTIFY_ID_HERE
SPOTIFY_CLIENT_SECRET=YOUR_SPOTIFY_SECRET_HERE
```

### 5\. Run the Application

```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:5000` to see the bot in action.

## ☁️ Deployment

This application is deployed on **Render**. The deployment is configured via a `Procfile` (using `gunicorn`) and the `requirements.txt`. All API keys are securely stored in Render's environment variable manager.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
