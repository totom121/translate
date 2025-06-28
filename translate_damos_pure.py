#!/usr/bin/env python3
"""
Pure DAMOS File Translator

A comprehensive translation system that translates as many words as possible
from DAMOS files without relying on predefined dictionaries.

Usage:
    python translate_damos_pure.py input.dam [options]
    
Examples:
    # Basic translation with auto-detection
    python translate_damos_pure.py your_file.dam
    
    # Specify output file and source language
    python translate_damos_pure.py your_file.dam -o translated.dam -l de
    
    # Use specific translation service
    python translate_damos_pure.py your_file.dam --service google
    
    # Batch processing
    python translate_damos_pure.py *.dam --batch
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.translator import PureTranslator, TranslationResult
from src.core.parser import DamosParser
from src.core.reconstructor import DamosReconstructor
from src.config.settings import TranslationConfig, TranslationService, SourceLanguage
from src.utils.logger import setup_logging
from src.utils.progress import ProgressTracker

class DamosPureTranslator:
    """
    Main application class for pure DAMOS file translation.
    """
    
    def __init__(self, config: TranslationConfig = None):
        """Initialize the DAMOS translator."""
        self.config = config or TranslationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.translator = PureTranslator(self.config)
        self.parser = DamosParser()
        self.reconstructor = DamosReconstructor()
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'total_parameters': 0,
            'translated_parameters': 0,
            'total_processing_time': 0.0,
            'translation_rate': 0.0
        }
    
    def translate_file(self, input_path: str, output_path: str = None, 
                      source_lang: str = None) -> dict:
        """
        Translate a single DAMOS file.
        
        Args:
            input_path: Path to input DAMOS file
            output_path: Path to output file (auto-generated if None)
            source_lang: Source language code (auto-detect if None)
            
        Returns:
            Dictionary with translation results and statistics
        """
        start_time = time.time()
        
        # Validate input file
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Generate output path if not provided
        if not output_path:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_pure_translated{input_file.suffix}")
        
        self.logger.info(f"Starting pure translation of: {input_path}")
        self.logger.info(f"Output file: {output_path}")
        
        try:
            # Step 1: Parse DAMOS file
            self.logger.info("Parsing DAMOS file...")
            parameters = self.parser.parse_file(input_path)
            self.logger.info(f"Found {len(parameters)} parameters to translate")
            
            if not parameters:
                self.logger.warning("No parameters found in DAMOS file")
                return self._create_result_summary(input_path, output_path, [], 0, start_time)
            
            # Step 2: Extract descriptions for translation
            descriptions = []
            for param in parameters:
                if param.get('description') and param['description'].strip():
                    descriptions.append(param['description'])
            
            self.logger.info(f"Extracting {len(descriptions)} descriptions for translation")
            
            # Step 3: Translate descriptions
            self.logger.info(f"Translating descriptions from {source_lang or 'auto-detected'} to English...")
            
            # Use progress tracking for large files
            progress = ProgressTracker(len(descriptions), "Translating")
            
            translation_results = []
            batch_size = self.config.batch_size
            
            for i in range(0, len(descriptions), batch_size):
                batch = descriptions[i:i + batch_size]
                
                # Translate batch
                batch_results = self.translator.translate_batch(
                    batch, source_lang, 'en'
                )
                translation_results.extend(batch_results)
                
                # Update progress
                progress.update(len(batch_results))
                
                # Log progress for large files
                if len(descriptions) > 100 and i % (batch_size * 5) == 0:
                    self.logger.info(f"Translated {i + len(batch)}/{len(descriptions)} descriptions")
            
            progress.finish()
            
            # Step 4: Update parameters with translations
            self._update_parameters_with_translations(parameters, translation_results)
            
            # Step 5: Reconstruct DAMOS file
            self.logger.info("Reconstructing DAMOS file with translations...")
            self.reconstructor.reconstruct_file(
                input_path, output_path, parameters, translation_results
            )
            
            # Step 6: Generate report
            if self.config.generate_report:
                report_path = output_path.replace('.dam', '_pure_translation_report.txt')
                self._generate_translation_report(
                    translation_results, report_path, input_path, output_path
                )
                self.logger.info(f"Translation report created: {report_path}")
            
            # Calculate final statistics
            processing_time = time.time() - start_time
            successful_translations = sum(1 for r in translation_results if r.confidence > 0.5)
            
            result = self._create_result_summary(
                input_path, output_path, translation_results, 
                successful_translations, start_time
            )
            
            self.logger.info(f"Translation completed successfully in {processing_time:.2f} seconds")
            self.logger.info(f"Translation rate: {result['translation_rate']:.1f}% ({successful_translations}/{len(descriptions)} parameters)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            raise
    
    def translate_batch(self, input_files: List[str], output_dir: str = None) -> List[dict]:
        """
        Translate multiple DAMOS files.
        
        Args:
            input_files: List of input file paths
            output_dir: Output directory (same as input if None)
            
        Returns:
            List of translation result dictionaries
        """
        results = []
        
        for input_file in input_files:
            try:
                # Generate output path
                if output_dir:
                    output_path = str(Path(output_dir) / f"{Path(input_file).stem}_pure_translated.dam")
                else:
                    output_path = None
                
                # Translate file
                result = self.translate_file(input_file, output_path)
                results.append(result)
                
                self.stats['files_processed'] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to translate {input_file}: {e}")
                results.append({
                    'input_file': input_file,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _update_parameters_with_translations(self, parameters: List[dict], 
                                           translation_results: List[TranslationResult]):
        """Update parameter descriptions with translation results."""
        result_index = 0
        
        for param in parameters:
            if param.get('description') and param['description'].strip():
                if result_index < len(translation_results):
                    result = translation_results[result_index]
                    param['translated_description'] = result.translated
                    param['translation_confidence'] = result.confidence
                    param['translation_service'] = result.service_used
                    result_index += 1
    
    def _generate_translation_report(self, results: List[TranslationResult], 
                                   report_path: str, input_path: str, output_path: str):
        """Generate detailed translation report."""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("DAMOS Pure Translation Report\n")
            f.write("=" * 50 + "\n\n")
            
            # Summary statistics
            total_params = len(results)
            successful = sum(1 for r in results if r.confidence > 0.5)
            translation_rate = (successful / total_params * 100) if total_params > 0 else 0
            
            f.write(f"Input file: {input_path}\n")
            f.write(f"Output file: {output_path}\n")
            f.write(f"Total parameters: {total_params}\n")
            f.write(f"Successfully translated: {successful}\n")
            f.write(f"Translation rate: {translation_rate:.1f}%\n\n")
            
            # Service usage statistics
            service_usage = {}
            for result in results:
                service = result.service_used
                service_usage[service] = service_usage.get(service, 0) + 1
            
            f.write("Translation services used:\n")
            for service, count in sorted(service_usage.items()):
                percentage = (count / total_params * 100) if total_params > 0 else 0
                f.write(f"  {service}: {count} parameters ({percentage:.1f}%)\n")
            f.write("\n")
            
            # Translation quality distribution
            confidence_ranges = {
                'High (0.8-1.0)': 0,
                'Medium (0.5-0.8)': 0,
                'Low (0.0-0.5)': 0
            }
            
            for result in results:
                if result.confidence >= 0.8:
                    confidence_ranges['High (0.8-1.0)'] += 1
                elif result.confidence >= 0.5:
                    confidence_ranges['Medium (0.5-0.8)'] += 1
                else:
                    confidence_ranges['Low (0.0-0.5)'] += 1
            
            f.write("Translation quality distribution:\n")
            for range_name, count in confidence_ranges.items():
                percentage = (count / total_params * 100) if total_params > 0 else 0
                f.write(f"  {range_name}: {count} parameters ({percentage:.1f}%)\n")
            f.write("\n")
            
            # Detailed translations
            f.write("Detailed Translations:\n")
            f.write("-" * 30 + "\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"Parameter {i}:\n")
                f.write(f"  Original: {result.original}\n")
                f.write(f"  Translated: {result.translated}\n")
                f.write(f"  Service: {result.service_used}\n")
                f.write(f"  Confidence: {result.confidence:.2f}\n")
                f.write(f"  Translation rate: {result.translation_rate:.1f}%\n")
                f.write(f"  Processing time: {result.processing_time:.3f}s\n\n")
    
    def _create_result_summary(self, input_path: str, output_path: str, 
                             results: List[TranslationResult], successful: int, 
                             start_time: float) -> dict:
        """Create a summary of translation results."""
        processing_time = time.time() - start_time
        total_params = len(results)
        translation_rate = (successful / total_params * 100) if total_params > 0 else 0
        
        return {
            'input_file': input_path,
            'output_file': output_path,
            'success': True,
            'total_parameters': total_params,
            'translated_parameters': successful,
            'translation_rate': translation_rate,
            'processing_time': processing_time,
            'translator_stats': self.translator.get_statistics(),
            'results': results
        }
    
    def get_health_status(self) -> dict:
        """Get health status of all translation services."""
        return {
            'translator_health': self.translator.health_check(),
            'available_services': [s.value for s in self.translator.available_services],
            'cache_stats': self.translator.cache.get_statistics() if self.translator.cache else None
        }

def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Pure DAMOS File Translator - Translate as many words as possible",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Input/Output arguments
    parser.add_argument('input', nargs='+', help='Input DAMOS file(s)')
    parser.add_argument('-o', '--output', help='Output file path (auto-generated if not specified)')
    parser.add_argument('--output-dir', help='Output directory for batch processing')
    
    # Language arguments
    parser.add_argument('-l', '--language', choices=['auto', 'de', 'fr', 'it', 'es'],
                       default='auto', help='Source language (default: auto-detect)')
    
    # Translation service arguments
    parser.add_argument('--service', choices=['google', 'deepl', 'azure', 'local'],
                       default='deepl', help='Primary translation service to use (default: deepl)')
    parser.add_argument('--fallback', nargs='+', choices=['google', 'deepl', 'azure', 'local'],
                       help='Fallback translation services')
    
    # Processing arguments
    parser.add_argument('--batch', action='store_true', help='Process multiple files in batch mode')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for translation (default: 100)')
    parser.add_argument('--max-workers', type=int, default=5, help='Maximum concurrent workers (default: 5)')
    
    # Quality arguments
    parser.add_argument('--min-confidence', type=float, default=0.7,
                       help='Minimum confidence threshold (default: 0.7)')
    parser.add_argument('--no-cache', action='store_true', help='Disable translation caching')
    
    # Output arguments
    parser.add_argument('--no-report', action='store_true', help='Skip generating translation report')
    parser.add_argument('--report-format', choices=['txt', 'json', 'html'], default='txt',
                       help='Report format (default: txt)')
    
    # Logging arguments
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress non-error output')
    parser.add_argument('--log-file', help='Log to file instead of console')
    
    # Utility arguments
    parser.add_argument('--health-check', action='store_true', help='Perform health check and exit')
    parser.add_argument('--list-services', action='store_true', help='List available translation services')
    parser.add_argument('--clear-cache', action='store_true', help='Clear translation cache and exit')
    
    return parser

def main():
    """Main application entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING if args.quiet else logging.INFO
    setup_logging(level=log_level, log_file=args.log_file)
    
    logger = logging.getLogger(__name__)
    
    try:
        # Create translation configuration
        config = TranslationConfig()
        
        # Apply command line arguments to config
        if args.service:
            config.primary_service = TranslationService(args.service)
        
        if args.fallback:
            config.fallback_services = [TranslationService(s) for s in args.fallback]
        
        if args.language != 'auto':
            config.source_language = SourceLanguage(args.language)
        
        config.batch_size = args.batch_size
        config.max_concurrent_requests = args.max_workers
        config.min_confidence_threshold = args.min_confidence
        config.enable_cache = not args.no_cache
        config.generate_report = not args.no_report
        
        # Create translator instance
        translator = DamosPureTranslator(config)
        
        # Handle utility commands
        if args.health_check:
            health = translator.get_health_status()
            print("Translation Service Health Check:")
            print(f"Available services: {health['available_services']}")
            for service, status in health['translator_health'].items():
                print(f"  {service}: {status['status']}")
            return
        
        if args.list_services:
            from src.translators.factory import TranslatorFactory
            services = TranslatorFactory.get_supported_services()
            print("Supported translation services:")
            for service in services:
                print(f"  {service.value}")
            return
        
        if args.clear_cache:
            translator.translator.clear_cache()
            print("Translation cache cleared")
            return
        
        # Process files
        if args.batch or len(args.input) > 1:
            # Batch processing
            logger.info(f"Processing {len(args.input)} files in batch mode")
            results = translator.translate_batch(args.input, args.output_dir)
            
            # Print summary
            successful = sum(1 for r in results if r.get('success', False))
            print(f"\nBatch processing complete:")
            print(f"  Files processed: {len(results)}")
            print(f"  Successful: {successful}")
            print(f"  Failed: {len(results) - successful}")
            
        else:
            # Single file processing
            input_file = args.input[0]
            result = translator.translate_file(input_file, args.output, args.language)
            
            # Print summary
            print(f"\n✓ Translation successful!")
            print(f"  Input: {result['input_file']}")
            print(f"  Output: {result['output_file']}")
            print(f"  Parameters translated: {result['translated_parameters']}/{result['total_parameters']} ({result['translation_rate']:.1f}%)")
            print(f"  Processing time: {result['processing_time']:.2f} seconds")
            
            if result['translator_stats']:
                stats = result['translator_stats']
                print(f"  Service usage: {stats.get('service_usage', {})}")
                if 'cache_hit_rate' in stats:
                    print(f"  Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    
    except KeyboardInterrupt:
        logger.info("Translation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
