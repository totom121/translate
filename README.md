# DAMOS File Translator

A comprehensive translator for DAMOS (Data Acquisition and Measurement Object Specification) files used in automotive ECU development. This tool translates automotive terminology from any language to English while preserving the exact file structure and format compatibility with automotive development tools.

## Features

🚗 **Automotive Context Awareness**: Specialized translation engine with extensive automotive terminology dictionaries

🌍 **Multi-Language Support**: Auto-detects source language and supports German, French, Italian, Spanish, and more

📁 **Format Preservation**: Maintains exact DAMOS file structure, memory addresses, and formatting

⚡ **Batch Processing**: Translate multiple files or entire directories efficiently

📊 **Detailed Reporting**: Comprehensive translation reports with statistics and quality metrics

🔍 **Validation Tools**: Built-in validation to ensure translated files maintain structural integrity

## Installation

### Prerequisites

- Python 3.7 or higher
- Optional: `chardet` for better file encoding detection

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd translate

# Install optional dependencies
pip install chardet

# Make the translator executable
chmod +x translate_damos.py
```

## Usage

### Command Line Interface

#### Translate a Single File

```bash
# Auto-detect language and translate
python translate_damos.py your_file.dam

# Specify output file
python translate_damos.py your_file.dam -o translated_file.dam

# Manual language selection
python translate_damos.py your_file.dam -l german -o translated_file.dam
python translate_damos.py your_file.dam -l french -o translated_file.dam
python translate_damos.py your_file.dam -l italian -o translated_file.dam
python translate_damos.py your_file.dam -l spanish -o translated_file.dam

# Interactive language selection
python translate_damos.py your_file.dam --interactive

# List all supported languages
python translate_damos.py --list-languages
```

#### Batch Translation

```bash
# Translate all .dam files in a directory
python translate_damos.py ./damos_files --batch -o ./translated_files

# Use custom file pattern
python translate_damos.py ./damos_files --batch --pattern "*.damos" -o ./output
```

#### Validation

```bash
# Validate a translated file against the original
python translate_damos.py original.dam --validate translated.dam
```

### Python API

```python
from damos_translator import DamosTranslatorApp

# Initialize the translator
app = DamosTranslatorApp()

# Translate a single file
result = app.translate_file(
    input_path="your_file.dam",
    output_path="translated_file.dam",
    source_language="german",  # Optional: auto-detected if not specified
    create_report=True
)

if result['success']:
    print(f"Translation successful!")
    print(f"Translated {result['statistics']['translated_parameters']} parameters")
else:
    print(f"Translation failed: {result['error']}")

# Batch processing
results = app.translate_batch(
    input_directory="./damos_files",
    output_directory="./translated_files",
    source_language="german"
)
```

## Supported Languages

### Currently Supported Source Languages

- **German** 🇩🇪 - Comprehensive automotive dictionary with 500+ terms
- **French** 🇫🇷 - Basic automotive terminology support
- **Italian** ���🇹 - Basic automotive terminology support  
- **Spanish** 🇪🇸 - Basic automotive terminology support

### Target Language

- **English** 🇺🇸 - All translations are to English

### Manual Language Selection

The translator supports multiple ways to specify the source language:

1. **Auto-Detection** (default): `python translate_damos.py file.dam`
2. **Manual Selection**: `python translate_damos.py file.dam -l german`
3. **Interactive Mode**: `python translate_damos.py file.dam --interactive`
4. **List Languages**: `python translate_damos.py --list-languages`

#### Interactive Mode Example

```bash
$ python translate_damos.py your_file.dam --interactive

🌍 Interactive Language Selection
========================================

Available languages:
  1. 🔍 Auto-Detection
     Let the system detect the language automatically

  2. 🇩🇪 German
     Comprehensive automotive dictionary (500+ terms)

  3. 🇫🇷 French
     Comprehensive automotive dictionary (200+ terms)

  4. 🇮🇹 Italian
     Comprehensive automotive dictionary (200+ terms)

  5. 🇪🇸 Spanish
     Comprehensive automotive dictionary (200+ terms)

Select language (1-5) or 'q' to quit: 2

✅ Selected: 🇩🇪 German
   Comprehensive automotive dictionary (500+ terms)

📚 Sample automotive terms in German:
   • Abgastemperatur → exhaust gas temperature
   • Katalysator → catalytic converter
   • Lambdasonde → lambda sensor
   • Drosselklappe → throttle valve
   • Motortemperatur → engine temperature

📊 Dictionary contains 500+ total entries

