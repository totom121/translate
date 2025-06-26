"""
DAMOS Translator Main Application

Main application that orchestrates the complete DAMOS file translation process,
including parsing, translation, and reconstruction with comprehensive error handling
and progress reporting.
"""

import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

from .parser import DamosParser
from .translator import AutomotiveTranslator
from .reconstructor import DamosReconstructor
from .language_detector import LanguageDetector

class DamosTranslatorApp:
    """
    Main application class for DAMOS file translation.
    """
    
    def __init__(self, log_level: str = 'INFO'):
        self.setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.parser = DamosParser()
        self.translator = AutomotiveTranslator()
        self.reconstructor = DamosReconstructor()
        self.language_detector = LanguageDetector()
        
        # Application statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_duration': 0,
            'files_processed': 0,
            'total_parameters': 0,
            'translated_parameters': 0,
            'errors': [],
            'warnings': []
        }
    
    def setup_logging(self, log_level: str):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('damos_translator.log')
            ]
        )
    
    def translate_file(self, input_path: str, output_path: Optional[str] = None, 
                      source_language: Optional[str] = None, 
                      create_report: bool = True) -> Dict[str, Any]:
        """
        Translate a single DAMOS file.
        
        Args:
            input_path: Path to input DAMOS file
            output_path: Path for output file (auto-generated if None)
            source_language: Source language (auto-detected if None)
            create_report: Whether to create a translation report
            
        Returns:
            Translation results and statistics
        """
        self.stats['start_time'] = time.time()
        self.logger.info(f"Starting translation of: {input_path}")
        
        try:
            # Validate input file
            if not Path(input_path).exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            if not self.parser.validate_damos_format(input_path):
                self.logger.warning(f"File may not be a valid DAMOS file: {input_path}")
                self.stats['warnings'].append("Input file format validation failed")
            
            # Generate output path if not provided
            if output_path is None:
                input_file = Path(input_path)
                output_path = str(input_file.parent / f"{input_file.stem}_translated{input_file.suffix}")
            
            # Step 1: Parse the DAMOS file
            self.logger.info("Parsing DAMOS file...")
            parsed_data = self.parser.parse_file(input_path)
            parsed_data['original_file_path'] = input_path
            
            self.stats['total_parameters'] = len(parsed_data['parameters'])
            self.logger.info(f"Found {self.stats['total_parameters']} parameters")
            
            # Step 2: Extract translatable content
            translatable_content = self.parser.extract_translatable_content(parsed_data)
            descriptions = [desc for _, _, desc in translatable_content]
            
            # Step 3: Auto-detect language if not specified
            if source_language is None:
                detected_lang, confidence = self.language_detector.detect_language_from_descriptions(descriptions)
                source_language = detected_lang
                self.logger.info(f"Auto-detected language: {source_language} (confidence: {confidence:.2f})")
                
                if confidence < 0.3:
                    self.logger.warning(f"Low language detection confidence: {confidence:.2f}")
                    self.stats['warnings'].append(f"Low language detection confidence: {confidence:.2f}")
            
            # Step 4: Translate descriptions
            self.logger.info(f"Translating {len(descriptions)} descriptions from {source_language} to English...")
            translation_results = self.translator.translate_multiple_descriptions(descriptions, source_language)
            
            # Count successful translations
            self.stats['translated_parameters'] = sum(
                1 for result in translation_results 
                if result['translated'] != result['original']
            )
            
            self.logger.info(f"Successfully translated {self.stats['translated_parameters']} parameters")
            
            # Step 5: Reconstruct the file
            self.logger.info("Reconstructing DAMOS file with translations...")
            reconstruction_stats = self.reconstructor.reconstruct_file(
                parsed_data, translation_results, output_path
            )
            
            # Step 6: Create translation report if requested
            report_path = None
            if create_report:
                self.logger.info("Creating translation report...")
                report_path = self.reconstructor.create_translation_report(
                    parsed_data, translation_results, output_path
                )
            
            # Compile final results
            self.stats['end_time'] = time.time()
            self.stats['total_duration'] = self.stats['end_time'] - self.stats['start_time']
            self.stats['files_processed'] = 1
            
            results = {
                'success': True,
                'input_path': input_path,
                'output_path': output_path,
                'report_path': report_path,
                'source_language': source_language,
                'statistics': {
                    'total_parameters': self.stats['total_parameters'],
                    'translated_parameters': self.stats['translated_parameters'],
                    'translation_rate': (self.stats['translated_parameters'] / 
                                       self.stats['total_parameters'] if self.stats['total_parameters'] > 0 else 0),
                    'processing_time': self.stats['total_duration'],
                    'file_size_original': Path(input_path).stat().st_size,
                    'file_size_translated': Path(output_path).stat().st_size if Path(output_path).exists() else 0
                },
                'reconstruction_stats': reconstruction_stats,
                'translation_stats': self.translator.get_translation_statistics(),
                'warnings': self.stats['warnings'],
                'errors': self.stats['errors']
            }
            
            self.logger.info(f"Translation completed successfully in {self.stats['total_duration']:.2f} seconds")
            return results
            
        except Exception as e:
            self.stats['errors'].append(str(e))
            self.logger.error(f"Translation failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'input_path': input_path,
                'statistics': self.stats,
                'warnings': self.stats['warnings'],
                'errors': self.stats['errors']
            }
    
    def translate_batch(self, input_directory: str, output_directory: Optional[str] = None,
                       source_language: Optional[str] = None, 
                       file_pattern: str = "*.dam") -> List[Dict[str, Any]]:
        """
        Translate multiple DAMOS files in a directory.
        
        Args:
            input_directory: Directory containing DAMOS files
            output_directory: Output directory (created if doesn't exist)
            source_language: Source language for all files
            file_pattern: File pattern to match (default: *.dam)
            
        Returns:
            List of translation results for each file
        """
        input_dir = Path(input_directory)
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_directory}")
        
        # Setup output directory
        if output_directory is None:
            output_dir = input_dir / "translated"
        else:
            output_dir = Path(output_directory)
        
        output_dir.mkdir(exist_ok=True)
        
        # Find DAMOS files
        damos_files = list(input_dir.glob(file_pattern))
        if not damos_files:
            self.logger.warning(f"No files matching pattern '{file_pattern}' found in {input_directory}")
            return []
        
        self.logger.info(f"Found {len(damos_files)} files to translate")
        
        # Process each file
        results = []
        for i, file_path in enumerate(damos_files, 1):
            self.logger.info(f"Processing file {i}/{len(damos_files)}: {file_path.name}")
            
            output_path = output_dir / f"{file_path.stem}_translated{file_path.suffix}"
            
            result = self.translate_file(
                str(file_path), 
                str(output_path), 
                source_language
            )
            
            result['batch_info'] = {
                'file_number': i,
                'total_files': len(damos_files),
                'progress_percent': (i / len(damos_files)) * 100
            }
            
            results.append(result)
            
            if result['success']:
                self.logger.info(f"✓ Successfully translated {file_path.name}")
            else:
                self.logger.error(f"✗ Failed to translate {file_path.name}: {result.get('error', 'Unknown error')}")
        
        # Create batch summary report
        self._create_batch_report(results, output_dir)
        
        return results
    
    def _create_batch_report(self, results: List[Dict[str, Any]], output_dir: Path):
        """Create a summary report for batch processing."""
        report_path = output_dir / "batch_translation_summary.txt"
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("DAMOS Batch Translation Summary\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Total files processed: {len(results)}\n")
            f.write(f"Successful translations: {len(successful)}\n")
            f.write(f"Failed translations: {len(failed)}\n")
            f.write(f"Success rate: {len(successful)/len(results)*100:.1f}%\n\n")
            
            if successful:
                total_params = sum(r['statistics']['total_parameters'] for r in successful)
                total_translated = sum(r['statistics']['translated_parameters'] for r in successful)
                
                f.write(f"Total parameters processed: {total_params}\n")
                f.write(f"Total parameters translated: {total_translated}\n")
                f.write(f"Overall translation rate: {total_translated/total_params*100:.1f}%\n\n")
            
            if failed:
                f.write("Failed Files:\n")
                f.write("-" * 20 + "\n")
                for result in failed:
                    f.write(f"  {Path(result['input_path']).name}: {result.get('error', 'Unknown error')}\n")
                f.write("\n")
            
            f.write("Successful Files:\n")
            f.write("-" * 20 + "\n")
            for result in successful:
                stats = result['statistics']
                f.write(f"  {Path(result['input_path']).name}:\n")
                f.write(f"    Parameters: {stats['total_parameters']}\n")
                f.write(f"    Translated: {stats['translated_parameters']}\n")
                f.write(f"    Rate: {stats['translation_rate']*100:.1f}%\n")
                f.write(f"    Time: {stats['processing_time']:.2f}s\n\n")
        
        self.logger.info(f"Batch summary report created: {report_path}")
    
    def validate_translation(self, original_path: str, translated_path: str) -> Dict[str, Any]:
        """
        Validate a translated DAMOS file against the original.
        
        Args:
            original_path: Path to original file
            translated_path: Path to translated file
            
        Returns:
            Validation results
        """
        self.logger.info(f"Validating translation: {translated_path}")
        
        try:
            # Parse both files
            original_data = self.parser.parse_file(original_path)
            translated_data = self.parser.parse_file(translated_path)
            
            # Compare structures
            comparison = self.reconstructor.compare_files(original_path, translated_path)
            
            validation = {
                'valid': True,
                'original_parameters': len(original_data['parameters']),
                'translated_parameters': len(translated_data['parameters']),
                'structure_preserved': comparison.get('structural_changes', []) == [],
                'file_comparison': comparison,
                'issues': []
            }
            
            # Check parameter count
            if validation['original_parameters'] != validation['translated_parameters']:
                validation['valid'] = False
                validation['issues'].append("Parameter count mismatch")
            
            # Check for structural issues
            if not validation['structure_preserved']:
                validation['issues'].append("File structure may have been modified")
            
            return validation
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'issues': [f"Validation failed: {e}"]
            }


