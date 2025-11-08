"""
Currency API Module
Integration with ExchangeRate.host for currency exchange rates
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from config.settings import settings


class CurrencyAPI:
    """ExchangeRate.host Currency API integration."""
    
    def __init__(self):
        """Initialize Currency API client."""
        self.base_url = "https://api.exchangerate.host"
        self.timeout = 10  # No API key needed, so shorter timeout
    
    async def get_exchange_rates(
        self,
        base_currency: str = "EUR",
        target_currencies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get current exchange rates.
        
        Args:
            base_currency: Base currency code (e.g., 'EUR', 'USD')
            target_currencies: List of target currencies (optional)
            
        Returns:
            Exchange rates data dictionary
        """
        try:
            params = {
                "base": base_currency,
                "format": "json"
            }
            
            if target_currencies:
                params["symbols"] = ",".join(target_currencies)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/latest",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_rates_data(data)
                    else:
                        logger.error(f"Currency API error: {response.status}")
                        return self._get_error_response()
                        
        except Exception as e:
            logger.error(f"Currency API error: {str(e)}")
            return self._get_error_response()
    
    async def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Dict[str, Any]:
        """
        Convert currency amount.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Conversion result
        """
        try:
            params = {
                "amount": amount,
                "from": from_currency,
                "to": to_currency
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/convert",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_conversion_data(data)
                    else:
                        logger.error(f"Currency conversion error: {response.status}")
                        return self._get_error_response()
                        
        except Exception as e:
            logger.error(f"Currency conversion error: {str(e)}")
            return self._get_error_response()
    
    async def get_historical_rates(
        self,
        date: str,
        base_currency: str = "EUR"
    ) -> Dict[str, Any]:
        """
        Get historical exchange rates for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            base_currency: Base currency code
            
        Returns:
            Historical rates data
        """
        try:
            params = {
                "base": base_currency,
                "format": "json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{date}",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_rates_data(data)
                    else:
                        logger.error(f"Historical rates error: {response.status}")
                        return self._get_error_response()
                        
        except Exception as e:
            logger.error(f"Historical rates error: {str(e)}")
            return self._get_error_response()
    
    async def get_currency_symbols(self) -> Dict[str, Any]:
        """Get list of supported currency symbols."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/symbols",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_symbols_data(data)
                    else:
                        return self._get_error_response()
                        
        except Exception as e:
            logger.error(f"Currency symbols error: {str(e)}")
            return self._get_error_response()
    
    def _format_rates_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format exchange rates data."""
        try:
            return {
                "base": data.get("base", "EUR"),
                "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
                "rates": data.get("rates", {}),
                "success": data.get("success", True),
                "timestamp": data.get("timestamp", int(datetime.now().timestamp()))
            }
            
        except Exception as e:
            logger.error(f"Error formatting rates data: {str(e)}")
            return self._get_error_response()
    
    def _format_conversion_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format currency conversion data."""
        try:
            return {
                "amount": data.get("query", {}).get("amount", 0),
                "from": data.get("query", {}).get("from", ""),
                "to": data.get("query", {}).get("to", ""),
                "result": data.get("result", 0),
                "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
                "success": data.get("success", True)
            }
            
        except Exception as e:
            logger.error(f"Error formatting conversion data: {str(e)}")
            return self._get_error_response()
    
    def _format_symbols_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format currency symbols data."""
        try:
            return {
                "symbols": data.get("symbols", {}),
                "success": data.get("success", True)
            }
            
        except Exception as e:
            logger.error(f"Error formatting symbols data: {str(e)}")
            return self._get_error_response()
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Get error response structure."""
        return {
            "error": "Currency data unavailable",
            "rates": {},
            "success": False
        }


# Export the API class
__all__ = ["CurrencyAPI"]