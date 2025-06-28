"""
Automotive Dictionary Module

Manages automotive terminology dictionaries for different languages and provides
context-aware translation capabilities for automotive terms.
"""

import json
import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class AutomotiveDictionary:
    """
    Manages automotive terminology dictionaries and provides translation services.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dictionaries = {}
        self.current_dir = Path(__file__).parent
        self.dict_dir = self.current_dir / "dictionaries"
        
        # Load available dictionaries
        self._load_dictionaries()
        
    def _load_dictionaries(self):
        """Load all available automotive dictionaries."""
        if not self.dict_dir.exists():
            self.logger.warning(f"Dictionary directory not found: {self.dict_dir}")
            return
            
        for dict_file in self.dict_dir.glob("*.json"):
            language = dict_file.stem.split('_')[0]  # e.g., 'german' from 'german_automotive.json'
            
            try:
                with open(dict_file, 'r', encoding='utf-8') as f:
                    self.dictionaries[language] = json.load(f)
                self.logger.info(f"Loaded {language} automotive dictionary")
            except Exception as e:
                self.logger.error(f"Failed to load dictionary {dict_file}: {e}")
    
    def get_available_languages(self) -> List[str]:
        """Get list of available source languages."""
        return list(self.dictionaries.keys())
    
    def translate_term(self, term: str, source_language: str) -> Optional[str]:
        """
        Translate a single automotive term.
        
        Args:
            term: The term to translate
            source_language: Source language code
            
        Returns:
            Translated term or None if not found
        """
        if source_language not in self.dictionaries:
            return None
            
        dictionary = self.dictionaries[source_language]
        
        # Direct lookup in automotive terms
        if term in dictionary.get('automotive_terms', {}):
            return dictionary['automotive_terms'][term]
        
        # Case-insensitive lookup
        term_lower = term.lower()
        for key, value in dictionary.get('automotive_terms', {}).items():
            if key.lower() == term_lower:
                return value
        
        return None
    
    def translate_phrase(self, phrase: str, source_language: str) -> Optional[str]:
        """
        Translate a common automotive phrase.
        
        Args:
            phrase: The phrase to translate
            source_language: Source language code
            
        Returns:
            Translated phrase or None if not found
        """
        if source_language not in self.dictionaries:
            return None
            
        dictionary = self.dictionaries[source_language]
        
        # Direct lookup in common phrases
        if phrase in dictionary.get('common_phrases', {}):
            return dictionary['common_phrases'][phrase]
        
        # Case-insensitive lookup
        phrase_lower = phrase.lower()
        for key, value in dictionary.get('common_phrases', {}).items():
            if key.lower() == phrase_lower:
                return value
        
        return None
    
    def translate_description(self, description: str, source_language: str) -> str:
        """
        Translate a complete parameter description using automotive context.
        
        Args:
            description: The description to translate
            source_language: Source language code
            
        Returns:
            Translated description
        """
        if source_language not in self.dictionaries:
            return description
        
        translated = description
        dictionary = self.dictionaries[source_language]
        
        # First, try to translate common phrases (longer matches first)
        phrases = dictionary.get('common_phrases', {})
        for phrase, translation in sorted(phrases.items(), key=len, reverse=True):
            if phrase in translated:
                translated = translated.replace(phrase, translation)
        
        # Then translate individual automotive terms
        terms = dictionary.get('automotive_terms', {})
        
        # Sort by length (longest first) to avoid partial replacements
        for term, translation in sorted(terms.items(), key=len, reverse=True):
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term) + r'\b'
            translated = re.sub(pattern, translation, translated, flags=re.IGNORECASE)
        
        # Handle units (preserve them as-is or translate if needed)
        units = dictionary.get('units', {})
        for unit, translation in units.items():
            if unit in translated and unit != translation:
                translated = translated.replace(unit, translation)
        
        return translated
    
    def get_translation_confidence(self, description: str, source_language: str) -> float:
        """
        Calculate confidence score for translation based on known terms and actual translation changes.
        
        Args:
            description: The description to analyze
            source_language: Source language code
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if source_language not in self.dictionaries:
            return 0.0
        
        # Get the actual translation
        translated = self.translate_description(description, source_language)
        
        # If nothing was translated, confidence is low
        if translated == description:
            return 0.1
        
        dictionary = self.dictionaries[source_language]
        words = description.split()
        total_words = len(words)
        
        if total_words == 0:
            return 1.0
        
        known_words = 0
        automotive_terms_found = 0
        
        # Check automotive terms
        for word in words:
            word_clean = word.strip('.,;:!?()[]{}').lower()
            
            # Check in automotive terms
            for term in dictionary.get('automotive_terms', {}):
                if term.lower() == word_clean or term.lower() in description.lower():
                    known_words += 1
                    automotive_terms_found += 1
                    break
        
        # Check common phrases
        phrase_matches = 0
        for phrase in dictionary.get('common_phrases', {}):
            if phrase.lower() in description.lower():
                phrase_matches += 1
                known_words += len(phrase.split()) * 0.5
        
        # Base confidence on word coverage
        word_confidence = min(known_words / total_words, 1.0) if total_words > 0 else 0.0
        
        # Boost confidence if we have automotive terms or phrases
        if automotive_terms_found > 0:
            word_confidence = min(word_confidence + 0.3, 1.0)
        
        if phrase_matches > 0:
            word_confidence = min(word_confidence + 0.2, 1.0)
        
        # If we actually translated something, boost confidence significantly
        translation_ratio = len([w for w in translated.split() if w not in description.split()]) / max(len(translated.split()), 1)
        if translation_ratio > 0.1:  # If more than 10% of words were translated
            word_confidence = min(word_confidence + 0.4, 1.0)
        
        return word_confidence
    
    def add_custom_term(self, source_language: str, term: str, translation: str):
        """
        Add a custom term to the dictionary (runtime only).
        
        Args:
            source_language: Source language code
            term: Original term
            translation: English translation
        """
        if source_language not in self.dictionaries:
            self.dictionaries[source_language] = {
                'automotive_terms': {},
                'common_phrases': {},
                'units': {}
            }
        
        self.dictionaries[source_language]['automotive_terms'][term] = translation
        self.logger.info(f"Added custom term: {term} -> {translation}")
    
    def get_dictionary_stats(self, source_language: str) -> Dict:
        """
        Get statistics about a dictionary.
        
        Args:
            source_language: Source language code
            
        Returns:
            Dictionary statistics
        """
        if source_language not in self.dictionaries:
            return {}
        
        dictionary = self.dictionaries[source_language]
        
        return {
            'language': source_language,
            'automotive_terms': len(dictionary.get('automotive_terms', {})),
            'common_phrases': len(dictionary.get('common_phrases', {})),
            'units': len(dictionary.get('units', {})),
            'total_entries': (
                len(dictionary.get('automotive_terms', {})) +
                len(dictionary.get('common_phrases', {})) +
                len(dictionary.get('units', {}))
            )
        }
    
    def find_similar_terms(self, term: str, source_language: str, max_results: int = 5) -> List[Tuple[str, str, float]]:
        """
        Find similar terms in the dictionary using fuzzy matching.
        
        Args:
            term: Term to find similar matches for
            source_language: Source language code
            max_results: Maximum number of results to return
            
        Returns:
            List of tuples: (original_term, translation, similarity_score)
        """
        if source_language not in self.dictionaries:
            return []
        
        try:
            from difflib import SequenceMatcher
        except ImportError:
            self.logger.warning("difflib not available for fuzzy matching")
            return []
        
        dictionary = self.dictionaries[source_language]
        automotive_terms = dictionary.get('automotive_terms', {})
        
        similarities = []
        
        for dict_term, translation in automotive_terms.items():
            similarity = SequenceMatcher(None, term.lower(), dict_term.lower()).ratio()
            if similarity > 0.6:  # Only include reasonably similar terms
                similarities.append((dict_term, translation, similarity))
        
        # Sort by similarity score (descending) and return top results
        similarities.sort(key=lambda x: x[2], reverse=True)
        return similarities[:max_results]
