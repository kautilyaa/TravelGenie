"""
YouTube Utilities - Helper functions for YouTube video processing
Handles video downloading, streaming, and metadata extraction
"""

import re
import logging
from typing import Dict, Optional, Any, Tuple
from urllib.parse import urlparse, parse_qs
import requests
import cv2
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeHelper:
    """
    Helper class for YouTube video operations.
    """
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube video URL
        
        Returns:
            Video ID or None
        """
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([\w-]+)',
            r'(?:youtu\.be\/)([\w-]+)',
            r'(?:youtube\.com\/embed\/)([\w-]+)',
            r'(?:youtube\.com\/v\/)([\w-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Try parsing as standard URL
        try:
            parsed = urlparse(url)
            if 'youtube.com' in parsed.netloc:
                params = parse_qs(parsed.query)
                if 'v' in params:
                    return params['v'][0]
        except:
            pass
        
        return None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate if URL is a valid YouTube URL.
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid YouTube URL
        """
        video_id = YouTubeHelper.extract_video_id(url)
        return video_id is not None
    
    @staticmethod
    def get_video_info(url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get video metadata without API key (basic info).
        
        Args:
            url: YouTube video URL
            api_key: Optional YouTube API key for detailed info
        
        Returns:
            Video metadata
        """
        video_id = YouTubeHelper.extract_video_id(url)
        if not video_id:
            return {"error": "Invalid YouTube URL"}
        
        info = {
            "video_id": video_id,
            "url": url,
            "embed_url": f"https://www.youtube.com/embed/{video_id}",
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        }
        
        # If API key provided, get detailed info
        if api_key:
            try:
                api_url = f"https://www.googleapis.com/youtube/v3/videos"
                params = {
                    "part": "snippet,contentDetails,statistics",
                    "id": video_id,
                    "key": api_key
                }
                
                response = requests.get(api_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data["items"]:
                        item = data["items"][0]
                        info.update({
                            "title": item["snippet"]["title"],
                            "description": item["snippet"]["description"],
                            "channel": item["snippet"]["channelTitle"],
                            "duration": item["contentDetails"]["duration"],
                            "views": item["statistics"].get("viewCount", 0),
                            "likes": item["statistics"].get("likeCount", 0)
                        })
            except Exception as e:
                logger.error(f"Error fetching video info: {e}")
        
        return info
    
    @staticmethod
    def get_stream_url(youtube_url: str, quality: str = "best") -> Optional[str]:
        """
        Get direct stream URL for a YouTube video.
        
        Args:
            youtube_url: YouTube video URL
            quality: Video quality preference
        
        Returns:
            Direct stream URL or None
        """
        try:
            # Try using youtube-dl/yt-dlp (if available)
            import yt_dlp
            
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                formats = info.get('formats', [])
                
                # Find best quality stream
                for f in formats:
                    if f.get('ext') == 'mp4' and f.get('url'):
                        return f['url']
                
                # Fallback to any available stream
                if formats and formats[0].get('url'):
                    return formats[0]['url']
                    
        except ImportError:
            logger.warning("yt-dlp not available, trying alternative methods")
        except Exception as e:
            logger.error(f"Error getting stream URL with yt-dlp: {e}")
        
        # Try pafy as fallback
        try:
            import pafy
            video = pafy.new(youtube_url)
            best = video.getbest(preftype="mp4")
            if best:
                return best.url
        except ImportError:
            logger.warning("pafy not available")
        except Exception as e:
            logger.error(f"Error getting stream URL with pafy: {e}")
        
        return None
    
    @staticmethod
    def create_video_capture(url: str) -> Optional[cv2.VideoCapture]:
        """
        Create OpenCV VideoCapture from YouTube URL.
        
        Args:
            url: YouTube video URL
        
        Returns:
            VideoCapture object or None
        """
        # Get stream URL
        stream_url = YouTubeHelper.get_stream_url(url)
        
        if not stream_url:
            logger.error("Could not get stream URL")
            return None
        
        try:
            # Create video capture
            cap = cv2.VideoCapture(stream_url)
            
            if not cap.isOpened():
                logger.error("Could not open video stream")
                return None
            
            return cap
            
        except Exception as e:
            logger.error(f"Error creating video capture: {e}")
            return None
    
    @staticmethod
    def extract_thumbnail(url: str, time_sec: float = 0) -> Optional[np.ndarray]:
        """
        Extract a thumbnail frame from YouTube video.
        
        Args:
            url: YouTube video URL
            time_sec: Time in seconds to extract frame from
        
        Returns:
            Frame as numpy array or None
        """
        cap = YouTubeHelper.create_video_capture(url)
        
        if not cap:
            return None
        
        try:
            # Seek to specified time
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(fps * time_sec)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Read frame
            ret, frame = cap.read()
            
            if ret:
                return frame
            
        except Exception as e:
            logger.error(f"Error extracting thumbnail: {e}")
        
        finally:
            cap.release()
        
        return None


class VideoStreamManager:
    """
    Manages multiple video streams for concurrent processing.
    """
    
    def __init__(self):
        """Initialize stream manager."""
        self.streams: Dict[str, cv2.VideoCapture] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def add_stream(self, stream_id: str, url: str) -> bool:
        """
        Add a new video stream.
        
        Args:
            stream_id: Unique identifier for the stream
            url: YouTube video URL
        
        Returns:
            True if stream added successfully
        """
        if stream_id in self.streams:
            logger.warning(f"Stream {stream_id} already exists")
            return False
        
        # Create video capture
        cap = YouTubeHelper.create_video_capture(url)
        
        if not cap:
            return False
        
        # Store stream and metadata
        self.streams[stream_id] = cap
        self.metadata[stream_id] = {
            "url": url,
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        }
        
        logger.info(f"Added stream: {stream_id}")
        return True
    
    def read_frame(self, stream_id: str) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from a stream.
        
        Args:
            stream_id: Stream identifier
        
        Returns:
            Tuple of (success, frame)
        """
        if stream_id not in self.streams:
            return False, None
        
        return self.streams[stream_id].read()
    
    def remove_stream(self, stream_id: str):
        """
        Remove a video stream.
        
        Args:
            stream_id: Stream identifier
        """
        if stream_id in self.streams:
            self.streams[stream_id].release()
            del self.streams[stream_id]
            del self.metadata[stream_id]
            logger.info(f"Removed stream: {stream_id}")
    
    def get_stream_info(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """
        Get stream metadata.
        
        Args:
            stream_id: Stream identifier
        
        Returns:
            Stream metadata or None
        """
        return self.metadata.get(stream_id)
    
    def cleanup(self):
        """Release all video streams."""
        for stream_id in list(self.streams.keys()):
            self.remove_stream(stream_id)
        logger.info("All streams cleaned up")


class TravelVideoClassifier:
    """
    Classifies YouTube videos for travel relevance.
    """
    
    # Travel-related keywords for classification
    TRAVEL_KEYWORDS = {
        "destination": ["travel", "destination", "visit", "explore", "tour"],
        "accommodation": ["hotel", "hostel", "airbnb", "resort", "stay"],
        "transportation": ["flight", "train", "bus", "car", "rental"],
        "activity": ["adventure", "sightseeing", "museum", "beach", "hiking"],
        "food": ["restaurant", "food", "cuisine", "dining", "local"],
        "culture": ["culture", "tradition", "festival", "history", "heritage"],
        "tips": ["tips", "guide", "advice", "budget", "itinerary"],
        "vlog": ["vlog", "diary", "journey", "experience", "story"]
    }
    
    @classmethod
    def classify_video(
        cls,
        title: str = "",
        description: str = "",
        tags: list = None
    ) -> Dict[str, Any]:
        """
        Classify a video's travel relevance.
        
        Args:
            title: Video title
            description: Video description
            tags: Video tags
        
        Returns:
            Classification results
        """
        text = f"{title} {description} {' '.join(tags or [])}".lower()
        
        categories = {}
        for category, keywords in cls.TRAVEL_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                categories[category] = score
        
        # Calculate overall travel score
        total_score = sum(categories.values())
        is_travel_related = total_score > 2
        
        # Determine primary category
        primary_category = max(categories.items(), key=lambda x: x[1])[0] if categories else "general"
        
        return {
            "is_travel_related": is_travel_related,
            "travel_score": total_score,
            "categories": categories,
            "primary_category": primary_category,
            "confidence": min(total_score / 10, 1.0)  # Normalize to 0-1
        }


# Example usage
def example_usage():
    """Example usage of YouTube utilities."""
    # Example YouTube URL
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Extract video ID
    video_id = YouTubeHelper.extract_video_id(url)
    print(f"Video ID: {video_id}")
    
    # Validate URL
    is_valid = YouTubeHelper.validate_url(url)
    print(f"Valid URL: {is_valid}")
    
    # Get video info
    info = YouTubeHelper.get_video_info(url)
    print(f"Video Info: {info}")
    
    # Classify video
    classification = TravelVideoClassifier.classify_video(
        title="Paris Travel Guide 2024",
        description="Complete guide to visiting Paris including hotels and restaurants"
    )
    print(f"Classification: {classification}")


if __name__ == "__main__":
    example_usage()
