"""
Base Translation Module

Provides core translation capabilities using Google Translate API
with fallback mechanisms and automotive dictionary integration.
"""

import logging
import time
import re
from typing import Dict, List, Optional, Any
from translate import Translator
from .automotive_dictionary import AutomotiveDictionary

class BaseTranslator:
    """
    Base translation engine that provides core German-to-English translation
    with automotive dictionary enhancement.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.translator = Translator(to_lang="en")
        self.automotive_dict = AutomotiveDictionary()
        
        # Translation cache to avoid repeated API calls
        self.translation_cache = {}
        
        # Rate limiting
        self.last_api_call = 0
        self.min_api_interval = 0.1  # 100ms between API calls
        
        # Statistics
        self.stats = {
            'total_translations': 0,
            'api_translations': 0,
            'cache_hits': 0,
            'dictionary_enhancements': 0,
            'failed_translations': 0
        }
    
    def translate_text(self, text: str, source_language: str = 'german') -> Dict[str, Any]:
        """
        Translate text from source language to English with automotive enhancements.
        
        Args:
            text: Text to translate
            source_language: Source language code
            
        Returns:
            Dictionary with translation results and metadata
        """
        if not text or not text.strip():
            return {
                'original': text,
                'translated': text,
                'source_language': source_language,
                'method': 'no_translation_needed',
                'confidence': 1.0,
                'automotive_terms_enhanced': 0
            }
        
        # Check cache first
        cache_key = f"{text}_{source_language}"
        if cache_key in self.translation_cache:
            self.stats['cache_hits'] += 1
            return self.translation_cache[cache_key]
        
        self.stats['total_translations'] += 1
        
        # Convert language code for Google Translate
        google_lang_code = self._convert_language_code(source_language)
        
        # If already English, just enhance with automotive dictionary
        if source_language.lower() in ['english', 'en']:
            enhanced_text = self._enhance_with_automotive_dict(text, 'english')
            result = {
                'original': text,
                'translated': enhanced_text,
                'source_language': source_language,
                'method': 'automotive_enhancement_only',
                'confidence': 1.0,
                'automotive_terms_enhanced': self._count_automotive_enhancements(text, enhanced_text)
            }
            self.translation_cache[cache_key] = result
            return result
        
        try:
            # Rate limiting
            self._rate_limit()
            
            # Perform base translation using translate library
            self.logger.debug(f"Translating with translate library: {text[:50]}...")
            
            # Update translator for source language
            self.translator.from_lang = google_lang_code
            base_translation = self.translator.translate(text)
            
            self.stats['api_translations'] += 1
            
            # Enhance the base translation with automotive dictionary
            enhanced_translation = self._enhance_with_automotive_dict(base_translation, source_language, text)
            
            # Calculate confidence based on translation quality
            confidence = self._calculate_translation_confidence(text, base_translation, enhanced_translation)
            
            result = {
                'original': text,
                'translated': enhanced_translation,
                'base_translation': base_translation,
                'source_language': source_language,
                'method': 'translate_library_with_automotive_enhancement',
                'confidence': confidence,
                'automotive_terms_enhanced': self._count_automotive_enhancements(base_translation, enhanced_translation)
            }
            
            if enhanced_translation != base_translation:
                self.stats['dictionary_enhancements'] += 1
            
            # Cache the result
            self.translation_cache[cache_key] = result
            return result
            
        except Exception as e:
            self.logger.warning(f"Translation library failed for '{text[:50]}...': {e}")
            self.stats['failed_translations'] += 1
            
            # Fallback to dictionary-only translation
            return self._fallback_dictionary_translation(text, source_language)
    
    def translate_multiple_texts(self, texts: List[str], source_language: str = 'german') -> List[Dict[str, Any]]:
        """
        Translate multiple texts efficiently with batch processing.
        
        Args:
            texts: List of texts to translate
            source_language: Source language code
            
        Returns:
            List of translation results
        """
        if not texts:
            return []
        
        results = []
        for text in texts:
            result = self.translate_text(text, source_language)
            results.append(result)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.05)
        
        return results
    
    def _convert_language_code(self, language_code: str) -> str:
        """Convert internal language codes to Google Translate codes."""
        language_mapping = {
            'german': 'de',
            'french': 'fr',
            'italian': 'it',
            'spanish': 'es',
            'english': 'en'
        }
        return language_mapping.get(language_code.lower(), language_code)
    
    def _rate_limit(self):
        """Implement rate limiting for API calls."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.min_api_interval:
            sleep_time = self.min_api_interval - time_since_last_call
            time.sleep(sleep_time)
        
        self.last_api_call = time.time()
    
    def _enhance_with_automotive_dict(self, translated_text: str, source_language: str, original_text: str = None) -> str:
        """
        Enhance translated text with automotive dictionary terms.
        
        Args:
            translated_text: Base translated text
            source_language: Original source language
            original_text: Original text (for context)
            
        Returns:
            Enhanced translation with automotive terms
        """
        if source_language not in self.automotive_dict.dictionaries:
            return translated_text
        
        enhanced = translated_text
        dictionary = self.automotive_dict.dictionaries[source_language]
        
        # If we have the original text, look for automotive terms there
        # and replace their translations in the enhanced text
        if original_text:
            automotive_terms = dictionary.get('automotive_terms', {})
            
            for original_term, english_term in automotive_terms.items():
                # Check if the original term exists in the original text
                if original_term.lower() in original_text.lower():
                    # Try to find and replace potential translations of this term
                    # This is a heuristic approach - look for similar words in the translation
                    
                    # Simple approach: if the English term is significantly different,
                    # and we can find a similar word in the translation, replace it
                    words_in_translation = enhanced.split()
                    
                    for i, word in enumerate(words_in_translation):
                        # Remove punctuation for comparison
                        clean_word = re.sub(r'[^\w]', '', word.lower())
                        clean_english_term = re.sub(r'[^\w]', '', english_term.lower())
                        
                        # If the word might be a poor translation of our automotive term
                        # (heuristic: similar length or starts with same letter)
                        if (len(clean_word) > 3 and 
                            (abs(len(clean_word) - len(clean_english_term)) <= 2 or
                             clean_word[0] == clean_english_term[0])):
                            
                            # Check if this might be a translation of our automotive term
                            # by seeing if the original term was likely translated to this word
                            if self._might_be_translation_of(clean_word, original_term, english_term):
                                # Replace with the proper automotive term
                                words_in_translation[i] = word.replace(clean_word, english_term)
                                break
                    
                    enhanced = ' '.join(words_in_translation)
        
        # Also do direct replacement of any automotive terms that might appear
        automotive_terms = dictionary.get('automotive_terms', {})
        for term, translation in automotive_terms.items():
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(term) + r'\b'
            enhanced = re.sub(pattern, translation, enhanced, flags=re.IGNORECASE)
        
        # Handle common phrases
        phrases = dictionary.get('common_phrases', {})
        for phrase, translation in sorted(phrases.items(), key=len, reverse=True):
            if phrase.lower() in enhanced.lower():
                enhanced = enhanced.replace(phrase, translation)
        
        return enhanced
    
    def _might_be_translation_of(self, translated_word: str, original_term: str, correct_translation: str) -> bool:
        """
        Heuristic to determine if a translated word might be a poor translation
        of an automotive term that we have a better translation for.
        """
        # Simple heuristics:
        # 1. If the translated word is very different from our correct translation
        # 2. And the original term is an automotive term
        # 3. Then it might be worth replacing
        
        if translated_word.lower() == correct_translation.lower():
            return False  # Already correct
        
        # If the lengths are very different, it might be a poor translation
        if abs(len(translated_word) - len(correct_translation)) > 3:
            return True
        
        # If they start with different letters, might be poor translation
        if (len(translated_word) > 0 and len(correct_translation) > 0 and
            translated_word[0].lower() != correct_translation[0].lower()):
            return True
        
        return False
    
    def _count_automotive_enhancements(self, original: str, enhanced: str) -> int:
        """Count how many automotive enhancements were made."""
        if original == enhanced:
            return 0
        
        # Simple count of word differences
        original_words = set(original.lower().split())
        enhanced_words = set(enhanced.lower().split())
        
        return len(enhanced_words - original_words)
    
    def _calculate_translation_confidence(self, original: str, base_translation: str, enhanced_translation: str) -> float:
        """Calculate confidence score for the translation."""
        # Base confidence starts moderate for translate library
        confidence = 0.7
        
        # Boost confidence if we made automotive enhancements
        if enhanced_translation != base_translation:
            confidence = min(confidence + 0.15, 1.0)
        
        # Reduce confidence if translation seems too similar to original (might not have translated)
        similarity_ratio = len(set(original.lower().split()) & set(base_translation.lower().split())) / max(len(original.split()), 1)
        if similarity_ratio > 0.7:
            confidence *= 0.7
        
        return confidence
    
    def _fallback_dictionary_translation(self, text: str, source_language: str) -> Dict[str, Any]:
        """
        Fallback translation using only automotive dictionary.
        
        Args:
            text: Text to translate
            source_language: Source language code
            
        Returns:
            Dictionary translation result
        """
        self.logger.info(f"Using dictionary fallback for: {text[:50]}...")
        
        # Use automotive dictionary only
        dict_translation = self.automotive_dict.translate_description(text, source_language)
        confidence = self.automotive_dict.get_translation_confidence(text, source_language)
        
        result = {
            'original': text,
            'translated': dict_translation,
            'source_language': source_language,
            'method': 'dictionary_fallback',
            'confidence': confidence,
            'automotive_terms_enhanced': self._count_automotive_enhancements(text, dict_translation)
        }
        
        # Cache the result
        cache_key = f"{text}_{source_language}"
        self.translation_cache[cache_key] = result
        
        return result
    
    def get_translation_statistics(self) -> Dict[str, Any]:
        """Get translation statistics and performance metrics."""
        total = self.stats['total_translations']
        
        stats = dict(self.stats)
        
        if total > 0:
            stats['api_usage_rate'] = self.stats['api_translations'] / total
            stats['cache_hit_rate'] = self.stats['cache_hits'] / total
            stats['enhancement_rate'] = self.stats['dictionary_enhancements'] / total
            stats['failure_rate'] = self.stats['failed_translations'] / total
        else:
            stats['api_usage_rate'] = 0.0
            stats['cache_hit_rate'] = 0.0
            stats['enhancement_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        stats['cache_size'] = len(self.translation_cache)
        
        return stats
    
    def clear_cache(self):
        """Clear the translation cache."""
        self.translation_cache.clear()
        self.logger.info("Translation cache cleared")
