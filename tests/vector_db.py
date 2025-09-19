import chromadb
import hashlib
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
load_dotenv()

class VectorDB:
    def __init__(self, persist_dir: str = "./chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.client = chromadb.PersistentClient(path=persist_dir)

        # Use model name in collection name so embeddings stay separate
        safe_name = model_name.replace("/", "_").replace("-", "_").lower()
        self.collection_name = f"docs_{safe_name}"

        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        self.model = SentenceTransformer(model_name)

    @staticmethod
    def debug_print(input_text: str = ""):
        IS_DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        if IS_DEBUG:
            print(f"DEBUG MODE Input Text: {input_text}")
        
    def _make_id(self, text: str) -> str:
        """Generate a stable unique ID from text using MD5 hash."""
        return hashlib.md5(text.lower().encode("utf-8")).hexdigest()

    def add(self, docs: list[str]):
        """Add documents, skipping duplicates."""
        for doc in docs:
            doc_id = self._make_id(doc)

            # Check if already exists
            existing = self.collection.get(ids=[doc_id])
            if existing["documents"]:
                self.debug_print(f"⚠️ Skipping duplicate: {doc[:50]}...")
                continue

            embedding = self.model.encode([doc]).tolist()
            self.collection.add(
                documents=[doc],
                embeddings=embedding,  # type: ignore
                ids=[doc_id]
            )
            self.debug_print(f"✅ Added: {doc[:50]}...")

    def query(self, text: str, n_results: int = 3):
        """Query the database with semantic search."""
        embedding = self.model.encode([text]).tolist()
        results = self.collection.query(
            query_embeddings=embedding,  # type: ignore
            n_results=n_results
        )
        return results
    
    def clear(self) -> None:
        """Clear the entire collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        self.debug_print("🗑️ Cleared the vector database.")


# Example usage
if __name__ == "__main__":
    db = VectorDB(model_name="all-MiniLM-L6-v2")

    docs = [
        "My name is Chen.",
        "My favorite programming language is Python.",
    ]

    db.add(docs)

    query = "Who likes Python?"
    results = db.query(query)
    print("🔎 Query Results:", results["documents"])