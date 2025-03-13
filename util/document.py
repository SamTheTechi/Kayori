from datetime import datetime, timezone
from langchain_core.documents import Document


def memory_constructor(memory: str):
    return Document(
        page_content=memory,
        metadata={"time": str(datetime.now(timezone.utc).isoformat())}
    )
