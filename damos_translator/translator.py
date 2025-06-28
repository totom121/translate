"""
Automotive Translator Module

Main translation engine that combines automotive dictionaries with general translation
capabilities to provide context-aware translation of automotive terminology.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from .automotive_dictionary import AutomotiveDictionary
from .language_detector import LanguageDetector
from .simple_translator import SimpleTranslator

class AutomotiveTranslator:
    """
    Main translation engine for automotive terminology with context awareness.
    """
    
    def __init__(self, use_external_api: bool = True):
        self.logger = logging.getLogger(__name__)
        self.automotive_dict = AutomotiveDictionary()
        self.language_detector = LanguageDetector()
        self.simple_translator = SimpleTranslator()
        self.use_external_api = use_external_api
        
        # Translation cache to avoid repeated translations
        self.translation_cache = {}
        
        # Statistics tracking
        self.stats = {
            'total_translations': 0,
            'dictionary_hits': 0,
            'api_calls': 0,
            'cache_hits': 0,
            'failed_translations': 0,
            'base_translations': 0
        }
    
    def translate_description(self, description: str, source_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate a parameter description with automotive context awareness.
        
        Args:
            description: The description to translate
            source_language: Source language (auto-detected if None)
            
        Returns:
            Dictionary with translation results and metadata
        """
        if not description or not description.strip():
            return {
                'original': description,
                'translated': description,
                'source_language': 'unknown',
                'confidence': 0.0,
                'method': 'no_translation_needed',
                'automotive_terms_found': 0
            }
        
        # Check cache first
        cache_key = f"{description}_{source_language}"
        if cache_key in self.translation_cache:
            self.stats['cache_hits'] += 1
            return self.translation_cache[cache_key]
        
        self.stats['total_translations'] += 1
        
        # Auto-detect language if not provided
        if source_language is None:
            detected_lang, confidence = self.language_detector.detect_language(description)
            source_language = detected_lang
        else:
            confidence = 1.0
        
        # If language is unknown or English, return as-is
        if source_language in ['unknown', 'english']:
            result = {
                'original': description,
                'translated': description,
                'source_language': source_language,
                'confidence': confidence,
                'method': 'no_translation_needed',
                'automotive_terms_found': 0
            }
            self.translation_cache[cache_key] = result
            return result
        
        # Use simple rule-based translator for full translation with automotive enhancement
        translation_result = self.simple_translator.translate_text(description, source_language)
        
        result = {
            'original': description,
            'translated': translation_result['translated'],
            'source_language': source_language,
            'confidence': translation_result['confidence'],
            'method': translation_result['method'],
            'automotive_terms_found': translation_result.get('rules_applied', 0)
        }
        
        self.stats['base_translations'] += 1
        
        if result['translated'] != description:
            self.stats['dictionary_hits'] += 1
        else:
            self.stats['failed_translations'] += 1
        
        # Cache the result
        self.translation_cache[cache_key] = result
        return result
    
    def translate_multiple_descriptions(self, descriptions: List[str], 
                                      source_language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Translate multiple descriptions efficiently.
        
        Args:
            descriptions: List of descriptions to translate
            source_language: Source language (auto-detected if None)
            
        Returns:
            List of translation results
        """
        if not descriptions:
            return []
        
        # Auto-detect language from all descriptions if not provided
        if source_language is None:
            detected_lang, confidence = self.language_detector.detect_language_from_descriptions(descriptions)
            source_language = detected_lang
            self.logger.info(f"Auto-detected language: {source_language} (confidence: {confidence:.2f})")
        
        results = []
        for desc in descriptions:
            result = self.translate_description(desc, source_language)
            results.append(result)
        
        return results
    
    def _count_automotive_terms(self, description: str, source_language: str) -> int:
        """Count how many automotive terms are found in the description."""
        if source_language not in self.automotive_dict.dictionaries:
            return 0
        
        dictionary = self.automotive_dict.dictionaries[source_language]
        automotive_terms = dictionary.get('automotive_terms', {})
        
        count = 0
        description_lower = description.lower()
        
        for term in automotive_terms:
            if term.lower() in description_lower:
                count += 1
        
        return count
    
    def _translate_with_external_api(self, text: str, source_language: str) -> Optional[str]:
        """
        Translate using external API as fallback (placeholder implementation).
        
        In a real implementation, this would call services like:
        - Google Translate API
        - Microsoft Translator
        - DeepL API
        - etc.
        """
        # Placeholder implementation - in real use, integrate with translation APIs
        self.logger.debug(f"External API translation requested for: {text[:50]}...")
        
        # For now, return None to indicate API translation is not available
        # In production, implement actual API calls here
        return None
    
    def _combine_translations(self, dict_translation: str, api_translation: str, 
                            original: str, source_language: str) -> str:
        """
        Intelligently combine dictionary and API translations.
        
        Prioritizes automotive terms from dictionary while using API for general language.
        """
        if not api_translation:
            return dict_translation
        
        # If dictionary translation changed significantly, prefer it (has automotive terms)
        if dict_translation != original and len(dict_translation) > len(original) * 0.8:
            return dict_translation
        
        # Otherwise, use API translation but replace known automotive terms
        combined = api_translation
        
        if source_language in self.automotive_dict.dictionaries:
            dictionary = self.automotive_dict.dictionaries[source_language]
            automotive_terms = dictionary.get('automotive_terms', {})
            
            # Replace automotive terms in API translation with dictionary versions
            for term, translation in automotive_terms.items():
                if term.lower() in original.lower():
                    # Use word boundaries to avoid partial replacements
                    pattern = r'\b' + re.escape(term) + r'\b'
                    combined = re.sub(pattern, translation, combined, flags=re.IGNORECASE)
        
        return combined
    
    def get_translation_statistics(self) -> Dict[str, Any]:
        """Get translation statistics and performance metrics."""
        total = self.stats['total_translations']
        
        stats = dict(self.stats)
        
        if total > 0:
            stats['dictionary_hit_rate'] = self.stats['dictionary_hits'] / total
            stats['cache_hit_rate'] = self.stats['cache_hits'] / total
            stats['failure_rate'] = self.stats['failed_translations'] / total
        else:
            stats['dictionary_hit_rate'] = 0.0
            stats['cache_hit_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        stats['available_languages'] = self.automotive_dict.get_available_languages()
        stats['cache_size'] = len(self.translation_cache)
        
        return stats
    
    def clear_cache(self):
        """Clear the translation cache."""
        self.translation_cache.clear()
        self.logger.info("Translation cache cleared")
    
    def add_custom_translation(self, source_language: str, original: str, translation: str):
        """
        Add a custom translation to the automotive dictionary.
        
        Args:
            source_language: Source language code
            original: Original term
            translation: English translation
        """
        self.automotive_dict.add_custom_term(source_language, original, translation)
        
        # Clear cache entries that might be affected
        keys_to_remove = [key for key in self.translation_cache.keys() 
                         if original.lower() in key.lower()]
        for key in keys_to_remove:
            del self.translation_cache[key]
    
    def validate_translation_quality(self, original: str, translated: str, 
                                   source_language: str) -> Dict[str, Any]:
        """
        Validate the quality of a translation.
        
        Args:
            original: Original text
            translated: Translated text
            source_language: Source language
            
        Returns:
            Quality assessment dictionary
        """
        assessment = {
            'length_ratio': len(translated) / len(original) if original else 0,
            'automotive_terms_preserved': 0,
            'has_automotive_context': self.language_detector.is_automotive_text(original),
            'translation_confidence': 0.0,
            'quality_score': 0.0
        }
        
        # Check if automotive terms were properly translated
        if source_language in self.automotive_dict.dictionaries:
            dictionary = self.automotive_dict.dictionaries[source_language]
            automotive_terms = dictionary.get('automotive_terms', {})
            
            preserved_terms = 0
            total_terms = 0
            
            for term, translation in automotive_terms.items():
                if term.lower() in original.lower():
                    total_terms += 1
                    if translation.lower() in translated.lower():
                        preserved_terms += 1
            
            if total_terms > 0:
                assessment['automotive_terms_preserved'] = preserved_terms / total_terms
        
        # Calculate overall quality score
        factors = [
            assessment['automotive_terms_preserved'] * 0.4,  # 40% weight for automotive terms
            (1.0 if 0.5 <= assessment['length_ratio'] <= 2.0 else 0.5) * 0.2,  # 20% for reasonable length
            (1.0 if assessment['has_automotive_context'] else 0.8) * 0.2,  # 20% for automotive context
            (1.0 if translated != original else 0.0) * 0.2  # 20% for actual translation
        ]
        
        assessment['quality_score'] = sum(factors)
        assessment['translation_confidence'] = self.automotive_dict.get_translation_confidence(
            original, source_language
        )
        
        return assessment
