"""
Text processing utilities for translation.
"""

import re
from typing import List, Tuple

class TextProcessor:
    """
    Text processing utilities for preparing and cleaning text for translation.
    """
    
    def __init__(self):
        """Initialize text processor."""
        # Patterns for text cleaning
        self.cleanup_patterns = [
            (r'\s+', ' '),  # Multiple spaces to single space
            (r'^\s+|\s+$', ''),  # Leading/trailing whitespace
        ]
        
        # Patterns to preserve during translation
        self.preserve_patterns = [
            (r'\$[0-9A-Fa-f]+', 'HEXADDR'),  # Hex addresses like $818760
            (r'\b[A-Z][A-Z0-9_]+\b', 'PARAM'),  # Parameter names like ABGMSIGH
            (r'\b\d+\.\d+\b', 'DECIMAL'),  # Decimal numbers
            (r'\b\d+\b', 'INTEGER'),  # Integer numbers
        ]
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess text before translation.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Preprocessed text ready for translation
        """
        if not text:
            return text
        
        # Basic cleanup
        processed = text
        for pattern, replacement in self.cleanup_patterns:
            processed = re.sub(pattern, replacement, processed)
        
        return processed.strip()
    
    def postprocess(self, translated: str, original: str) -> str:
        """
        Postprocess translated text.
        
        Args:
            translated: Translated text
            original: Original text for reference
            
        Returns:
            Postprocessed text
        """
        if not translated:
            return translated
        
        # Restore original capitalization patterns where appropriate
        processed = self._restore_capitalization(translated, original)
        
        # Clean up spacing
        for pattern, replacement in self.cleanup_patterns:
            processed = re.sub(pattern, replacement, processed)
        
        return processed.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of word tokens
        """
        if not text:
            return []
        
        # Simple word tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def extract_technical_terms(self, text: str) -> List[str]:
        """
        Extract technical terms and identifiers from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of technical terms found
        """
        technical_terms = []
        
        # Extract hex addresses
        hex_addresses = re.findall(r'\$[0-9A-Fa-f]+', text)
        technical_terms.extend(hex_addresses)
        
        # Extract parameter names (uppercase with underscores/numbers)
        param_names = re.findall(r'\b[A-Z][A-Z0-9_]+\b', text)
        technical_terms.extend(param_names)
        
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        technical_terms.extend(numbers)
        
        return technical_terms
    
    def preserve_technical_terms(self, text: str) -> Tuple[str, dict]:
        """
        Replace technical terms with placeholders for translation.
        
        Args:
            text: Text with technical terms
            
        Returns:
            Tuple of (text_with_placeholders, replacement_map)
        """
        replacement_map = {}
        processed_text = text
        
        for pattern, placeholder_prefix in self.preserve_patterns:
            matches = re.finditer(pattern, processed_text)
            for i, match in enumerate(matches):
                original_term = match.group()
                placeholder = f"__{placeholder_prefix}_{i}__"
                replacement_map[placeholder] = original_term
                processed_text = processed_text.replace(original_term, placeholder, 1)
        
        return processed_text, replacement_map
    
    def restore_technical_terms(self, text: str, replacement_map: dict) -> str:
        """
        Restore technical terms from placeholders.
        
        Args:
            text: Text with placeholders
            replacement_map: Map of placeholders to original terms
            
        Returns:
            Text with restored technical terms
        """
        restored_text = text
        
        for placeholder, original_term in replacement_map.items():
            restored_text = restored_text.replace(placeholder, original_term)
        
        return restored_text
    
    def _restore_capitalization(self, translated: str, original: str) -> str:
        """
        Restore capitalization patterns from original text.
        
        Args:
            translated: Translated text
            original: Original text with capitalization
            
        Returns:
            Translated text with restored capitalization
        """
        original_words = original.split()
        translated_words = translated.split()
        
        restored_words = []
        
        for i, translated_word in enumerate(translated_words):
            if i < len(original_words):
                original_word = original_words[i]
                
                # If original was all caps, make translation all caps
                if original_word.isupper() and len(original_word) > 1:
                    restored_words.append(translated_word.upper())
                # If original was capitalized, capitalize translation
                elif original_word and original_word[0].isupper():
                    restored_words.append(translated_word.capitalize())
                else:
                    restored_words.append(translated_word)
            else:
                restored_words.append(translated_word)
        
        return ' '.join(restored_words)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(self.tokenize(text1))
        words2 = set(self.tokenize(text2))
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def is_technical_text(self, text: str) -> bool:
        """
        Determine if text appears to be technical/automotive content.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text appears technical
        """
        technical_indicators = [
            r'\$[0-9A-Fa-f]+',  # Hex addresses
            r'\b[A-Z]{3,}[0-9_]*\b',  # Parameter names
            r'\b\d+\.\d+\b',  # Decimal numbers
            r'\b(?:temperatur|druck|motor|sensor|signal|wert)\b',  # Technical terms
        ]
        
        technical_count = 0
        for pattern in technical_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                technical_count += 1
        
        # Consider technical if multiple indicators present
        return technical_count >= 2

