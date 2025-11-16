"""
Configuration Management - Handles app configuration and environment variables
Provides secure access to API keys and settings
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


@dataclass
class APIConfig:
    """API configuration settings."""
    anthropic_api_key: str = ""
    google_maps_api_key: str = ""
    youtube_api_key: str = ""
    openweather_api_key: str = ""
    
    def __post_init__(self):
        """Load API keys from environment variables."""
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY", "")
    
    def validate(self) -> Dict[str, bool]:
        """
        Validate API keys are present.
        
        Returns:
            Dictionary of API key validation status
        """
        return {
            "anthropic": bool(self.anthropic_api_key),
            "google_maps": bool(self.google_maps_api_key),
            "youtube": bool(self.youtube_api_key),
            "openweather": bool(self.openweather_api_key)
        }


@dataclass
class AppConfig:
    """Application configuration settings."""
    app_name: str = "Travel Genie"
    app_version: str = "1.0.0"
    debug_mode: bool = False
    max_chat_history: int = 50
    video_analysis_duration: int = 30
    mcp_server_timeout: int = 10
    
    # UI Configuration
    theme: str = "light"
    sidebar_state: str = "expanded"
    show_analytics: bool = True
    
    # Model Configuration
    claude_model: str = "claude-sonnet-4-20250514"
    claude_temperature: float = 0.7
    claude_max_tokens: int = 4096
    
    yolo_model: str = "yolo11n.pt"
    yolo_confidence: float = 0.25
    yolo_device: str = "cpu"
    
    def __post_init__(self):
        """Load configuration from environment or config file."""
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.claude_model = os.getenv("CLAUDE_MODEL", self.claude_model)
        self.yolo_device = os.getenv("YOLO_DEVICE", self.yolo_device)


# @dataclass
# class ServerConfig:
#     """MCP Server configuration settings."""
#     servers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
#     stdio_buffer_size: int = 65536
#     process_timeout: int = 30
#     auto_restart: bool = True
#     health_check_interval: int = 60
    
#     def __post_init__(self):
#         """Initialize server configurations."""
#         self.servers = {
#             "itinerary": {
#                 "name": "travel-itinerary",
#                 "path": "mcp_servers/itinerary_server.py",
#                 "enabled": True,
#                 "auto_start": True
#             },
#             "maps": {
#                 "name": "travel-maps",
#                 "path": "mcp_servers/maps_server.py",
#                 "enabled": True,
#                 "auto_start": True
#             },
#             "booking": {
#                 "name": "travel-booking",
#                 "path": "mcp_servers/booking_server.py",
#                 "enabled": True,
#                 "auto_start": True
#             }
#         }
@dataclass
class ServerConfig:
    """MCP Server configuration settings."""
    servers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    stdio_buffer_size: int = 65536
    process_timeout: int = 30
    auto_restart: bool = True
    health_check_interval: int = 60
    # Add transport and port configuration
    transport: str = "stdio"  # "stdio" or "sse" (Server-Sent Events)
    default_host: str = "localhost"
    default_port_start: int = 8000  # Starting port number
    
    def __post_init__(self):
        """Initialize server configurations."""
        self.servers = {
            "itinerary": {
                "name": "travel-itinerary",
                "path": "mcp_servers/itinerary_server.py",
                "enabled": True,
                "auto_start": True,
                "host": os.getenv("MCP_ITINERARY_HOST", self.default_host),
                "port": int(os.getenv("MCP_ITINERARY_PORT", self.default_port_start)),
                "transport": os.getenv("MCP_ITINERARY_TRANSPORT", self.transport)
            },
            "maps": {
                "name": "travel-maps",
                "path": "mcp_servers/maps_server.py",
                "enabled": True,
                "auto_start": True,
                "host": os.getenv("MCP_MAPS_HOST", self.default_host),
                "port": int(os.getenv("MCP_MAPS_PORT", self.default_port_start + 1)),
                "transport": os.getenv("MCP_MAPS_TRANSPORT", self.transport)
            },
            "booking": {
                "name": "travel-booking",
                "path": "mcp_servers/booking_server.py",
                "enabled": True,
                "auto_start": True,
                "host": os.getenv("MCP_BOOKING_HOST", self.default_host),
                "port": int(os.getenv("MCP_BOOKING_PORT", self.default_port_start + 2)),
                "transport": os.getenv("MCP_BOOKING_TRANSPORT", self.transport)
            }
        }

class ConfigManager:
    """
    Manages all application configurations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path or os.getenv("CONFIG_PATH", "config.json")
        self.api_config = APIConfig()
        self.app_config = AppConfig()
        self.server_config = ServerConfig()
        
        # Load custom configuration if exists
        self._load_custom_config()
        
        # Validate configuration
        self._validate_config()
    
    def _load_custom_config(self):
        """Load custom configuration from file if exists."""
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    custom_config = json.load(f)
                
                # Update app config
                if "app" in custom_config:
                    for key, value in custom_config["app"].items():
                        if hasattr(self.app_config, key):
                            setattr(self.app_config, key, value)
                
                # Update server config
                if "servers" in custom_config:
                    self.server_config.servers.update(custom_config["servers"])
                
                logger.info(f"Loaded custom configuration from {config_file}")
                
            except Exception as e:
                logger.error(f"Error loading custom config: {e}")
    
    def _validate_config(self):
        """Validate configuration settings."""
        # Check API keys
        api_status = self.api_config.validate()
        
        # Log warnings for missing API keys
        if not api_status["anthropic"]:
            logger.warning("Anthropic API key not configured - Chat features will be limited")
        
        if not api_status["youtube"]:
            logger.warning("YouTube API key not configured - Video analysis may be limited")
        
        # Validate paths
        for server_name, server_info in self.server_config.servers.items():
            server_path = Path(server_info["path"])
            if not server_path.exists():
                logger.warning(f"Server file not found: {server_path}")
                server_info["enabled"] = False
    
    def save_config(self, path: Optional[str] = None):
        """
        Save current configuration to file.
        
        Args:
            path: Optional path to save configuration
        """
        save_path = path or self.config_path
        
        config_data = {
            "app": {
                "app_name": self.app_config.app_name,
                "app_version": self.app_config.app_version,
                "debug_mode": self.app_config.debug_mode,
                "theme": self.app_config.theme,
                "claude_model": self.app_config.claude_model,
                "yolo_model": self.app_config.yolo_model
            },
            "servers": self.server_config.servers
        }
        
        try:
            with open(save_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a service.
        
        Args:
            service: Service name
        
        Returns:
            API key or None
        """
        service_map = {
            "anthropic": self.api_config.anthropic_api_key,
            "claude": self.api_config.anthropic_api_key,
            "google_maps": self.api_config.google_maps_api_key,
            "youtube": self.api_config.youtube_api_key,
            "openweather": self.api_config.openweather_api_key
        }
        
        return service_map.get(service.lower())
    
    def update_setting(self, category: str, key: str, value: Any):
        """
        Update a configuration setting.
        
        Args:
            category: Configuration category ('app', 'server', 'api')
            key: Setting key
            value: New value
        """
        if category == "app" and hasattr(self.app_config, key):
            setattr(self.app_config, key, value)
            logger.info(f"Updated app setting: {key} = {value}")
        
        elif category == "server" and key in self.server_config.servers:
            self.server_config.servers[key].update(value)
            logger.info(f"Updated server config: {key}")
        
        elif category == "api" and hasattr(self.api_config, key):
            setattr(self.api_config, key, value)
            logger.info(f"Updated API config: {key}")
        
        else:
            logger.warning(f"Unknown configuration: {category}.{key}")
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """
        Get configuration formatted for Streamlit.
        
        Returns:
            Streamlit-compatible configuration
        """
        return {
            "page_title": self.app_config.app_name,
            "page_icon": "✈️",
            "layout": "wide",
            "initial_sidebar_state": self.app_config.sidebar_state,
            "menu_items": {
                "About": f"{self.app_config.app_name} v{self.app_config.app_version}",
                "Report a bug": "https://github.com/yourusername/travel-genie/issues"
            }
        }


# Global configuration instance
config = ConfigManager()

# Export commonly used configurations
APP_NAME = config.app_config.app_name
APP_VERSION = config.app_config.app_version
DEBUG_MODE = config.app_config.debug_mode
CLAUDE_API_KEY = config.api_config.anthropic_api_key

def get_config() -> ConfigManager:
    """Get global configuration instance."""
    return config
