import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

class VectorDB:
    def __init__(self, db_path: str):
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        # Usamos un modelo local ligero para los embeddings
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="project_context",
            embedding_function=self.emb_fn
        )

    def add_documents(self, documents: list, ids: list, metadatas: list = None):
        """Añade o actualiza documentos en la colección."""
        self.collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def query(self, query_text: str, n_results: int = 5):
        """Busca los fragmentos más relevantes para una consulta."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        # Formatear resultados para el prompt
        context_parts = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                source = results['metadatas'][0][i].get('source', 'unknown')
                context_parts.append(f"### Fragmento de {source}\n{doc}")
        return "\n\n".join(context_parts)
