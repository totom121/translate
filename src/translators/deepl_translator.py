"""
DeepL API translator implementation.
"""

import requests
import time
from typing import Tuple, Optional, List

from .base import BaseTranslator, TranslationError
from ..config.settings import TranslationConfig

class DeepLTranslator(BaseTranslator):
    """
    DeepL API translator implementation.
    
    DeepL provides high-quality neural machine translation with excellent
    support for European languages including German automotive terminology.
    """
    
    def __init__(self, config: TranslationConfig):
        """Initialize DeepL translator."""
        super().__init__(config)
        self.api_key = config.deepl_api_key
        
        # DeepL API endpoints
        if self.api_key and self.api_key.endswith(':fx'):
            # Free API
            self.base_url = "https://api-free.deepl.com/v2"
        else:
            # Pro API
            self.base_url = "https://api.deepl.com/v2"
        
        self.translate_url = f"{self.base_url}/translate"
        self.usage_url = f"{self.base_url}/usage"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 60 / config.rate_limit_per_minute if config.rate_limit_per_minute > 0 else 0
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, float]:
        """
        Translate text using DeepL API.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_text, confidence_score)
        """
        if not self.is_available():
            raise TranslationError("DeepL API key not configured", "deepl")
        
        # Rate limiting
        self._enforce_rate_limit()
        
        # Map language codes to DeepL format
        source_lang_deepl = self._map_language_code(source_lang)
        target_lang_deepl = self._map_language_code(target_lang)
        
        # Prepare request
        data = {
            'auth_key': self.api_key,
            'text': text,
            'target_lang': target_lang_deepl,
            'preserve_formatting': '1',
            'formality': 'default'
        }
        
        if source_lang_deepl and source_lang_deepl != 'auto':
            data['source_lang'] = source_lang_deepl
        
        try:
            response = requests.post(
                self.translate_url,
                data=data,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'translations' not in result or not result['translations']:
                raise TranslationError("Invalid response format from DeepL", "deepl")
            
            translation = result['translations'][0]
            translated_text = translation['text']
            
            # DeepL doesn't provide confidence scores, calculate our own
            confidence = self.calculate_confidence(text, translated_text)
            
            # Boost confidence for DeepL (known for high quality)
            confidence = min(confidence + 0.25, 1.0)
            
            return translated_text, confidence
            
        except requests.exceptions.RequestException as e:
            raise TranslationError(f"DeepL API request failed: {e}", "deepl")
        except KeyError as e:
            raise TranslationError(f"Unexpected response format: {e}", "deepl")
        except Exception as e:
            raise TranslationError(f"DeepL translation error: {e}", "deepl")
    
    def is_available(self) -> bool:
        """Check if DeepL API is available."""
        return bool(self.api_key)
    
    def health_check(self) -> bool:
        """Perform health check by checking API usage."""
        if not self.is_available():
            return False
        
        try:
            self._enforce_rate_limit()
            
            response = requests.get(
                self.usage_url,
                params={'auth_key': self.api_key},
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            usage_data = response.json()
            return 'character_count' in usage_data
            
        except Exception:
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages for DeepL."""
        return [
            'bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi', 'fr', 'hu', 'id', 'it',
            'ja', 'ko', 'lt', 'lv', 'nb', 'nl', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sv',
            'tr', 'uk', 'zh'
        ]
    
    def _map_language_code(self, lang_code: str) -> str:
        """
        Map language codes to DeepL format.
        
        Args:
            lang_code: Standard language code
            
        Returns:
            DeepL-compatible language code
        """
        if not lang_code or lang_code == 'auto':
            return None
        
        # DeepL language code mapping
        mapping = {
            'de': 'DE',
            'en': 'EN',
            'fr': 'FR',
            'it': 'IT',
            'es': 'ES',
            'pt': 'PT',
            'ru': 'RU',
            'ja': 'JA',
            'zh': 'ZH',
            'nl': 'NL',
            'pl': 'PL',
            'sv': 'SV',
            'da': 'DA',
            'fi': 'FI',
            'no': 'NB',
            'cs': 'CS',
            'sk': 'SK',
            'sl': 'SL',
            'et': 'ET',
            'lv': 'LV',
            'lt': 'LT',
            'bg': 'BG',
            'hu': 'HU',
            'ro': 'RO',
            'el': 'EL',
            'tr': 'TR',
            'uk': 'UK',
            'ko': 'KO',
            'id': 'ID'
        }
        
        return mapping.get(lang_code.lower(), lang_code.upper())
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests."""
        if self.min_request_interval > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        
        self.last_request_time = time.time()
    
    def calculate_confidence(self, original: str, translated: str) -> float:
        """
        Calculate confidence score for DeepL translations.
        
        DeepL is known for high-quality translations, especially for European languages.
        """
        if not translated or translated == original:
            return 0.0
        
        # Base confidence for DeepL
        base_confidence = 0.85
        
        # Boost for technical content
        if any(term in original.lower() for term in ['temperatur', 'druck', 'motor', 'sensor']):
            base_confidence += 0.05
        
        # Boost for German source (DeepL's strength)
        if any(word in original.lower() for word in ['der', 'die', 'das', 'und', 'für']):
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def get_usage_info(self) -> Optional[dict]:
        """
        Get API usage information.
        
        Returns:
            Dictionary with usage information or None if unavailable
        """
        if not self.is_available():
            return None
        
        try:
            self._enforce_rate_limit()
            
            response = requests.get(
                self.usage_url,
                params={'auth_key': self.api_key},
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.warning(f"Failed to get usage info: {e}")
            return None

