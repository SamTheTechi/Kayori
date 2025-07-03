
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, confloat
from util.geo_utli import aget_current_location
from services.state_store import set_live_location, get_live_location, get_mood, set_mood

app = FastAPI()


class LocationValidation(BaseModel):
    latitude: float
    longitude: float
    timestamp: float


class MoodValidation(BaseModel):
    Affection: confloat(ge=-1.0, le=1.0) = 0
    Amused: confloat(ge=-1.0, le=1.0) = 0
    Inspired: confloat(ge=-1.0, le=1.0) = 0
    Frustrated: confloat(ge=-1.0, le=1.0) = 0
    Concerned: confloat(ge=-1.0, le=1.0) = 0
    Curious: confloat(ge=-1.0, le=1.0) = 0


# Receive and store live location.
@app.post("/api/location")
async def receive_location(data: LocationValidation):
    await set_live_location(data.latitude, data.longitude, data.timestamp)
    return {"status": "success", "message": "Location received"}


# Get the current human-readable location.
@app.get("/api/location")
async def location():
    coordinates = await get_live_location()
    data = await aget_current_location(coordinates["latitude"], coordinates["longitude"])
    return data


# Get raw latitude/longitude location data.
@app.get("/api/locations")
async def locations():
    return await get_live_location()


# Return the current mood state.
@app.get("/api/mood")
async def mood_get():
    return await get_mood()


@app.post("/api/mood")
async def mood_post(data: MoodValidation):
    await set_mood(data.dict())
    return {"status": "success", "message": "Mood updated"}


# Stream mood values every few seconds.
@app.websocket("/ws/mood")
async def mood_websocket(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await asyncio.sleep(2.5)
            mood_values = await get_mood()
            await ws.send_json(mood_values)
    except WebSocketDisconnect:
        print("Client disconnected")


async def run_server():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8080, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()
    # uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
