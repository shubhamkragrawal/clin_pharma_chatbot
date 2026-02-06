import os
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


class EmbeddingIndexer:
    def __init__(self, json_folder="data/json", db_path="data/chromadb"):
        self.json_folder = json_folder
        self.db_path = db_path
        
        # Load embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="pdf_documents",
            metadata={"hnsw:space": "cosine"}
        )
        print("Embedding model loaded!")
    
    def chunk_text(self, text, chunk_size=500, overlap=50):
        """Split text into chunks with overlap"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def index_documents(self):
        """Load JSONs and create embeddings"""
        json_files = list(Path(self.json_folder).glob("*.json"))
        
        if not json_files:
            print(f"No JSON files found in {self.json_folder}")
            return
        
        print(f"Found {len(json_files)} JSON files to index")
        
        # Clear existing collection if it has data
        try:
            count = self.collection.count()
            if count > 0:
                # Get all IDs and delete them
                all_data = self.collection.get()
                if all_data['ids']:
                    self.collection.delete(ids=all_data['ids'])
                    print(f"Cleared {count} existing documents")
        except Exception as e:
            print(f"Note: {e}")
        
        doc_id = 0
        
        for json_file in json_files:
            print(f"Indexing: {json_file.name}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            filename = data['filename']
            
            for page in data['pages']:
                page_num = page['page_number']
                text = page['text']
                
                if not text.strip():
                    continue
                
                # Chunk the text
                chunks = self.chunk_text(text)
                
                for chunk_idx, chunk in enumerate(chunks):
                    # Create metadata
                    metadata = {
                        "filename": filename,
                        "page": page_num,
                        "chunk": chunk_idx
                    }
                    
                    # Add to collection
                    self.collection.add(
                        documents=[chunk],
                        metadatas=[metadata],
                        ids=[f"doc_{doc_id}"]
                    )
                    
                    doc_id += 1
            
            print(f"  ✓ Indexed {filename}")
        
        print(f"\nIndexing complete! Total chunks: {doc_id}")
    
    def search(self, query, n_results=5):
        """Search for relevant chunks"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results


if __name__ == "__main__":
    indexer = EmbeddingIndexer()
    indexer.index_documents()