from pathlib import Path
import json
import re
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class TextChunk:
    text: str
    metadata: Dict
    
class TranscriptChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def clean_text(self, text: str) -> str:
        """Remove unnecessary whitespace and normalize text"""
        # Remove multiple newlines and spaces
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def split_into_chunks(self, text: str, title: str, video_id: str) -> List[TextChunk]:
        """Split text into overlapping chunks while trying to maintain sentence boundaries"""
        text = self.clean_text(text)
        chunks = []
        
        # Split into sentences (crude but functional for now)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create chunk with metadata
                chunk_text = ' '.join(current_chunk)
                chunks.append(TextChunk(
                    text=chunk_text,
                    metadata={
                        'title': title,
                        'video_id': video_id,
                        'length': len(chunk_text),
                        'chunk_index': len(chunks)
                    }
                ))
                
                # Keep some sentences for overlap
                overlap_start = max(0, len(current_chunk) - self.overlap)
                current_chunk = current_chunk[overlap_start:]
                current_length = sum(len(s) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(TextChunk(
                text=chunk_text,
                metadata={
                    'title': title,
                    'video_id': video_id,
                    'length': len(chunk_text),
                    'chunk_index': len(chunks)
                }
            ))
        
        return chunks

def process_transcripts():
    chunker = TranscriptChunker()
    all_chunks = []
    data_dir = Path('data')
    
    # Process each channel directory
    for channel_dir in data_dir.iterdir():
        if not channel_dir.is_dir():
            continue
        
        json_path = channel_dir / 'processed_videos.json'
        if not json_path.exists():
            continue
        
        with open(json_path, 'r', encoding='utf-8') as f:
            videos = json.load(f)
        
        # Process each video
        for video in videos:
            if 'transcript' not in video or 'text' not in video['transcript']:
                continue
                
            chunks = chunker.split_into_chunks(
                video['transcript']['text'],
                video['title'],
                video['video_id']
            )
            all_chunks.extend(chunks)
    
    # Save chunks (for now, we'll improve storage later)
    chunks_dir = Path('processed_chunks')
    chunks_dir.mkdir(exist_ok=True)
    
    for i, chunk in enumerate(all_chunks):
        chunk_file = chunks_dir / f'chunk_{i:04d}.json'
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump({
                'text': chunk.text,
                'metadata': chunk.metadata
            }, f, indent=2)

if __name__ == "__main__":
    process_transcripts()