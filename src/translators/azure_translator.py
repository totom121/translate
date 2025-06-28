"""
Azure Translator implementation.
"""

import requests
import time
import uuid
from typing import Tuple, Optional, List

from .base import BaseTranslator, TranslationError
from ..config.settings import TranslationConfig

class AzureTranslator(BaseTranslator):
    """
    Azure Translator implementation.
    
    Uses Microsoft Azure Cognitive Services Translator for translation.
    Supports a wide range of languages with good quality for technical content.
    """
    
    def __init__(self, config: TranslationConfig):
        """Initialize Azure Translator."""
        super().__init__(config)
        self.api_key = config.azure_api_key
        self.region = config.azure_region or 'global'
        
        # Azure Translator endpoints
        self.base_url = "https://api.cognitive.microsofttranslator.com"
        self.translate_url = f"{self.base_url}/translate"
        self.detect_url = f"{self.base_url}/detect"
        self.languages_url = f"{self.base_url}/languages"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 60 / config.rate_limit_per_minute if config.rate_limit_per_minute > 0 else 0
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, float]:
        """
        Translate text using Azure Translator.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_text, confidence_score)
        """
        if not self.is_available():
            raise TranslationError("Azure Translator API key not configured", "azure")
        
        # Rate limiting
        self._enforce_rate_limit()
        
        # Prepare headers
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Ocp-Apim-Subscription-Region': self.region,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        
        # Prepare parameters
        params = {
            'api-version': '3.0',
            'to': target_lang
        }
        
        if source_lang and source_lang != 'auto':
            params['from'] = source_lang
        
        # Prepare body
        body = [{'text': text}]
        
        try:
            response = requests.post(
                self.translate_url,
                params=params,
                headers=headers,
                json=body,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            result = response.json()
            
            if not result or 'translations' not in result[0]:
                raise TranslationError("Invalid response format from Azure Translator", "azure")
            
            translation = result[0]['translations'][0]
            translated_text = translation['text']
            
            # Azure provides confidence scores for some translations
            confidence = translation.get('confidence', None)
            if confidence is None:
                confidence = self.calculate_confidence(text, translated_text)
            
            return translated_text, confidence
            
        except requests.exceptions.RequestException as e:
            raise TranslationError(f"Azure Translator API request failed: {e}", "azure")
        except (KeyError, IndexError) as e:
            raise TranslationError(f"Unexpected response format: {e}", "azure")
        except Exception as e:
            raise TranslationError(f"Azure Translator error: {e}", "azure")
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language using Azure Translator.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code or None if detection fails
        """
        if not self.is_available():
            return None
        
        try:
            self._enforce_rate_limit()
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Ocp-Apim-Subscription-Region': self.region,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }
            
            params = {'api-version': '3.0'}
            body = [{'text': text}]
            
            response = requests.post(
                self.detect_url,
                params=params,
                headers=headers,
                json=body,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result and 'language' in result[0]:
                return result[0]['language']
            
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
        
        return None
    
    def is_available(self) -> bool:
        """Check if Azure Translator is available."""
        return bool(self.api_key)
    
    def health_check(self) -> bool:
        """Perform health check by getting supported languages."""
        if not self.is_available():
            return False
        
        try:
            self._enforce_rate_limit()
            
            response = requests.get(
                self.languages_url,
                params={'api-version': '3.0', 'scope': 'translation'},
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            languages = response.json()
            return 'translation' in languages and len(languages['translation']) > 0
            
        except Exception:
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages from Azure Translator."""
        if not self.is_available():
            return []
        
        try:
            self._enforce_rate_limit()
            
            response = requests.get(
                self.languages_url,
                params={'api-version': '3.0', 'scope': 'translation'},
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            
            languages = response.json()
            if 'translation' in languages:
                return list(languages['translation'].keys())
            
        except Exception as e:
            self.logger.warning(f"Failed to get supported languages: {e}")
        
        # Fallback to common languages
        return [
            'af', 'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es',
            'et', 'fa', 'fi', 'fr', 'ga', 'gu', 'he', 'hi', 'hr', 'hu', 'hy', 'id', 'is',
            'it', 'ja', 'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'lo', 'lt', 'lv', 'mg',
            'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'nb', 'ne', 'nl', 'pa', 'pl',
            'pt', 'ro', 'ru', 'sk', 'sl', 'sm', 'sq', 'sr', 'sv', 'sw', 'ta', 'te', 'th',
            'tl', 'to', 'tr', 'ty', 'uk', 'ur', 'uz', 'vi', 'zh'
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
        Calculate confidence score for Azure Translator.
        
        Azure Translator provides good quality translations with consistent results.
        """
        if not translated or translated == original:
            return 0.0
        
        # Base confidence for Azure Translator
        base_confidence = 0.75
        
        # Boost for technical content
        if any(term in original.lower() for term in ['temperatur', 'druck', 'motor', 'sensor']):
            base_confidence += 0.05
        
        # Boost for longer text (usually more context)
        if len(original.split()) > 3:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> List[Tuple[str, float]]:
        """
        Translate multiple texts in a single request for efficiency.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of (translated_text, confidence) tuples
        """
        if not self.is_available():
            raise TranslationError("Azure Translator API key not configured", "azure")
        
        if not texts:
            return []
        
        # Azure supports batch translation
        self._enforce_rate_limit()
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Ocp-Apim-Subscription-Region': self.region,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        
        params = {
            'api-version': '3.0',
            'to': target_lang
        }
        
        if source_lang and source_lang != 'auto':
            params['from'] = source_lang
        
        # Prepare body with all texts
        body = [{'text': text} for text in texts]
        
        try:
            response = requests.post(
                self.translate_url,
                params=params,
                headers=headers,
                json=body,
                timeout=self.config.timeout_seconds * 2  # Longer timeout for batch
            )
            response.raise_for_status()
            
            results = response.json()
            
            translations = []
            for i, result in enumerate(results):
                if 'translations' in result and result['translations']:
                    translation = result['translations'][0]
                    translated_text = translation['text']
                    confidence = translation.get('confidence', 
                                               self.calculate_confidence(texts[i], translated_text))
                    translations.append((translated_text, confidence))
                else:
                    # Fallback for failed translation
                    translations.append((texts[i], 0.0))
            
            return translations
            
        except Exception as e:
            # Fallback to individual translations
            self.logger.warning(f"Batch translation failed, falling back to individual: {e}")
            return [self.translate(text, source_lang, target_lang) for text in texts]

