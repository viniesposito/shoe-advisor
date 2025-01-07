from typing import List, Dict
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import json
import logging
from pathlib import Path

import os
from dotenv import load_dotenv

load_dotenv()

class YouTubeCaptionCollector:
    def __init__(self, api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.formatter = TextFormatter()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('youtube_collector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_channel_videos(self, channel_id: str, published_after: datetime, max_results: int = 50) -> List[Dict]:
        try:
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response.get('items'):
                self.logger.error(f"No channel found for ID {channel_id}")
                return []
                
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            videos = []
            next_page_token = None
            
            while True:
                playlist_response = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                
                for item in playlist_response['items']:
                    video_date = datetime.strptime(
                        item['snippet']['publishedAt'],
                        '%Y-%m-%dT%H:%M:%SZ'
                    )
                    
                    if video_date < published_after:
                        return videos
                        
                    videos.append({
                        'video_id': item['snippet']['resourceId']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt']
                    })
                    
                    if len(videos) >= max_results:
                        return videos
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            return videos
            
        except Exception as e:
            self.logger.error(f"Error fetching videos for channel {channel_id}: {str(e)}")
            return []

    def get_video_captions(self, video_id: str) -> Dict:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            formatted_transcript = self.formatter.format_transcript(transcript)
            
            return {
                'text': formatted_transcript,
                'segments': transcript
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching captions for video {video_id}: {str(e)}")
            return None

    def process_channel(self, channel_id: str, output_dir: str, months_back: int = 24) -> List[Dict]:
        transcript_dir = Path(output_dir) / 'transcripts'
        transcript_dir.mkdir(parents=True, exist_ok=True)
        
        published_after = datetime.now() - timedelta(days=30.44 * months_back)
        
        videos = self.get_channel_videos(channel_id, published_after)
        self.logger.info(f"Found {len(videos)} videos for channel {channel_id}")
        
        processed_videos = []
        
        for video in videos:
            video_id = video['video_id']
            transcript_path = transcript_dir / f"{video_id}.json"
            
            if transcript_path.exists():
                with open(transcript_path, 'r') as f:
                    transcript = json.load(f)
            else:
                transcript = self.get_video_captions(video_id)
                if transcript:
                    with open(transcript_path, 'w') as f:
                        json.dump(transcript, f, indent=2)
            
            if transcript:
                processed_videos.append({
                    **video,
                    'transcript': transcript
                })
            
        return processed_videos

def main():
    channels = [
        # {
        #     'name': 'Kofuzi',
        #     'id': 'UCe43pe3w4L6w3tNMRkWiJBA'
        # },
        # {
        #     'name':'Seth James Demoor',
        #     'id':'UCeSHo5kTvzoik4STh7MuMCA'
        # },
        {
            'name':'Ben Parkes',
            'id':'UCZPqG0yh_xPm2AyLjffbDvw'
        },
        {
            'name':'The Run Testers',
            'id':'UCOBM9FasII4dKbyE_HKkbjw'
        },
        {
            'name':'Believe in the Run',
            'id':'UC2-2J_y_jpOYz8Rld5C6C5w'
        },
        
    ]
    
    collector = YouTubeCaptionCollector(os.getenv("YOUTUBE_API_KEY"))
    
    for channel in channels:
        print(f"Processing channel {channel['name']}.\n")
        output_dir = f"data/{channel['name'].lower().replace(' ', '_')}"
        videos = collector.process_channel(channel['id'], output_dir)
        
        with open(f"{output_dir}/processed_videos.json", 'w') as f:
            json.dump(videos, f, indent=2)

if __name__ == "__main__":
    main()