Confirm selection? (y/n): y
```

## Automotive Terminology

The translator includes specialized dictionaries for automotive terms:

### German Automotive Terms (Examples)

| German | English |
|--------|---------|
| Abgastemperatur | exhaust gas temperature |
| Katalysator | catalytic converter |
| Lambdasonde | lambda sensor |
| Drosselklappe | throttle valve |
| Motortemperatur | engine temperature |
| Kraftstoffpumpe | fuel pump |
| Leerlaufregelung | idle speed control |
| Zündzeitpunkt | ignition timing |
| Klopfregelung | knock control |
| Abgasrückführung | exhaust gas recirculation |

### Common Automotive Phrases

| German | English |
|--------|---------|
| hinter Katalysator | downstream catalytic converter |
| vor Katalysator | upstream catalytic converter |
| bei Kaltstart | during cold start |
| oberer Grenzwert | upper limit |
| unterer Grenzwert | lower limit |

## File Format Support

### DAMOS File Structure

The translator preserves all DAMOS file components:

- **Header Information**: Version, EPR data, metadata
- **Parameter Definitions**: `/SPZ` entries with descriptions
- **Memory Addresses**: Exact preservation of memory locations
- **Data Types**: All numeric and configuration data
- **Comments and Directives**: Non-translatable content preserved

### Example Translation

**Original (German):**
```
72, /SPZ, ABGMSIGH, {Abgastemperaturschwelle für Signalunterbrechung mit Ri-Diagnose hinter KAT}, 1, $818760, $818760
```

**Translated (English):**
```
72, /SPZ, ABGMSIGH, {exhaust gas temperature threshold for signal interruption with Ri diagnosis downstream catalytic converter}, 1, $818760, $818760
```

## Translation Quality

### Quality Metrics

- **Automotive Term Coverage**: Percentage of automotive terms successfully translated
- **Structure Preservation**: Validation that file format remains intact
- **Translation Confidence**: Confidence score based on dictionary coverage
- **File Integrity**: Verification of parameter counts and memory addresses

### Quality Assurance

1. **Dictionary-First Approach**: Prioritizes automotive-specific translations
2. **Context Awareness**: Understands automotive terminology relationships
3. **Format Validation**: Ensures output files maintain DAMOS compatibility
4. **Comprehensive Testing**: Validated against real automotive DAMOS files

## Examples

### Example 1: German ECU Parameters

**Input File**: `me7_5_german.dam`
```
48, /SPZ, A0, {Übertragungsfunktionskoeffizient}, 1, $816010, $816010
72, /SPZ, ABGMSIGH, {Abgastemperaturschwelle für Signalunterbrechung}, 1, $818760, $818760
```

**Command**:
```bash
python translate_damos.py me7_5_german.dam -o me7_5_english.dam
```

**Output File**: `me7_5_english.dam`
```
48, /SPZ, A0, {transfer function coefficient}, 1, $816010, $816010
72, /SPZ, ABGMSIGH, {exhaust gas temperature threshold for signal interruption}, 1, $818760, $818760
```

### Example 2: Batch Processing

**Directory Structure**:
```
damos_files/
├── ecu1_german.dam
├── ecu2_german.dam
└── ecu3_german.dam
```

**Command**:
```bash
python translate_damos.py damos_files --batch -o translated_files
```

**Result**:
```
translated_files/
├── ecu1_german_translated.dam
├── ecu2_german_translated.dam
├── ecu3_german_translated.dam
├── batch_translation_summary.txt
└── individual translation reports...
```

## Advanced Features

### Custom Terminology

Add custom automotive terms at runtime:

```python
from damos_translator import AutomotiveTranslator

translator = AutomotiveTranslator()
translator.add_custom_translation('german', 'Sonderterm', 'special term')
```

### Translation Statistics

```python
result = app.translate_file("input.dam", "output.dam")
stats = result['statistics']

print(f"Parameters processed: {stats['total_parameters']}")
print(f"Translation rate: {stats['translation_rate']*100:.1f}%")
print(f"Processing time: {stats['processing_time']:.2f} seconds")
```

### Language Detection

```python
from damos_translator import LanguageDetector

detector = LanguageDetector()
language, confidence = detector.detect_language("Abgastemperatur für Katalysator")
print(f"Detected: {language} (confidence: {confidence:.2f})")
```

## Testing

### Run Integration Tests

Test the translator with the included German DAMOS file:

```bash
python tests/test_integration.py
```

### Test with Your Own Files

```bash
# Validate translation quality
python translate_damos.py your_original.dam --validate your_translated.dam

# Test language detection
python -c "
from damos_translator import LanguageDetector
detector = LanguageDetector()
with open('your_file.dam', 'r') as f:
    content = f.read()
lang, conf = detector.detect_language(content[:1000])
print(f'Detected: {lang} ({conf:.2f})')
"
```

## Troubleshooting

### Common Issues

1. **File Encoding Problems**
   ```bash
   pip install chardet  # Improves encoding detection
   ```

2. **Low Translation Quality**
   - Check if source language is supported
   - Verify automotive terminology in dictionaries
   - Use manual language specification: `-l german`

3. **Structure Validation Failures**
   - Ensure input file is valid DAMOS format
   - Check for file corruption
   - Validate with original automotive tools

### Debug Mode

Enable detailed logging:

```bash
python translate_damos.py your_file.dam --log-level DEBUG
```

### Performance Optimization

For large files or batch processing:

```bash
# Process files in smaller batches
python translate_damos.py large_directory --batch --pattern "*.dam"

# Monitor memory usage
python -c "
import psutil
import os
print(f'Memory usage: {psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024:.1f} MB')
"
```

## Contributing

### Adding New Languages

1. Create language dictionary: `damos_translator/dictionaries/[language]_automotive.json`
2. Add language patterns to `language_detector.py`
3. Test with sample files
4. Submit pull request

### Expanding Automotive Dictionaries

Automotive terminology contributions are welcome! Please ensure:

- Terms are technically accurate
- Translations are industry-standard
- Context is preserved (e.g., "Bank 1" vs "Bank 2")

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:

1. Check existing issues in the repository
2. Create detailed bug reports with sample files
3. Include DAMOS file format specifications when possible
4. Provide automotive context for terminology questions

## Acknowledgments

- Automotive terminology sourced from industry standards
- DAMOS format specifications from automotive development community
- Testing performed with real ECU development files

---

**Note**: This translator is designed for automotive development professionals working with DAMOS files. Always validate translated files with your automotive development tools before use in production environments.
