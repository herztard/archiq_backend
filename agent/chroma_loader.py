from decimal import Decimal
from typing import List, Optional, Dict
import logging

from django.db import connection
from django.conf import settings
from llama_index.core import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from .vector_db import VectorDBConnection


class ChromaDBLoader:
    def __init__(self):
        self.chroma_client = VectorDBConnection.get_client()
        
        try:
            self.embedding_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
        except NotImplementedError as e:
            if "Cannot copy out of meta tensor" in str(e):
                import torch
                from sentence_transformers import SentenceTransformer
                
                print("Using alternative model loading method for newer PyTorch versions")
                model = SentenceTransformer(settings.EMBEDDING_MODEL)
                if hasattr(model, "to_empty"):
                    try:
                        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                        model = model.to_empty(device=device)
                        model.eval()
                        self.embedding_model = HuggingFaceEmbedding(model=model)
                    except Exception as inner_e:
                        print(f"Failed with to_empty() method: {inner_e}")
                        with torch.no_grad():
                            model = SentenceTransformer(settings.EMBEDDING_MODEL, device="cpu")
                            self.embedding_model = HuggingFaceEmbedding(model=model)
                else:
                    print("Model doesn't have to_empty() method, falling back to CPU")
                    with torch.no_grad():
                        model = SentenceTransformer(settings.EMBEDDING_MODEL, device="cpu")
                        self.embedding_model = HuggingFaceEmbedding(model=model)
            else:
                raise

    def fetch_data(self, table_name: str, columns: List[str]):
        with connection.cursor() as cursor:
            query = f"SELECT {', '.join(columns)} FROM {table_name};"
            cursor.execute(query)
            column_names = [col[0] for col in cursor.description]
            result = [dict(zip(column_names, row)) for row in cursor.fetchall()]
            return result

    def load_data(
            self,
            table: str,
            sql_table: str,
            id_column: str,
            text_columns: List[str],
            metadata_columns: Optional[List[str]] = None,
            column_names: Optional[Dict[str, str]] = None
    ):
        columns_set = {id_column}
        columns_set.update(text_columns)
        if metadata_columns:
            columns_set.update(metadata_columns)
        columns = list(columns_set)

        print(f"🔄 Загружаем данные из таблицы '{sql_table}' для колонок: {columns} ...")
        rows = self.fetch_data(sql_table, columns)
        if not rows:
            print(f"⚠️ Нет данных в таблице '{sql_table}'!")
            return

        print(f"✅ Найдено {len(rows)} записей из таблицы '{sql_table}'!")

        documents = []
        for row in rows:
            doc_id = str(row[id_column])
            texts = []
            for col in text_columns:
                value = row.get(col)
                if value:
                    if column_names and col in column_names.keys():
                        if column_names[col] == "":
                            texts.append(str(value))
                        else:
                            texts.append(f"{column_names[col]}: {value}")
                    else:
                        texts.append(str(value))
            text_content = "\n".join(texts)

            metadata = {}
            if metadata_columns:
                for col in metadata_columns:
                    value = row.get(col)
                    if isinstance(value, Decimal):
                        value = float(value)
                    metadata[col] = value
            metadata["id"] = row.get(id_column)
            documents.append(Document(doc_id=doc_id, text=text_content, metadata=metadata))

        collection = self.chroma_client.get_or_create_collection(table)

        doc_texts = [doc.text.lower() for doc in documents]
        try:
            embeddings = self.embedding_model._get_text_embeddings(doc_texts)
            
            ids = [doc.doc_id for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            collection.add(
                ids=ids,
                documents=doc_texts,
                metadatas=metadatas,
                embeddings=embeddings
            )

            num_records = len(collection.get()["ids"])
            print(f"📊 Записей в коллекции '{table}' ChromaDB: {num_records}")
            print("✅ Данные успешно загружены, эмбеддинги вычислены и индексированы в ChromaDB!")
        except Exception as e:
            print(f"❌ Ошибка при создании эмбеддингов или добавлении в коллекцию: {e}")
            raise