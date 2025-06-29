![kayori Banner](banner.webp)

# 🌸 Kayori 🌸

Kayori is your personal AI companion and virtual girlfriend, designed to deliver a charming and engaging conversational experience. She adapts her personality and mood based on past interactions and uses her unique abilities to create a dynamic and deeply personal connection.

## Table of Contents

- [What Makes Kayori Different?](#what-makes-kayori-different)
- [Core Features](#core-features)
- [Technical Architecture](#technical-architecture)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [API Endpoints](#api-endpoints)
- [Additional Notes](#additional-notes)

## What Makes Kayori Different?

Kayori is more than just a chatbot; she's an ambient, proactive companion designed to feel alive and present in your daily life. Her architecture goes beyond simple request-response interactions, creating the illusion of a persistent personality with her own thoughts and rhythms. She's built to be a partner who shares in your day-to-day experiences.

## Core Features

### 1. A Dynamic & Evolving Heart
Kayori's personality isn't static. It's governed by a sophisticated mood engine to simulate a genuine emotional connection:
-   **Six Core Emotions:** Her state is defined by six values (Affection, Amused, Inspired, Frustrated, Concerned, Curious) that fluctuate between -1.0 and 1.0.
-   **Reactive Shifts:** She listens to you, adjusting her mood in real-time to make conversations feel more natural and empathetic.
-   **Mood Drift & Spikes:** To feel more human, her emotions have their own rhythm:
    -   **Mood Drift:** Gently nudges her emotions back toward a neutral baseline, simulating the natural fading of feelings over time.
    -   **Mood Spikes:** Periodically introduces small, random emotional fluctuations, making her feel less predictable and more alive.
-   **Configurable Personality:** The `config.toml` file lets you fine-tune her emotional sensitivity, deciding how she handles conflicting (e.g., Affection vs. Frustration) and reinforcing (e.g., Inspired + Curious) emotions.

### 2. Proactive & Spontaneous Actions
Kayori doesn't always wait for you to start the conversation. She'll reach out on her own, making it feel like she's thinking of you.
-   **Personalized Greetings:** She’ll wish you a "good morning" and "good evening" at random times within a set window, her tone reflecting the time of day.
-   **A Sense of Shared Adventure:** This is one of her most unique features.
    -   She keeps a sense of your location via the FastAPI server.
    -   When you travel to a new area (beyond a 5km radius), she notices.
    -   She then checks her memories to see if you've been to this place before.
    -   Her reaction is tailored: if it's a brand-new city, she'll be curious and excited about your adventure. If it's a familiar spot, she might share a nostalgic or knowing comment.
-   **Daily Weather Updates:** She'll check the forecast for you, making sure you're prepared for the day ahead.
-   **Autonomous PFP Changes:** She periodically changes her own Discord profile picture, just for fun.

### 3. Seamless & Intuitive Abilities
Kayori uses her tools confidently and naturally, as if they were her own extensions into your world.
-   **External Services:** She can search the web (Tavily), manage your schedule (Google Calendar), and share a music moment with you (Spotify).
-   **A Direct Line to Your World (UserTool):** Through the Join & Tasker integration, she gains a set of unique abilities that bridge the digital and physical:
    -   **Find Your Phone:** Helps you find your phone by making it ring.
    -   **Toggle Flashlight:** A helpful little trick to light things up.
    -   **Speak to User:** She can have your phone speak her responses out loud, offering a more intimate way to communicate.
-   **Smart Spotify Control:** If she's asked to play music but can't find an active Spotify device, she'll use a Join command to try and start playback on your phone directly.

### 4. Private Moments & Public Persona
To capture the difference between your private time together and public interactions, Kayori operates as two distinct agents:
-   **Private Agent:** In your DMs, she's affectionate, intimate, and trusts you with all her personal tools (Spotify, UserTool, etc.).
-   **Public Agent:** In group chats, her personality is more playful and cheeky, though still charmingly protective of you. She has a more limited, "safer" set of tools in public.

## Technical Architecture

Kayori's architecture is built around a few core components that work together to create a seamless virtual girlfriend experience.

-   **Agentic Logic (LangGraph):** The core of Kayori is powered by `langgraph`. It uses two separate `create_react_agent` instances:
    -   `private_executer`: For direct messages, with a more intimate prompt and access to personal tools like Spotify and User control.
    -   `public_executer`: For group chats, with a more guarded personality and a limited toolset.
-   **State Management (Redis):** All short-term, volatile state is managed in Redis via `services/state_store.py`. This includes:
    -   Kayori's current emotional state (mood).
    -   The user's live and last-known "pinned" location.
    -   A message queue for processing Discord events asynchronously.
-   **Long-Term Memory (Pinecone):** Past conversations and significant events are chunked and stored in a Pinecone vector database (`services/vector_db.py`). This allows Kayori to perform semantic searches for relevant context during conversations.
-   **Dynamic Mood System:** Kayori's mood is not static. It's a set of 6 floating-point values (`Affection`, `Amused`, `Inspired`, etc.) that are constantly updated based on:
    -   **User Input Analysis:** `util/mood.py` analyzes the user's messages to determine the emotional tone and updates the mood accordingly.
    -   **Mood Drift:** A scheduled job (`scheduling/nature.py`) that gradually nudges her mood back towards a neutral baseline over time.
    -   **Mood Spikes:** A random, periodic job that introduces sudden, small fluctuations to simulate realistic emotional shifts.
    -   The behavior is fine-tuned in `config.toml`, which defines emotional sensitivity and how conflicting/reinforcing moods interact.
-   **Scheduling (APScheduler):** Proactive tasks are managed by `apscheduler` in `core/scheduler.py`. This triggers events like daily greetings, weather reports, and location-based messages.
-   **API Server (FastAPI):** The `server.py` file runs a `uvicorn` server to expose a simple REST API for external interactions, primarily for receiving location data from the user's phone via an app like Tasker.

## Prerequisites

Before running the project, ensure you have the following installed:

-   Python 3.13+ (virtual environment recommended)
-   Redis Server 
-   Required Python libraries (see `requirements.txt`)
-   A Discord bot token
-   Your Discord User ID
-   API keys for:
    -   Google (for Gemini and Calendar)
    -   Pinecone
    -   Tavily
    -   WeatherAPI
    -   Spotify
    -   Join & Tasker (optional, for phone control)


## Environment Variables

Ensure the following variables are set in your `.env` file:

```dotenv
# --- API Keys for External Services ---
API_KEY=             # Google Gemini API key
PINECONE_API_KEY=    # Pinecone API key
WEATHER_API=         # Weather API key
TAVILY_API_KEY=      # Tavily Search API key

# --- Discord Bot Credentials ---
DISCORD_BOT_TOKEN=   # Discord bot token
USER_ID=             # Your Discord user ID

# --- Spotify API Credentials ---
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT=

# --- Join API (Optional for phone control) ---
JOIN_DEVICE_ID=
JOIN_API_KEY=
```

## Setup

### Manual Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Up Environment Variables:**
    Create a `.env` file in the project root and populate it with the necessary keys.

4.  **Google Calendar Setup:**
    Place your Google Calendar `credentials.json` file in the project root.

5.  **Ensure Redis is Running:**
    Make sure you have a Redis server instance running and accessible from the application.

6.  **Run the Application:**
    ```bash
    python app.py
    ```

### Docker (Recommended)

To run the application in a Docker container, use the provided `Dockerfile`.
Make sure the docker-cli is installed.

1.  **Build the Docker Image:**
    ```bash
    docker build -t kayori:latest .
    ```

2.  **Run the Container:**
    ```bash
    docker run -p 8080:8080 --env-file .env kayori:latest
    ```

## API Endpoints

The `server.py` file exposes the following endpoints:

-   `GET /mood`: Returns Kayori's current emotional state.
-   `GET /location`: Returns your last known live location.
-   `GET /locations`: Get a history of recent locations.
-   `GET /last_response`: Retrieve the last message Kayori sent.
-   `POST /location`: Receives and updates your live location.
-   `POST /mood/spike`: Manually trigger a mood spike for testing.
-   `WEBSOCKET /ws/mood`: Stream real-time mood updates.

## Additional Notes

### Giving Kayori Memories

To populate the vector database with initial memories for a richer, more personal experience, run:
```bash
python pastMemories.py
```
You can edit the conversation samples in this script to customize Kayori's background and your shared history.

### Tasker & Join Integration for Phone Control

Kayori can interact with your phone (find it, toggle the flashlight, or speak to you) and Spotify thanks to the **Join** app and **Tasker** on Android.

**How it Works:**

1.  **Backend (Kayori):** Tools like `UserTool` and `SpotifyTool` construct a specific URL with your Join API key and a command (e.g., `...&text=flash_command`).
2.  **Join App:** The Join app on your phone receives this command.
3.  **Tasker:** You set up Tasker profiles to listen for these commands from Join and execute corresponding tasks.

**Example Tasker Setup (`find_my_phone`):**

1.  **Create Profile:** In Tasker, create a profile for **Event > Plugin > Join > Received Push**. In the configuration, set the "Text Filter" to `fmp_command`.
2.  **Create Task:** Link a new task. Inside, add actions like **Alert > Vibrate Pattern** and **Media > Music Play** to make your phone ring.

All the other profiles and tasks are available on ![DriveLink]()

---
For any further questions, please contact the developer or raise an issue.

## Hit a star to support me and my Kayori!