def print_supported_languages():
    """Print all supported languages with descriptions."""
    print("🌍 Supported Languages for DAMOS Translation")
    print("=" * 50)
    print()
    
    languages = {
        'auto': {
            'name': 'Auto-Detection',
            'description': 'Automatically detect the source language',
            'flag': '🔍',
            'coverage': 'N/A'
        },
        'german': {
            'name': 'German',
            'description': 'Comprehensive automotive dictionary with 500+ terms',
            'flag': '🇩🇪',
            'coverage': 'Excellent'
        },
        'french': {
            'name': 'French',
            'description': 'Basic automotive terminology support',
            'flag': '🇫🇷',
            'coverage': 'Good'
        },
        'italian': {
            'name': 'Italian',
            'description': 'Basic automotive terminology support',
            'flag': '🇮🇹',
            'coverage': 'Good'
        },
        'spanish': {
            'name': 'Spanish',
            'description': 'Basic automotive terminology support',
            'flag': '🇪🇸',
            'coverage': 'Good'
        }
    }
    
    for code, info in languages.items():
        print(f"{info['flag']} {info['name']} ({code})")
        print(f"   {info['description']}")
        print(f"   Coverage: {info['coverage']}")
        print()
    
    print("Usage examples:")
    print("  python translate_damos.py file.dam -l auto      # Auto-detect language")
    print("  python translate_damos.py file.dam -l german    # Force German")
    print("  python translate_damos.py file.dam -l french    # Force French")
    print("  python translate_damos.py file.dam -l italian   # Force Italian")
    print("  python translate_damos.py file.dam -l spanish   # Force Spanish")
    print("  python translate_damos.py file.dam --interactive # Interactive selection")


