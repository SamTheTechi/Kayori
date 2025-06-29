
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from services.state_store import set_live_location, get_live_location, get_mood


class Validation(BaseModel):
    latitude: float
    longitude: float
    timestamp: float


app = FastAPI()


@app.post("/location")
async def receive_location(data: Validation):
    await set_live_location(data.latitude, data.longitude, data.timestamp)

    print(f"Received Location: {data.dict()}")

    return {"msg": "Location received!"}


@app.get("/mood")
async def mood():
    return await get_mood()


@app.get("/location")
async def location():
    return await get_live_location()


# TODO: Implement a WebSocket endpoint for real-time mood updates.
# @app.websocket("/ws/mood")

# TODO: Implement an endpoint to get location history.
# @app.get("/locations")

# TODO Implement an endpoint to manually trigger a mood spike.
# @app.post("/mood/spike")

# TODO: Implement an endpoint to get the last response from Kayori.
# @app.get("/last_response")


async def run_server():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8080, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()
