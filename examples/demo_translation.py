#!/usr/bin/env python3
"""
DAMOS Translator Demo

This script demonstrates the key features of the DAMOS translator
using the German DAMOS file included in the repository.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from damos_translator import DamosTranslatorApp, DamosParser, AutomotiveTranslator

def demo_basic_translation():
    """Demonstrate basic translation functionality."""
    print("🚗 DAMOS Translator Demo")
    print("=" * 50)
    
    # Initialize the translator
    app = DamosTranslatorApp(log_level='WARNING')
    
    # Path to the German DAMOS file
    german_file = Path(__file__).parent.parent / "your_file.dam"
    output_file = Path(__file__).parent / "demo_translated.dam"
    
    if not german_file.exists():
        print("❌ German DAMOS file not found!")
        return
    
    print(f"📁 Input file: {german_file}")
    print(f"📁 Output file: {output_file}")
    print()
    
    # Translate the file
    print("🔄 Translating German DAMOS file...")
    result = app.translate_file(
        str(german_file),
        str(output_file),
        source_language='german',
        create_report=True
    )
    
    if result['success']:
        stats = result['statistics']
        print("✅ Translation successful!")
        print(f"   📊 Parameters processed: {stats['total_parameters']}")
        print(f"   🔤 Parameters translated: {stats['translated_parameters']}")
        print(f"   📈 Translation rate: {stats['translation_rate']*100:.1f}%")
        print(f"   ⏱️  Processing time: {stats['processing_time']:.2f} seconds")
        print(f"   📄 Report: {result['report_path']}")
        print()
        
        # Show some example translations
        show_translation_examples(result['report_path'])
        
    else:
        print(f"❌ Translation failed: {result['error']}")

def show_translation_examples(report_path):
    """Show some example translations from the report."""
    print("🔍 Translation Examples:")
    print("-" * 30)
    
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find and display first few translation examples
        in_examples = False
        example_count = 0
        max_examples = 5
        
        for line in lines:
            if "Detailed Translations:" in line:
                in_examples = True
                continue
            
            if in_examples and example_count < max_examples:
                if line.startswith("Parameter "):
                    print(f"\n🔧 {line.strip()}")
                elif "Original (german):" in line:
                    original = line.split("Original (german): ")[1].strip()
                    print(f"   🇩🇪 German: {original}")
                elif "Translated:" in line:
                    translated = line.split("Translated: ")[1].strip()
                    print(f"   🇺🇸 English: {translated}")
                    example_count += 1
                    
    except Exception as e:
        print(f"Could not read examples: {e}")

def demo_automotive_dictionary():
    """Demonstrate automotive dictionary functionality."""
    print("\n📚 Automotive Dictionary Demo")
    print("-" * 30)
    
    from damos_translator.automotive_dictionary import AutomotiveDictionary
    
    auto_dict = AutomotiveDictionary()
    
    # Show dictionary statistics
    stats = auto_dict.get_dictionary_stats('german')
    print(f"German automotive dictionary: {stats['total_entries']} entries")
    print(f"  - Automotive terms: {stats['automotive_terms']}")
    print(f"  - Common phrases: {stats['common_phrases']}")
    print(f"  - Units: {stats['units']}")
    print()
    
    # Test some translations
    test_terms = [
        "Abgastemperatur",
        "Katalysator", 
        "Lambdasonde",
        "Drosselklappe",
        "Motortemperatur",
        "Kraftstoffpumpe"
    ]
    
    print("🔤 Term Translation Examples:")
    for term in test_terms:
        translation = auto_dict.translate_term(term, 'german')
        print(f"   {term} → {translation}")

def demo_language_detection():
    """Demonstrate language detection."""
    print("\n🌍 Language Detection Demo")
    print("-" * 30)
    
    from damos_translator.language_detector import LanguageDetector
    
    detector = LanguageDetector()
    
    test_descriptions = [
        "Abgastemperaturschwelle für Katalysator",
        "température d'échappement pour catalyseur",
        "temperatura di scarico per catalizzatore",
        "temperatura de escape para catalizador",
        "exhaust temperature for catalyst"
    ]
    
    for desc in test_descriptions:
        language, confidence = detector.detect_language(desc)
        print(f"   '{desc[:30]}...' → {language} ({confidence:.2f})")

if __name__ == '__main__':
    try:
        demo_basic_translation()
        demo_automotive_dictionary()
        demo_language_detection()
        
        print("\n🎉 Demo completed successfully!")
        print("Try running: python translate_damos.py your_file.dam -l german")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

