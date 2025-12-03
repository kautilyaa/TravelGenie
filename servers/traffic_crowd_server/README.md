# Traffic & Crowd Analysis Server

A Model Context Protocol (MCP) server that provides real-time analysis of location data including crowd density, foot traffic, vehicle traffic, and real-time video frame analysis.

## Features

- **Real-time Location Analysis**: Get current traffic and crowd conditions for any location
- **Video Frame Analysis**: Analyze video frames in real-time for crowd, vehicle, and pedestrian detection
- **Traffic Pattern Analysis**: Understand historical traffic patterns and peak hours
- **Multi-location Comparison**: Compare traffic conditions across multiple locations
- **Computer Vision**: Uses OpenCV for advanced image processing and detection

## Tools

### `analyze_location_traffic`
Get real-time traffic and crowd data for a specific location.

**Parameters:**
- `location` (str): Location name or coordinates (lat,lon)
- `analysis_type` (str): Type of analysis - 'comprehensive', 'crowd', 'traffic', 'foot_traffic'

**Returns:** Dict containing traffic and crowd analysis data

**Example:**
```python
analyze_location_traffic("Times Square, New York", "comprehensive")
```

### `analyze_video_frame_realtime`
Analyze a real-time video frame for crowd, foot traffic, and vehicle detection.

**Parameters:**
- `frame_data` (str): Base64 encoded image string or file path to image
- `frame_type` (str): Type of input - 'base64' (default) or 'file_path'
- `location` (str, optional): Optional location name for context

**Returns:** Dict containing real-time frame analysis results

**Example:**
```python
# With base64 encoded image
analyze_video_frame_realtime(base64_image_string, "base64", "Central Park")

# With file path
analyze_video_frame_realtime("/path/to/image.jpg", "file_path", "Central Park")
```

### `analyze_youtube_video`
Analyze a YouTube video (including live streams) for crowd, foot traffic, and vehicle detection. Perfect for analyzing live camera feeds from locations.

**Parameters:**
- `youtube_url` (str): YouTube video URL (supports regular videos and live streams)
- `location` (str, optional): Optional location name for context
- `sample_frames` (int): Number of frames to sample and analyze (default: 5)
- `frame_interval` (int): Interval between sampled frames in seconds (default: 10)

**Returns:** Dict containing aggregated video analysis results with crowd, traffic, and activity data

**Example:**
```python
# Analyze a live YouTube stream
analyze_youtube_video(
    "https://www.youtube.com/watch?v=abc123",
    location="Times Square, New York",
    sample_frames=10,
    frame_interval=15
)

# Analyze a regular YouTube video
analyze_youtube_video(
    "https://youtu.be/xyz789",
    location="Central Park"
)
```

### `get_traffic_patterns`
Get historical traffic patterns for a location.

**Parameters:**
- `location` (str): Location name or coordinates
- `start_date` (str, optional): Start date in YYYY-MM-DD format (defaults to 7 days ago)
- `end_date` (str, optional): End date in YYYY-MM-DD format (defaults to today)
- `pattern_type` (str): Pattern type - 'daily', 'hourly', 'weekly'

**Returns:** Dict containing traffic pattern analysis

**Example:**
```python
get_traffic_patterns("Times Square", "2025-01-01", "2025-01-07", "daily")
```

### `compare_location_traffic`
Compare traffic and crowd data across multiple locations.

**Parameters:**
- `locations` (List[str]): List of location names or coordinates
- `analysis_type` (str): Type of analysis - 'comprehensive', 'crowd', 'traffic', 'foot_traffic'

**Returns:** Dict containing comparative traffic analysis

**Example:**
```python
compare_location_traffic(["Times Square", "Central Park", "Brooklyn Bridge"], "comprehensive")
```

### `get_traffic_details`
Get detailed information about a specific traffic analysis search.

**Parameters:**
- `search_id` (str): The search ID returned from traffic analysis tools

**Returns:** JSON string with detailed traffic information

## Resources

### `traffic://searches`
List all available traffic and crowd analysis searches.

### `traffic://{search_id}`
Get detailed information about a specific traffic analysis search.

## Video Frame Analysis

The server uses computer vision techniques for real-time frame analysis:

