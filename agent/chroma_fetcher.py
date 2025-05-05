from typing import Dict, List, Tuple, Any

from .vector_db import VectorDBConnection


class ChromaDBFetcher:
    def __init__(self):
        self.chroma_client = VectorDBConnection.get_client()

    def fetch_collection_data(self, collection_name: str) -> Dict[str, Any]:
        collection = self.chroma_client.get_collection(name=collection_name)
        data = collection.get()
        return data

    def fetch_all_data_all_collections(self) -> List[Tuple[str, Dict[str, Any]]]:
        collections = self.chroma_client.list_collections()
        print(f"Найдено {len(collections)} коллекций в ChromaDB")
        
        results = []
        for collection in collections:
            try:
                collection_name = collection.name
                data = self.fetch_collection_data(collection_name)
                results.append((collection_name, data))
                print(f"Данные из коллекции '{collection_name}' успешно получены")
            except Exception as e:
                print(f"Ошибка при получении данных из коллекции '{collection.name if hasattr(collection, 'name') else collection}': {str(e)}")
        
        return results

    def list_collections(self):
        collections = self.chroma_client.list_collections()
        if not collections:
            print("⚠️ В ChromaDB нет коллекций!")
            return []
        collection_names = [col.name for col in collections]
        print("📂 Доступные коллекции в ChromaDB:", collection_names)
        return collection_names

    def count_records(self, collection_name):
        try:
            collection = self.chroma_client.get_collection(collection_name)
            record_count = len(collection.get()["ids"])
            print(f"📊 Количество записей в '{collection_name}': {record_count}")
            return record_count
        except Exception as e:
            print(f"⚠️ Ошибка при получении данных из '{collection_name}': {e}")
            return 0

    def fetch_all_data(self, collection_name):
        try:
            collection = self.chroma_client.get_collection(collection_name)
            print(f"🔄 Получаем все данные из коллекции '{collection_name}'...")
            all_data = collection.get(include=["embeddings", "metadatas", "documents"])

            if not all_data or not all_data.get("ids"):
                print("⚠️ В коллекции нет данных!")
                return []

            documents = []
            for doc_id, doc_text, metadata, embedding in zip(
                    all_data.get("ids", []),
                    all_data.get("documents", []),
                    all_data.get("metadatas", []),
                    all_data.get("embeddings", [])
            ):
                if hasattr(embedding, "tolist"):
                    embedding_conv = embedding.tolist()
                else:
                    embedding_conv = embedding

                documents.append({
                    "id": doc_id,
                    "text": doc_text,
                    "metadata": metadata or {},
                    #"embeddings": embedding_conv
                })

            print(f"✅ Получено {len(documents)} записей из коллекции '{collection_name}'!")
            return documents

        except Exception as e:
            print(f"⚠️ Ошибка при получении данных из '{collection_name}': {e}")
            return []

