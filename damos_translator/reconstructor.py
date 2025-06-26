"""
DAMOS File Reconstructor

Rebuilds DAMOS files with translated content while preserving the exact file structure,
formatting, and compatibility with automotive development tools.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from pathlib import Path

class DamosReconstructor:
    """
    Reconstructs DAMOS files with translated descriptions while preserving format integrity.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pattern for parameter lines that need translation
        self.parameter_pattern = re.compile(
            r'^(\d+),\s*/SPZ,\s*([^,]+),\s*\{([^}]*)\},\s*(.+)$'
        )
    
    def reconstruct_file(self, parsed_data: Dict, translation_results: List[Dict[str, Any]], 
                        output_path: str, preserve_encoding: bool = True) -> Dict[str, Any]:
        """
        Reconstruct a DAMOS file with translated descriptions.
        
        Args:
            parsed_data: Original parsed DAMOS data
            translation_results: List of translation results
            output_path: Path for the output file
            preserve_encoding: Whether to preserve original encoding
            
        Returns:
            Reconstruction statistics and metadata
        """
        self.logger.info(f"Reconstructing DAMOS file: {output_path}")
        
        # Create translation lookup
        translation_lookup = {}
        for i, result in enumerate(translation_results):
            if i < len(parsed_data['parameters']):
                param = parsed_data['parameters'][i]
                translation_lookup[param.line_number] = result['translated']
        
        # Process original lines
        output_lines = []
        lines_processed = 0
        lines_translated = 0
        
        for i, original_line in enumerate(parsed_data['original_lines']):
            line_number = i + 1
            
            if line_number in translation_lookup:
                # This line contains a parameter that needs translation
                translated_line = self._translate_parameter_line(
                    original_line, translation_lookup[line_number]
                )
                output_lines.append(translated_line)
                
                if translated_line != original_line:
                    lines_translated += 1
            else:
                # Keep original line unchanged
                output_lines.append(original_line)
            
            lines_processed += 1
        
        # Write output file
        encoding = 'utf-8'  # Default encoding
        if preserve_encoding:
            # Try to detect original encoding
            encoding = self._detect_file_encoding(parsed_data.get('original_file_path', ''))
        
        try:
            with open(output_path, 'w', encoding=encoding, newline='') as f:
                f.writelines(output_lines)
        except UnicodeEncodeError:
            # Fallback to UTF-8 if original encoding fails
            self.logger.warning(f"Failed to write with {encoding}, falling back to UTF-8")
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                f.writelines(output_lines)
            encoding = 'utf-8'
        
        # Validate output file
        validation_result = self._validate_output_file(output_path, parsed_data)
        
        stats = {
            'output_path': output_path,
            'total_lines': lines_processed,
            'lines_translated': lines_translated,
            'translation_rate': lines_translated / lines_processed if lines_processed > 0 else 0,
            'output_encoding': encoding,
            'file_size_bytes': Path(output_path).stat().st_size,
            'validation_passed': validation_result['valid'],
            'validation_details': validation_result
        }
        
        self.logger.info(f"Reconstruction complete: {lines_translated}/{lines_processed} lines translated")
        return stats
    
    def _translate_parameter_line(self, original_line: str, translated_description: str) -> str:
        """
        Replace the description in a parameter line while preserving all other formatting.
        
        Args:
            original_line: Original parameter line
            translated_description: New translated description
            
        Returns:
            Line with translated description
        """
        match = self.parameter_pattern.match(original_line.strip())
        if not match:
            # If line doesn't match expected pattern, return original
            return original_line
        
        # Extract components
        param_id = match.group(1)
        param_name = match.group(2)
        original_desc = match.group(3)
        rest_of_line = match.group(4)
        
        # Preserve original line formatting (leading/trailing whitespace)
        leading_whitespace = original_line[:len(original_line) - len(original_line.lstrip())]
        trailing_whitespace = original_line[len(original_line.rstrip()):]
        
        # Reconstruct line with translated description
        new_line = f"{leading_whitespace}{param_id}, /SPZ, {param_name}, {{{translated_description}}}, {rest_of_line}{trailing_whitespace}"
        
        return new_line
    
    def _detect_file_encoding(self, file_path: str) -> str:
        """
        Detect the encoding of the original file.
        
        Args:
            file_path: Path to the original file
            
        Returns:
            Detected encoding string
        """
        if not file_path or not Path(file_path).exists():
            return 'utf-8'
        
        try:
            import chardet
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except ImportError:
            self.logger.warning("chardet not available, using utf-8")
            return 'utf-8'
        except Exception as e:
            self.logger.warning(f"Encoding detection failed: {e}, using utf-8")
            return 'utf-8'
    
    def _validate_output_file(self, output_path: str, original_parsed_data: Dict) -> Dict[str, Any]:
        """
        Validate that the output file maintains structural integrity.
        
        Args:
            output_path: Path to the output file
            original_parsed_data: Original parsed data for comparison
            
        Returns:
            Validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'line_count_match': False,
            'structure_preserved': False,
            'parameter_count_match': False
        }
        
        try:
            # Read output file
            with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                output_lines = f.readlines()
            
            # Check line count
            original_line_count = len(original_parsed_data['original_lines'])
            output_line_count = len(output_lines)
            
            validation['line_count_match'] = (original_line_count == output_line_count)
            if not validation['line_count_match']:
                validation['errors'].append(
                    f"Line count mismatch: original={original_line_count}, output={output_line_count}"
                )
                validation['valid'] = False
            
            # Check parameter structure
            output_param_count = 0
            for line in output_lines:
                if self.parameter_pattern.match(line.strip()):
                    output_param_count += 1
            
            original_param_count = len(original_parsed_data['parameters'])
            validation['parameter_count_match'] = (original_param_count == output_param_count)
            
            if not validation['parameter_count_match']:
                validation['errors'].append(
                    f"Parameter count mismatch: original={original_param_count}, output={output_param_count}"
                )
                validation['valid'] = False
            
            # Check header preservation
            header_lines = original_parsed_data['header'].lines
            if len(output_lines) >= len(header_lines):
                header_preserved = True
                for i, header_line in enumerate(header_lines):
                    if i < len(output_lines):
                        # Check if header structure is preserved (allowing for minor formatting differences)
                        if header_line.strip() and output_lines[i].strip():
                            if not self._lines_structurally_similar(header_line, output_lines[i]):
                                header_preserved = False
                                break
                
                validation['structure_preserved'] = header_preserved
                if not header_preserved:
                    validation['warnings'].append("Header structure may have been modified")
            
            # Check for encoding issues
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError:
                validation['warnings'].append("Output file may have encoding issues")
            
        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Validation failed: {str(e)}")
        
        return validation
    
    def _lines_structurally_similar(self, line1: str, line2: str) -> bool:
        """
        Check if two lines have similar structure (ignoring minor formatting differences).
        
        Args:
            line1: First line to compare
            line2: Second line to compare
            
        Returns:
            True if lines are structurally similar
        """
        # Remove extra whitespace and compare
        clean1 = ' '.join(line1.split())
        clean2 = ' '.join(line2.split())
        
        # For header lines, check if they start with the same directive
        if line1.strip().startswith('/') and line2.strip().startswith('/'):
            directive1 = line1.strip().split(',')[0] if ',' in line1 else line1.strip()
            directive2 = line2.strip().split(',')[0] if ',' in line2 else line2.strip()
            return directive1 == directive2
        
        # For other lines, check if they're exactly the same after cleaning
        return clean1 == clean2
    
    def create_translation_report(self, parsed_data: Dict, translation_results: List[Dict[str, Any]], 
                                output_path: str) -> str:
        """
        Create a detailed translation report.
        
        Args:
            parsed_data: Original parsed data
            translation_results: Translation results
            output_path: Path for the report file
            
        Returns:
            Path to the created report file
        """
        report_path = output_path.replace('.dam', '_translation_report.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("DAMOS Translation Report\n")
            f.write("=" * 50 + "\n\n")
            
            # Summary statistics
            total_params = len(translation_results)
            translated_params = sum(1 for r in translation_results if r['translated'] != r['original'])
            
            f.write(f"Total parameters: {total_params}\n")
            f.write(f"Translated parameters: {translated_params}\n")
            f.write(f"Translation rate: {translated_params/total_params*100:.1f}%\n\n")
            
            # Language detection summary
            languages = {}
            for result in translation_results:
                lang = result['source_language']
                languages[lang] = languages.get(lang, 0) + 1
            
            f.write("Detected languages:\n")
            for lang, count in languages.items():
                f.write(f"  {lang}: {count} parameters ({count/total_params*100:.1f}%)\n")
            f.write("\n")
            
            # Translation method summary
            methods = {}
            for result in translation_results:
                method = result['method']
                methods[method] = methods.get(method, 0) + 1
            
            f.write("Translation methods:\n")
            for method, count in methods.items():
                f.write(f"  {method}: {count} parameters ({count/total_params*100:.1f}%)\n")
            f.write("\n")
            
            # Detailed translations
            f.write("Detailed Translations:\n")
            f.write("-" * 30 + "\n\n")
            
            for i, result in enumerate(translation_results):
                if result['translated'] != result['original']:
                    param = parsed_data['parameters'][i]
                    f.write(f"Parameter {param.parameter_id}: {param.parameter_name}\n")
                    f.write(f"  Original ({result['source_language']}): {result['original']}\n")
                    f.write(f"  Translated: {result['translated']}\n")
                    f.write(f"  Method: {result['method']}\n")
                    f.write(f"  Confidence: {result['confidence']:.2f}\n")
                    f.write(f"  Automotive terms: {result['automotive_terms_found']}\n")
                    f.write("\n")
        
        self.logger.info(f"Translation report created: {report_path}")
        return report_path
    
    def compare_files(self, original_path: str, translated_path: str) -> Dict[str, Any]:
        """
        Compare original and translated DAMOS files.
        
        Args:
            original_path: Path to original file
            translated_path: Path to translated file
            
        Returns:
            Comparison results
        """
        comparison = {
            'files_exist': False,
            'size_difference': 0,
            'line_differences': [],
            'structural_changes': [],
            'encoding_differences': False
        }
        
        try:
            original_file = Path(original_path)
            translated_file = Path(translated_path)
            
            if not (original_file.exists() and translated_file.exists()):
                comparison['files_exist'] = False
                return comparison
            
            comparison['files_exist'] = True
            comparison['size_difference'] = translated_file.stat().st_size - original_file.stat().st_size
            
            # Read both files
            with open(original_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_lines = f.readlines()
            
            with open(translated_path, 'r', encoding='utf-8', errors='ignore') as f:
                translated_lines = f.readlines()
            
            # Compare line by line
            max_lines = max(len(original_lines), len(translated_lines))
            for i in range(max_lines):
                orig_line = original_lines[i] if i < len(original_lines) else ""
                trans_line = translated_lines[i] if i < len(translated_lines) else ""
                
                if orig_line != trans_line:
                    comparison['line_differences'].append({
                        'line_number': i + 1,
                        'original': orig_line.strip(),
                        'translated': trans_line.strip()
                    })
            
        except Exception as e:
            comparison['error'] = str(e)
        
        return comparison

