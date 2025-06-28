#!/usr/bin/env python3
"""
Test script for the pure DAMOS translator.
"""

import sys
sys.path.insert(0, "src")

from src.core.translator import PureTranslator
from src.config.settings import TranslationConfig, TranslationService

def test_local_translator():
    """Test the local translator with German automotive terms."""
    
    # Configure to use only local translator
    config = TranslationConfig()
    config.primary_service = TranslationService.LOCAL
    config.fallback_services = []  # No fallbacks
    
    # Create translator
    translator = PureTranslator(config)
    
    # Test phrases from the DAMOS file
    test_phrases = [
        "Abgastemperaturschwelle für Signalunterbrechung",
        "oberer Grenzwert Anpassung AGR-Rate", 
        "unterer Grenzwert Anpassung AGR-Rate",
        "maximal mögliche AGR-Rate",
        "Anzahl Fahrzyklen mit Bedingung",
        "Temperatur Motor Sensor",
        "Druck Steuerung Regelung",
        "Zündung Einspritzung Ventil",
        "Katalysator Abgas Benzin",
        "Fehlerzeit bei unplausiblen Werten"
    ]
    
    print("🚀 Testing Pure DAMOS Translator (Local Mode)")
    print("=" * 60)
    
    total_translated = 0
    total_words = 0
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n{i}. Testing: '{phrase}'")
        
        try:
            result = translator.translate(phrase, 'de', 'en')
            
            print(f"   Original:    {result.original}")
            print(f"   Translated:  {result.translated}")
            print(f"   Service:     {result.service_used}")
            print(f"   Confidence:  {result.confidence:.3f}")
            print(f"   Translation Rate: {result.translation_rate:.1f}%")
            print(f"   Words: {result.translated_words}/{result.word_count}")
            
            if result.confidence > 0.3:
                total_translated += 1
            
            total_words += result.word_count
            
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Successfully translated: {total_translated}/{len(test_phrases)} phrases")
    print(f"   Success rate: {total_translated/len(test_phrases)*100:.1f}%")
    
    # Test translator statistics
    stats = translator.get_statistics()
    print(f"\n📈 Translator Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == '__main__':
    test_local_translator()

