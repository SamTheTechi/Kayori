
![Kaori Banner](banner.webp)


# 🌸 Kaori 🌸

Kaori is an interactive Multi Agentic girlfriend designed to deliver a charming and engaging conversational experience. She adapts her personality and mood based on past interactions,also capiable to using multiple tools and services to create dynamic, personalized experience.


## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Additional Notes](#additional-notes)

## Features

- **Conversational Agent:** Kaori is designed with a playful, human-like personality that adapts its mood based on predefined emotional states.
- **Permanent momory:** Uses Pinecone for storing and retrieving context from past interactions.
- **Location base exprience:** Automates tasks such as updating profile pictures, sending personalized greetings, messaging upon location changes, and weather upates daily.
- **Tool Integrations:** Connects with Spotify, Google calender, Tavily search, and more for to enhance user experience and engagement..
- **Discord Bot:** Operates on Discord to provide real-time conversation and interaction.

## Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.13.2 (or a compatible version, recommand to create venv)
- Required Python libraries (see `requirements.txt`)
- A Discord bot token (from the Discord Developer Portal)
- Firebase credentials (`firebase.json`)
- Google calender (`credentials.json`)
- Pinecone API keys
- Additional API keys for:
  - Tavily
  - HuggingFace Inference API (for embeddings)
  - Google Gemini
  - Spotify
  - WeatherAPI

## Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies:**

   Use pip to install all required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables:**

   Create a `.env` file in the project root and populate it with the necessary keys (see the [Environment Variables](#environment-variables) section).

4. **Firebase Setup:**

   Place your Firebase credentials JSON file (e.g., `firebase.json`) in the project root.

5. **Calender Setup:**

   Place your google calender JSON file (e.g., `credentials.json`) in the project root.

## Environment Variables

Ensure that the following environment variables are set in your `.env` file:

```dotenv
# API Keys for External Services
TAVILY_API_KEY=
EMBD=                              # HuggingFace API key for embedding model
API_KEY=                           # Google Gemini API key
PINECONE=                          # Pinecone API key
PINECONE2=                         # Secondary Pinecone API key if needed or same can be used
WEATHER_API=                       # Weather API key

# Discord Bot Credentials
DISCORD_BOT_TOKEN=                 # Discord bot token from Discord Developer Portal

# Spotify API Credentials
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT=

# Miscellaneous
TZ=                                # Your time zone, e.g., Asia/Kolkata
USER_ID=                           # Your Discord user ID (Developer mode enabled)
```

## Running the Application

The project concurrently starts both the Discord bot and a backend server. To run the application:

```bash
python app.py
```

## Docker Setup (recommend)

To run the application in a Docker container, use the Dockerfile provided in the project.

```dockerfile
FROM python:3.13.2-slim

WORKDIR /home/Asuna

RUN apt-get update && apt-get install -y \
  libgl1-mesa-glx \
  gcc \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --upgrade pip

COPY . .

EXPOSE 8080

CMD [ "python", "app.py" ]
```

### Building and Running the Docker Container

1. **Build the Docker Image:**

   ```bash
   docker build -t kaori .
   ```

2. **Run the Container:**

   ```bash
   docker run -p 80:8080 --env-file .env kaori
   ```

## Additional Notes

### Memory populate

To get an out-of-the-box experience, run the following command for a better experience:

```bash
python pastMemories.py
```
This script contains sample conversation pieces to populate the vector database.
You can edit the sample conversation pieces to customize your experience with the Karoi chatbot.

### Tasker setup

To enable Kaori to send location-based weather updates, you need to set up Tasker on your mobile device:

1. **Download and Install Tasker:**
   - Install Tasker from the [Google Play Store](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm).

2. **Create a New Task to Get Location:**
   - Open Tasker and navigate to the "Tasks" tab.
   - Click the `+` button to create a new task.
   - Name the task "GetLocation" and tap the checkmark.

3. **Add a Location Action:**
   - Click the `+` button inside the task and select "Location".
   - Set accuracy preferences as needed.
   - Add an action to "Variable Split" the retrieved location into separate latitude and longitude values.

4. **Store the Location in a JSON Format:**
   - Add a "Variable Set" action.
   - Name the variable `%JSON_BODY`.
   - Set its value to:
     ```json
     {
        "latitude": %LOCN1,
        "longitude": %LOCN2,
        "timestamp":"%TIME"
     }
     ```

5. **Send the Data to the Server:**
   - Add an "HTTP Request" action.
   - Set the method to `POST`.
   - In the "Server:Port" field, enter:
     ```
     http://<your-ip>:80 or 8080
     ```
   - Set the "Body" field to `%JSON_BODY`.

6. **Create a Profile for Recurring Location Updates:**
   - Go to the "Profiles" tab and click the `+` button.
   - Select "Time" and set it to trigger every `20` minutes.
   - Link this profile to the "GetLocation" task.

7. **Enable Tasker:**
   - Ensure Tasker is enabled so it runs in the background.

Now, Tasker will periodically send your location data to the Kaori server, allowing it to get to know more about you ;).

---
For any further questions or issues, please refer to the documentation of the respective APIs and services integrated within this project or just contact the SamTheTechi

## Hit a star for supporting me and my Kaori!
