"""
Language detection utilities.
"""

import re
from typing import Optional, NamedTuple
from collections import Counter

class LanguageDetection(NamedTuple):
    """Result of language detection."""
    language: str
    confidence: float

class LanguageDetector:
    """
    Simple rule-based language detector for automotive technical text.
    
    Focuses on detecting German, French, Italian, and Spanish text
    commonly found in automotive DAMOS files.
    """
    
    def __init__(self):
        """Initialize language detector with linguistic patterns."""
        
        # Language-specific word patterns
        self.language_patterns = {
            'de': {  # German
                'common_words': [
                    'der', 'die', 'das', 'und', 'oder', 'mit', 'für', 'von', 'zu', 'bei',
                    'nach', 'vor', 'über', 'unter', 'zwischen', 'während', 'ohne', 'gegen',
                    'durch', 'um', 'an', 'auf', 'in', 'aus', 'bis', 'seit', 'ab', 'hinter',
                    'ist', 'sind', 'war', 'waren', 'wird', 'werden', 'haben', 'hat', 'hatte',
                    'wert', 'zeit', 'temperatur', 'druck', 'geschwindigkeit', 'motor',
                    'steuerung', 'regelung', 'überwachung', 'messung', 'sensor', 'signal'
                ],
                'endings': [r'ung$', r'keit$', r'heit$', r'schaft$', r'ismus$', r'tion$'],
                'compounds': [r'\w+temperatur', r'\w+druck', r'\w+steuerung', r'\w+sensor'],
                'articles': ['der', 'die', 'das', 'den', 'dem', 'des'],
                'prepositions': ['für', 'mit', 'bei', 'von', 'zu', 'nach', 'vor', 'über']
            },
            
            'fr': {  # French
                'common_words': [
                    'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'avec',
                    'pour', 'par', 'dans', 'sur', 'sous', 'entre', 'pendant', 'sans', 'contre',
                    'est', 'sont', 'était', 'étaient', 'sera', 'seront', 'avoir', 'avait',
                    'valeur', 'temps', 'température', 'pression', 'vitesse', 'moteur',
                    'contrôle', 'régulation', 'surveillance', 'mesure', 'capteur', 'signal'
                ],
                'endings': [r'tion$', r'ment$', r'eur$', r'euse$', r'ique$', r'able$'],
                'articles': ['le', 'la', 'les', 'un', 'une', 'des', 'du'],
                'prepositions': ['de', 'du', 'pour', 'avec', 'dans', 'sur', 'sous', 'entre']
            },
            
            'it': {  # Italian
                'common_words': [
                    'il', 'la', 'lo', 'gli', 'le', 'un', 'una', 'uno', 'di', 'e', 'o', 'con',
                    'per', 'da', 'in', 'su', 'sotto', 'tra', 'durante', 'senza', 'contro',
                    'è', 'sono', 'era', 'erano', 'sarà', 'saranno', 'avere', 'aveva',
                    'valore', 'tempo', 'temperatura', 'pressione', 'velocità', 'motore',
                    'controllo', 'regolazione', 'sorveglianza', 'misura', 'sensore', 'segnale'
                ],
                'endings': [r'zione$', r'mento$', r'tore$', r'trice$', r'ico$', r'bile$'],
                'articles': ['il', 'la', 'lo', 'gli', 'le', 'un', 'una', 'uno'],
                'prepositions': ['di', 'da', 'per', 'con', 'in', 'su', 'sotto', 'tra']
            },
            
            'es': {  # Spanish
                'common_words': [
                    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'y', 'o', 'con',
                    'para', 'por', 'en', 'sobre', 'bajo', 'entre', 'durante', 'sin', 'contra',
                    'es', 'son', 'era', 'eran', 'será', 'serán', 'tener', 'tenía',
                    'valor', 'tiempo', 'temperatura', 'presión', 'velocidad', 'motor',
                    'control', 'regulación', 'vigilancia', 'medida', 'sensor', 'señal'
                ],
                'endings': [r'ción$', r'miento$', r'dor$', r'dora$', r'ico$', r'able$'],
                'articles': ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'],
                'prepositions': ['de', 'del', 'para', 'por', 'con', 'en', 'sobre', 'bajo']
            }
        }
    
    def detect(self, text: str) -> LanguageDetection:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            LanguageDetection with language code and confidence
        """
        if not text or not text.strip():
            return LanguageDetection('unknown', 0.0)
        
        text_lower = text.lower()
        word_tokens = re.findall(r'\b\w+\b', text_lower)
        
        if not word_tokens:
            return LanguageDetection('unknown', 0.0)
        
        # Calculate scores for each language
        language_scores = {}
        
        for lang_code, patterns in self.language_patterns.items():
            score = self._calculate_language_score(text_lower, word_tokens, patterns)
            language_scores[lang_code] = score
        
        # Find the language with the highest score
        if not language_scores:
            return LanguageDetection('unknown', 0.0)
        
        best_language = max(language_scores, key=language_scores.get)
        best_score = language_scores[best_language]
        
        # Convert score to confidence (0.0 to 1.0)
        confidence = min(best_score / 10.0, 1.0)  # Normalize to 0-1 range
        
        # Require minimum confidence threshold
        if confidence < 0.3:
            return LanguageDetection('unknown', confidence)
        
        return LanguageDetection(best_language, confidence)
    
    def _calculate_language_score(self, text: str, word_tokens: list, patterns: dict) -> float:
        """
        Calculate language score based on linguistic patterns.
        
        Args:
            text: Lowercase text
            word_tokens: List of word tokens
            patterns: Language-specific patterns
            
        Returns:
            Language score (higher = more likely)
        """
        score = 0.0
        
        # Score based on common words
        common_words = patterns.get('common_words', [])
        word_counter = Counter(word_tokens)
        
        for word in common_words:
            if word in word_counter:
                # Weight by frequency and word importance
                frequency = word_counter[word]
                importance = 2.0 if word in patterns.get('articles', []) else 1.0
                score += frequency * importance
        
        # Score based on word endings
        endings = patterns.get('endings', [])
        for ending_pattern in endings:
            matches = re.findall(ending_pattern, text)
            score += len(matches) * 0.5
        
        # Score based on compound words (especially for German)
        compounds = patterns.get('compounds', [])
        for compound_pattern in compounds:
            matches = re.findall(compound_pattern, text)
            score += len(matches) * 1.5
        
        # Score based on prepositions
        prepositions = patterns.get('prepositions', [])
        for prep in prepositions:
            if prep in word_counter:
                score += word_counter[prep] * 1.2
        
        return score
    
    def is_automotive_text(self, text: str) -> bool:
        """
        Determine if text appears to be automotive-related.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text appears automotive-related
        """
        automotive_terms = [
            # German
            'motor', 'abgas', 'katalysator', 'benzin', 'diesel', 'temperatur',
            'druck', 'sensor', 'steuerung', 'regelung', 'zündung', 'einspritzung',
            
            # French
            'moteur', 'échappement', 'catalyseur', 'essence', 'diesel', 'température',
            'pression', 'capteur', 'contrôle', 'régulation', 'allumage', 'injection',
            
            # Italian
            'motore', 'scarico', 'catalizzatore', 'benzina', 'diesel', 'temperatura',
            'pressione', 'sensore', 'controllo', 'regolazione', 'accensione', 'iniezione',
            
            # Spanish
            'motor', 'escape', 'catalizador', 'gasolina', 'diesel', 'temperatura',
            'presión', 'sensor', 'control', 'regulación', 'encendido', 'inyección'
        ]
        
        text_lower = text.lower()
        automotive_count = sum(1 for term in automotive_terms if term in text_lower)
        
        # Consider automotive if multiple terms present
        return automotive_count >= 2
    
    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes."""
        return list(self.language_patterns.keys())
    
    def detect_with_fallback(self, text: str, fallback_lang: str = 'de') -> LanguageDetection:
        """
        Detect language with fallback for automotive text.
        
        Args:
            text: Text to analyze
            fallback_lang: Fallback language for automotive text
            
        Returns:
            LanguageDetection result
        """
        detection = self.detect(text)
        
        # If detection failed but text appears automotive, use fallback
        if detection.language == 'unknown' and self.is_automotive_text(text):
            return LanguageDetection(fallback_lang, 0.6)
        
        return detection

