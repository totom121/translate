"""
Google Translate API implementation.
"""

import requests
import time
from typing import Tuple, Optional, List
from urllib.parse import quote

from .base import BaseTranslator, TranslationError
from ..config.settings import TranslationConfig

class GoogleTranslator(BaseTranslator):
    """
    Google Translate API implementation.
    
    Uses the Google Cloud Translation API for high-quality translations.
    Supports automatic language detection and a wide range of languages.
    """
    
    def __init__(self, config: TranslationConfig):
        """Initialize Google Translator."""
        super().__init__(config)
        self.api_key = config.google_api_key
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
        self.detect_url = "https://translation.googleapis.com/language/translate/v2/detect"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 60 / config.rate_limit_per_minute if config.rate_limit_per_minute > 0 else 0
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, float]:
        """
        Translate text using Google Translate API.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_text, confidence_score)
        """
        if not self.is_available():
            raise TranslationError("Google Translate API key not configured", "google")
        
        # Rate limiting
        self._enforce_rate_limit()
        
        # Prepare request
        params = {
            'key': self.api_key,
            'q': text,
            'target': target_lang,
            'format': 'text'
        }
        
        if source_lang and source_lang != 'auto':
            params['source'] = source_lang
        
        try:
            response = requests.post(
                self.base_url,
                params=params,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or 'translations' not in data['data']:
                raise TranslationError("Invalid response format from Google Translate", "google")
            
            translation = data['data']['translations'][0]
            translated_text = translation['translatedText']
            
            # Google doesn't provide confidence scores, so we calculate our own
            confidence = self.calculate_confidence(text, translated_text)
            
            # Boost confidence for Google Translate (generally high quality)
            confidence = min(confidence + 0.2, 1.0)
            
            return translated_text, confidence
            
        except requests.exceptions.RequestException as e:
            raise TranslationError(f"Google Translate API request failed: {e}", "google")
        except KeyError as e:
            raise TranslationError(f"Unexpected response format: {e}", "google")
        except Exception as e:
            raise TranslationError(f"Google Translate error: {e}", "google")
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language using Google Translate API.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code or None if detection fails
        """
        if not self.is_available():
            return None
        
        try:
            self._enforce_rate_limit()
            
            params = {
                'key': self.api_key,
                'q': text
            }
            
            response = requests.post(
                self.detect_url,
                params=params,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'detections' in data['data']:
                detection = data['data']['detections'][0][0]
                return detection.get('language')
            
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
        
        return None
    
    def is_available(self) -> bool:
        """Check if Google Translate API is available."""
        return bool(self.api_key)
    
    def health_check(self) -> bool:
        """Perform health check by translating a simple phrase."""
        if not self.is_available():
            return False
        
        try:
            # Simple test translation
            translated, confidence = self.translate("hello", "en", "es")
            return bool(translated and confidence > 0)
        except Exception:
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages from Google Translate."""
        # Common languages supported by Google Translate
        return [
            'af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb',
            'ny', 'zh', 'co', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr',
            'fy', 'gl', 'ka', 'de', 'el', 'gu', 'ht', 'ha', 'haw', 'iw', 'hi', 'hmn', 'hu',
            'is', 'ig', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km', 'ko', 'ku', 'ky',
            'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn',
            'my', 'ne', 'no', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'ru', 'sm', 'gd', 'sr',
            'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta',
            'te', 'th', 'tr', 'uk', 'ur', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu'
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
        Calculate confidence score for Google Translate.
        
        Google Translate generally provides high-quality translations,
        so we use a more optimistic confidence calculation.
        """
        if not translated or translated == original:
            return 0.0
        
        # Base confidence for Google Translate
        base_confidence = 0.8
        
        # Adjust based on text characteristics
        if len(translated.split()) > 1:  # Multi-word translations are generally more reliable
            base_confidence += 0.1
        
        if any(char.isdigit() for char in original):  # Technical text with numbers
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)

