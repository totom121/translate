"""
Pure Translation Engine

A comprehensive translation system that translates as many words as possible
without relying on predefined dictionaries. Uses multiple translation services
with intelligent fallback and caching.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config.settings import TranslationConfig, TranslationService, SourceLanguage
from ..translators import TranslatorFactory
from .cache import TranslationCache
from ..utils.text_processor import TextProcessor
from ..utils.language_detector import LanguageDetector

@dataclass
class TranslationResult:
    """Result of a translation operation."""
    original: str
    translated: str
    source_language: str
    target_language: str
    confidence: float
    service_used: str
    processing_time: float
    word_count: int
    translated_words: int
    
    @property
    def translation_rate(self) -> float:
        """Calculate the percentage of words translated."""
        if self.word_count == 0:
            return 0.0
        return (self.translated_words / self.word_count) * 100

class PureTranslator:
    """
    Pure translation engine that translates text without predefined dictionaries.
    
    Features:
    - Multiple translation service support with intelligent fallback
    - Automatic language detection
    - Translation caching for performance
    - Batch processing for efficiency
    - Quality validation and confidence scoring
    - Comprehensive error handling and retry logic
    """
    
    def __init__(self, config: TranslationConfig = None):
        """
        Initialize the pure translator.
        
        Args:
            config: Translation configuration settings
        """
        self.config = config or TranslationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.cache = TranslationCache(
            max_size=self.config.cache_max_size,
            ttl_hours=self.config.cache_ttl_hours
        ) if self.config.enable_cache else None
        
        self.text_processor = TextProcessor()
        self.language_detector = LanguageDetector()
        self.translator_factory = TranslatorFactory()
        
        # Initialize translation services
        self._initialize_services()
        
        # Statistics
        self.stats = {
            'total_translations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'service_usage': {},
            'failed_translations': 0,
            'total_processing_time': 0.0
        }
    
    def _initialize_services(self):
        """Initialize available translation services."""
        self.available_services = []
        
        # Try to initialize each service
        for service in [self.config.primary_service] + self.config.fallback_services:
            try:
                translator = self.translator_factory.create_translator(service, self.config)
                if translator.is_available():
                    self.available_services.append(service)
                    self.logger.info(f"Initialized translation service: {service.value}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize {service.value}: {e}")
        
        if not self.available_services:
            raise RuntimeError("No translation services available")
        
        self.logger.info(f"Available translation services: {[s.value for s in self.available_services]}")
    
    def translate(self, text: str, source_lang: str = None, target_lang: str = None) -> TranslationResult:
        """
        Translate a single text string.
        
        Args:
            text: Text to translate
            source_lang: Source language code (auto-detect if None)
            target_lang: Target language code (default: en)
            
        Returns:
            TranslationResult with translation details
        """
        start_time = time.time()
        
        # Validate input
        if not text or not text.strip():
            return self._create_empty_result(text, source_lang, target_lang, start_time)
        
        # Set default target language
        target_lang = target_lang or self.config.target_language
        
        # Detect source language if not provided
        if not source_lang or source_lang == 'auto':
            detected_lang = self.language_detector.detect(text)
            source_lang = detected_lang.language if detected_lang.confidence > 0.8 else 'auto'
        
        # Check cache first
        cache_key = self._generate_cache_key(text, source_lang, target_lang)
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.stats['cache_hits'] += 1
                self.logger.debug(f"Cache hit for: {text[:50]}...")
                return cached_result
            self.stats['cache_misses'] += 1
        
        # Preprocess text
        processed_text = self.text_processor.preprocess(text)
        
        # Attempt translation with available services
        translation_result = self._translate_with_fallback(
            processed_text, source_lang, target_lang, start_time
        )
        
        # Post-process translation
        if translation_result.translated:
            translation_result.translated = self.text_processor.postprocess(
                translation_result.translated, text
            )
        
        # Calculate translation statistics
        translation_result = self._calculate_translation_stats(translation_result, text)
        
        # Cache the result
        if self.cache and translation_result.confidence >= self.config.min_confidence_threshold:
            self.cache.set(cache_key, translation_result)
        
        # Update statistics
        self._update_stats(translation_result)
        
        return translation_result
    
    def translate_batch(self, texts: List[str], source_lang: str = None, 
                       target_lang: str = None, max_workers: int = None) -> List[TranslationResult]:
        """
        Translate multiple texts in parallel.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            max_workers: Maximum number of concurrent workers
            
        Returns:
            List of TranslationResult objects
        """
        if not texts:
            return []
        
        max_workers = max_workers or min(len(texts), self.config.max_concurrent_requests)
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all translation tasks
            future_to_text = {
                executor.submit(self.translate, text, source_lang, target_lang): text
                for text in texts
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_text):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    text = future_to_text[future]
                    self.logger.error(f"Translation failed for '{text[:50]}...': {e}")
                    results.append(self._create_error_result(text, source_lang, target_lang, str(e)))
        
        # Sort results to maintain original order
        text_to_result = {result.original: result for result in results}
        ordered_results = [text_to_result.get(text) for text in texts]
        
        return [result for result in ordered_results if result is not None]
    
    def _translate_with_fallback(self, text: str, source_lang: str, 
                                target_lang: str, start_time: float) -> TranslationResult:
        """
        Attempt translation with fallback to other services.
        
        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language
            start_time: Translation start time
            
        Returns:
            TranslationResult
        """
        last_error = None
        
        for service in self.available_services:
            try:
                translator = self.translator_factory.create_translator(service, self.config)
                
                # Attempt translation
                translated_text, confidence = translator.translate(text, source_lang, target_lang)
                
                if translated_text and confidence >= self.config.min_confidence_threshold:
                    processing_time = time.time() - start_time
                    
                    return TranslationResult(
                        original=text,
                        translated=translated_text,
                        source_language=source_lang,
                        target_language=target_lang,
                        confidence=confidence,
                        service_used=service.value,
                        processing_time=processing_time,
                        word_count=0,  # Will be calculated later
                        translated_words=0  # Will be calculated later
                    )
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Translation failed with {service.value}: {e}")
                continue
        
        # All services failed
        processing_time = time.time() - start_time
        self.logger.error(f"All translation services failed for: {text[:50]}...")
        
        return TranslationResult(
            original=text,
            translated=text,  # Return original if translation fails
            source_language=source_lang,
            target_language=target_lang,
            confidence=0.0,
            service_used="none",
            processing_time=processing_time,
            word_count=0,
            translated_words=0
        )
    
    def _calculate_translation_stats(self, result: TranslationResult, original_text: str) -> TranslationResult:
        """Calculate translation statistics."""
        original_words = self.text_processor.tokenize(original_text)
        translated_words = self.text_processor.tokenize(result.translated)
        
        # Count how many words were actually translated (changed)
        translated_count = 0
        for i, orig_word in enumerate(original_words):
            if i < len(translated_words):
                if orig_word.lower() != translated_words[i].lower():
                    translated_count += 1
        
        result.word_count = len(original_words)
        result.translated_words = translated_count
        
        return result
    
    def _generate_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate a cache key for the translation."""
        import hashlib
        key_string = f"{text}|{source_lang}|{target_lang}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _create_empty_result(self, text: str, source_lang: str, target_lang: str, start_time: float) -> TranslationResult:
        """Create a result for empty input."""
        return TranslationResult(
            original=text,
            translated=text,
            source_language=source_lang or 'unknown',
            target_language=target_lang or 'en',
            confidence=0.0,
            service_used="none",
            processing_time=time.time() - start_time,
            word_count=0,
            translated_words=0
        )
    
    def _create_error_result(self, text: str, source_lang: str, target_lang: str, error: str) -> TranslationResult:
        """Create a result for translation errors."""
        return TranslationResult(
            original=text,
            translated=text,
            source_language=source_lang or 'unknown',
            target_language=target_lang or 'en',
            confidence=0.0,
            service_used=f"error: {error}",
            processing_time=0.0,
            word_count=0,
            translated_words=0
        )
    
    def _update_stats(self, result: TranslationResult):
        """Update translation statistics."""
        self.stats['total_translations'] += 1
        self.stats['total_processing_time'] += result.processing_time
        
        if result.service_used not in self.stats['service_usage']:
            self.stats['service_usage'][result.service_used] = 0
        self.stats['service_usage'][result.service_used] += 1
        
        if result.confidence == 0.0:
            self.stats['failed_translations'] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get translation statistics."""
        stats = self.stats.copy()
        
        if stats['total_translations'] > 0:
            stats['average_processing_time'] = stats['total_processing_time'] / stats['total_translations']
            stats['success_rate'] = ((stats['total_translations'] - stats['failed_translations']) / 
                                   stats['total_translations']) * 100
            
            if self.cache:
                total_requests = stats['cache_hits'] + stats['cache_misses']
                if total_requests > 0:
                    stats['cache_hit_rate'] = (stats['cache_hits'] / total_requests) * 100
        
        return stats
    
    def clear_cache(self):
        """Clear the translation cache."""
        if self.cache:
            self.cache.clear()
            self.logger.info("Translation cache cleared")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on all translation services."""
        health_status = {}
        
        for service in self.available_services:
            try:
                translator = self.translator_factory.create_translator(service, self.config)
                is_healthy = translator.health_check()
                health_status[service.value] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'available': translator.is_available()
                }
            except Exception as e:
                health_status[service.value] = {
                    'status': 'error',
                    'error': str(e),
                    'available': False
                }
        
        return health_status

