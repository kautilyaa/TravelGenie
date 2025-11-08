"""
YOLO11 Video Analyzer - Real-time object detection on YouTube video feeds
Uses Ultralytics YOLO11 for live inference on travel-related video content
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Generator
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
import logging
import threading
from queue import Queue
import time
from ultralytics import YOLO
import pafy
import streamlink
from collections import defaultdict
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Represents an object detection result."""
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    timestamp: float
    frame_number: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoAnalysisResult:
    """Results from video analysis."""
    video_url: str
    total_frames: int
    detections: List[Detection]
    summary: Dict[str, Any]
    duration: float
    fps: float
    resolution: Tuple[int, int]
    timestamp: datetime = field(default_factory=datetime.now)


class YouTubeVideoStream:
    """
    Handles YouTube video streaming for analysis.
    """
    
    def __init__(self, url: str, quality: str = "best"):
        """
        Initialize YouTube video stream.
        
        Args:
            url: YouTube video URL
            quality: Video quality ('best', '720p', '480p', etc.)
        """
        self.url = url
        self.quality = quality
        self.stream = None
        self.video = None
        self.cap = None
        self.fps = 30
        self.resolution = (1280, 720)
    
    def start(self) -> bool:
        """
        Start the video stream.
        
        Returns:
            True if stream started successfully
        """
        try:
            # Try multiple methods to get YouTube stream
            stream_url = self._get_stream_url()
            if not stream_url:
                logger.error("Failed to get stream URL")
                return False
            
            # Open video capture
            self.cap = cv2.VideoCapture(stream_url)
            if not self.cap.isOpened():
                logger.error("Failed to open video stream")
                return False
            
            # Get video properties
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.resolution = (width, height)
            
            logger.info(f"Started stream: {self.resolution} @ {self.fps} fps")
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream: {e}")
            return False
    
    def _get_stream_url(self) -> Optional[str]:
        """
        Get the actual stream URL from YouTube.
        
        Returns:
            Stream URL or None
        """
        try:
            # Method 1: Try with pafy (requires youtube-dl backend)
            try:
                import pafy
                video = pafy.new(self.url)
                if self.quality == "best":
                    stream = video.getbest()
                else:
                    streams = video.streams
                    stream = next((s for s in streams if s.resolution == self.quality), video.getbest())
                return stream.url
            except:
                pass
            
            # Method 2: Try with streamlink
            try:
                streams = streamlink.streams(self.url)
                if self.quality in streams:
                    stream = streams[self.quality]
                else:
                    stream = streams.get("best") or streams.get("worst")
                return stream.url
            except:
                pass
            
            # Method 3: Direct URL if it's already a direct stream
            if self.url.startswith("http"):
                return self.url
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting stream URL: {e}")
            return None
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the stream.
        
        Returns:
            Tuple of (success, frame)
        """
        if self.cap is None:
            return False, None
        
        return self.cap.read()
    
    def stop(self):
        """Stop the video stream."""
        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info("Stream stopped")


class YOLO11Analyzer:
    """
    YOLO11 video analyzer for real-time object detection on travel videos.
    """
    
    # Travel-related object classes to focus on
    TRAVEL_CLASSES = {
        "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
        "truck", "boat", "traffic light", "stop sign", "bench", "bird",
        "backpack", "umbrella", "handbag", "suitcase", "skis", "snowboard",
        "sports ball", "kite", "surfboard", "bottle", "cup", "fork", "knife",
        "spoon", "bowl", "banana", "apple", "sandwich", "orange", "pizza",
        "cake", "chair", "couch", "bed", "dining table", "laptop", "mouse",
        "keyboard", "cell phone", "book", "clock", "vase", "teddy bear"
    }
    
    # Landmark and scene detection categories (for travel context)
    TRAVEL_CONTEXTS = {
        "beach": ["surfboard", "umbrella", "person"],
        "city": ["car", "bus", "traffic light", "person", "bicycle"],
        "airport": ["airplane", "suitcase", "person", "handbag"],
        "restaurant": ["fork", "knife", "spoon", "cup", "dining table"],
        "hotel": ["bed", "couch", "chair", "laptop"],
        "outdoor": ["backpack", "bicycle", "bird", "kite"]
    }
    
    def __init__(
        self,
        model_path: str = "yolo11n.pt",  # Using nano version for speed
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        device: str = "cpu"
    ):
        """
        Initialize YOLO11 analyzer.
        
        Args:
            model_path: Path to YOLO11 model weights
            confidence_threshold: Minimum confidence for detections
            iou_threshold: IOU threshold for NMS
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        
        # Load YOLO11 model
        self.model = self._load_model()
        
        # Analysis state
        self.is_analyzing = False
        self.frame_queue = Queue(maxsize=30)
        self.result_queue = Queue()
        self.detections_buffer = []
        
        # Statistics
        self.stats = defaultdict(int)
        self.context_scores = defaultdict(float)
    
    def _load_model(self) -> YOLO:
        """
        Load YOLO11 model.
        
        Returns:
            Loaded YOLO model
        """
        try:
            # Load YOLO11 model
            model = YOLO(self.model_path)
            model.to(self.device)
            logger.info(f"Loaded YOLO11 model: {self.model_path}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fallback to downloading default model
            model = YOLO("yolo11n.pt")
            model.to(self.device)
            return model
    
    async def analyze_youtube_video(
        self,
        url: str,
        duration_seconds: int = 30,
        skip_frames: int = 5,
        real_time: bool = True
    ) -> VideoAnalysisResult:
        """
        Analyze a YouTube video with YOLO11.
        
        Args:
            url: YouTube video URL
            duration_seconds: How long to analyze (seconds)
            skip_frames: Process every Nth frame
            real_time: Display real-time results
        
        Returns:
            Analysis results
        """
        # Initialize video stream
        stream = YouTubeVideoStream(url)
        if not stream.start():
            return VideoAnalysisResult(
                video_url=url,
                total_frames=0,
                detections=[],
                summary={"error": "Failed to start stream"},
                duration=0,
                fps=0,
                resolution=(0, 0)
            )
        
        # Analysis variables
        detections = []
        frame_count = 0
        start_time = time.time()
        max_frames = int(duration_seconds * stream.fps)
        
        try:
            while frame_count < max_frames:
                # Read frame
                ret, frame = stream.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Skip frames for performance
                if frame_count % skip_frames != 0:
                    continue
                
                # Run YOLO inference
                frame_detections = self._process_frame(frame, frame_count)
                detections.extend(frame_detections)
                
                # Update statistics
                self._update_statistics(frame_detections)
                
                # Real-time display (optional)
                if real_time:
                    display_frame = self._draw_detections(frame, frame_detections)
                    # This would be sent to Streamlit instead of cv2.imshow
                    # For now, we'll just log progress
                    if frame_count % 30 == 0:
                        logger.info(f"Processed {frame_count}/{max_frames} frames")
                
                # Check if should stop
                if time.time() - start_time > duration_seconds:
                    break
            
        finally:
            stream.stop()
        
        # Calculate analysis duration
        duration = time.time() - start_time
        
        # Generate summary
        summary = self._generate_summary(detections)
        
        return VideoAnalysisResult(
            video_url=url,
            total_frames=frame_count,
            detections=detections,
            summary=summary,
            duration=duration,
            fps=stream.fps,
            resolution=stream.resolution
        )
    
    def _process_frame(
        self,
        frame: np.ndarray,
        frame_number: int
    ) -> List[Detection]:
        """
        Process a single frame with YOLO11.
        
        Args:
            frame: Video frame
            frame_number: Frame number
        
        Returns:
            List of detections
        """
        detections = []
        
        try:
            # Run YOLO inference
            results = self.model(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            # Process results
            for r in results:
                if r.boxes is not None:
                    for box in r.boxes:
                        # Get detection info
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        xyxy = box.xyxy[0].tolist()
                        
                        # Get class name
                        class_name = self.model.names[cls]
                        
                        # Filter for travel-related objects
                        if class_name.lower() in self.TRAVEL_CLASSES:
                            detection = Detection(
                                class_name=class_name,
                                confidence=conf,
                                bbox=tuple(map(int, xyxy)),
                                timestamp=time.time(),
                                frame_number=frame_number,
                                metadata={
                                    "class_id": cls,
                                    "area": (xyxy[2] - xyxy[0]) * (xyxy[3] - xyxy[1])
                                }
                            )
                            detections.append(detection)
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
        
        return detections
    
    def _draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Detection]
    ) -> np.ndarray:
        """
        Draw detection boxes on frame.
        
        Args:
            frame: Video frame
            detections: List of detections
        
        Returns:
            Frame with drawn detections
        """
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            
            # Draw box
            color = (0, 255, 0) if det.confidence > 0.5 else (0, 255, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det.class_name} {det.confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 4), (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def _update_statistics(self, detections: List[Detection]):
        """
        Update detection statistics.
        
        Args:
            detections: List of detections
        """
        for det in detections:
            self.stats[det.class_name] += 1
            
            # Update context scores
            for context, indicators in self.TRAVEL_CONTEXTS.items():
                if det.class_name.lower() in indicators:
                    self.context_scores[context] += det.confidence
    
    def _generate_summary(self, detections: List[Detection]) -> Dict[str, Any]:
        """
        Generate analysis summary.
        
        Args:
            detections: All detections from video
        
        Returns:
            Summary dictionary
        """
        if not detections:
            return {
                "total_detections": 0,
                "unique_objects": 0,
                "travel_context": "unknown",
                "top_objects": []
            }
        
        # Count unique objects
        object_counts = defaultdict(int)
        confidence_sum = defaultdict(float)
        
        for det in detections:
            object_counts[det.class_name] += 1
            confidence_sum[det.class_name] += det.confidence
        
        # Calculate average confidence
        avg_confidence = {
            obj: confidence_sum[obj] / object_counts[obj]
            for obj in object_counts
        }
        
        # Determine travel context
        if self.context_scores:
            travel_context = max(self.context_scores, key=self.context_scores.get)
        else:
            travel_context = "general"
        
        # Get top objects
        top_objects = sorted(
            object_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        summary = {
            "total_detections": len(detections),
            "unique_objects": len(object_counts),
            "travel_context": travel_context,
            "context_confidence": self.context_scores.get(travel_context, 0),
            "top_objects": [
                {
                    "name": name,
                    "count": count,
                    "avg_confidence": avg_confidence[name]
                }
                for name, count in top_objects
            ],
            "object_counts": dict(object_counts),
            "travel_indicators": {
                "has_luggage": any(d.class_name in ["suitcase", "backpack", "handbag"] for d in detections),
                "has_transportation": any(d.class_name in ["car", "bus", "train", "airplane", "boat"] for d in detections),
                "has_people": any(d.class_name == "person" for d in detections),
                "outdoor_scene": any(d.class_name in ["bird", "kite", "bicycle"] for d in detections)
            }
        }
        
        return summary
    
    def analyze_frame_generator(
        self,
        stream: YouTubeVideoStream,
        skip_frames: int = 5
    ) -> Generator[Tuple[np.ndarray, List[Detection]], None, None]:
        """
        Generator for real-time frame analysis.
        
        Args:
            stream: Video stream
            skip_frames: Process every Nth frame
        
        Yields:
            Tuple of (frame, detections)
        """
        frame_count = 0
        
        while True:
            ret, frame = stream.read()
            if not ret:
                break
            
            frame_count += 1
            
            if frame_count % skip_frames != 0:
                yield frame, []
                continue
            
            detections = self._process_frame(frame, frame_count)
            self._update_statistics(detections)
            
            # Draw detections on frame
            display_frame = self._draw_detections(frame.copy(), detections)
            
            yield display_frame, detections


# Example usage and testing
async def main():
    """Example usage of YOLO11 Video Analyzer."""
    # Initialize analyzer
    analyzer = YOLO11Analyzer()
    
    # Example YouTube URL (travel video)
    youtube_url = "https://www.youtube.com/watch?v=EXAMPLE"
    
    print(f"Analyzing video: {youtube_url}")
    
    # Analyze video
    result = await analyzer.analyze_youtube_video(
        url=youtube_url,
        duration_seconds=30,
        skip_frames=5,
        real_time=False
    )
    
    # Print results
    print(f"\nAnalysis Results:")
    print(f"Total frames processed: {result.total_frames}")
    print(f"Total detections: {result.summary['total_detections']}")
    print(f"Travel context: {result.summary['travel_context']}")
    print(f"Top objects detected:")
    for obj in result.summary['top_objects'][:5]:
        print(f"  - {obj['name']}: {obj['count']} times (avg confidence: {obj['avg_confidence']:.2f})")


if __name__ == "__main__":
    # Run example
    asyncio.run(main())
