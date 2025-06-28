"""
Configuration settings for the DAMOS translator.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TranslationService(Enum):
    """Available translation services."""
    GOOGLE = "google"
    DEEPL = "deepl"
    AZURE = "azure"
    LIBRE = "libre"
    LOCAL = "local"

class SourceLanguage(Enum):
    """Supported source languages."""
    GERMAN = "de"
    FRENCH = "fr"
    ITALIAN = "it"
    SPANISH = "es"
    AUTO = "auto"

@dataclass
class TranslationConfig:
    """Translation configuration settings."""
    
    # Primary translation service
    primary_service: TranslationService = TranslationService.GOOGLE
    
    # Fallback services (in order of preference)
    fallback_services: List[TranslationService] = None
    
    # Source and target languages
    source_language: SourceLanguage = SourceLanguage.AUTO
    target_language: str = "en"
    
    # API keys and credentials
    google_api_key: Optional[str] = None
    deepl_api_key: Optional[str] = None
    azure_api_key: Optional[str] = None
    azure_region: Optional[str] = None
    
    # Translation settings
    max_retries: int = 3
    timeout_seconds: int = 30
    batch_size: int = 100
    
    # Caching settings
    enable_cache: bool = True
    cache_ttl_hours: int = 24
    cache_max_size: int = 10000
    
    # Quality settings
    min_confidence_threshold: float = 0.7
    enable_back_translation_validation: bool = False
    
    # Performance settings
    max_concurrent_requests: int = 5
    rate_limit_per_minute: int = 100
    
    def __post_init__(self):
        """Initialize default fallback services if not provided."""
        if self.fallback_services is None:
            self.fallback_services = [
                TranslationService.DEEPL,
                TranslationService.AZURE,
                TranslationService.LIBRE,
                TranslationService.LOCAL
            ]
        
        # Load API keys from environment variables
        self.google_api_key = self.google_api_key or os.getenv('GOOGLE_TRANSLATE_API_KEY')
        self.deepl_api_key = self.deepl_api_key or os.getenv('DEEPL_API_KEY')
        self.azure_api_key = self.azure_api_key or os.getenv('AZURE_TRANSLATOR_KEY')
        self.azure_region = self.azure_region or os.getenv('AZURE_TRANSLATOR_REGION', 'global')

@dataclass
class DamosConfig:
    """DAMOS file processing configuration."""
    
    # File encoding settings
    default_encoding: str = "utf-8"
    fallback_encodings: List[str] = None
    
    # Processing settings
    preserve_formatting: bool = True
    preserve_comments: bool = True
    preserve_addresses: bool = True
    
    # Output settings
    generate_report: bool = True
    report_format: str = "txt"  # txt, json, html
    include_statistics: bool = True
    include_confidence_scores: bool = True
    
    def __post_init__(self):
        """Initialize default fallback encodings if not provided."""
        if self.fallback_encodings is None:
            self.fallback_encodings = [
                "utf-8",
                "latin-1", 
                "cp1252",
                "iso-8859-1"
            ]

# Global configuration instance
translation_config = TranslationConfig()
damos_config = DamosConfig()

def load_config_from_file(config_path: str) -> None:
    """Load configuration from a file."""
    # TODO: Implement configuration file loading
    pass

def get_available_services() -> List[TranslationService]:
    """Get list of available translation services based on API keys."""
    available = []
    
    if translation_config.google_api_key:
        available.append(TranslationService.GOOGLE)
    
    if translation_config.deepl_api_key:
        available.append(TranslationService.DEEPL)
    
    if translation_config.azure_api_key:
        available.append(TranslationService.AZURE)
    
    # LibreTranslate and Local are always available
    available.extend([TranslationService.LIBRE, TranslationService.LOCAL])
    
    return available

