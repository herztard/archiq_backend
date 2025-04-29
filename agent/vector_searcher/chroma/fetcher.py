from agent.vector_searcher.vector_db import VectorDBConnection


class ChromaDBFetcher:
    def __init__(self):
        self.chroma_client = VectorDBConnection.get_client()

    def list_collections(self):
        collections = self.chroma_client.list_collections()
        if not collections:
            print("⚠️ В ChromaDB нет коллекций!")
            return []
        collection_names = [col for col in collections]
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


    def fetch_all_data_all_collections(self):
        all_data = {}
        collections = self.list_collections()
        for coll in collections:
            data = self.fetch_all_data(coll)
            all_data[coll] = data
        return all_data
