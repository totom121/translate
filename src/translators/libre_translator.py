"""
LibreTranslate implementation for free, open-source translation.
"""

import requests
import time
from typing import Tuple, Optional, List

from .base import BaseTranslator, TranslationError
from ..config.settings import TranslationConfig

class LibreTranslator(BaseTranslator):
    """
    LibreTranslate implementation.
    
    Uses LibreTranslate, a free and open-source machine translation API.
    Can be self-hosted or use public instances. Good fallback option
    when commercial services are unavailable.
    """
    
    def __init__(self, config: TranslationConfig):
        """Initialize LibreTranslate translator."""
        super().__init__(config)
        
        # Default to public LibreTranslate instance
        self.base_url = "https://libretranslate.de"
        self.api_key = None  # LibreTranslate can work without API key
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 60 / config.rate_limit_per_minute if config.rate_limit_per_minute > 0 else 1.0  # Conservative rate limit
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, float]:
        """
        Translate text using LibreTranslate.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_text, confidence_score)
        """
        # Rate limiting
        self._enforce_rate_limit()
        
        # Prepare request data
        data = {
            'q': text,
            'source': source_lang if source_lang != 'auto' else 'auto',
            'target': target_lang,
            'format': 'text'
        }
        
        if self.api_key:
            data['api_key'] = self.api_key
        
        try:
            response = requests.post(
                f"{self.base_url}/translate",
                data=data,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'translatedText' not in result:
                raise TranslationError("Invalid response format from LibreTranslate", "libre")
            
            translated_text = result['translatedText']
            
            # LibreTranslate doesn't provide confidence scores
            confidence = self.calculate_confidence(text, translated_text)
            
            return translated_text, confidence
            
        except requests.exceptions.RequestException as e:
            raise TranslationError(f"LibreTranslate API request failed: {e}", "libre")
        except KeyError as e:
            raise TranslationError(f"Unexpected response format: {e}", "libre")
        except Exception as e:
            raise TranslationError(f"LibreTranslate error: {e}", "libre")
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language using LibreTranslate.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code or None if detection fails
        """
        try:
            self._enforce_rate_limit()
            
            data = {'q': text}
            if self.api_key:
                data['api_key'] = self.api_key
            
            response = requests.post(
                f"{self.base_url}/detect",
                data=data,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            result = response.json()
            
            if isinstance(result, list) and result:
                # LibreTranslate returns a list of detections
                best_detection = max(result, key=lambda x: x.get('confidence', 0))
                return best_detection.get('language')
            
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
        
        return None
    
    def is_available(self) -> bool:
        """Check if LibreTranslate is available."""
        try:
            # Test with a simple request
            response = requests.get(
                f"{self.base_url}/languages",
                timeout=5  # Short timeout for availability check
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def health_check(self) -> bool:
        """Perform health check by getting supported languages."""
        try:
            self._enforce_rate_limit()
            
            response = requests.get(
                f"{self.base_url}/languages",
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            languages = response.json()
            return isinstance(languages, list) and len(languages) > 0
            
        except Exception:
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages from LibreTranslate."""
        try:
            self._enforce_rate_limit()
            
            response = requests.get(
                f"{self.base_url}/languages",
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            languages = response.json()
            if isinstance(languages, list):
                return [lang['code'] for lang in languages if 'code' in lang]
            
        except Exception as e:
            self.logger.warning(f"Failed to get supported languages: {e}")
        
        # Fallback to common languages typically supported by LibreTranslate
        return [
            'ar', 'az', 'ca', 'cs', 'da', 'de', 'el', 'en', 'eo', 'es', 'fa', 'fi', 'fr',
            'ga', 'he', 'hi', 'hu', 'id', 'it', 'ja', 'ko', 'nl', 'pl', 'pt', 'ru', 'sk',
            'sv', 'tr', 'uk', 'zh'
        ]
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests."""
        if self.min_request_interval > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        
        self.last_request_time = time.time()
    
    def calculate_confidence(self, original: str, translated: str) -> float:
        """
        Calculate confidence score for LibreTranslate.
        
        LibreTranslate is open-source and may have variable quality,
        so we use a more conservative confidence calculation.
        """
        if not translated or translated == original:
            return 0.0
        
        # Base confidence for LibreTranslate (more conservative)
        base_confidence = 0.6
        
        # Boost for common language pairs
        if any(word in original.lower() for word in ['der', 'die', 'das', 'le', 'la', 'el']):
            base_confidence += 0.1
        
        # Boost for longer text (more context)
        if len(original.split()) > 2:
            base_confidence += 0.05
        
        # Penalty for very short translations
        if len(translated.split()) < len(original.split()) * 0.5:
            base_confidence -= 0.1
        
        return max(min(base_confidence, 0.8), 0.1)  # Cap at 0.8 for LibreTranslate
    
    def set_api_url(self, url: str):
        """
        Set custom LibreTranslate API URL.
        
        Args:
            url: Custom LibreTranslate instance URL
        """
        self.base_url = url.rstrip('/')
        self.logger.info(f"LibreTranslate URL set to: {self.base_url}")
    
    def set_api_key(self, api_key: str):
        """
        Set API key for LibreTranslate instance that requires authentication.
        
        Args:
            api_key: API key for LibreTranslate
        """
        self.api_key = api_key
        self.logger.info("LibreTranslate API key configured")
    
    def get_usage_info(self) -> Optional[dict]:
        """
        Get usage information if available.
        
        Returns:
            Dictionary with usage information or None
        """
        # LibreTranslate typically doesn't provide usage info
        # but we can return basic statistics
        return {
            'service': 'LibreTranslate',
            'base_url': self.base_url,
            'has_api_key': bool(self.api_key),
            'note': 'LibreTranslate typically does not provide usage statistics'
        }

