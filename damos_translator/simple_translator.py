"""
Simple Rule-Based German-English Translator

Provides basic German-to-English translation using rule-based patterns
specifically designed for automotive technical documentation.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from .automotive_dictionary import AutomotiveDictionary
from .comprehensive_german_dict import ComprehensiveGermanDict

class SimpleTranslator:
    """
    Simple rule-based translator for German automotive technical terms.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.automotive_dict = AutomotiveDictionary()
        self.comprehensive_dict = ComprehensiveGermanDict()
        
        # German grammar patterns and rules
        self.grammar_rules = {
            # Common German word endings and their English equivalents
            'word_endings': {
                'ung': 'tion',      # Regelung -> regulation
                'keit': 'ity',      # Geschwindigkeit -> velocity  
                'heit': 'ity',      # Sicherheit -> safety
                'schaft': 'ship',   # Eigenschaft -> property
                'lich': 'ly',       # möglich -> possible
                'bar': 'able',      # verfügbar -> available
                'los': 'less',      # kraftlos -> powerless
                'voll': 'ful',      # kraftvoll -> powerful
            },
            
            # Common German prefixes
            'prefixes': {
                'un': 'un',         # unmöglich -> impossible
                'vor': 'pre',       # Vorheizung -> preheating
                'nach': 'post',     # Nachbehandlung -> post-treatment
                'über': 'over',     # Überdruck -> overpressure
                'unter': 'under',   # Unterdruck -> underpressure
                'ab': 'off',        # Abschaltung -> shutdown
                'an': 'on',         # Anschaltung -> startup
                'aus': 'out',       # Ausgang -> output
                'ein': 'in',        # Eingang -> input
                'mit': 'with',      # Mittelwert -> mean value
                'zwischen': 'inter', # Zwischenwert -> intermediate value
            },
            
            # Common German compound word patterns
            'compound_patterns': [
                # Pattern: [word]temperatur -> [word] temperature
                (r'(\w+)temperatur', r'\1 temperature'),
                # Pattern: [word]druck -> [word] pressure  
                (r'(\w+)druck', r'\1 pressure'),
                # Pattern: [word]geschwindigkeit -> [word] speed
                (r'(\w+)geschwindigkeit', r'\1 speed'),
                # Pattern: [word]wert -> [word] value
                (r'(\w+)wert', r'\1 value'),
                # Pattern: [word]zeit -> [word] time
                (r'(\w+)zeit', r'\1 time'),
                # Pattern: [word]faktor -> [word] factor
                (r'(\w+)faktor', r'\1 factor'),
                # Pattern: [word]schwelle -> [word] threshold
                (r'(\w+)schwelle', r'\1 threshold'),
                # Pattern: [word]grenze -> [word] limit
                (r'(\w+)grenze', r'\1 limit'),
                # Pattern: [word]bereich -> [word] range
                (r'(\w+)bereich', r'\1 range'),
                # Pattern: [word]stufe -> [word] stage/level
                (r'(\w+)stufe', r'\1 stage'),
                # Pattern: [word]menge -> [word] amount
                (r'(\w+)menge', r'\1 amount'),
                # Pattern: [word]anzahl -> [word] number
                (r'(\w+)anzahl', r'\1 number'),
                # Pattern: [word]zähler -> [word] counter
                (r'(\w+)zähler', r'\1 counter'),
                # Pattern: [word]filter -> [word] filter
                (r'(\w+)filter', r'\1 filter'),
                # Pattern: [word]regler -> [word] controller
                (r'(\w+)regler', r'\1 controller'),
                # Pattern: [word]sensor -> [word] sensor
                (r'(\w+)sensor', r'\1 sensor'),
                # Pattern: [word]ventil -> [word] valve
                (r'(\w+)ventil', r'\1 valve'),
                # Pattern: [word]pumpe -> [word] pump
                (r'(\w+)pumpe', r'\1 pump'),
                # Pattern: [word]motor -> [word] motor
                (r'(\w+)motor', r'\1 motor'),
            ],
            
            # Common German sentence patterns
            'sentence_patterns': [
                # "für [something]" -> "for [something]"
                (r'\bfür\b', 'for'),
                # "mit [something]" -> "with [something]"
                (r'\bmit\b', 'with'),
                # "bei [something]" -> "at [something]"
                (r'\bbei\b', 'at'),
                # "von [something]" -> "from [something]"
                (r'\bvon\b', 'from'),
                # "zu [something]" -> "to [something]"
                (r'\bzu\b', 'to'),
                # "nach [something]" -> "after [something]"
                (r'\bnach\b', 'after'),
                # "vor [something]" -> "before [something]"
                (r'\bvor\b', 'before'),
                # "über [something]" -> "above [something]"
                (r'\büber\b', 'above'),
                # "unter [something]" -> "below [something]"
                (r'\bunter\b', 'below'),
                # "zwischen [something]" -> "between [something]"
                (r'\bzwischen\b', 'between'),
                # "während [something]" -> "during [something]"
                (r'\bwährend\b', 'during'),
                # "ohne [something]" -> "without [something]"
                (r'\bohne\b', 'without'),
                # "gegen [something]" -> "against [something]"
                (r'\bgegen\b', 'against'),
                # "durch [something]" -> "through [something]"
                (r'\bdurch\b', 'through'),
                # "um [something]" -> "around [something]"
                (r'\bum\b', 'around'),
                # "an [something]" -> "on [something]"
                (r'\ban\b', 'on'),
                # "auf [something]" -> "on [something]"
                (r'\bauf\b', 'on'),
                # "in [something]" -> "in [something]"
                (r'\bin\b', 'in'),
                # "aus [something]" -> "from [something]"
                (r'\baus\b', 'from'),
                # "bis [something]" -> "until [something]"
                (r'\bbis\b', 'until'),
                # "seit [something]" -> "since [something]"
                (r'\bseit\b', 'since'),
                # "ab [something]" -> "from [something]"
                (r'\bab\b', 'from'),
            ]
        }
        
        # Translation cache
        self.translation_cache = {}
        
        # Statistics
        self.stats = {
            'total_translations': 0,
            'dictionary_translations': 0,
            'rule_based_translations': 0,
            'cache_hits': 0,
            'partial_translations': 0
        }
    
    def translate_text(self, text: str, source_language: str = 'german') -> Dict[str, Any]:
        """
        Translate German text to English using rule-based approach.
        
        Args:
            text: Text to translate
            source_language: Source language (should be 'german')
            
        Returns:
            Translation result dictionary
        """
        if not text or not text.strip():
            return {
                'original': text,
                'translated': text,
                'source_language': source_language,
                'method': 'no_translation_needed',
                'confidence': 1.0,
                'rules_applied': 0
            }
        
        # Check cache first
        cache_key = f"{text}_{source_language}"
        if cache_key in self.translation_cache:
            self.stats['cache_hits'] += 1
            return self.translation_cache[cache_key]
        
        self.stats['total_translations'] += 1
        
        # If not German, just enhance with automotive dictionary
        if source_language.lower() not in ['german', 'de']:
            enhanced = self.automotive_dict.translate_description(text, source_language)
            result = {
                'original': text,
                'translated': enhanced,
                'source_language': source_language,
                'method': 'automotive_dictionary_only',
                'confidence': 0.6,
                'rules_applied': 0
            }
            self.translation_cache[cache_key] = result
            return result
        
        # Multi-stage comprehensive translation approach
        translated = text
        rules_applied = 0
        translation_stages = []
        
        # Stage 1: Apply automotive dictionary first (highest priority for technical terms)
        automotive_translation = self.automotive_dict.translate_description(text, source_language)
        if automotive_translation != text:
            translated = automotive_translation
            self.stats['dictionary_translations'] += 1
            translation_stages.append('automotive_dict')
        
        # Stage 2: Word-by-word comprehensive translation
        words = translated.split()
        comprehensive_words = []
        
        for word in words:
            # Remove punctuation for translation, but preserve it
            clean_word = re.sub(r'[^\w]', '', word)
            punctuation = word[len(clean_word):]
            
            # Try comprehensive dictionary first
            translated_word = self.comprehensive_dict.translate_word(clean_word)
            if translated_word != clean_word:
                comprehensive_words.append(translated_word + punctuation)
                rules_applied += 1
            else:
                # If not found, try word ending transformation
                transformed_word = self._transform_word_endings(clean_word)
                if transformed_word != clean_word:
                    comprehensive_words.append(transformed_word + punctuation)
                    rules_applied += 1
                else:
                    comprehensive_words.append(word)
        
        translated = ' '.join(comprehensive_words)
        if comprehensive_words != words:
            translation_stages.append('comprehensive_dict')
        
        # Stage 3: Apply compound word patterns (for complex technical terms)
        for pattern, replacement in self.grammar_rules['compound_patterns']:
            if re.search(pattern, translated, re.IGNORECASE):
                new_translation = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
                if new_translation != translated:
                    translated = new_translation
                    rules_applied += 1
                    if 'compound_patterns' not in translation_stages:
                        translation_stages.append('compound_patterns')
        
        # Stage 4: Apply sentence patterns (prepositions, conjunctions, etc.)
        for pattern, replacement in self.grammar_rules['sentence_patterns']:
            if re.search(pattern, translated, re.IGNORECASE):
                new_translation = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
                if new_translation != translated:
                    translated = new_translation
                    rules_applied += 1
                    if 'sentence_patterns' not in translation_stages:
                        translation_stages.append('sentence_patterns')
        
        # Stage 5: Post-processing cleanup and final automotive enhancement
        # Clean up multiple spaces and normalize
        translated = re.sub(r'\s+', ' ', translated).strip()
        
        # Final automotive dictionary pass (in case new automotive terms were created)
        final_automotive = self.automotive_dict.translate_description(translated, 'english')
        if final_automotive != translated:
            translated = final_automotive
            rules_applied += 1
            if 'final_automotive' not in translation_stages:
                translation_stages.append('final_automotive')
        
        # Stage 6: Advanced compound word decomposition for untranslated complex terms
        translated = self._decompose_complex_compounds(translated)
        if translated != ' '.join(comprehensive_words):
            rules_applied += 1
            if 'compound_decomposition' not in translation_stages:
                translation_stages.append('compound_decomposition')
        
        # Calculate confidence
        confidence = self._calculate_confidence(text, translated, rules_applied)
        
        # Determine method
        method = 'rule_based_translation'
        if automotive_translation != text:
            method = 'automotive_dictionary_with_rules'
        if rules_applied > 0:
            self.stats['rule_based_translations'] += 1
        if translated != text and translated != automotive_translation:
            self.stats['partial_translations'] += 1
        
        result = {
            'original': text,
            'translated': translated,
            'source_language': source_language,
            'method': method,
            'confidence': confidence,
            'rules_applied': rules_applied
        }
        
        # Cache the result
        self.translation_cache[cache_key] = result
        return result
    
    def translate_multiple_texts(self, texts: List[str], source_language: str = 'german') -> List[Dict[str, Any]]:
        """
        Translate multiple texts efficiently.
        
        Args:
            texts: List of texts to translate
            source_language: Source language
            
        Returns:
            List of translation results
        """
        if not texts:
            return []
        
        results = []
        for text in texts:
            result = self.translate_text(text, source_language)
            results.append(result)
        
        return results
    
    def _transform_word_endings(self, word: str) -> str:
        """
        Transform German word endings to English equivalents.
        
        Args:
            word: German word
            
        Returns:
            Word with transformed ending
        """
        if len(word) < 4:  # Skip very short words
            return word
        
        # Remove punctuation for processing
        clean_word = re.sub(r'[^\w]', '', word)
        punctuation = word[len(clean_word):]
        
        # Apply ending transformations
        for german_ending, english_ending in self.grammar_rules['word_endings'].items():
            if clean_word.lower().endswith(german_ending):
                # Replace the ending
                root = clean_word[:-len(german_ending)]
                transformed = root + english_ending
                return transformed + punctuation
        
        return word
    
    def _decompose_complex_compounds(self, text: str) -> str:
        """
        Advanced compound word decomposition for complex German technical terms.
        
        Args:
            text: Text with potential compound words
            
        Returns:
            Text with decomposed compound words
        """
        words = text.split()
        decomposed_words = []
        
        for word in words:
            # Skip if already translated (contains English words)
            if self._is_likely_english(word):
                decomposed_words.append(word)
                continue
            
            # Try to decompose long German compound words
            if len(word) > 8 and self._is_likely_german_compound(word):
                decomposed = self._decompose_german_compound(word)
                if decomposed != word:
                    decomposed_words.append(decomposed)
                else:
                    decomposed_words.append(word)
            else:
                decomposed_words.append(word)
        
        return ' '.join(decomposed_words)
    
    def _is_likely_english(self, word: str) -> bool:
        """Check if a word is likely already in English."""
        clean_word = re.sub(r'[^\w]', '', word.lower())
        
        # Common English indicators
        english_patterns = [
            'temperature', 'pressure', 'speed', 'value', 'control', 'system',
            'engine', 'motor', 'sensor', 'signal', 'threshold', 'limit',
            'range', 'factor', 'counter', 'time', 'with', 'for', 'the',
            'and', 'or', 'not', 'in', 'on', 'at', 'to', 'from'
        ]
        
        return any(pattern in clean_word for pattern in english_patterns)
    
    def _is_likely_german_compound(self, word: str) -> bool:
        """Check if a word is likely a German compound word."""
        clean_word = re.sub(r'[^\w]', '', word.lower())
        
        # German compound indicators
        german_indicators = [
            'temperatur', 'druck', 'geschwindigkeit', 'wert', 'zeit', 'faktor',
            'schwelle', 'grenze', 'bereich', 'stufe', 'menge', 'anzahl',
            'zähler', 'zhler', 'filter', 'regler', 'sensor', 'ventil',
            'pumpe', 'motor', 'steuerung', 'regelung', 'überwachung',
            'diagnose', 'erkennung', 'messung', 'prüfung', 'kontrolle'
        ]
        
        return any(indicator in clean_word for indicator in german_indicators)
    
    def _decompose_german_compound(self, word: str) -> str:
        """
        Decompose a German compound word into its components and translate.
        
        Args:
            word: German compound word
            
        Returns:
            Translated decomposed word
        """
        clean_word = re.sub(r'[^\w]', '', word)
        punctuation = word[len(clean_word):]
        
        # Try to find compound components
        components = []
        remaining = clean_word.lower()
        
        # Look for known compound endings first (most specific)
        compound_endings = [
            'temperatur', 'geschwindigkeit', 'druck', 'wert', 'zeit', 'faktor',
            'schwelle', 'grenze', 'bereich', 'stufe', 'menge', 'anzahl',
            'zähler', 'zhler', 'filter', 'regler', 'sensor', 'ventil',
            'pumpe', 'motor', 'steuerung', 'regelung', 'überwachung',
            'diagnose', 'erkennung', 'messung', 'prüfung', 'kontrolle',
            'unterbrechung', 'verbindung', 'anpassung', 'einstellung',
            'konfiguration', 'aktivierung', 'deaktivierung', 'initialisierung'
        ]
        
        # Find the longest matching ending
        found_ending = None
        for ending in sorted(compound_endings, key=len, reverse=True):
            if remaining.endswith(ending):
                found_ending = ending
                remaining = remaining[:-len(ending)]
                break
        
        if found_ending:
            # Translate the prefix part
            if remaining:
                prefix_translation = self.comprehensive_dict.translate_word(remaining)
                if prefix_translation == remaining:
                    # Try automotive dictionary for the prefix
                    prefix_translation = self._translate_automotive_prefix(remaining)
                components.append(prefix_translation)
            
            # Translate the ending
            ending_translation = self.comprehensive_dict.translate_word(found_ending)
            components.append(ending_translation)
            
            # Join components appropriately
            if len(components) == 2:
                return f"{components[0]} {components[1]}{punctuation}"
            else:
                return f"{components[0]}{punctuation}"
        
        # If no compound ending found, try word-by-word translation
        translated_word = self.comprehensive_dict.translate_word(clean_word)
        return translated_word + punctuation
    
    def _translate_automotive_prefix(self, prefix: str) -> str:
        """Translate automotive-specific prefixes."""
        automotive_prefixes = {
            'abgas': 'exhaust gas',
            'motor': 'engine',
            'kraft': 'force',
            'dreh': 'rotation',
            'luft': 'air',
            'öl': 'oil',
            'wasser': 'water',
            'benzin': 'gasoline',
            'diesel': 'diesel',
            'katalysator': 'catalytic converter',
            'lambda': 'lambda',
            'sauerstoff': 'oxygen',
            'stickstoff': 'nitrogen',
            'kohlen': 'carbon',
            'partikel': 'particle',
            'ruß': 'soot',
            'filter': 'filter',
            'turbo': 'turbo',
            'kompressor': 'compressor',
            'einspritz': 'injection',
            'zünd': 'ignition',
            'brems': 'brake',
            'lenk': 'steering',
            'getriebe': 'transmission',
            'kupplung': 'clutch',
            'differential': 'differential',
            'achse': 'axle',
            'rad': 'wheel',
            'reifen': 'tire'
        }
        
        return automotive_prefixes.get(prefix.lower(), prefix)
    
    def _calculate_confidence(self, original: str, translated: str, rules_applied: int) -> float:
        """
        Calculate confidence score for the translation.
        
        Args:
            original: Original text
            translated: Translated text
            rules_applied: Number of transformation rules applied
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence
        if translated == original:
            return 0.1  # Very low confidence if nothing was translated
        
        # Start with higher base confidence for comprehensive system
        confidence = 0.7
        
        # Boost confidence based on rules applied
        confidence += min(rules_applied * 0.05, 0.2)
        
        # Boost confidence if we have automotive terms
        automotive_terms_found = self._count_automotive_terms(original)
        if automotive_terms_found > 0:
            confidence += min(automotive_terms_found * 0.03, 0.15)
        
        # Calculate translation coverage (how many German words were translated)
        original_words = original.lower().split()
        translated_words = translated.lower().split()
        
        # Count how many words were actually translated (not just copied)
        translated_count = 0
        for i, orig_word in enumerate(original_words):
            if i < len(translated_words):
                clean_orig = re.sub(r'[^\w]', '', orig_word)
                clean_trans = re.sub(r'[^\w]', '', translated_words[i])
                
                # Check if word was actually translated
                if (clean_orig != clean_trans and 
                    not self._is_likely_english(clean_orig) and
                    self._is_likely_english(clean_trans)):
                    translated_count += 1
        
        # Boost confidence based on translation coverage
        if len(original_words) > 0:
            coverage_ratio = translated_count / len(original_words)
            confidence += min(coverage_ratio * 0.2, 0.2)
        
        # Penalize if too many German words remain untranslated
        remaining_german = self._count_remaining_german_words(translated)
        if remaining_german > 0:
            penalty = min(remaining_german * 0.05, 0.3)
            confidence -= penalty
        
        return max(min(confidence, 1.0), 0.1)  # Keep between 0.1 and 1.0
    
    def _count_remaining_german_words(self, text: str) -> int:
        """Count how many German words remain untranslated."""
        words = text.lower().split()
        german_count = 0
        
        common_german_words = [
            'der', 'die', 'das', 'und', 'oder', 'mit', 'für', 'von', 'zu', 'bei',
            'nach', 'vor', 'über', 'unter', 'zwischen', 'während', 'ohne', 'gegen',
            'durch', 'um', 'an', 'auf', 'in', 'aus', 'bis', 'seit', 'ab', 'hinter',
            'im', 'am', 'zum', 'zur', 'beim', 'vom', 'ins', 'ans', 'ist', 'sind',
            'war', 'waren', 'wird', 'werden', 'haben', 'hat', 'hatte', 'hatten',
            'sein', 'kann', 'könnte', 'soll', 'muss', 'darf', 'will', 'möchte',
            'wert', 'zeit', 'druck', 'temperatur', 'geschwindigkeit', 'faktor',
            'schwelle', 'grenze', 'bereich', 'anzahl', 'menge', 'zähler', 'zhler',
            'erkennung', 'diagnose', 'steuerung', 'regelung', 'überwachung',
            'messung', 'prüfung', 'kontrolle', 'einstellung', 'konfiguration'
        ]
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in common_german_words:
                german_count += 1
        
        return german_count
    
    def _count_automotive_terms(self, text: str) -> int:
        """Count automotive terms in the text."""
        if 'german' not in self.automotive_dict.dictionaries:
            return 0
        
        dictionary = self.automotive_dict.dictionaries['german']
        automotive_terms = dictionary.get('automotive_terms', {})
        
        count = 0
        text_lower = text.lower()
        
        for term in automotive_terms:
            if term.lower() in text_lower:
                count += 1
        
        return count
    
    def get_translation_statistics(self) -> Dict[str, Any]:
        """Get translation statistics."""
        total = self.stats['total_translations']
        
        stats = dict(self.stats)
        
        if total > 0:
            stats['dictionary_rate'] = self.stats['dictionary_translations'] / total
            stats['rule_based_rate'] = self.stats['rule_based_translations'] / total
            stats['cache_hit_rate'] = self.stats['cache_hits'] / total
            stats['partial_translation_rate'] = self.stats['partial_translations'] / total
        else:
            stats['dictionary_rate'] = 0.0
            stats['rule_based_rate'] = 0.0
            stats['cache_hit_rate'] = 0.0
            stats['partial_translation_rate'] = 0.0
        
        stats['cache_size'] = len(self.translation_cache)
        
        return stats
    
    def clear_cache(self):
        """Clear the translation cache."""
        self.translation_cache.clear()
        self.logger.info("Translation cache cleared")
