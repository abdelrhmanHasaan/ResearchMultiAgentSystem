import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any

import chromadb
import ollama

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self, collection_name: str = "research_docs", db_path: str = "./chroma_db", embedding_model: str = "nomic-embed-text"):
        self.embedding_model = embedding_model
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def _generate_embedding(self, text: str) -> List[float]:
        try:
            response = ollama.embeddings(model=self.embedding_model, prompt=text)
            return response.get("embedding", [])
        except Exception as e:
            logger.error(f"Error generating embedding with {self.embedding_model}: {e}")
            return []

    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def ingest_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Ingests a list of documents (dictionaries) into ChromaDB.
        Expects documents to have at least 'content' and 'url' keys.
        """
        ids = []
        embeddings = []
        metadatas = []
        documents_text = []

        for doc in documents:
            content = doc.get("content", "")
            url = doc.get("url", "unknown")
            if not content:
                continue

            chunks = self._split_text(content)

            for idx, chunk in enumerate(chunks):
                # Deduplication logic using hash
                chunk_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
                doc_id = f"{url}_{chunk_hash[:10]}_{idx}"

                embedding = self._generate_embedding(chunk)
                if not embedding:
                    continue

                ids.append(doc_id)
                embeddings.append(embedding)
                documents_text.append(chunk)
                metadatas.append({
                    "url": url,
                    "timestamp": datetime.utcnow().isoformat(),
                    "chunk_index": idx
                })

        if ids:
            try:
                # Upsert handles deduplication if ids are identical
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents_text,
                    metadatas=metadatas
                )
                logger.info(f"Successfully ingested {len(ids)} document chunks into ChromaDB.")
            except Exception as e:
                logger.error(f"Error ingesting documents into ChromaDB: {e}")

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Searches the vector store using the generated embedding of the query.
        """
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            return {"documents": [], "metadatas": []}

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return {"documents": [], "metadatas": []}
