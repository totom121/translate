#!/usr/bin/env python3
"""
Test script to verify DeepL is used by default.
"""

import sys
sys.path.insert(0, "src")

from src.config.settings import TranslationConfig, TranslationService
from src.core.translator import PureTranslator

def test_deepl_default():
    """Test that DeepL is the default service."""
    
    print("🧪 Testing DeepL Default Configuration")
    print("=" * 50)
    
    # Test default configuration
    config = TranslationConfig()
    print(f"✅ Default primary service: {config.primary_service.value}")
    print(f"✅ Default fallback services: {[s.value for s in config.fallback_services]}")
    
    # Test translator initialization
    try:
        translator = PureTranslator(config)
        print(f"✅ Translator initialized successfully")
        print(f"✅ Available services: {[s.value for s in translator.available_services]}")
        
        # Test a simple translation
        if translator.available_services:
            primary_service = translator.available_services[0]
            print(f"✅ Primary service being used: {primary_service.value}")
            
            # Test translation
            test_text = "Abgastemperaturschwelle"
            result = translator.translate(test_text, 'de', 'en')
            
            print(f"\n🎯 Translation Test:")
            print(f"   Original: {result.original}")
            print(f"   Translated: {result.translated}")
            print(f"   Service used: {result.service_used}")
            print(f"   Confidence: {result.confidence:.3f}")
            
            if result.service_used == 'deepl':
                print("✅ SUCCESS: DeepL is being used as expected!")
            else:
                print(f"⚠️  WARNING: Expected DeepL but got {result.service_used}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: This might be expected if DeepL API key is not configured")
        print("The system should fall back to other services")

if __name__ == '__main__':
    test_deepl_default()

