"""
Factory for creating translation service instances.
"""

from typing import Dict, Type
from ..config.settings import TranslationService, TranslationConfig
from .base import BaseTranslator
from .google_translator import GoogleTranslator
from .deepl_translator import DeepLTranslator
from .azure_translator import AzureTranslator
from .libre_translator import LibreTranslator
from .local_translator import LocalTranslator

class TranslatorFactory:
    """Factory for creating translator instances."""
    
    _translators: Dict[TranslationService, Type[BaseTranslator]] = {
        TranslationService.GOOGLE: GoogleTranslator,
        TranslationService.DEEPL: DeepLTranslator,
        TranslationService.AZURE: AzureTranslator,
        TranslationService.LIBRE: LibreTranslator,
        TranslationService.LOCAL: LocalTranslator,
    }
    
    def create_translator(self, service: TranslationService, config: TranslationConfig) -> BaseTranslator:
        """
        Create a translator instance for the specified service.
        
        Args:
            service: Translation service to create
            config: Translation configuration
            
        Returns:
            Translator instance
            
        Raises:
            ValueError: If service is not supported
        """
        if service not in self._translators:
            raise ValueError(f"Unsupported translation service: {service}")
        
        translator_class = self._translators[service]
        return translator_class(config)
    
    @classmethod
    def get_supported_services(cls) -> list[TranslationService]:
        """Get list of supported translation services."""
        return list(cls._translators.keys())
    
    @classmethod
    def register_translator(cls, service: TranslationService, translator_class: Type[BaseTranslator]):
        """
        Register a custom translator implementation.
        
        Args:
            service: Translation service enum
            translator_class: Translator class to register
        """
        cls._translators[service] = translator_class