- **Crowd Detection**: Uses blob detection to estimate crowd density
- **Vehicle Detection**: Uses edge detection and contour analysis to identify vehicles
- **Pedestrian Detection**: Uses HOG (Histogram of Oriented Gradients) descriptor for pedestrian detection
- **Activity Scoring**: Combines all metrics to provide an overall activity score

## YouTube Video Analysis

The server can analyze YouTube videos and live streams:

- **Live Stream Support**: Works with live YouTube streams for real-time location monitoring
- **Frame Sampling**: Samples frames at configurable intervals for efficient analysis
- **Aggregated Results**: Provides average, min, and max values across sampled frames
- **Video Metadata**: Extracts video information including title, duration, and live status
- **Stream Processing**: Uses yt-dlp to extract video streams and OpenCV to process frames

## Installation

1. Install dependencies:
```bash
pip install -e .
```

Or install manually:
```bash
pip install fastmcp mcp requests opencv-python numpy yt-dlp typing-extensions
```

2. Run the server:
```bash
python main.py
```

## Usage

### Basic Location Analysis
```python
# Get comprehensive traffic analysis
result = analyze_location_traffic("Times Square, New York", "comprehensive")
print(result)
```

### Real-time Video Frame Analysis
```python
# Read image file and convert to base64
import base64
with open("location_frame.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Analyze frame
result = analyze_video_frame_realtime(image_data, "base64", "Times Square")
print(result)
```

### YouTube Video Analysis
```python
# Analyze a live YouTube stream from a location
result = analyze_youtube_video(
    "https://www.youtube.com/watch?v=live_stream_id",
    location="Times Square, New York",
    sample_frames=10,
    frame_interval=15
)
print(result)

# The result includes:
# - Aggregated crowd density analysis
# - Vehicle traffic analysis
# - Foot traffic analysis
# - Overall activity score
# - Individual frame analyses
```

### Traffic Pattern Analysis
```python
# Get traffic patterns
patterns = get_traffic_patterns("Times Square", pattern_type="daily")
print(patterns)
```

### Compare Multiple Locations
```python
# Compare traffic across locations
comparison = compare_location_traffic(
    ["Times Square", "Central Park", "Brooklyn Bridge"],
    "comprehensive"
)
print(comparison)
```

## Data Storage

All analysis results are stored in the `traffic_crowd_data/` directory as JSON files. Each search is saved with a unique search ID that can be retrieved later using `get_traffic_details()`.

## Technical Details

### Computer Vision Methods

1. **Crowd Density Estimation**:
   - Uses SimpleBlobDetector for blob detection
   - Estimates density based on detected blobs
   - Classifies crowd levels: Low, Medium, High, Very High

2. **Vehicle Detection**:
   - Gaussian blur for noise reduction
   - Canny edge detection
   - Contour analysis to identify vehicles
   - Filters by contour area to distinguish vehicles

3. **Pedestrian Detection**:
   - HOG (Histogram of Oriented Gradients) descriptor
   - Default people detector from OpenCV
   - Multi-scale detection for accuracy

### Traffic Pattern Simulation

Currently, the server simulates traffic patterns based on:
- Time of day (peak hours: 7-9 AM, 5-7 PM)
- Day of week (weekend patterns)
- Historical averages

In production, this would integrate with real-time traffic APIs such as:
- Google Maps Traffic API
- TomTom Traffic API
- HERE Traffic API
- Local traffic monitoring systems

## Integration with Travel Assistant

This server integrates seamlessly with the Travel Assistant system:

1. **Location Planning**: Use traffic data to recommend best visit times
2. **Route Optimization**: Consider traffic conditions when planning routes
3. **Crowd Avoidance**: Help users avoid crowded locations
4. **Real-time Updates**: Provide live traffic conditions during trips

## Future Enhancements

- Integration with real-time traffic APIs
- Machine learning models for improved detection accuracy
- Historical data storage and trend analysis
- Continuous live stream monitoring (currently samples frames)
- Integration with weather data for traffic correlation
- Mobile app integration for live camera feeds
- Support for other video platforms (Twitch, Facebook Live, etc.)

## Requirements

- Python 3.12.1+
- OpenCV 4.8.0+
- NumPy 1.24.0+
- yt-dlp 2023.12.30+ (for YouTube video analysis)
- FastMCP 2.5.1+
- Requests 2.32.3+

## License

See main project LICENSE file.

