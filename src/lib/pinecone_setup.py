import os
from pathlib import Path
import json
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from typing import List, Dict
import time

load_dotenv()

class VideoProcessor:
    def __init__(self):
        self.openai_client = OpenAI()
        self.pinecone = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            # Find a good breakpoint near the chunk size
            end = start + chunk_size
            if end < len(text):
                # Try to break at a sentence or period
                while end > start and text[end] not in '.!?\n':
                    end -= 1
                if end == start:  # If no good breakpoint found
                    end = start + chunk_size
                    
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = end - overlap
            if start < 0:
                start = 0
                
        return chunks

    def process_video_chunks(self, video: Dict) -> List[Dict]:
        """Process a video into chunks with embeddings"""
        if 'transcript' not in video or 'text' not in video['transcript']:
            print(f"No transcript found for video: {video.get('title', 'Unknown')}")
            return []
            
        chunks = self.chunk_text(video['transcript']['text'])
        chunk_data = []
        
        for i, chunk_text in enumerate(chunks):
            try:
                # Rate limiting - OpenAI has a rate limit
                time.sleep(0.1)
                
                # Get embedding for chunk
                embedding = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=chunk_text
                ).data[0].embedding
                
                # Store chunk data
                chunk_data.append({
                    'id': f"{video['video_id']}_chunk_{i}",
                    'values': embedding,
                    'metadata': {
                        'title': video['title'],
                        'video_id': video['video_id'],
                        'chunk_text': chunk_text,
                        'chunk_index': i
                    }
                })
                
                print(f"Processed chunk {i} for video {video['video_id']}")
                
            except Exception as e:
                print(f"Error processing chunk {i} for video {video['video_id']}: {e}")
                continue
                
        return chunk_data

    def process_videos(self):
        """Process all videos and upload to Pinecone"""
        # Get or create index
        index_name = 'running-shoes'
        
        try:
            index = self.pinecone.Index(index_name)
            print(f"Connected to existing index: {index_name}")
        except Exception as e:
            print(f"Error connecting to index: {e}")
            return
        
        # Process each channel's videos
        data_dir = Path('data')
        all_chunks = []
        
        for channel_dir in data_dir.iterdir():
            if not channel_dir.is_dir():
                continue
                
            json_path = channel_dir / 'processed_videos.json'
            if not json_path.exists():
                continue
                
            print(f"\nProcessing channel: {channel_dir.name}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                videos = json.load(f)
                
            # Process each video
            for video in videos:
                print(f"\nProcessing video: {video['title']}")
                chunks = self.process_video_chunks(video)
                all_chunks.extend(chunks)
                
                # Upload chunks in batches
                if len(all_chunks) >= 100:
                    index.upsert(vectors=all_chunks)
                    print(f"Uploaded {len(all_chunks)} chunks to Pinecone")
                    all_chunks = []
        
        # Upload any remaining chunks
        if all_chunks:
            index.upsert(vectors=all_chunks)
            print(f"Uploaded final {len(all_chunks)} chunks to Pinecone")

def main():
    processor = VideoProcessor()
    processor.process_videos()

if __name__ == "__main__":
    main()