"""
Response Simulator
Simulates MCP server responses with configurable delays
"""

import time
import random
from typing import Dict, Any, Optional

class ResponseSimulator:
    """Simulates MCP server responses with realistic delays"""
    
    def __init__(self, base_delay_ms: int = 50, variance_ms: int = 20):
        self.base_delay_ms = base_delay_ms
        self.variance_ms = variance_ms
        self.enabled = True
    
    def simulate_delay(self):
        """Simulate network/processing delay"""
        if not self.enabled:
            return
        
        delay_ms = self.base_delay_ms + random.randint(-self.variance_ms, self.variance_ms)
        delay_ms = max(0, delay_ms)  # Ensure non-negative
        time.sleep(delay_ms / 1000.0)
    
    def simulate_response(
        self,
        data: Dict[str, Any],
        delay: Optional[float] = None
    ) -> Dict[str, Any]:
        """Simulate a response with delay"""
        if delay is None:
            self.simulate_delay()
        else:
            time.sleep(delay)
        
        return data
    
    def simulate_error(
        self,
        error_message: str,
        error_rate: float = 0.0
    ) -> Optional[Dict[str, Any]]:
        """Simulate an error response based on error rate"""
        if random.random() < error_rate:
            return {
                "error": error_message,
                "success": False
            }
        return None
