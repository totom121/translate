"""
Local translation implementation using offline models.
"""

import re
from typing import Tuple, Optional, List, Dict

from .base import BaseTranslator, TranslationError
from ..config.settings import TranslationConfig

class LocalTranslator(BaseTranslator):
    """
    Local translation implementation that works offline.
    
    Uses rule-based translation patterns and linguistic analysis
    to provide basic translation capabilities without external dependencies.
    Particularly effective for technical automotive terminology.
    """
    
    def __init__(self, config: TranslationConfig):
        """Initialize Local Translator."""
        super().__init__(config)
        self._initialize_translation_rules()
    
    def _initialize_translation_rules(self):
        """Initialize translation rules and patterns."""
        
        # Core vocabulary mappings
        self.vocabulary = {
            # Articles and pronouns
            'der': 'the', 'die': 'the', 'das': 'the', 'den': 'the', 'dem': 'the', 'des': 'of the',
            'ein': 'a', 'eine': 'a', 'einen': 'a', 'einem': 'a', 'einer': 'a', 'eines': 'a',
            'und': 'and', 'oder': 'or', 'aber': 'but', 'wenn': 'if', 'dann': 'then',
            
            # Prepositions
            'für': 'for', 'fr': 'for', 'mit': 'with', 'bei': 'at', 'von': 'from', 'zu': 'to',
            'nach': 'after', 'vor': 'before', 'über': 'above', 'unter': 'under', 'zwischen': 'between',
            'während': 'during', 'ohne': 'without', 'gegen': 'against', 'durch': 'through',
            'um': 'around', 'an': 'at', 'auf': 'on', 'in': 'in', 'aus': 'from',
            'bis': 'until', 'seit': 'since', 'ab': 'from', 'hinter': 'behind',
            'im': 'in the', 'am': 'at the', 'zum': 'to the', 'zur': 'to the',
            'beim': 'at the', 'vom': 'from the', 'ins': 'into the', 'ans': 'to the',
            
            # Common verbs
            'ist': 'is', 'sind': 'are', 'war': 'was', 'waren': 'were', 'wird': 'will be',
            'werden': 'become', 'haben': 'have', 'hat': 'has', 'hatte': 'had', 'hatten': 'had',
            'sein': 'be', 'kann': 'can', 'könnte': 'could', 'soll': 'should', 'muss': 'must',
            
            # Technical terms
            'wert': 'value', 'zeit': 'time', 'temperatur': 'temperature', 'druck': 'pressure',
            'geschwindigkeit': 'speed', 'faktor': 'factor', 'schwelle': 'threshold',
            'grenze': 'limit', 'bereich': 'range', 'anzahl': 'number', 'menge': 'amount',
            'zähler': 'counter', 'zhler': 'counter', 'messung': 'measurement', 'sensor': 'sensor',
            'signal': 'signal', 'spannung': 'voltage', 'strom': 'current', 'leistung': 'power',
            
            # Automotive terms
            'motor': 'engine', 'abgas': 'exhaust gas', 'katalysator': 'catalytic converter',
            'benzin': 'gasoline', 'diesel': 'diesel', 'öl': 'oil', 'kraftstoff': 'fuel',
            'zündung': 'ignition', 'einspritzung': 'injection', 'ventil': 'valve',
            'kolben': 'piston', 'zylinder': 'cylinder', 'getriebe': 'transmission',
            'bremse': 'brake', 'lenkung': 'steering', 'rad': 'wheel', 'reifen': 'tire',
            
            # Adjectives
            'groß': 'large', 'klein': 'small', 'hoch': 'high', 'niedrig': 'low',
            'lang': 'long', 'kurz': 'short', 'neu': 'new', 'alt': 'old',
            'gut': 'good', 'schlecht': 'bad', 'schnell': 'fast', 'langsam': 'slow',
            'stark': 'strong', 'schwach': 'weak', 'warm': 'warm', 'kalt': 'cold',
            'oberer': 'upper', 'unterer': 'lower', 'maximal': 'maximum', 'minimal': 'minimum',
            'optimal': 'optimal', 'normal': 'normal', 'aktiv': 'active', 'passiv': 'passive',
            
            # Numbers and quantities
            'max': 'maximum', 'min': 'minimum', 'alle': 'all', 'jede': 'each',
            'viele': 'many', 'wenige': 'few', 'mehr': 'more', 'weniger': 'less',
            
            # Actions
            'starten': 'start', 'stoppen': 'stop', 'messen': 'measure', 'prüfen': 'check',
            'kontrollieren': 'control', 'regeln': 'regulate', 'überwachen': 'monitor',
            'erkennen': 'recognize', 'erkennung': 'recognition', 'diagnose': 'diagnosis',
            'fehler': 'error', 'störung': 'fault', 'warnung': 'warning', 'alarm': 'alarm',
            
            # Status terms
            'ein': 'on', 'aus': 'off', 'offen': 'open', 'geschlossen': 'closed',
            'aktiv': 'active', 'inaktiv': 'inactive', 'bereit': 'ready', 'besetzt': 'busy',
            'verfügbar': 'available', 'blockiert': 'blocked', 'gesperrt': 'locked',
            
            # Compound word components
            'steuerung': 'control', 'regelung': 'regulation', 'überwachung': 'monitoring',
            'einstellung': 'setting', 'konfiguration': 'configuration', 'anpassung': 'adaptation',
            'korrektur': 'correction', 'verstärkung': 'amplification', 'dämpfung': 'damping',
            'filter': 'filter', 'regler': 'controller', 'wandler': 'converter',
            'verstärker': 'amplifier', 'begrenzer': 'limiter', 'schalter': 'switch',
        }
        
        # Word ending transformation rules
        self.ending_rules = [
            (r'ung$', 'tion'),      # Steuerung -> control + tion
            (r'keit$', 'ity'),      # Geschwindigkeit -> speed + ity  
            (r'heit$', 'ness'),     # Sicherheit -> safety + ness
            (r'schaft$', 'ship'),   # Eigenschaft -> property + ship
            (r'ismus$', 'ism'),     # Mechanismus -> mechanism + ism
            (r'tion$', 'tion'),     # Already correct
            (r'ität$', 'ity'),      # Qualität -> quality + ity
            (r'ieren$', 'ate'),     # Aktivieren -> activate
            (r'lich$', 'ly'),       # Schnell -> quickly
            (r'bar$', 'able'),      # Messbar -> measurable
        ]
        
        # Compound word patterns
        self.compound_patterns = [
            # Temperature compounds
            (r'(\w+)temperatur', r'\1 temperature'),
            (r'temperatur(\w+)', r'temperature \1'),
            
            # Pressure compounds  
            (r'(\w+)druck', r'\1 pressure'),
            (r'druck(\w+)', r'pressure \1'),
            
            # Speed compounds
            (r'(\w+)geschwindigkeit', r'\1 speed'),
            (r'geschwindigkeit(\w+)', r'speed \1'),
            
            # Control compounds
            (r'(\w+)steuerung', r'\1 control'),
            (r'steuerung(\w+)', r'control \1'),
            
            # Sensor compounds
            (r'(\w+)sensor', r'\1 sensor'),
            (r'sensor(\w+)', r'sensor \1'),
            
            # Value compounds
            (r'(\w+)wert', r'\1 value'),
            (r'wert(\w+)', r'value \1'),
            
            # Counter compounds
            (r'(\w+)zähler', r'\1 counter'),
            (r'(\w+)zhler', r'\1 counter'),  # Common misspelling
            (r'zähler(\w+)', r'counter \1'),
            
            # Time compounds
            (r'(\w+)zeit', r'\1 time'),
            (r'zeit(\w+)', r'time \1'),
        ]
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, float]:
        """
        Translate text using local rules and patterns.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (translated_text, confidence_score)
        """
        if target_lang != 'en':
            raise TranslationError(f"Local translator only supports translation to English, not {target_lang}", "local")
        
        if source_lang not in ['de', 'auto']:
            # For non-German languages, return original with low confidence
            return text, 0.1
        
        original_text = text
        translated_text = text.lower()
        
        # Track translation progress
        total_words = len(text.split())
        translated_words = 0
        
        # Step 1: Direct vocabulary translation
        words = translated_text.split()
        translated_word_list = []
        
        for word in words:
            # Clean word (remove punctuation for lookup)
            clean_word = re.sub(r'[^\w]', '', word)
            punctuation = word[len(clean_word):]
            
            # Try direct vocabulary lookup
            if clean_word in self.vocabulary:
                translated_word_list.append(self.vocabulary[clean_word] + punctuation)
                translated_words += 1
            else:
                # Try compound word patterns
                compound_translated = self._translate_compound_word(clean_word)
                if compound_translated != clean_word:
                    translated_word_list.append(compound_translated + punctuation)
                    translated_words += 1
                else:
                    # Try word ending transformations
                    ending_translated = self._apply_ending_rules(clean_word)
                    if ending_translated != clean_word:
                        translated_word_list.append(ending_translated + punctuation)
                        translated_words += 1
                    else:
                        # Keep original word
                        translated_word_list.append(word)
        
        translated_text = ' '.join(translated_word_list)
        
        # Step 2: Apply compound patterns to the full text
        for pattern, replacement in self.compound_patterns:
            translated_text = re.sub(pattern, replacement, translated_text, flags=re.IGNORECASE)
        
        # Step 3: Clean up and normalize
        translated_text = self._normalize_translation(translated_text, original_text)
        
        # Calculate confidence based on translation coverage
        confidence = self._calculate_local_confidence(original_text, translated_text, translated_words, total_words)
        
        return translated_text, confidence
    
    def _translate_compound_word(self, word: str) -> str:
        """Translate German compound words by breaking them down."""
        # Try to find known components in the compound word
        word_lower = word.lower()
        
        # Look for compound endings
        compound_endings = [
            'temperatur', 'druck', 'geschwindigkeit', 'steuerung', 'regelung',
            'überwachung', 'sensor', 'wert', 'zeit', 'zähler', 'zhler',
            'messung', 'prüfung', 'diagnose', 'kontrolle', 'signal'
        ]
        
        for ending in compound_endings:
            if word_lower.endswith(ending) and len(word_lower) > len(ending):
                prefix = word_lower[:-len(ending)]
                
                # Translate prefix if known
                prefix_translation = self.vocabulary.get(prefix, prefix)
                ending_translation = self.vocabulary.get(ending, ending)
                
                return f"{prefix_translation} {ending_translation}"
        
        # Look for compound beginnings
        compound_beginnings = [
            'motor', 'abgas', 'kraft', 'zünd', 'einspritz', 'brems', 'lenk'
        ]
        
        for beginning in compound_beginnings:
            if word_lower.startswith(beginning) and len(word_lower) > len(beginning):
                suffix = word_lower[len(beginning):]
                
                beginning_translation = self.vocabulary.get(beginning, beginning)
                suffix_translation = self.vocabulary.get(suffix, suffix)
                
                return f"{beginning_translation} {suffix_translation}"
        
        return word
    
    def _apply_ending_rules(self, word: str) -> str:
        """Apply German word ending transformation rules."""
        for pattern, replacement in self.ending_rules:
            if re.search(pattern, word):
                # Try to find the root word
                root = re.sub(pattern, '', word)
                if root in self.vocabulary:
                    return self.vocabulary[root] + replacement
                else:
                    return re.sub(pattern, replacement, word)
        
        return word
    
    def _normalize_translation(self, translated: str, original: str) -> str:
        """Normalize the translated text."""
        # Preserve original capitalization patterns
        original_words = original.split()
        translated_words = translated.split()
        
        normalized_words = []
        for i, word in enumerate(translated_words):
            if i < len(original_words):
                orig_word = original_words[i]
                # If original was capitalized, capitalize translation
                if orig_word and orig_word[0].isupper():
                    word = word.capitalize()
            normalized_words.append(word)
        
        # Clean up multiple spaces
        normalized = ' '.join(normalized_words)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _calculate_local_confidence(self, original: str, translated: str, translated_words: int, total_words: int) -> float:
        """Calculate confidence score for local translation."""
        if total_words == 0:
            return 0.0
        
        # Base confidence from translation coverage
        coverage_ratio = translated_words / total_words
        base_confidence = coverage_ratio * 0.7  # Max 0.7 from coverage
        
        # Boost for technical terms (automotive context)
        technical_terms = ['temperatur', 'druck', 'motor', 'sensor', 'signal', 'wert']
        technical_boost = sum(1 for term in technical_terms if term in original.lower()) * 0.05
        
        # Penalty for unchanged text
        if translated == original:
            base_confidence = 0.1
        
        # Penalty for very low translation rate
        if coverage_ratio < 0.3:
            base_confidence *= 0.5
        
        final_confidence = min(base_confidence + technical_boost, 0.9)  # Max 0.9 for local translator
        return max(final_confidence, 0.1)  # Min 0.1
    
    def is_available(self) -> bool:
        """Local translator is always available."""
        return True
    
    def health_check(self) -> bool:
        """Perform health check."""
        try:
            # Test basic translation
            result, confidence = self.translate("motor temperatur", "de", "en")
            return "engine" in result.lower() and "temperature" in result.lower()
        except Exception:
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages."""
        return ['de']  # Only German to English for now
    
    def detect_language(self, text: str) -> Optional[str]:
        """Simple German language detection."""
        german_indicators = [
            'der', 'die', 'das', 'und', 'oder', 'mit', 'für', 'von', 'zu',
            'temperatur', 'druck', 'motor', 'steuerung', 'regelung'
        ]
        
        text_lower = text.lower()
        german_count = sum(1 for indicator in german_indicators if indicator in text_lower)
        
        # If we find multiple German indicators, likely German
        if german_count >= 2:
            return 'de'
        
        return None

