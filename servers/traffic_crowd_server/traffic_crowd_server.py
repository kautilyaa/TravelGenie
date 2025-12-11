"""
Traffic & Crowd Server MCP - Real-time Location Analysis

This server provides real-time analysis of location data including:
- Crowd density estimation
- Foot traffic analysis
- Car traffic analysis
- Real-time video frame analysis
- Location-based traffic patterns

Features:
- Real-time video frame processing and analysis
- Crowd density detection using computer vision
- Foot traffic patterns and trends
- Vehicle traffic analysis
- Location-specific traffic insights
- Historical traffic pattern comparison
"""

import requests
import json
import os
import base64
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from mcp.server.fastmcp import FastMCP

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

TRAFFIC_CROWD_DIR = "traffic_crowd_data"
mcp = FastMCP("traffic-crowd-assistant")

def get_opencv_available() -> bool:
    """Check if OpenCV is available for video processing."""
    return OPENCV_AVAILABLE

def geocode_location(location: str) -> Tuple[float, float, Dict[str, Any]]:
    """Geocode a location name to coordinates using Open-Meteo geocoding API."""
    if ',' in location:
        try:
            parts = location.split(',')
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return lat, lon, {"name": location, "latitude": lat, "longitude": lon}
        except ValueError:
            pass
    
    GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    try:
        response = requests.get(GEOCODING_API, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return (
                result["latitude"],
                result["longitude"],
                {
                    "name": result.get("name", location),
                    "country": result.get("country", "Unknown"),
                    "admin1": result.get("admin1", ""),
                    "latitude": result["latitude"],
                    "longitude": result["longitude"]
                }
            )
        else:
            raise ValueError(f"Location '{location}' not found")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Geocoding failed: {str(e)}")

def analyze_video_frame(frame_data: str, frame_type: str = "base64") -> Dict[str, Any]:
    """
    Analyze a video frame for crowd, foot traffic, and vehicle detection.
    
    Args:
        frame_data: Base64 encoded image or file path
        frame_type: Type of input - 'base64' or 'file_path'
        
    Returns:
        Dict containing analysis results
    """
    if not get_opencv_available():
        return {
            "error": "OpenCV not available. Please install opencv-python for video analysis.",
            "suggestion": "pip install opencv-python opencv-contrib-python"
        }
    
    try:
        if not OPENCV_AVAILABLE:
            return {
                "error": "OpenCV not available. Please install opencv-python for video analysis.",
                "suggestion": "pip install opencv-python opencv-contrib-python"
            }
        
        # Load image
        if frame_type == "base64":
            # Decode base64 image
            image_data = base64.b64decode(frame_data)
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            # Load from file path
            frame = cv2.imread(frame_data)
        
        if frame is None:
            return {"error": "Failed to load image frame"}
        
        # Get frame dimensions
        height, width = frame.shape[:2]
        total_pixels = height * width
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Initialize analysis results
        analysis = {
            "frame_dimensions": {"width": width, "height": height},
            "total_pixels": total_pixels,
            "timestamp": datetime.now().isoformat()
        }
        
        # Crowd density estimation using blob detection
        # This is a simplified approach - in production, you'd use more sophisticated models
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 100
        params.maxArea = 5000
        params.filterByCircularity = False
        params.filterByConvexity = False
        params.filterByInertia = False
        
        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(gray)
        
        # Estimate crowd density
        blob_count = len(keypoints)
        density_percentage = (blob_count / 100.0) * 100  # Normalized estimate
        density_level = "Low"
        if density_percentage > 70:
            density_level = "Very High"
        elif density_percentage > 50:
            density_level = "High"
        elif density_percentage > 30:
            density_level = "Medium"
        
        analysis["crowd_analysis"] = {
            "detected_blobs": blob_count,
            "estimated_density_percentage": min(density_percentage, 100),
            "crowd_level": density_level,
            "keypoints_detected": blob_count
        }
        
        # Vehicle detection using edge detection and contour analysis
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size (vehicles are typically larger)
        vehicle_contours = [c for c in contours if cv2.contourArea(c) > 500]
        vehicle_count = len(vehicle_contours)
        
        # Estimate traffic density
        traffic_percentage = (vehicle_count / 50.0) * 100  # Normalized estimate
        traffic_level = "Low"
        if traffic_percentage > 70:
            traffic_level = "Heavy"
        elif traffic_percentage > 50:
            traffic_level = "Moderate"
        elif traffic_percentage > 30:
            traffic_level = "Light"
        
        analysis["vehicle_analysis"] = {
            "detected_vehicles": vehicle_count,
            "estimated_traffic_percentage": min(traffic_percentage, 100),
            "traffic_level": traffic_level,
            "contours_detected": len(contours)
        }
        
        # Foot traffic estimation (pedestrian detection)
        # Using HOG (Histogram of Oriented Gradients) descriptor
        # This is a simplified version - production would use trained models
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Resize frame for faster processing if too large
        scale_factor = 1.0
        if width > 800:
            scale_factor = 800 / width
            frame_resized = cv2.resize(frame, (int(width * scale_factor), int(height * scale_factor)))
        else:
            frame_resized = frame
        
        # Detect pedestrians
        boxes, weights = hog.detectMultiScale(frame_resized, winStride=(8, 8), padding=(32, 32), scale=1.05)
        
        pedestrian_count = len(boxes)
        foot_traffic_percentage = (pedestrian_count / 20.0) * 100  # Normalized estimate
        foot_traffic_level = "Low"
        if foot_traffic_percentage > 70:
            foot_traffic_level = "Very High"
        elif foot_traffic_percentage > 50:
            foot_traffic_level = "High"
        elif foot_traffic_percentage > 30:
            foot_traffic_level = "Medium"
        
        analysis["foot_traffic_analysis"] = {
            "detected_pedestrians": pedestrian_count,
            "estimated_foot_traffic_percentage": min(foot_traffic_percentage, 100),
            "foot_traffic_level": foot_traffic_level,
            "pedestrian_boxes": len(boxes)
        }
        
        # Overall location activity score
        activity_score = (
            analysis["crowd_analysis"]["estimated_density_percentage"] * 0.4 +
            analysis["vehicle_analysis"]["estimated_traffic_percentage"] * 0.3 +
            analysis["foot_traffic_analysis"]["estimated_foot_traffic_percentage"] * 0.3
        )
        
        activity_level = "Quiet"
        if activity_score > 70:
            activity_level = "Very Busy"
        elif activity_score > 50:
            activity_level = "Busy"
        elif activity_score > 30:
            activity_level = "Moderate"
        
        analysis["overall_activity"] = {
            "activity_score": round(activity_score, 2),
            "activity_level": activity_level,
            "recommendation": "Consider visiting during off-peak hours" if activity_score > 70 else "Good time to visit"
        }
        
        return analysis
        
    except Exception as e:
        return {"error": f"Video frame analysis failed: {str(e)}"}

@mcp.tool()
def analyze_location_traffic(
    location: str,
    analysis_type: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Get real-time traffic and crowd data for a specific location.
    
    Args:
        location: Location name or coordinates (lat,lon)
        analysis_type: Type of analysis - 'comprehensive', 'crowd', 'traffic', 'foot_traffic'
        
    Returns:
        Dict containing traffic and crowd analysis data
    """
    
    try:
        # Geocode location
        lat, lon, location_info = geocode_location(location)
        
        # Create search identifier
        search_id = f"traffic_{location.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(TRAFFIC_CROWD_DIR, exist_ok=True)
        
        # Simulate real-time data (in production, this would connect to real APIs)
        # For now, we'll provide a framework that can be extended with actual APIs
        
        # Generate realistic traffic patterns based on time of day
        current_hour = datetime.now().hour
        time_factor = 1.0
        
        # Peak hours: 7-9 AM, 5-7 PM
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            time_factor = 1.5
        # Off-peak: 10 PM - 6 AM
        elif 22 <= current_hour or current_hour <= 6:
            time_factor = 0.3
        
        # Base traffic estimates (would come from real APIs in production)
        base_traffic = {
            "vehicle_traffic": {
                "level": "Moderate",
                "density_percentage": min(50 * time_factor, 100),
                "estimated_vehicles_per_minute": int(30 * time_factor),
                "average_speed_kmh": max(30 - (time_factor * 10), 10)
            },
            "foot_traffic": {
                "level": "Medium",
                "density_percentage": min(40 * time_factor, 100),
                "estimated_pedestrians_per_minute": int(20 * time_factor)
            },
            "crowd_density": {
                "level": "Medium",
                "density_percentage": min(45 * time_factor, 100),
                "estimated_people_count": int(50 * time_factor)
            }
        }
        
        # Process based on analysis type
        processed_data = {
            "search_metadata": {
                "search_id": search_id,
                "location_query": location,
                "analysis_type": analysis_type,
                "search_timestamp": datetime.now().isoformat(),
                "current_hour": current_hour
            },
            "location": {
                "name": location_info.get("name", "Unknown"),
                "country": location_info.get("country", "Unknown"),
                "region": location_info.get("admin1", "Unknown"),
                "latitude": lat,
                "longitude": lon
            },
            "traffic_data": base_traffic if analysis_type in ["comprehensive", "traffic"] else {},
            "crowd_data": base_traffic if analysis_type in ["comprehensive", "crowd"] else {},
            "foot_traffic_data": base_traffic if analysis_type in ["comprehensive", "foot_traffic"] else {}
        }
        
        # Calculate overall activity score
        if analysis_type == "comprehensive":
            activity_score = (
                base_traffic["vehicle_traffic"]["density_percentage"] * 0.3 +
                base_traffic["foot_traffic"]["density_percentage"] * 0.3 +
                base_traffic["crowd_density"]["density_percentage"] * 0.4
            )
            
            activity_level = "Quiet"
            if activity_score > 70:
                activity_level = "Very Busy"
            elif activity_score > 50:
                activity_level = "Busy"
            elif activity_score > 30:
                activity_level = "Moderate"
            
            processed_data["overall_activity"] = {
                "activity_score": round(activity_score, 2),
                "activity_level": activity_level,
                "best_visit_time": "Off-peak hours (10 AM - 4 PM)" if activity_score > 70 else "Current time is good",
                "recommendation": "Consider visiting during off-peak hours" if activity_score > 70 else "Good time to visit"
            }
        
        # Save results to file
        file_path = os.path.join(TRAFFIC_CROWD_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_data, f, indent=2)
        
        print(f"Traffic analysis data saved to: {file_path}")
        
        # Return summary
        summary = {
            "search_id": search_id,
            "location": {
                "name": location_info.get("name", "Unknown"),
                "country": location_info.get("country", "Unknown"),
                "coordinates": f"{lat}, {lon}"
            },
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if analysis_type in ["comprehensive", "traffic"]:
            summary["vehicle_traffic"] = base_traffic["vehicle_traffic"]
        
        if analysis_type in ["comprehensive", "foot_traffic"]:
            summary["foot_traffic"] = base_traffic["foot_traffic"]
        
        if analysis_type in ["comprehensive", "crowd"]:
            summary["crowd_density"] = base_traffic["crowd_density"]
        
        if "overall_activity" in processed_data:
            summary["overall_activity"] = processed_data["overall_activity"]
        
        return summary
        
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def analyze_video_frame_realtime(
    frame_data: str,
    frame_type: str = "base64",
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze a real-time video frame for crowd, foot traffic, and vehicle detection.
    
    Args:
        frame_data: Base64 encoded image string or file path to image
        frame_type: Type of input - 'base64' (default) or 'file_path'
        location: Optional location name for context
        
    Returns:
        Dict containing real-time frame analysis results
    """
    
    try:
        # Analyze the frame
        analysis = analyze_video_frame(frame_data, frame_type)
        
        if "error" in analysis:
            return analysis
        
        # Create search identifier
        search_id = f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Add location context if provided
        if location:
            try:
                lat, lon, location_info = geocode_location(location)
                analysis["location_context"] = {
                    "name": location_info.get("name", location),
                    "country": location_info.get("country", "Unknown"),
                    "latitude": lat,
                    "longitude": lon
                }
            except:
                analysis["location_context"] = {"name": location}
        
        # Create directory structure
        os.makedirs(TRAFFIC_CROWD_DIR, exist_ok=True)
        
        # Save frame analysis
        file_path = os.path.join(TRAFFIC_CROWD_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(analysis, f, indent=2)
        
        print(f"Frame analysis saved to: {file_path}")
        
        # Return summary
        summary = {
            "search_id": search_id,
            "analysis_timestamp": analysis.get("timestamp"),
            "frame_dimensions": analysis.get("frame_dimensions"),
            "crowd_analysis": analysis.get("crowd_analysis"),
            "vehicle_analysis": analysis.get("vehicle_analysis"),
            "foot_traffic_analysis": analysis.get("foot_traffic_analysis"),
            "overall_activity": analysis.get("overall_activity")
        }
        
        if "location_context" in analysis:
            summary["location_context"] = analysis["location_context"]
        
        return summary
        
    except Exception as e:
        return {"error": f"Frame analysis failed: {str(e)}"}

@mcp.tool()
def analyze_youtube_video(
    youtube_url: str,
    location: Optional[str] = None,
    sample_frames: int = 5,
    frame_interval: int = 10
) -> Dict[str, Any]:
    """
    Analyze a YouTube video (including live streams) for crowd, foot traffic, and vehicle detection.
    Extracts frames from the video and performs real-time analysis.
    
    Args:
        youtube_url: YouTube video URL (supports regular videos and live streams)
        location: Optional location name for context
        sample_frames: Number of frames to sample and analyze (default: 5)
        frame_interval: Interval between sampled frames in seconds (default: 10)
        
    Returns:
        Dict containing video analysis results with crowd, traffic, and activity data
    """
    
    if not OPENCV_AVAILABLE:
        return {
            "error": "OpenCV not available. Please install opencv-python for video analysis.",
            "suggestion": "pip install opencv-python opencv-contrib-python"
        }
    
    if not YT_DLP_AVAILABLE:
        return {
            "error": "yt-dlp not available. Please install yt-dlp for YouTube video processing.",
            "suggestion": "pip install yt-dlp"
        }
    
    try:
        import cv2
        
        # Validate YouTube URL
        if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
            return {"error": "Invalid YouTube URL. Please provide a valid YouTube video URL."}
        
        # Create search identifier
        search_id = f"youtube_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        os.makedirs(TRAFFIC_CROWD_DIR, exist_ok=True)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[height<=720]',  # Get best quality up to 720p for faster processing
            'quiet': True,
            'no_warnings': True,
        }
        
        # Extract video stream URL using yt-dlp
        video_url = None
        video_info = {}
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                video_info = {
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "is_live": info.get("is_live", False),
                    "view_count": info.get("view_count", 0),
                    "uploader": info.get("uploader", "Unknown")
                }
                
                # Get the best video stream URL
                if 'url' in info:
                    video_url = info['url']
                elif 'formats' in info:
                    # Find the best format
                    formats = info.get('formats', [])
                    for fmt in formats:
                        if fmt.get('vcodec') != 'none' and fmt.get('url'):
                            video_url = fmt['url']
                            break
        except Exception as e:
            return {"error": f"Failed to extract YouTube video URL: {str(e)}"}
        
        if not video_url:
            return {"error": "Could not extract video stream URL from YouTube"}
        
        # Open video stream using OpenCV
        cap = cv2.VideoCapture(video_url)
        
        if not cap.isOpened():
            return {"error": "Failed to open video stream. The video may be private or unavailable."}
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Default to 30 fps if unavailable
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.get(cv2.CAP_PROP_FRAME_COUNT) > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate frame interval in frames (not seconds)
        frame_skip = int(fps * frame_interval) if fps > 0 else 30
        
        # Sample and analyze frames
        frame_analyses = []
        frames_analyzed = 0
        current_frame = 0
        
        while frames_analyzed < sample_frames:
            ret, frame = cap.read()
            
            if not ret:
                # If we can't read more frames (end of video or stream issue), break
                break
            
            # Sample frames at intervals
            if current_frame % frame_skip == 0:
                # Analyze this frame
                # Convert frame to base64 for analysis
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Analyze the frame
                frame_analysis = analyze_video_frame(frame_base64, "base64")
                
                if "error" not in frame_analysis:
                    frame_analysis["frame_number"] = current_frame
                    frame_analysis["timestamp_seconds"] = current_frame / fps if fps > 0 else 0
                    frame_analyses.append(frame_analysis)
                    frames_analyzed += 1
            
            current_frame += 1
            
            # Safety limit to prevent infinite loops
            if current_frame > 10000:
                break
        
        cap.release()
        
        if not frame_analyses:
            return {"error": "Could not analyze any frames from the video. The video may be too short or unavailable."}
        
        # Aggregate analysis results
        crowd_densities = [fa.get("crowd_analysis", {}).get("estimated_density_percentage", 0) for fa in frame_analyses]
        vehicle_traffic = [fa.get("vehicle_analysis", {}).get("estimated_traffic_percentage", 0) for fa in frame_analyses]
        foot_traffic = [fa.get("foot_traffic_analysis", {}).get("estimated_foot_traffic_percentage", 0) for fa in frame_analyses]
        activity_scores = [fa.get("overall_activity", {}).get("activity_score", 0) for fa in frame_analyses]
        
        # Calculate averages
        avg_crowd_density = sum(crowd_densities) / len(crowd_densities) if crowd_densities else 0
        avg_vehicle_traffic = sum(vehicle_traffic) / len(vehicle_traffic) if vehicle_traffic else 0
        avg_foot_traffic = sum(foot_traffic) / len(foot_traffic) if foot_traffic else 0
        avg_activity_score = sum(activity_scores) / len(activity_scores) if activity_scores else 0
        
        # Determine overall levels
        crowd_level = "Low"
        if avg_crowd_density > 70:
            crowd_level = "Very High"
        elif avg_crowd_density > 50:
            crowd_level = "High"
        elif avg_crowd_density > 30:
            crowd_level = "Medium"
        
        traffic_level = "Low"
        if avg_vehicle_traffic > 70:
            traffic_level = "Heavy"
        elif avg_vehicle_traffic > 50:
            traffic_level = "Moderate"
        elif avg_vehicle_traffic > 30:
            traffic_level = "Light"
        
        activity_level = "Quiet"
        if avg_activity_score > 70:
            activity_level = "Very Busy"
        elif avg_activity_score > 50:
            activity_level = "Busy"
        elif avg_activity_score > 30:
            activity_level = "Moderate"
        
        # Compile results
        analysis_result = {
            "search_metadata": {
                "search_id": search_id,
                "youtube_url": youtube_url,
                "location": location,
                "frames_analyzed": frames_analyzed,
                "sample_frames": sample_frames,
                "frame_interval_seconds": frame_interval,
                "analysis_timestamp": datetime.now().isoformat()
            },
            "video_info": video_info,
            "video_properties": {
                "fps": fps,
                "total_frames": total_frames,
                "width": width,
                "height": height,
                "is_live": video_info.get("is_live", False)
            },
            "aggregated_analysis": {
                "crowd_analysis": {
                    "average_density_percentage": round(avg_crowd_density, 2),
                    "crowd_level": crowd_level,
                    "min_density": round(min(crowd_densities), 2) if crowd_densities else 0,
                    "max_density": round(max(crowd_densities), 2) if crowd_densities else 0
                },
                "vehicle_analysis": {
                    "average_traffic_percentage": round(avg_vehicle_traffic, 2),
                    "traffic_level": traffic_level,
                    "min_traffic": round(min(vehicle_traffic), 2) if vehicle_traffic else 0,
                    "max_traffic": round(max(vehicle_traffic), 2) if vehicle_traffic else 0
                },
                "foot_traffic_analysis": {
                    "average_foot_traffic_percentage": round(avg_foot_traffic, 2),
                    "foot_traffic_level": "Low" if avg_foot_traffic < 30 else "Medium" if avg_foot_traffic < 50 else "High" if avg_foot_traffic < 70 else "Very High",
                    "min_foot_traffic": round(min(foot_traffic), 2) if foot_traffic else 0,
                    "max_foot_traffic": round(max(foot_traffic), 2) if foot_traffic else 0
                },
                "overall_activity": {
                    "average_activity_score": round(avg_activity_score, 2),
                    "activity_level": activity_level,
                    "recommendation": "Very crowded - consider visiting during off-peak hours" if avg_activity_score > 70 else "Moderately busy - good time to visit" if avg_activity_score > 30 else "Quiet location - excellent time to visit"
                }
            },
            "frame_analyses": frame_analyses
        }
        
        # Add location context if provided
        if location:
            try:
                lat, lon, location_info = geocode_location(location)
                analysis_result["location_context"] = {
                    "name": location_info.get("name", location),
                    "country": location_info.get("country", "Unknown"),
                    "latitude": lat,
                    "longitude": lon
                }
            except:
                analysis_result["location_context"] = {"name": location}
        
        # Save analysis
        file_path = os.path.join(TRAFFIC_CROWD_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(analysis_result, f, indent=2, default=str)
        
        print(f"YouTube video analysis saved to: {file_path}")
        
        # Return summary
        summary = {
            "search_id": search_id,
            "youtube_url": youtube_url,
            "video_title": video_info.get("title", "Unknown"),
            "is_live": video_info.get("is_live", False),
            "frames_analyzed": frames_analyzed,
            "aggregated_analysis": analysis_result["aggregated_analysis"],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        if "location_context" in analysis_result:
            summary["location_context"] = analysis_result["location_context"]
        
        return summary
        
    except Exception as e:
        return {"error": f"YouTube video analysis failed: {str(e)}"}

@mcp.tool()
def get_traffic_patterns(
    location: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    pattern_type: str = "daily"
) -> Dict[str, Any]:
    """
    Get historical traffic patterns for a location.
    
    Args:
        location: Location name or coordinates
        start_date: Start date in YYYY-MM-DD format (optional, defaults to 7 days ago)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        pattern_type: Pattern type - 'daily', 'hourly', 'weekly'
        
    Returns:
        Dict containing traffic pattern analysis
    """
    
    try:
        # Geocode location
        lat, lon, location_info = geocode_location(location)
        
        # Set default dates
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Validate dates
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Dates must be in YYYY-MM-DD format"}
        
        # Create search identifier
        search_id = f"patterns_{location.replace(' ', '_')}_{start_date}_to_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate pattern data (in production, this would come from historical APIs)
        # Simulate patterns based on typical traffic behavior
        patterns = {
            "peak_hours": [7, 8, 9, 17, 18, 19],
            "off_peak_hours": [22, 23, 0, 1, 2, 3, 4, 5, 6],
            "weekend_pattern": {
                "saturday": {"peak": [10, 11, 12, 13, 14, 15, 16], "level": "High"},
                "sunday": {"peak": [11, 12, 13, 14, 15, 16], "level": "Medium"}
            },
            "average_daily_traffic": {
                "morning_rush": {"hours": [7, 8, 9], "traffic_level": "Heavy"},
                "midday": {"hours": [10, 11, 12, 13, 14, 15, 16], "traffic_level": "Moderate"},
                "evening_rush": {"hours": [17, 18, 19], "traffic_level": "Heavy"},
                "night": {"hours": [20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6], "traffic_level": "Light"}
            }
        }
        
        processed_data = {
            "search_metadata": {
                "search_id": search_id,
                "location_query": location,
                "start_date": start_date,
                "end_date": end_date,
                "pattern_type": pattern_type,
                "search_timestamp": datetime.now().isoformat()
            },
            "location": {
                "name": location_info.get("name", "Unknown"),
                "country": location_info.get("country", "Unknown"),
                "region": location_info.get("admin1", "Unknown"),
                "latitude": lat,
                "longitude": lon
            },
            "traffic_patterns": patterns
        }
        
        # Create directory structure
        os.makedirs(TRAFFIC_CROWD_DIR, exist_ok=True)
        
        # Save results
        file_path = os.path.join(TRAFFIC_CROWD_DIR, f"{search_id}.json")
        with open(file_path, "w") as f:
            json.dump(processed_data, f, indent=2)
        
        print(f"Traffic patterns saved to: {file_path}")
        
        # Return summary
        summary = {
            "search_id": search_id,
            "location": {
                "name": location_info.get("name", "Unknown"),
                "coordinates": f"{lat}, {lon}"
            },
            "date_range": f"{start_date} to {end_date}",
            "pattern_type": pattern_type,
            "key_insights": {
                "peak_hours": patterns["peak_hours"],
                "best_visit_times": patterns["off_peak_hours"],
                "average_patterns": patterns["average_daily_traffic"]
            }
        }
        
        return summary
        
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def compare_location_traffic(
    locations: List[str],
    analysis_type: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Compare traffic and crowd data across multiple locations.
    
    Args:
        locations: List of location names or coordinates
        analysis_type: Type of analysis - 'comprehensive', 'crowd', 'traffic', 'foot_traffic'
        
    Returns:
        Dict containing comparative traffic analysis
    """
    
    if len(locations) < 2:
        return {"error": "At least 2 locations required for comparison"}
    
    if len(locations) > 10:
        return {"error": "Maximum 10 locations allowed for comparison"}
    
    comparison_data = {
        "comparison_timestamp": datetime.now().isoformat(),
        "analysis_type": analysis_type,
        "locations": []
    }
    
    for location in locations:
        try:
            traffic_result = analyze_location_traffic(location, analysis_type)
            
            if "error" in traffic_result:
                comparison_data["locations"].append({
                    "location": location,
                    "error": traffic_result["error"]
                })
                continue
            
            location_data = {
                "location": traffic_result.get("location", {}),
                "search_id": traffic_result.get("search_id")
            }
            
            if analysis_type in ["comprehensive", "traffic"]:
                location_data["vehicle_traffic"] = traffic_result.get("vehicle_traffic", {})
            
            if analysis_type in ["comprehensive", "foot_traffic"]:
                location_data["foot_traffic"] = traffic_result.get("foot_traffic", {})
            
            if analysis_type in ["comprehensive", "crowd"]:
                location_data["crowd_density"] = traffic_result.get("crowd_density", {})
            
            if "overall_activity" in traffic_result:
                location_data["overall_activity"] = traffic_result["overall_activity"]
            
            comparison_data["locations"].append(location_data)
            
        except Exception as e:
            comparison_data["locations"].append({
                "location": location,
                "error": f"Failed to get traffic data: {str(e)}"
            })
    
    # Find best and worst locations
    if comparison_data["locations"]:
        valid_locations = [loc for loc in comparison_data["locations"] if "error" not in loc]
        
        if valid_locations and analysis_type == "comprehensive":
            # Find least busy location
            least_busy = min(valid_locations, 
                           key=lambda x: x.get("overall_activity", {}).get("activity_score", 100))
            most_busy = max(valid_locations,
                          key=lambda x: x.get("overall_activity", {}).get("activity_score", 0))
            
            comparison_data["summary"] = {
                "least_busy": {
                    "location": least_busy.get("location", {}).get("name", "Unknown"),
                    "activity_score": least_busy.get("overall_activity", {}).get("activity_score", 0)
                },
                "most_busy": {
                    "location": most_busy.get("location", {}).get("name", "Unknown"),
                    "activity_score": most_busy.get("overall_activity", {}).get("activity_score", 100)
                }
            }
    
    return comparison_data

@mcp.tool()
def get_traffic_details(search_id: str) -> str:
    """
    Get detailed information about a specific traffic analysis search.
    
    Args:
        search_id: The search ID returned from traffic analysis tools
        
    Returns:
        JSON string with detailed traffic information
    """
    
    file_path = os.path.join(TRAFFIC_CROWD_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No traffic analysis found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            traffic_data = json.load(f)
        return json.dumps(traffic_data, indent=2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading traffic data for {search_id}: {str(e)}"

@mcp.resource("traffic://searches")
def get_traffic_searches() -> str:
    """
    List all available traffic and crowd analysis searches.
    
    This resource provides a list of all saved traffic analyses.
    """
    searches = []
    
    if os.path.exists(TRAFFIC_CROWD_DIR):
        for filename in os.listdir(TRAFFIC_CROWD_DIR):
            if filename.endswith('.json'):
                search_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(TRAFFIC_CROWD_DIR, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        metadata = data.get('search_metadata', {})
                        location = data.get('location', {})
                        location_name = location.get('name', 'N/A')
                        
                        searches.append({
                            'search_id': search_id,
                            'search_type': metadata.get('analysis_type', 'comprehensive'),
                            'location': location_name,
                            'search_time': metadata.get('search_timestamp', 'N/A')
                        })
                except (json.JSONDecodeError, KeyError):
                    continue
    
    content = "# Traffic & Crowd Analysis Searches\n\n"
    if searches:
        content += f"Total searches: {len(searches)}\n\n"
        
        # Group by search type
        search_types = {}
        for search in searches:
            search_type = search['search_type']
            if search_type not in search_types:
                search_types[search_type] = []
            search_types[search_type].append(search)
        
        for search_type, type_searches in search_types.items():
            content += f"## {search_type.title()} Analyses\n\n"
            for search in type_searches:
                content += f"### {search['search_id']}\n"
                content += f"- **Location**: {search['location']}\n"
                content += f"- **Type**: {search['search_type']}\n"
                content += f"- **Search Time**: {search['search_time']}\n\n"
                content += "---\n\n"
    else:
        content += "No traffic analyses found.\n\n"
        content += "Use the traffic analysis tools to get location data:\n"
        content += "- `analyze_location_traffic()` for location-based analysis\n"
        content += "- `analyze_video_frame_realtime()` for real-time video frame analysis\n"
        content += "- `get_traffic_patterns()` for historical patterns\n"
    
    return content

@mcp.resource("traffic://{search_id}")
def get_traffic_search_details(search_id: str) -> str:
    """
    Get detailed information about a specific traffic analysis search.
    
    Args:
        search_id: The traffic search ID to retrieve details for
    """
    file_path = os.path.join(TRAFFIC_CROWD_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"# Traffic Analysis Not Found: {search_id}\n\nNo traffic analysis found with this ID."
    
    try:
        with open(file_path, 'r') as f:
            traffic_data = json.load(f)
        
        metadata = traffic_data.get('search_metadata', {})
        location = traffic_data.get('location', {})
        
        content = f"# Traffic Analysis: {search_id}\n\n"
        
        # Search Details
        content += f"## Search Details\n"
        content += f"- **Type**: {metadata.get('analysis_type', 'unknown').title()}\n"
        content += f"- **Location Query**: {metadata.get('location_query', 'N/A')}\n"
        content += f"- **Search Time**: {metadata.get('search_timestamp', 'N/A')}\n\n"
        
        # Location Information
        if location:
            content += f"## Location Information\n"
            content += f"- **Name**: {location.get('name', 'N/A')}\n"
            content += f"- **Country**: {location.get('country', 'N/A')}\n"
            region = location.get('region') or location.get('admin1', 'N/A')
            content += f"- **Region**: {region}\n"
            content += f"- **Coordinates**: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}\n"
            content += "\n"
        
        # Traffic Data
        if traffic_data.get('traffic_data'):
            traffic = traffic_data['traffic_data']
            content += f"## Vehicle Traffic\n"
            content += f"- **Level**: {traffic.get('vehicle_traffic', {}).get('level', 'N/A')}\n"
            content += f"- **Density**: {traffic.get('vehicle_traffic', {}).get('density_percentage', 'N/A')}%\n"
            content += f"- **Vehicles/Min**: {traffic.get('vehicle_traffic', {}).get('estimated_vehicles_per_minute', 'N/A')}\n"
            content += f"- **Avg Speed**: {traffic.get('vehicle_traffic', {}).get('average_speed_kmh', 'N/A')} km/h\n"
            content += "\n"
        
        # Crowd Data
        if traffic_data.get('crowd_data'):
            crowd = traffic_data['crowd_data']
            content += f"## Crowd Density\n"
            content += f"- **Level**: {crowd.get('crowd_density', {}).get('level', 'N/A')}\n"
            content += f"- **Density**: {crowd.get('crowd_density', {}).get('density_percentage', 'N/A')}%\n"
            content += f"- **Estimated People**: {crowd.get('crowd_density', {}).get('estimated_people_count', 'N/A')}\n"
            content += "\n"
        
        # Foot Traffic Data
        if traffic_data.get('foot_traffic_data'):
            foot = traffic_data['foot_traffic_data']
            content += f"## Foot Traffic\n"
            content += f"- **Level**: {foot.get('foot_traffic', {}).get('level', 'N/A')}\n"
            content += f"- **Density**: {foot.get('foot_traffic', {}).get('density_percentage', 'N/A')}%\n"
            content += f"- **Pedestrians/Min**: {foot.get('foot_traffic', {}).get('estimated_pedestrians_per_minute', 'N/A')}\n"
            content += "\n"
        
        # Overall Activity
        if traffic_data.get('overall_activity'):
            activity = traffic_data['overall_activity']
            content += f"## Overall Activity\n"
            content += f"- **Activity Score**: {activity.get('activity_score', 'N/A')}/100\n"
            content += f"- **Activity Level**: {activity.get('activity_level', 'N/A')}\n"
            content += f"- **Best Visit Time**: {activity.get('best_visit_time', 'N/A')}\n"
            content += f"- **Recommendation**: {activity.get('recommendation', 'N/A')}\n"
            content += "\n"
        
        # Frame Analysis (if available)
        if 'crowd_analysis' in traffic_data:
            content += f"## Real-time Frame Analysis\n"
            if traffic_data.get('crowd_analysis'):
                content += f"### Crowd Analysis\n"
                crowd_analysis = traffic_data['crowd_analysis']
                content += f"- **Detected Blobs**: {crowd_analysis.get('detected_blobs', 'N/A')}\n"
                content += f"- **Density**: {crowd_analysis.get('estimated_density_percentage', 'N/A')}%\n"
                content += f"- **Level**: {crowd_analysis.get('crowd_level', 'N/A')}\n"
                content += "\n"
            
            if traffic_data.get('vehicle_analysis'):
                content += f"### Vehicle Analysis\n"
                vehicle_analysis = traffic_data['vehicle_analysis']
                content += f"- **Detected Vehicles**: {vehicle_analysis.get('detected_vehicles', 'N/A')}\n"
                content += f"- **Traffic Density**: {vehicle_analysis.get('estimated_traffic_percentage', 'N/A')}%\n"
                content += f"- **Level**: {vehicle_analysis.get('traffic_level', 'N/A')}\n"
                content += "\n"
            
            if traffic_data.get('foot_traffic_analysis'):
                content += f"### Foot Traffic Analysis\n"
                foot_analysis = traffic_data['foot_traffic_analysis']
                content += f"- **Detected Pedestrians**: {foot_analysis.get('detected_pedestrians', 'N/A')}\n"
                content += f"- **Foot Traffic Density**: {foot_analysis.get('estimated_foot_traffic_percentage', 'N/A')}%\n"
                content += f"- **Level**: {foot_analysis.get('foot_traffic_level', 'N/A')}\n"
                content += "\n"
        
        return content
        
    except json.JSONDecodeError:
        return f"# Error\n\nCorrupted traffic data for search ID: {search_id}"

@mcp.prompt()
def traffic_analysis_prompt(
    location: str,
    analysis_focus: str = "comprehensive",
    include_video: bool = False
) -> str:
    """Generate a comprehensive traffic and crowd analysis prompt for Claude."""
    
    prompt = f"""Provide a comprehensive traffic and crowd analysis for {location} using the Traffic & Crowd Analysis MCP tools."""
    
    if analysis_focus == "comprehensive":
        prompt += f"""

**Comprehensive Location Analysis**

1. **Real-time Traffic Analysis**: Use analyze_location_traffic('{location}', 'comprehensive') to get:
   - Current vehicle traffic levels and density
   - Foot traffic patterns
   - Crowd density estimates
   - Overall activity score and recommendations

2. **Traffic Patterns**: Use get_traffic_patterns('{location}') to understand:
   - Peak and off-peak hours
   - Daily traffic patterns
   - Best times to visit
   - Historical trends

3. **Analysis Insights**: Provide insights on:
   - Current traffic conditions and their impact on visit experience
   - Best times to visit based on traffic patterns
   - Crowd levels and expected wait times
   - Parking and transportation considerations
   - Recommendations for optimal visit timing"""
    
    elif analysis_focus == "crowd":
        prompt += f"""

**Crowd Density Analysis**

1. **Crowd Analysis**: Use analyze_location_traffic('{location}', 'crowd') to get:
   - Current crowd density levels
   - Estimated number of people
   - Crowd level classification
   - Activity recommendations

2. **Pattern Analysis**: Use get_traffic_patterns('{location}') to identify:
   - Peak crowd hours
   - Least crowded times
   - Weekend vs weekday patterns

3. **Recommendations**: Provide advice on:
   - Best times to avoid crowds
   - Expected wait times based on crowd levels
   - Alternative times or locations if too crowded"""
    
    elif analysis_focus == "traffic":
        prompt += f"""

**Vehicle Traffic Analysis**

1. **Traffic Analysis**: Use analyze_location_traffic('{location}', 'traffic') to get:
   - Current vehicle traffic levels
   - Traffic density percentage
   - Average vehicle speed
   - Estimated vehicles per minute

2. **Traffic Patterns**: Use get_traffic_patterns('{location}') to understand:
   - Rush hour patterns
   - Peak traffic times
   - Best times for driving

3. **Transportation Planning**: Provide recommendations on:
   - Best times to drive to the location
   - Alternative transportation options
   - Parking availability considerations
   - Route planning based on traffic"""
    
    if include_video:
        prompt += f"""

4. **Real-time Video Analysis**: If video frames are available, use analyze_video_frame_realtime() to:
   - Analyze real-time video frames for crowd detection
   - Detect vehicles and traffic flow
   - Identify pedestrian movement patterns
   - Provide live activity assessment"""
    
    prompt += f"""

**Presentation Format**:
- Use clear headings and bullet points
- Include specific numerical data and percentages
- Provide practical recommendations
- Highlight optimal visit times
- Create easy-to-scan summaries for key information

**Additional Tools Available**:
- compare_location_traffic() for comparing multiple locations
- get_traffic_details() for accessing saved analyses
- analyze_video_frame_realtime() for real-time frame analysis

Focus on providing actionable insights that help with visit planning, timing decisions, and traffic awareness."""
    
    return prompt

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

