import chromadb
from chromadb import Settings
from archiq_backend import settings

class VectorDBConnection:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH, settings=Settings(allow_reset=True)
            )
        return cls._client



def get_collection(collection_name: str):
    client = VectorDBConnection.get_client()
    return client.get_or_create_collection(name=collection_name)
