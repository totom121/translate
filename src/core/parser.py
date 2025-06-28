"""
DAMOS file parser for extracting translatable content.
"""

import re
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

class DamosParser:
    """
    Parser for DAMOS files that extracts parameters and descriptions for translation.
    
    DAMOS files contain automotive calibration data with German technical descriptions
    that need to be translated to English while preserving the file structure.
    """
    
    def __init__(self):
        """Initialize DAMOS parser."""
        self.logger = logging.getLogger(__name__)
        
        # DAMOS file patterns
        self.parameter_pattern = re.compile(
            r'^(\d+),\s*/SPZ,\s*([A-Z0-9_]+),\s*\{([^}]*)\},\s*(\d+),\s*(\$[0-9A-Fa-f]+),\s*(\$[0-9A-Fa-f]+).*$',
            re.MULTILINE
        )
        
        # Additional patterns for different DAMOS formats
        self.alternative_patterns = [
            # Pattern for parameters with different formatting
            re.compile(r'^(\d+),\s*/SPZ,\s*([A-Z0-9_]+),\s*\{([^}]*)\}.*$', re.MULTILINE),
            # Pattern for other parameter types
            re.compile(r'^(\d+),\s*/([A-Z]+),\s*([A-Z0-9_]+),\s*\{([^}]*)\}.*$', re.MULTILINE),
        ]
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a DAMOS file and extract parameters with descriptions.
        
        Args:
            file_path: Path to the DAMOS file
            
        Returns:
            List of parameter dictionaries
            
        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file encoding is not supported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"DAMOS file not found: {file_path}")
        
        self.logger.info(f"Parsing DAMOS file: {file_path}")
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                self.logger.debug(f"Successfully read file with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise UnicodeDecodeError(f"Could not decode file with any supported encoding: {encodings}")
        
        # Count total lines for logging
        total_lines = len(content.splitlines())
        self.logger.info(f"Parsing DAMOS file: {file_path} ({total_lines} lines)")
        
        # Extract parameters
        parameters = self._extract_parameters(content)
        
        self.logger.info(f"Found {len(parameters)} parameters to translate")
        
        return parameters
    
    def _extract_parameters(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract parameters from DAMOS file content.
        
        Args:
            content: DAMOS file content
            
        Returns:
            List of parameter dictionaries
        """
        parameters = []
        
        # Primary pattern matching
        matches = self.parameter_pattern.finditer(content)
        
        for match in matches:
            param = {
                'line_number': match.group(1),
                'parameter_name': match.group(2),
                'description': match.group(3).strip(),
                'type': match.group(4) if len(match.groups()) >= 4 else None,
                'address1': match.group(5) if len(match.groups()) >= 5 else None,
                'address2': match.group(6) if len(match.groups()) >= 6 else None,
                'full_line': match.group(0),
                'start_pos': match.start(),
                'end_pos': match.end()
            }
            
            # Only include parameters with non-empty descriptions
            if param['description'] and param['description'].strip():
                parameters.append(param)
        
        # Try alternative patterns if primary didn't find enough
        if len(parameters) < 100:  # Threshold for "enough" parameters
            self.logger.info("Trying alternative patterns for parameter extraction")
            
            for pattern in self.alternative_patterns:
                alt_matches = pattern.finditer(content)
                
                for match in alt_matches:
                    # Check if this parameter was already found
                    param_name = match.group(2) if len(match.groups()) >= 2 else match.group(3)
                    
                    if not any(p['parameter_name'] == param_name for p in parameters):
                        param = {
                            'line_number': match.group(1),
                            'parameter_name': param_name,
                            'description': match.group(3) if len(match.groups()) >= 3 else match.group(4),
                            'type': None,
                            'address1': None,
                            'address2': None,
                            'full_line': match.group(0),
                            'start_pos': match.start(),
                            'end_pos': match.end()
                        }
                        
                        # Only include parameters with non-empty descriptions
                        if param['description'] and param['description'].strip():
                            parameters.append(param)
        
        # Sort parameters by line number for consistent processing
        parameters.sort(key=lambda x: int(x['line_number']) if x['line_number'].isdigit() else 0)
        
        return parameters
    
    def validate_damos_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate that a file is a proper DAMOS file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Dictionary with validation results
        """
        file_path = Path(file_path)
        
        validation_result = {
            'is_valid': False,
            'file_exists': file_path.exists(),
            'file_size': file_path.stat().st_size if file_path.exists() else 0,
            'encoding': None,
            'has_damos_header': False,
            'parameter_count': 0,
            'errors': []
        }
        
        if not validation_result['file_exists']:
            validation_result['errors'].append("File does not exist")
            return validation_result
        
        # Check file size
        if validation_result['file_size'] == 0:
            validation_result['errors'].append("File is empty")
            return validation_result
        
        # Try to read file
        try:
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    validation_result['encoding'] = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                validation_result['errors'].append("Could not decode file with supported encodings")
                return validation_result
            
            # Check for DAMOS header patterns
            damos_indicators = [
                'Created by ASAP2DAM',
                '/SPZ,',
                '/EPR,',
                '/EAD,',
                'DAMPAR'
            ]
            
            for indicator in damos_indicators:
                if indicator in content:
                    validation_result['has_damos_header'] = True
                    break
            
            # Count parameters
            matches = self.parameter_pattern.finditer(content)
            validation_result['parameter_count'] = len(list(matches))
            
            # Determine if valid
            validation_result['is_valid'] = (
                validation_result['has_damos_header'] and 
                validation_result['parameter_count'] > 0
            )
            
            if not validation_result['has_damos_header']:
                validation_result['errors'].append("No DAMOS header indicators found")
            
            if validation_result['parameter_count'] == 0:
                validation_result['errors'].append("No translatable parameters found")
        
        except Exception as e:
            validation_result['errors'].append(f"Error reading file: {e}")
        
        return validation_result
    
    def get_file_statistics(self, file_path: str) -> Dict[str, Any]:
        """
        Get statistics about a DAMOS file.
        
        Args:
            file_path: Path to the DAMOS file
            
        Returns:
            Dictionary with file statistics
        """
        try:
            parameters = self.parse_file(file_path)
            
            # Calculate statistics
            total_params = len(parameters)
            descriptions_with_content = sum(1 for p in parameters if p['description'].strip())
            
            # Analyze description lengths
            desc_lengths = [len(p['description']) for p in parameters if p['description'].strip()]
            avg_desc_length = sum(desc_lengths) / len(desc_lengths) if desc_lengths else 0
            
            # Count unique parameter names
            unique_names = set(p['parameter_name'] for p in parameters)
            
            # Detect likely language
            all_descriptions = ' '.join(p['description'] for p in parameters if p['description'].strip())
            likely_language = self._detect_likely_language(all_descriptions)
            
            return {
                'total_parameters': total_params,
                'parameters_with_descriptions': descriptions_with_content,
                'unique_parameter_names': len(unique_names),
                'average_description_length': avg_desc_length,
                'likely_language': likely_language,
                'file_size_bytes': Path(file_path).stat().st_size,
                'sample_descriptions': [p['description'] for p in parameters[:5] if p['description'].strip()]
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'total_parameters': 0
            }
    
    def _detect_likely_language(self, text: str) -> str:
        """
        Simple language detection for DAMOS content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Likely language code
        """
        text_lower = text.lower()
        
        # Language indicators
        language_indicators = {
            'german': ['der', 'die', 'das', 'und', 'für', 'mit', 'temperatur', 'druck', 'motor', 'steuerung'],
            'french': ['le', 'la', 'les', 'et', 'pour', 'avec', 'température', 'pression', 'moteur', 'contrôle'],
            'italian': ['il', 'la', 'lo', 'e', 'per', 'con', 'temperatura', 'pressione', 'motore', 'controllo'],
            'spanish': ['el', 'la', 'los', 'y', 'para', 'con', 'temperatura', 'presión', 'motor', 'control']
        }
        
        language_scores = {}
        
        for language, indicators in language_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            language_scores[language] = score
        
        if language_scores:
            likely_language = max(language_scores, key=language_scores.get)
            if language_scores[likely_language] > 0:
                return likely_language
        
        return 'unknown'

