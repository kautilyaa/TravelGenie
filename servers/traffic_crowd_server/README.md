# Traffic & Crowd Server

MCP server for real-time traffic and crowd analysis using computer vision.

## Features

- **analyze_location_traffic**: Get traffic and crowd data for locations
- **analyze_video_frame_realtime**: Analyze video frames for crowd/vehicle detection
- **analyze_youtube_video**: Analyze YouTube videos/live streams
- **get_traffic_patterns**: Get historical traffic patterns
- **compare_location_traffic**: Compare traffic across multiple locations

## Setup

1. Install dependencies: `uv sync`
2. Configure Claude Desktop to use this server

## Usage

```
Analyze traffic at Times Square, New York
Analyze this YouTube live stream: https://youtube.com/watch?v=...
```

## Requirements

- Python 3.12.1+
- opencv-python, numpy, yt-dlp, fastmcp, mcp, requests
- No API key required
