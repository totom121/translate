"""
Integration tests for the DAMOS translator system.
Tests the complete translation workflow with the German DAMOS file.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from damos_translator import DamosTranslatorApp, DamosParser, AutomotiveTranslator

class TestDamosTranslatorIntegration(unittest.TestCase):
    """Integration tests for the complete DAMOS translation system."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.app = DamosTranslatorApp(log_level='WARNING')  # Reduce log noise in tests
        
        # Path to the German DAMOS file
        self.german_file = Path(__file__).parent.parent / "your_file.dam"
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_german_damos_file_exists(self):
        """Test that the German DAMOS file exists and is readable."""
        self.assertTrue(self.german_file.exists(), "German DAMOS file not found")
        self.assertTrue(self.german_file.is_file(), "German DAMOS file is not a file")
        
        # Test file is readable
        with open(self.german_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1000)  # Read first 1KB
            self.assertGreater(len(content), 0, "German DAMOS file appears to be empty")
    
    def test_parse_german_damos_file(self):
        """Test parsing the German DAMOS file."""
        parser = DamosParser()
        
        # Validate DAMOS format
        is_valid = parser.validate_damos_format(str(self.german_file))
        self.assertTrue(is_valid, "German DAMOS file failed format validation")
        
        # Parse the file
        parsed_data = parser.parse_file(str(self.german_file))
        
        # Verify parsing results
        self.assertIsInstance(parsed_data, dict)
        self.assertIn('header', parsed_data)
        self.assertIn('parameters', parsed_data)
        self.assertIn('structure', parsed_data)
        
        # Check we found parameters
        self.assertGreater(len(parsed_data['parameters']), 0, "No parameters found in German DAMOS file")
        
        # Check header information
        header = parsed_data['header']
        self.assertGreater(len(header.lines), 0, "No header lines found")
        
        print(f"✓ Parsed {len(parsed_data['parameters'])} parameters from German DAMOS file")
    
    def test_language_detection_german(self):
        """Test language detection on German DAMOS descriptions."""
        parser = DamosParser()
        parsed_data = parser.parse_file(str(self.german_file))
        
        # Extract descriptions
        descriptions = [param.description for param in parsed_data['parameters'] if param.description.strip()]
        self.assertGreater(len(descriptions), 0, "No descriptions found to test language detection")
        
        # Test language detection
        from damos_translator.language_detector import LanguageDetector
        detector = LanguageDetector()
        
        language, confidence = detector.detect_language_from_descriptions(descriptions[:10])  # Test first 10
        
        self.assertEqual(language, 'german', f"Expected German, detected: {language}")
        self.assertGreater(confidence, 0.3, f"Low confidence for German detection: {confidence}")
        
        print(f"✓ Language detection: {language} (confidence: {confidence:.2f})")
    
    def test_automotive_dictionary_german_terms(self):
        """Test that German automotive terms are properly loaded and translated."""
        from damos_translator.automotive_dictionary import AutomotiveDictionary
        
        auto_dict = AutomotiveDictionary()
        
        # Check German dictionary is loaded
        self.assertIn('german', auto_dict.get_available_languages())
        
        # Test some common automotive terms
        test_terms = [
            ('Abgastemperatur', 'exhaust gas temperature'),
            ('Katalysator', 'catalytic converter'),
            ('Lambdasonde', 'lambda sensor'),
            ('Drosselklappe', 'throttle valve'),
            ('Motortemperatur', 'engine temperature')
        ]
        
        for german_term, expected_english in test_terms:
            translation = auto_dict.translate_term(german_term, 'german')
            self.assertEqual(translation, expected_english, 
                           f"Translation failed: {german_term} -> {translation} (expected: {expected_english})")
        
        print(f"✓ German automotive dictionary loaded with {auto_dict.get_dictionary_stats('german')['total_entries']} entries")
    
    def test_translate_german_descriptions(self):
        """Test translation of actual German descriptions from the DAMOS file."""
        parser = DamosParser()
        parsed_data = parser.parse_file(str(self.german_file))
        
        translator = AutomotiveTranslator(use_external_api=False)  # Use only dictionary for testing
        
        # Get some sample descriptions
        sample_descriptions = []
        for param in parsed_data['parameters'][:5]:  # Test first 5 parameters
            if param.description.strip():
                sample_descriptions.append(param.description)
        
        self.assertGreater(len(sample_descriptions), 0, "No descriptions found for translation testing")
        
        # Translate descriptions
        results = translator.translate_multiple_descriptions(sample_descriptions, 'german')
        
        self.assertEqual(len(results), len(sample_descriptions))
        
        # Check translation results
        translated_count = 0
        for i, result in enumerate(results):
            self.assertIn('original', result)
            self.assertIn('translated', result)
            self.assertIn('source_language', result)
            self.assertIn('confidence', result)
            
            if result['translated'] != result['original']:
                translated_count += 1
                print(f"✓ Translated: '{result['original'][:50]}...' -> '{result['translated'][:50]}...'")
        
        print(f"✓ Successfully translated {translated_count}/{len(sample_descriptions)} descriptions")
    
    def test_complete_translation_workflow(self):
        """Test the complete translation workflow with the German DAMOS file."""
        output_file = self.test_dir / "translated_german_file.dam"
        
        # Run complete translation
        result = self.app.translate_file(
            str(self.german_file),
            str(output_file),
            source_language='german',
            create_report=True
        )
        
        # Check translation was successful
        self.assertTrue(result['success'], f"Translation failed: {result.get('error', 'Unknown error')}")
        
        # Check output file was created
        self.assertTrue(output_file.exists(), "Translated file was not created")
        self.assertGreater(output_file.stat().st_size, 0, "Translated file is empty")
        
        # Check statistics
        stats = result['statistics']
        self.assertGreater(stats['total_parameters'], 0, "No parameters processed")
        self.assertGreaterEqual(stats['translated_parameters'], 0, "Negative translated parameters count")
        
        # Check report was created
        if result['report_path']:
            report_file = Path(result['report_path'])
            self.assertTrue(report_file.exists(), "Translation report was not created")
        
        print(f"✓ Complete translation: {stats['translated_parameters']}/{stats['total_parameters']} parameters")
        print(f"✓ Translation rate: {stats['translation_rate']*100:.1f}%")
        print(f"✓ Processing time: {stats['processing_time']:.2f} seconds")
        print(f"✓ Output file: {output_file}")
        
        return result
    
    def test_file_structure_preservation(self):
        """Test that the translated file preserves the original structure."""
        output_file = self.test_dir / "structure_test.dam"
        
        # Translate the file
        result = self.app.translate_file(str(self.german_file), str(output_file))
        self.assertTrue(result['success'], "Translation failed")
        
        # Parse both original and translated files
        parser = DamosParser()
        original_data = parser.parse_file(str(self.german_file))
        translated_data = parser.parse_file(str(output_file))
        
        # Compare structures
        self.assertEqual(len(original_data['parameters']), len(translated_data['parameters']),
                        "Parameter count mismatch between original and translated files")
        
        # Check that parameter IDs and names are preserved
        for orig_param, trans_param in zip(original_data['parameters'], translated_data['parameters']):
            self.assertEqual(orig_param.parameter_id, trans_param.parameter_id,
                           f"Parameter ID mismatch: {orig_param.parameter_id} vs {trans_param.parameter_id}")
            self.assertEqual(orig_param.parameter_name, trans_param.parameter_name,
                           f"Parameter name mismatch: {orig_param.parameter_name} vs {trans_param.parameter_name}")
            self.assertEqual(orig_param.memory_address, trans_param.memory_address,
                           f"Memory address mismatch: {orig_param.memory_address} vs {trans_param.memory_address}")
        
        print("✓ File structure preserved correctly")
    
    def test_validation_workflow(self):
        """Test the validation workflow."""
        output_file = self.test_dir / "validation_test.dam"
        
        # First translate the file
        result = self.app.translate_file(str(self.german_file), str(output_file))
        self.assertTrue(result['success'], "Translation failed")
        
        # Then validate it
        validation_result = self.app.validate_translation(str(self.german_file), str(output_file))
        
        self.assertIn('valid', validation_result)
        self.assertIn('original_parameters', validation_result)
        self.assertIn('translated_parameters', validation_result)
        
        if not validation_result['valid']:
            print(f"Validation issues: {validation_result.get('issues', [])}")
        
        print(f"✓ Validation result: {'PASSED' if validation_result['valid'] else 'FAILED'}")


def run_integration_tests():
    """Run integration tests and provide a summary."""
    print("Running DAMOS Translator Integration Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDamosTranslatorIntegration)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("Integration Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'SUCCESS' if success else 'FAILURE'}")
    
    return success


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)

