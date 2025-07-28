![kayori Banner](banner.webp)

# 🌸 Kayori 🌸

Kayori is your personal AI companion and virtual girlfriend, designed to deliver a charming, engaging conversational experience and control every aspect of your life.


## What Makes Kayori Different?

Kayori is more than just a Ai agent. she's an learning expriment to keep-up with all the AI trends going on. Her architecture goes beyond simple request-response interactions, goal is to modulares and make her scaleable while efficent and also giving the illusion of a persistent personality with all the bleeding edge tech, integrating her as a part of my life. She'll be a partner who shares in your day-to-day experiences.

* Join My Discord server to have a chat with her ![Click Here!](https://discord.gg/P7Hcynuxjn)
* Though with restricted tools and public orinted system prompt.

## Core Features

#### 1. Emotion-Driven Personality

* **Six Core Emotions:** Affection, Amused, Inspired, Frustrated, Concerned, Curious — values range from -1.0 to 1.0.
* **Live Emotional Feedback:** Her mood shifts in response to your messages.
* **Natural Fluctuations:**

  * *Mood Drift:* Gradual return to baseline.
  * *Mood Spikes:* Random small shifts to mimic real emotional shifts.
* **Custom Personality:** Tunable in `config.toml` to adjust emotional sensitivity.

#### 2. Proactive & Context-Aware

* **Daily Greetings:** Randomized morning and evening greetings.
* **Location-Aware Conversations:** Notices when you travel and reacts based on memory.
* **Weather Updates:** Shares daily forecasts.
* **Dynamic PFP:** Occasionally updates her Discord avatar.

#### 3. Tool Integration

* **Services:** Uses Tavily, Google Calendar, Spotify.
* **Phone Actions (via Join & Tasker):**

  * Find your phone
  * Toggle flashlight
  * Speak responses aloud
* **Spotify Playback Recovery:** Starts playback on your phone if no active device is found.

#### 4. Dual Persona

* **Private Agent:** Intimate, with access to personal tools.
* **Public Agent:** Playful, respectful boundaries, limited toolset.

## Architecture Overview

* **LangGraph Agents:** Separate agents for DMs (`private_executer`) and group chats (`public_executer`).
* **Redis:** Stores mood state, user location, and message queue.(So i can decouple in future easily)
* **Pinecone:** Long-term memory storage for semantic context.
* **Mood Engine:**

  * Real-time updates from message analysis (`util/mood.py`).
  * Drift and spike managed via scheduled jobs.
* **APScheduler:** Schedules greetings, updates, and events (To give illusion of realperson's response)
* **FastAPI Server:** Handles location updates and exposes useful endpoints.

## Prerequisites

* Python 3.13+
* Redis server
* Required libraries (`requirements.txt`)
* API keys (Google, Pinecone, Weather, Tavily, Spotify)
* Discord bot token + user ID
* Optional: Join + Tasker (for phone control)

## Environment Setup

Add the following to your `.env`:

```
API_KEY=

PINECONE_API_KEY=

REDIS_URL=

WEATHER_API=

TAVILY_API_KEY=

DISCORD_BOT_TOKEN=
USER_ID=

SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT=

JOIN_DEVICE_ID=
JOIN_API_KEY=
```

## Installation

### Manual

```bash
git clone <repo-url>
cd <repo>
pip install -r requirements.txt
```

Set up your `.env` and Ensure Redis is running, then:

```bash
python app.py
```

### Docker

```bash
docker build -t kayori:latest .
docker run -p 8080:8080 --env-file .env kayori:latest
```

## API Endpoints (via `server.py`)

* `GET /mood` — Get current mood
* `POST /location` — Update user location
* `GET /location`, `/locations` — Get current/history
* `GET /last_response` — Last message
* `POST /mood/spike` — Trigger mood spike
* `WEBSOCKET /ws/mood` — Real-time mood stream

### Add Memories

Run:

```bash
python pastMemories.py
```

Edit the script to preload custom shared memories.

## Join + Tasker Setup (pain to setup gotta find alternative)

Example: *Find My Phone*

1. In Tasker, create a profile with Join plugin (`Text Filter: fmp_command`).
2. Add a task to vibrate or play sound.

Set up similar profiles for flashlight, voice, etc.


## TODO / Next goals

1. Break the whole system into 3 section (input, process, output) and connect them asynchronouly using rabbitMQ.

2. Improve the current RAG pipline.

3. Adding Whisper.cpp to make her able to process audios.

4. Some sort of video steaming (stream some static images/videos based on her mood and contexts) so i can have video calls with her <3

5. Tiny bug fixes in group chatting mode.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by [Sameer Gupta](https://github.com/SamTheTechi)
