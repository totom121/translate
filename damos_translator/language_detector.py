"""
Language Detection Module

Automatically detects the source language of DAMOS file descriptions
to enable automatic translation without manual language specification.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from collections import Counter

class LanguageDetector:
    """
    Detects the source language of automotive text descriptions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Language-specific patterns and indicators
        self.language_patterns = {
            'german': {
                'common_words': [
                    'der', 'die', 'das', 'und', 'oder', 'mit', 'für', 'bei', 'von', 'zu', 'im', 'am',
                    'ist', 'sind', 'wird', 'werden', 'hat', 'haben', 'kann', 'soll', 'muss',
                    'nach', 'vor', 'über', 'unter', 'zwischen', 'während', 'ohne', 'gegen'
                ],
                'automotive_indicators': [
                    'Motor', 'Temperatur', 'Druck', 'Sensor', 'Ventil', 'Steuerung', 'Regelung',
                    'Katalysator', 'Lambdasonde', 'Drosselklappe', 'Einspritzung', 'Zündung',
                    'Abgas', 'Kraftstoff', 'Leerlauf', 'Drehzahl', 'Zylinder', 'Kolben'
                ],
                'character_patterns': ['ä', 'ö', 'ü', 'ß'],
                'word_endings': ['ung', 'tion', 'heit', 'keit', 'schaft', 'tum'],
                'compound_indicators': ['temperatur', 'druck', 'sensor', 'ventil', 'steuerung']
            },
            'french': {
                'common_words': [
                    'le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'avec', 'pour', 'par', 'dans',
                    'est', 'sont', 'sera', 'seront', 'a', 'ont', 'peut', 'doit', 'va',
                    'après', 'avant', 'sur', 'sous', 'entre', 'pendant', 'sans', 'contre'
                ],
                'automotive_indicators': [
                    'moteur', 'température', 'pression', 'capteur', 'valve', 'contrôle', 'régulation',
                    'catalyseur', 'sonde', 'papillon', 'injection', 'allumage',
                    'échappement', 'carburant', 'ralenti', 'régime', 'cylindre', 'piston'
                ],
                'character_patterns': ['é', 'è', 'ê', 'ë', 'à', 'â', 'ç', 'î', 'ï', 'ô', 'ù', 'û', 'ü', 'ÿ'],
                'word_endings': ['tion', 'sion', 'ment', 'ance', 'ence', 'eur', 'euse'],
                'compound_indicators': ['température', 'pression', 'capteur', 'valve', 'contrôle']
            },
            'italian': {
                'common_words': [
                    'il', 'la', 'lo', 'gli', 'le', 'di', 'del', 'della', 'e', 'o', 'con', 'per', 'da', 'in',
                    'è', 'sono', 'sarà', 'saranno', 'ha', 'hanno', 'può', 'deve', 'va',
                    'dopo', 'prima', 'sopra', 'sotto', 'tra', 'durante', 'senza', 'contro'
                ],
                'automotive_indicators': [
                    'motore', 'temperatura', 'pressione', 'sensore', 'valvola', 'controllo', 'regolazione',
                    'catalizzatore', 'sonda', 'farfalla', 'iniezione', 'accensione',
                    'scarico', 'carburante', 'minimo', 'regime', 'cilindro', 'pistone'
                ],
                'character_patterns': ['à', 'è', 'é', 'ì', 'í', 'î', 'ò', 'ó', 'ù', 'ú'],
                'word_endings': ['zione', 'sione', 'mento', 'anza', 'enza', 'ore', 'tore'],
                'compound_indicators': ['temperatura', 'pressione', 'sensore', 'valvola', 'controllo']
            },
            'spanish': {
                'common_words': [
                    'el', 'la', 'los', 'las', 'de', 'del', 'y', 'o', 'con', 'para', 'por', 'en',
                    'es', 'son', 'será', 'serán', 'ha', 'han', 'puede', 'debe', 'va',
                    'después', 'antes', 'sobre', 'bajo', 'entre', 'durante', 'sin', 'contra'
                ],
                'automotive_indicators': [
                    'motor', 'temperatura', 'presión', 'sensor', 'válvula', 'control', 'regulación',
                    'catalizador', 'sonda', 'mariposa', 'inyección', 'encendido',
                    'escape', 'combustible', 'ralentí', 'régimen', 'cilindro', 'pistón'
                ],
                'character_patterns': ['á', 'é', 'í', 'ó', 'ú', 'ñ', 'ü'],
                'word_endings': ['ción', 'sión', 'miento', 'anza', 'encia', 'dor', 'dora'],
                'compound_indicators': ['temperatura', 'presión', 'sensor', 'válvula', 'control']
            }
        }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of a text string.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (language_code, confidence_score)
        """
        if not text or not text.strip():
            return 'unknown', 0.0
        
        text_lower = text.lower()
        scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0.0
            total_indicators = 0
            
            # Check common words
            common_word_matches = 0
            for word in patterns['common_words']:
                if word in text_lower:
                    common_word_matches += text_lower.count(word)
            
            # Check automotive indicators
            automotive_matches = 0
            for indicator in patterns['automotive_indicators']:
                if indicator.lower() in text_lower:
                    automotive_matches += text_lower.count(indicator.lower())
            
            # Check character patterns
            character_matches = 0
            for char in patterns['character_patterns']:
                character_matches += text.count(char)
            
            # Check word endings
            ending_matches = 0
            words = text_lower.split()
            for word in words:
                for ending in patterns['word_endings']:
                    if word.endswith(ending):
                        ending_matches += 1
            
            # Check compound word indicators
            compound_matches = 0
            for compound in patterns['compound_indicators']:
                if compound in text_lower:
                    compound_matches += text_lower.count(compound)
            
            # Calculate weighted score
            word_count = len(text_lower.split())
            if word_count > 0:
                score = (
                    (common_word_matches * 2.0) +
                    (automotive_matches * 3.0) +
                    (character_matches * 1.5) +
                    (ending_matches * 1.0) +
                    (compound_matches * 2.5)
                ) / word_count
            
            scores[language] = score
        
        # Find the language with the highest score
        if not scores:
            return 'unknown', 0.0
        
        best_language = max(scores, key=scores.get)
        best_score = scores[best_language]
        
        # Normalize confidence score
        confidence = min(best_score, 1.0)
        
        # Require minimum confidence threshold
        if confidence < 0.1:
            return 'unknown', confidence
        
        return best_language, confidence
    
    def detect_language_from_descriptions(self, descriptions: List[str]) -> Tuple[str, float]:
        """
        Detect language from multiple descriptions for better accuracy.
        
        Args:
            descriptions: List of description strings
            
        Returns:
            Tuple of (language_code, confidence_score)
        """
        if not descriptions:
            return 'unknown', 0.0
        
        # Combine all descriptions for analysis
        combined_text = ' '.join(descriptions)
        
        # Also analyze individual descriptions
        individual_results = []
        for desc in descriptions:
            if desc.strip():
                lang, conf = self.detect_language(desc)
                if lang != 'unknown':
                    individual_results.append((lang, conf))
        
        # Get result from combined text
        combined_lang, combined_conf = self.detect_language(combined_text)
        
        # If we have individual results, use voting
        if individual_results:
            language_votes = Counter(lang for lang, conf in individual_results)
            most_common_lang = language_votes.most_common(1)[0][0]
            
            # Calculate average confidence for the most common language
            confidences = [conf for lang, conf in individual_results if lang == most_common_lang]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Combine with overall result
            if most_common_lang == combined_lang:
                # Both methods agree, increase confidence
                final_confidence = min((avg_confidence + combined_conf) / 2 * 1.2, 1.0)
                return most_common_lang, final_confidence
            else:
                # Methods disagree, use the one with higher confidence
                if avg_confidence > combined_conf:
                    return most_common_lang, avg_confidence
                else:
                    return combined_lang, combined_conf
        
        return combined_lang, combined_conf
    
    def is_automotive_text(self, text: str) -> bool:
        """
        Determine if text appears to be automotive-related.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text appears automotive-related
        """
        text_lower = text.lower()
        
        # Common automotive keywords across languages
        automotive_keywords = [
            # English
            'engine', 'motor', 'temperature', 'pressure', 'sensor', 'valve', 'control',
            'catalyst', 'lambda', 'throttle', 'injection', 'ignition', 'exhaust', 'fuel',
            'idle', 'speed', 'cylinder', 'piston', 'rpm', 'torque', 'boost',
            
            # German
            'motor', 'temperatur', 'druck', 'sensor', 'ventil', 'steuerung', 'regelung',
            'katalysator', 'lambdasonde', 'drosselklappe', 'einspritzung', 'zündung',
            'abgas', 'kraftstoff', 'leerlauf', 'drehzahl', 'zylinder', 'kolben',
            
            # French
            'moteur', 'température', 'pression', 'capteur', 'valve', 'contrôle',
            'catalyseur', 'sonde', 'papillon', 'injection', 'allumage', 'échappement',
            
            # Italian
            'motore', 'temperatura', 'pressione', 'sensore', 'valvola', 'controllo',
            'catalizzatore', 'farfalla', 'iniezione', 'accensione', 'scarico',
            
            # Spanish
            'temperatura', 'presión', 'válvula', 'catalizador', 'mariposa',
            'inyección', 'encendido', 'escape', 'combustible'
        ]
        
        matches = sum(1 for keyword in automotive_keywords if keyword in text_lower)
        word_count = len(text_lower.split())
        
        if word_count == 0:
            return False
        
        # Consider it automotive if at least 20% of words are automotive-related
        automotive_ratio = matches / word_count
        return automotive_ratio >= 0.2
    
    def get_language_statistics(self, descriptions: List[str]) -> Dict:
        """
        Get detailed statistics about language detection results.
        
        Args:
            descriptions: List of descriptions to analyze
            
        Returns:
            Dictionary with language statistics
        """
        stats = {
            'total_descriptions': len(descriptions),
            'non_empty_descriptions': 0,
            'automotive_descriptions': 0,
            'language_distribution': Counter(),
            'confidence_scores': [],
            'unknown_descriptions': 0
        }
        
        for desc in descriptions:
            if desc.strip():
                stats['non_empty_descriptions'] += 1
                
                if self.is_automotive_text(desc):
                    stats['automotive_descriptions'] += 1
                
                lang, conf = self.detect_language(desc)
                stats['language_distribution'][lang] += 1
                stats['confidence_scores'].append(conf)
                
                if lang == 'unknown':
                    stats['unknown_descriptions'] += 1
        
        # Calculate average confidence
        if stats['confidence_scores']:
            stats['average_confidence'] = sum(stats['confidence_scores']) / len(stats['confidence_scores'])
        else:
            stats['average_confidence'] = 0.0
        
        return stats

