"""
DAMOS File Parser

Parses DAMOS files to extract translatable content while preserving the exact file structure.
Handles the specific DAMOS format with headers, parameter definitions, and memory addresses.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class DamosParameter:
    """Represents a single DAMOS parameter with its components."""
    line_number: int
    full_line: str
    parameter_id: str
    parameter_name: str
    description: str
    data_type: str
    memory_address: str
    memory_address2: str
    
@dataclass
class DamosHeader:
    """Represents DAMOS file header information."""
    lines: List[str]
    version_info: str
    epr_info: str
    other_metadata: Dict[str, str]

class DamosParser:
    """
    Parser for DAMOS files that extracts translatable content while preserving structure.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Regex patterns for DAMOS file structure
        self.parameter_pattern = re.compile(
            r'^(\d+),\s*/SPZ,\s*([^,]+),\s*\{([^}]*)\},\s*(\d+),\s*(\$[0-9A-F]+),\s*(\$[0-9A-F]+)'
        )
        
        # Pattern for header lines
        self.header_patterns = {
            'version': re.compile(r'^\*\*\* Created by (.+) \*\*\*'),
            'epr': re.compile(r'^/EPR,'),
            'metadata': re.compile(r'^/([A-Z]+),')
        }
        
        # Pattern for other DAMOS directives
        self.directive_pattern = re.compile(r'^/([A-Z]+),')
        
    def parse_file(self, file_path: str) -> Dict:
        """
        Parse a DAMOS file and extract all components.
        
        Args:
            file_path: Path to the DAMOS file
            
        Returns:
            Dictionary containing parsed components
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            # Try with different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        lines = file.readlines()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Could not decode file {file_path} with any supported encoding")
        
        self.logger.info(f"Parsing DAMOS file: {file_path} ({len(lines)} lines)")
        
        header = self._parse_header(lines)
        parameters = self._parse_parameters(lines)
        structure = self._analyze_structure(lines)
        
        return {
            'header': header,
            'parameters': parameters,
            'structure': structure,
            'total_lines': len(lines),
            'original_lines': lines
        }
    
    def _parse_header(self, lines: List[str]) -> DamosHeader:
        """Extract header information from DAMOS file."""
        header_lines = []
        version_info = ""
        epr_info = ""
        metadata = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Stop at first parameter definition
            if self.parameter_pattern.match(line):
                break
                
            header_lines.append(lines[i])  # Keep original line with formatting
            
            # Extract specific header information
            if self.header_patterns['version'].match(line):
                version_info = line
            elif self.header_patterns['epr'].match(line):
                epr_info = line
            elif self.header_patterns['metadata'].match(line):
                match = self.header_patterns['metadata'].match(line)
                directive = match.group(1)
                metadata[directive] = line
        
        return DamosHeader(
            lines=header_lines,
            version_info=version_info,
            epr_info=epr_info,
            other_metadata=metadata
        )
    
    def _parse_parameters(self, lines: List[str]) -> List[DamosParameter]:
        """Extract parameter definitions from DAMOS file."""
        parameters = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip empty lines and comments
            if not line_stripped or line_stripped.startswith(';'):
                continue
                
            match = self.parameter_pattern.match(line_stripped)
            if match:
                param = DamosParameter(
                    line_number=i + 1,
                    full_line=line,
                    parameter_id=match.group(1),
                    parameter_name=match.group(2).strip(),
                    description=match.group(3).strip(),
                    data_type=match.group(4),
                    memory_address=match.group(5),
                    memory_address2=match.group(6)
                )
                parameters.append(param)
        
        self.logger.info(f"Found {len(parameters)} parameters to translate")
        return parameters
    
    def _analyze_structure(self, lines: List[str]) -> Dict:
        """Analyze the overall structure of the DAMOS file."""
        structure = {
            'header_end_line': 0,
            'parameter_start_line': 0,
            'parameter_end_line': 0,
            'total_parameters': 0,
            'directive_lines': [],
            'comment_lines': [],
            'empty_lines': []
        }
        
        parameter_found = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Track different line types
            if not line_stripped:
                structure['empty_lines'].append(i + 1)
            elif line_stripped.startswith(';'):
                structure['comment_lines'].append(i + 1)
            elif self.directive_pattern.match(line_stripped):
                structure['directive_lines'].append(i + 1)
            elif self.parameter_pattern.match(line_stripped):
                if not parameter_found:
                    structure['parameter_start_line'] = i + 1
                    structure['header_end_line'] = i
                    parameter_found = True
                structure['parameter_end_line'] = i + 1
                structure['total_parameters'] += 1
        
        return structure
    
    def extract_translatable_content(self, parsed_data: Dict) -> List[Tuple[int, str, str]]:
        """
        Extract only the translatable content (descriptions) from parsed data.
        
        Returns:
            List of tuples: (line_number, parameter_name, description)
        """
        translatable = []
        
        for param in parsed_data['parameters']:
            if param.description.strip():  # Only include non-empty descriptions
                translatable.append((
                    param.line_number,
                    param.parameter_name,
                    param.description
                ))
        
        return translatable
    
    def get_file_encoding(self, file_path: str) -> str:
        """
        Detect the encoding of a DAMOS file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding string
        """
        import chardet
        
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Read first 10KB for detection
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception:
            return 'utf-8'
    
    def validate_damos_format(self, file_path: str) -> bool:
        """
        Validate if a file appears to be a valid DAMOS file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file appears to be valid DAMOS format
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                first_lines = [file.readline().strip() for _ in range(10)]
            
            # Check for DAMOS signature patterns
            has_version = any('Created by' in line and 'ASAP2DAM' in line for line in first_lines)
            has_epr = any(line.startswith('/EPR,') for line in first_lines)
            has_parameters = False
            
            # Check for parameter patterns in first 100 lines
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for i, line in enumerate(file):
                    if i > 100:
                        break
                    if self.parameter_pattern.match(line.strip()):
                        has_parameters = True
                        break
            
            return has_version or has_epr or has_parameters
            
        except Exception as e:
            self.logger.error(f"Error validating DAMOS format: {e}")
            return False

