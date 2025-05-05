# app/services/vector_searcher.py
from icecream import ic
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from archiq_backend import settings
from .searcher_llm import SearcherLLM
from .vector_db import VectorDBConnection


class VectorSearcher:
    def __init__(self, collection_name: str, top_k=3):
        self.chroma_client = VectorDBConnection.get_client()
        self.embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
        self.chroma_collection = self.chroma_client.get_collection(collection_name)
        self.vector_store = ChromaVectorStore(self.chroma_collection)
        self.llm = SearcherLLM.get_llm()
        self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store, embed_model=self.embed_model, llm=self.llm)
        self.query_engine = self.index.as_query_engine(similarity_top_k=top_k, verbose=True)

    def search_vector(self, query):
        response = self.query_engine.query(query.lower())
        return response
