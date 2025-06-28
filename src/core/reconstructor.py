"""
DAMOS file reconstructor for creating translated output files.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .translator import TranslationResult

class DamosReconstructor:
    """
    Reconstructs DAMOS files with translated descriptions while preserving
    the original file structure, formatting, and technical data.
    """
    
    def __init__(self):
        """Initialize DAMOS reconstructor."""
        self.logger = logging.getLogger(__name__)
    
    def reconstruct_file(self, input_path: str, output_path: str, 
                        parameters: List[Dict[str, Any]], 
                        translation_results: List[TranslationResult]) -> None:
        """
        Reconstruct DAMOS file with translated descriptions.
        
        Args:
            input_path: Path to original DAMOS file
            output_path: Path to output translated file
            parameters: List of parsed parameters
            translation_results: List of translation results
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            IOError: If output file cannot be written
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        self.logger.info(f"Reconstructing DAMOS file: {output_path}")
        
        # Read original file
        content = self._read_file_with_encoding(input_path)
        
        # Create translation mapping
        translation_map = self._create_translation_mapping(parameters, translation_results)
        
        # Apply translations to content
        translated_content = self._apply_translations(content, translation_map)
        
        # Write translated file
        self._write_translated_file(output_path, translated_content)
        
        # Log statistics
        translated_count = len([r for r in translation_results if r.confidence > 0.5])
        total_lines = len(content.splitlines())
        
        self.logger.info(f"Reconstruction complete: {translated_count}/{len(translation_results)} lines translated")
        self.logger.info(f"Output file: {output_path} ({total_lines} total lines)")
    
    def _read_file_with_encoding(self, file_path: Path) -> str:
        """
        Read file with automatic encoding detection.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as string
        """
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                self.logger.debug(f"Read file with encoding: {encoding}")
                return content
            except UnicodeDecodeError:
                continue
        
        raise UnicodeDecodeError(f"Could not decode file with any supported encoding: {encodings}")
    
    def _create_translation_mapping(self, parameters: List[Dict[str, Any]], 
                                  translation_results: List[TranslationResult]) -> Dict[str, str]:
        """
        Create mapping from original descriptions to translated descriptions.
        
        Args:
            parameters: List of parsed parameters
            translation_results: List of translation results
            
        Returns:
            Dictionary mapping original to translated descriptions
        """
        translation_map = {}
        
        # Create mapping based on parameter order
        result_index = 0
        
        for param in parameters:
            original_desc = param.get('description', '').strip()
            
            if original_desc and result_index < len(translation_results):
                result = translation_results[result_index]
                
                # Only use translation if confidence is reasonable
                if result.confidence > 0.3:  # Lower threshold for inclusion
                    translation_map[original_desc] = result.translated
                else:
                    # Keep original if translation confidence is too low
                    translation_map[original_desc] = original_desc
                
                result_index += 1
        
        self.logger.debug(f"Created translation mapping for {len(translation_map)} descriptions")
        return translation_map
    
    def _apply_translations(self, content: str, translation_map: Dict[str, str]) -> str:
        """
        Apply translations to file content while preserving structure.
        
        Args:
            content: Original file content
            translation_map: Mapping of original to translated descriptions
            
        Returns:
            Content with applied translations
        """
        translated_content = content
        translations_applied = 0
        
        # Apply translations in order of decreasing length to avoid partial matches
        sorted_originals = sorted(translation_map.keys(), key=len, reverse=True)
        
        for original_desc in sorted_originals:
            translated_desc = translation_map[original_desc]
            
            # Only replace if translation is different and non-empty
            if translated_desc and translated_desc != original_desc:
                # Create pattern to match the description within braces
                # This preserves the exact formatting and context
                pattern = re.escape(original_desc)
                
                # Replace all occurrences
                old_content = translated_content
                translated_content = re.sub(
                    pattern, 
                    translated_desc, 
                    translated_content,
                    flags=re.MULTILINE
                )
                
                # Count successful replacements
                if translated_content != old_content:
                    translations_applied += 1
        
        self.logger.info(f"Applied {translations_applied} translations to file content")
        return translated_content
    
    def _write_translated_file(self, output_path: Path, content: str) -> None:
        """
        Write translated content to output file.
        
        Args:
            output_path: Path to output file
            content: Translated content
        """
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with UTF-8 encoding for best compatibility
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.debug(f"Written translated file: {output_path}")
        except IOError as e:
            raise IOError(f"Failed to write output file {output_path}: {e}")
    
    def create_translation_report(self, translation_results: List[TranslationResult],
                                report_path: str, input_path: str, output_path: str,
                                additional_stats: Optional[Dict[str, Any]] = None) -> None:
        """
        Create detailed translation report.
        
        Args:
            translation_results: List of translation results
            report_path: Path to report file
            input_path: Original input file path
            output_path: Translated output file path
            additional_stats: Additional statistics to include
        """
        report_path = Path(report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("DAMOS Pure Translation Report\n")
            f.write("=" * 50 + "\n\n")
            
            # File information
            f.write(f"Input file: {input_path}\n")
            f.write(f"Output file: {output_path}\n")
            f.write(f"Report generated: {self._get_timestamp()}\n\n")
            
            # Summary statistics
            total_params = len(translation_results)
            high_confidence = sum(1 for r in translation_results if r.confidence >= 0.8)
            medium_confidence = sum(1 for r in translation_results if 0.5 <= r.confidence < 0.8)
            low_confidence = sum(1 for r in translation_results if r.confidence < 0.5)
            
            f.write("Summary Statistics:\n")
            f.write(f"  Total parameters: {total_params}\n")
            f.write(f"  High confidence (≥0.8): {high_confidence} ({high_confidence/total_params*100:.1f}%)\n")
            f.write(f"  Medium confidence (0.5-0.8): {medium_confidence} ({medium_confidence/total_params*100:.1f}%)\n")
            f.write(f"  Low confidence (<0.5): {low_confidence} ({low_confidence/total_params*100:.1f}%)\n\n")
            
            # Service usage statistics
            service_usage = {}
            for result in translation_results:
                service = result.service_used
                service_usage[service] = service_usage.get(service, 0) + 1
            
            f.write("Translation Services Used:\n")
            for service, count in sorted(service_usage.items()):
                percentage = (count / total_params * 100) if total_params > 0 else 0
                f.write(f"  {service}: {count} parameters ({percentage:.1f}%)\n")
            f.write("\n")
            
            # Translation rate statistics
            total_words = sum(r.word_count for r in translation_results)
            translated_words = sum(r.translated_words for r in translation_results)
            overall_translation_rate = (translated_words / total_words * 100) if total_words > 0 else 0
            
            f.write("Translation Coverage:\n")
            f.write(f"  Total words: {total_words}\n")
            f.write(f"  Translated words: {translated_words}\n")
            f.write(f"  Overall translation rate: {overall_translation_rate:.1f}%\n\n")
            
            # Processing time statistics
            total_time = sum(r.processing_time for r in translation_results)
            avg_time = total_time / total_params if total_params > 0 else 0
            
            f.write("Performance Statistics:\n")
            f.write(f"  Total processing time: {total_time:.2f} seconds\n")
            f.write(f"  Average time per parameter: {avg_time:.3f} seconds\n")
            f.write(f"  Parameters per second: {total_params/total_time:.1f}\n\n")
            
            # Additional statistics
            if additional_stats:
                f.write("Additional Statistics:\n")
                for key, value in additional_stats.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
            
            # Detailed translation results
            f.write("Detailed Translation Results:\n")
            f.write("-" * 40 + "\n\n")
            
            for i, result in enumerate(translation_results, 1):
                f.write(f"Parameter {i}:\n")
                f.write(f"  Original: {result.original}\n")
                f.write(f"  Translated: {result.translated}\n")
                f.write(f"  Source Language: {result.source_language}\n")
                f.write(f"  Service: {result.service_used}\n")
                f.write(f"  Confidence: {result.confidence:.3f}\n")
                f.write(f"  Translation Rate: {result.translation_rate:.1f}%\n")
                f.write(f"  Processing Time: {result.processing_time:.3f}s\n")
                f.write(f"  Word Count: {result.word_count} → {result.translated_words}\n\n")
        
        self.logger.info(f"Translation report created: {report_path}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for report."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_reconstruction(self, original_path: str, translated_path: str) -> Dict[str, Any]:
        """
        Validate that reconstruction preserved file structure.
        
        Args:
            original_path: Path to original file
            translated_path: Path to translated file
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_valid': False,
            'original_exists': Path(original_path).exists(),
            'translated_exists': Path(translated_path).exists(),
            'line_count_match': False,
            'structure_preserved': False,
            'errors': []
        }
        
        if not validation_result['original_exists']:
            validation_result['errors'].append("Original file does not exist")
            return validation_result
        
        if not validation_result['translated_exists']:
            validation_result['errors'].append("Translated file does not exist")
            return validation_result
        
        try:
            # Read both files
            original_content = self._read_file_with_encoding(Path(original_path))
            translated_content = self._read_file_with_encoding(Path(translated_path))
            
            # Check line counts
            original_lines = len(original_content.splitlines())
            translated_lines = len(translated_content.splitlines())
            validation_result['line_count_match'] = original_lines == translated_lines
            
            if not validation_result['line_count_match']:
                validation_result['errors'].append(
                    f"Line count mismatch: {original_lines} vs {translated_lines}"
                )
            
            # Check structure preservation (basic patterns)
            structure_patterns = [
                r'^\d+,\s*/SPZ,',  # Parameter lines
                r'^/[A-Z]+,',      # Header lines
                r'^\*\*\*',        # Comment lines
            ]
            
            structure_preserved = True
            for pattern in structure_patterns:
                original_matches = len(re.findall(pattern, original_content, re.MULTILINE))
                translated_matches = len(re.findall(pattern, translated_content, re.MULTILINE))
                
                if original_matches != translated_matches:
                    structure_preserved = False
                    validation_result['errors'].append(
                        f"Structure pattern mismatch for {pattern}: {original_matches} vs {translated_matches}"
                    )
            
            validation_result['structure_preserved'] = structure_preserved
            validation_result['is_valid'] = (
                validation_result['line_count_match'] and 
                validation_result['structure_preserved']
            )
        
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {e}")
        
        return validation_result

