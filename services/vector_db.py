import os
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def initalise_vector_db(name: str = "kayori", dimension: int = 768) -> PineconeVectorStore:
    API_KEY = os.getenv("PINECONE")
    if not API_KEY:
        raise ValueError("Pinecode api_key not found")

    pc = Pinecone(API_KEY)

    if name not in [index["name"] for index in pc.list_indexes()]:
        pc.create_index(name, dimension=dimension, spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        ))

    pineconeIndex = pc.Index(name)

    embedding = GoogleGenerativeAIEmbeddings(
        google_api_key=os.getenv("API_KEY"),
        model="models/embedding-001"
    )

    return PineconeVectorStore(
        embedding=embedding, index=pineconeIndex)
