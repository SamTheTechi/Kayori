import pytz
from datetime import datetime
from langchain_core.documents import Document


def memory_constructor(memory: str):

    # indian standard time
    ist_time = datetime.now(pytz.utc).astimezone(
        pytz.timezone("Asia/Kolkata")).isoformat()

    # pinecone format
    return Document(
        page_content=memory,
        metadata={"time": str(ist_time)}
    )


def location_constructor(lat: str, lon: str, suburb: str, city: str):

    # indian standard time
    ist_time = datetime.now(pytz.utc).astimezone(
        pytz.timezone("Asia/Kolkata")).isoformat()

    # pinecone format
    return Document(
        page_content=f"latitude: {lat}, longitude:{
            lon}, suburb:{suburb}, city: {city}",
        metadata={
            "time": str(ist_time)
        }
    )
