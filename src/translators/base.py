"""
Base translator interface and common functionality.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
import logging

from ..config.settings import TranslationConfig

class BaseTranslator(ABC):
    """
    Abstract base class for all translation services.
    
    Defines the interface that all translation implementations must follow.
    """
    
    def __init__(self, config: TranslationConfig):
        """
        Initialize the translator.
        
        Args:
            config: Translation configuration
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, float]:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_text, confidence_score)
            
        Raises:
            TranslationError: If translation fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the translation service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """
        Perform a health check on the translation service.
        
        Returns:
            True if service is healthy, False otherwise
        """
        pass
    
    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported language codes.
        
        Returns:
            List of supported language codes
        """
        # Default implementation - override in subclasses for specific services
        return ['de', 'fr', 'it', 'es', 'en']
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code or None if detection fails
        """
        # Default implementation - override in subclasses if service supports detection
        return None
    
    def validate_language_pair(self, source_lang: str, target_lang: str) -> bool:
        """
        Validate if the language pair is supported.
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            True if language pair is supported
        """
        supported = self.get_supported_languages()
        return (source_lang in supported or source_lang == 'auto') and target_lang in supported
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text before translation.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Basic preprocessing - can be overridden in subclasses
        return text.strip()
    
    def postprocess_text(self, text: str, original: str) -> str:
        """
        Postprocess translated text.
        
        Args:
            text: Translated text
            original: Original text for reference
            
        Returns:
            Postprocessed text
        """
        # Basic postprocessing - can be overridden in subclasses
        return text.strip()
    
    def calculate_confidence(self, original: str, translated: str) -> float:
        """
        Calculate confidence score for the translation.
        
        Args:
            original: Original text
            translated: Translated text
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Basic confidence calculation - override in subclasses for service-specific logic
        if not translated or translated == original:
            return 0.0
        
        # Simple heuristic based on length difference
        len_ratio = min(len(translated), len(original)) / max(len(translated), len(original))
        return min(len_ratio + 0.3, 1.0)

class TranslationError(Exception):
    """Exception raised when translation fails."""
    
    def __init__(self, message: str, service: str = None, error_code: str = None):
        """
        Initialize translation error.
        
        Args:
            message: Error message
            service: Translation service that failed
            error_code: Service-specific error code
        """
        super().__init__(message)
        self.service = service
        self.error_code = error_code
    
    def __str__(self):
        """String representation of the error."""
        parts = [super().__str__()]
        if self.service:
            parts.append(f"Service: {self.service}")
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        return " | ".join(parts)

