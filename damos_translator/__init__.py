"""
DAMOS File Translator

A comprehensive translator for DAMOS (Data Acquisition and Measurement Object Specification) files
used in automotive ECU development. Translates automotive terminology from any language to English
while preserving the exact file structure and format.

Author: Codegen AI
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Codegen AI"

from .parser import DamosParser
from .translator import AutomotiveTranslator
from .reconstructor import DamosReconstructor
from .main import DamosTranslatorApp

__all__ = [
    'DamosParser',
    'AutomotiveTranslator', 
    'DamosReconstructor',
    'DamosTranslatorApp'
]

