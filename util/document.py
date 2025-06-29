from util.get_current_time import get_current_time
from langchain_core.documents import Document


# Constructs a Document object for location data.
def location_constructor(lat: str, lon: str, suburb: str, city: str):

    # pinecone format
    return Document(
        page_content=f"latitude: {lat}, longitude:{
            lon}, suburb:{suburb}, city: {city}",
        metadata={
            "time": str(get_current_time())
        }
    )
