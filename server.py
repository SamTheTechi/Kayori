import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI


class Validation(BaseModel):
    latitude: float
    longitude: float
    device: str


app = FastAPI()


@app.post("/")
async def recive_location(data: Validation):
    print(f"Received Location: {data.dict()}")
    return {"msg": "recieved!"}


async def run_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()
