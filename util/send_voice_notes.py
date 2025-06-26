import os
import aiohttp
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


async def send_voice_note(reply: str):
    try:
        JOIN_DEVICE_ID: Optional[str] = os.getenv("JOIN_DEVICE_ID")
        JOIN_API_KEY: Optional[str] = os.getenv("JOIN_API_KEY")

        # send voice notes if and only if both the keys are prensent
        # this will not execut:
        if JOIN_DEVICE_ID and JOIN_API_KEY:
            url = (
                "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush"
                f"?apikey={JOIN_API_KEY}"
                f"&deviceId={JOIN_DEVICE_ID}"
                f"&text=say={reply}"
            )
            async with aiohttp.ClientSession() as client:
                await client.get(url)

    except Exception as e:
        print(e)
