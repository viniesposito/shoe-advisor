import json
from pathlib import Path
import numpy as np
from openai import OpenAI
import faiss
import pickle
from typing import List, Dict
import time

import os
from dotenv import load_dotenv

load_dotenv()

class ShoeKnowledgeBase:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize FAISS index
        # 1536 is the dimensionality of OpenAI's text-embedding-3-small embeddings
        self.index = faiss.IndexFlatL2(1536)
        
        # Store mapping of FAISS index positions to chunk data
        self.chunk_data: List[Dict] = []
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for a text using OpenAI's API"""
        try:
            # Add a small delay to respect rate limits
            time.sleep(0.1)
            
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            # Convert embedding to numpy array
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None

    def add_chunk(self, text: str, metadata: Dict):
        """Add a single chunk to the knowledge base"""
        embedding = self.get_embedding(text)
        if embedding is not None:
            # Add to FAISS index
            self.index.add(embedding.reshape(1, -1))
            # Store chunk data at same position
            self.chunk_data.append({
                'text': text,
                'metadata': metadata
            })
    
    def process_chunks_directory(self, chunks_dir: str):
        """Process all chunks in directory"""
        chunks_path = Path(chunks_dir)
        print(f"Processing chunks from {chunks_path}")
        
        for chunk_file in chunks_path.glob('chunk_*.json'):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk = json.load(f)
                print(f"Processing {chunk_file.name}")
                self.add_chunk(chunk['text'], chunk['metadata'])
    
    def save(self, directory: str):
        """Save the knowledge base to disk"""
        save_dir = Path(directory)
        save_dir.mkdir(exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(save_dir / 'shoe_knowledge.index'))
        
        # Save chunk data
        with open(save_dir / 'chunk_data.pkl', 'wb') as f:
            pickle.dump(self.chunk_data, f)
    
    def load(self, directory: str):
        """Load the knowledge base from disk"""
        load_dir = Path(directory)
        
        # Load FAISS index
        self.index = faiss.read_index(str(load_dir / 'shoe_knowledge.index'))
        
        # Load chunk data
        with open(load_dir / 'chunk_data.pkl', 'rb') as f:
            self.chunk_data = pickle.load(f)
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for most relevant chunks"""
        # Get query embedding
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return []
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)
        
        # Return relevant chunks
        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                'chunk': self.chunk_data[idx],
                'distance': float(distances[0][i])
            })
        
        return results

def main():
    # Initialize knowledge base
    kb = ShoeKnowledgeBase()
    
    # Process all chunks
    kb.process_chunks_directory('processed_chunks')
    
    # Save the knowledge base
    kb.save('shoe_knowledge')
    
    # Example search
    print("\nTesting search...")
    results = kb.search("What are good shoes for marathon racing?")
    for result in results:
        print("\nRelevant chunk:")
        print(f"Title: {result['chunk']['metadata']['title']}")
        print(f"Text: {result['chunk']['text'][:200]}...")
        print(f"Distance: {result['distance']}")

if __name__ == "__main__":
    main()