def interactive_language_selection():
    """Interactive language selection with preview."""
    print("\n🌍 Interactive Language Selection")
    print("=" * 40)
    
    languages = [
        ('auto', '🔍 Auto-Detection', 'Let the system detect the language automatically'),
        ('german', '🇩🇪 German', 'Comprehensive automotive dictionary (500+ terms)'),
        ('french', '🇫🇷 French', 'Basic automotive terminology support'),
        ('italian', '🇮🇹 Italian', 'Basic automotive terminology support'),
        ('spanish', '🇪🇸 Spanish', 'Basic automotive terminology support')
    ]
    
    print("\nAvailable languages:")
    for i, (code, name, desc) in enumerate(languages, 1):
        print(f"  {i}. {name}")
        print(f"     {desc}")
        print()
    
    while True:
        try:
            choice = input("Select language (1-5) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(languages):
                selected_code, selected_name, selected_desc = languages[choice_num - 1]
                
                print(f"\n✅ Selected: {selected_name}")
                print(f"   {selected_desc}")
                
                # Show preview for non-auto languages
                if selected_code != 'auto':
                    show_language_preview(selected_code)
                
                confirm = input("\nConfirm selection? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return selected_code
                else:
                    print("\nPlease select again:")
                    continue
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except ValueError:
            print("❌ Invalid input. Please enter a number 1-5 or 'q' to quit.")
        except KeyboardInterrupt:
            print("\n\n⏹️ Selection cancelled.")
            return None


def show_language_preview(language_code):
    """Show a preview of automotive terms for the selected language."""
    try:
        from .automotive_dictionary import AutomotiveDictionary
        
        auto_dict = AutomotiveDictionary()
        
        if language_code not in auto_dict.get_available_languages():
            print(f"   ⚠️ Dictionary for {language_code} not fully loaded")
            return
        
        # Get some sample terms
        dictionary = auto_dict.dictionaries[language_code]
        automotive_terms = dictionary.get('automotive_terms', {})
        
        if automotive_terms:
            print(f"\n📚 Sample automotive terms in {language_code.title()}:")
            
            # Show first 5 terms as examples
            sample_terms = list(automotive_terms.items())[:5]
            for original, translation in sample_terms:
                print(f"   • {original} → {translation}")
            
            stats = auto_dict.get_dictionary_stats(language_code)
            print(f"\n📊 Dictionary contains {stats['total_entries']} total entries")
        else:
            print(f"   ⚠️ No automotive terms loaded for {language_code}")
            
    except Exception as e:
        print(f"   ⚠️ Could not load dictionary preview: {e}")


def main():
    """Command-line interface for the DAMOS translator."""
    parser = argparse.ArgumentParser(description='Translate DAMOS files from any language to English')
    
    parser.add_argument('input', nargs='?', help='Input DAMOS file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-l', '--language', 
                       choices=['auto', 'german', 'french', 'italian', 'spanish'],
                       default='auto',
                       help='Source language: auto (auto-detect), german, french, italian, spanish (default: auto)')
    parser.add_argument('--batch', action='store_true', help='Process directory in batch mode')
    parser.add_argument('--pattern', default='*.dam', help='File pattern for batch mode (default: *.dam)')
    parser.add_argument('--no-report', action='store_true', help='Skip creating translation report')
    parser.add_argument('--validate', help='Validate translated file against original')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    parser.add_argument('--list-languages', action='store_true', 
                       help='List all supported languages and exit')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive mode for language selection')
    
    args = parser.parse_args()
    
    # Handle special commands first
    if args.list_languages:
        print_supported_languages()
        return 0
    
    # Initialize translator app
    app = DamosTranslatorApp(log_level=args.log_level)
    
    # Handle interactive language selection
    if args.interactive:
        args.language = interactive_language_selection()
        if args.language is None:
            print("Language selection cancelled.")
            return 1
    
    # Check if input is required but not provided
    if not args.input and not args.list_languages:
        parser.error("Input file or directory is required unless using --list-languages")
    
    # Convert 'auto' to None for auto-detection
    source_language = None if args.language == 'auto' else args.language
    
    try:
        if args.validate:
            # Validation mode
            result = app.validate_translation(args.input, args.validate)
            if result['valid']:
                print("✓ Validation passed")
                return 0
            else:
                print("✗ Validation failed:")
                for issue in result['issues']:
                    print(f"  - {issue}")
                return 1
        
        elif args.batch:
            # Batch processing mode
            results = app.translate_batch(
                args.input, 
                args.output, 
                source_language, 
                args.pattern
            )
            
            successful = sum(1 for r in results if r['success'])
            print(f"Batch processing complete: {successful}/{len(results)} files translated successfully")
            
            return 0 if successful == len(results) else 1
        
        else:
            # Single file mode
            result = app.translate_file(
                args.input, 
                args.output, 
                source_language, 
                not args.no_report
            )
            
            if result['success']:
                stats = result['statistics']
                print(f"✓ Translation successful!")
                print(f"  Output: {result['output_path']}")
                print(f"  Parameters translated: {stats['translated_parameters']}/{stats['total_parameters']} ({stats['translation_rate']*100:.1f}%)")
                print(f"  Processing time: {stats['processing_time']:.2f} seconds")
                
                if result['report_path']:
                    print(f"  Report: {result['report_path']}")
                
                return 0
            else:
                print(f"✗ Translation failed: {result['error']}")
                return 1
    
    except KeyboardInterrupt:
        print("\nTranslation interrupted by user")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
