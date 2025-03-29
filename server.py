import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from util.store import natures, location, update_location, current_pfp


class Validation(BaseModel):
    latitude: float
    longitude: float
    timestamp: float


app = FastAPI()


@app.post("/")
async def recive_location(data: Validation):
    update_location(data.latitude, data.longitude, data.timestamp)
    print(f"Received Location: {data.dict()}")
    return {"msg": "recieved!"}


@app.get("/mood")
async def get_mood():
    return natures


@app.get("/pfp")
async def get_pfp():
    return current_pfp["img"]


@app.get("/location")
async def get_location():
    return location


async def run_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()
