"""
Comprehensive German-English Dictionary

Provides extensive German-to-English translation coverage including:
- Basic German vocabulary
- Technical automotive terms
- Common prepositions and articles
- Compound word components
- Grammar particles
"""

class ComprehensiveGermanDict:
    """
    Comprehensive German-English dictionary for technical automotive translation.
    """
    
    def __init__(self):
        self.dictionary = {
            # Articles and pronouns
            'der': 'the', 'die': 'the', 'das': 'the', 'den': 'the', 'dem': 'the', 'des': 'of the',
            'ein': 'a', 'eine': 'a', 'einen': 'a', 'einem': 'a', 'einer': 'a', 'eines': 'a',
            'und': 'and', 'oder': 'or', 'aber': 'but', 'wenn': 'if', 'dann': 'then',
            'sich': 'itself', 'er': 'he', 'sie': 'she', 'es': 'it', 'wir': 'we', 'ihr': 'you', 'sie': 'they',
            
            # Prepositions and conjunctions
            'für': 'for', 'fr': 'for',  # Common abbreviation
            'mit': 'with', 'bei': 'at', 'von': 'from', 'zu': 'to', 'nach': 'after',
            'vor': 'before', 'über': 'above', 'unter': 'under', 'zwischen': 'between',
            'während': 'during', 'ohne': 'without', 'gegen': 'against', 'durch': 'through',
            'um': 'around', 'an': 'at', 'auf': 'on', 'in': 'in', 'aus': 'from',
            'bis': 'until', 'seit': 'since', 'ab': 'from', 'hinter': 'behind',
            'neben': 'beside', 'innerhalb': 'within', 'außerhalb': 'outside',
            'entlang': 'along', 'gegenüber': 'opposite', 'trotz': 'despite',
            'wegen': 'because of', 'statt': 'instead of', 'anstatt': 'instead of',
            'im': 'in the', 'am': 'at the', 'zum': 'to the', 'zur': 'to the',
            'beim': 'at the', 'vom': 'from the', 'ins': 'into the', 'ans': 'to the',
            
            # Basic verbs
            'ist': 'is', 'sind': 'are', 'war': 'was', 'waren': 'were', 'wird': 'will be',
            'werden': 'become', 'haben': 'have', 'hat': 'has', 'hatte': 'had', 'hatten': 'had',
            'sein': 'be', 'kann': 'can', 'könnte': 'could', 'soll': 'should', 'muss': 'must',
            'darf': 'may', 'will': 'wants', 'möchte': 'would like', 'lassen': 'let',
            'machen': 'make', 'tun': 'do', 'gehen': 'go', 'kommen': 'come', 'sehen': 'see',
            'wissen': 'know', 'denken': 'think', 'sagen': 'say', 'sprechen': 'speak',
            'hören': 'hear', 'fühlen': 'feel', 'nehmen': 'take', 'geben': 'give',
            'bringen': 'bring', 'halten': 'hold', 'stehen': 'stand', 'liegen': 'lie',
            'setzen': 'set', 'stellen': 'place', 'legen': 'lay', 'ziehen': 'pull',
            'drücken': 'push', 'öffnen': 'open', 'schließen': 'close', 'beginnen': 'begin',
            'enden': 'end', 'stoppen': 'stop', 'starten': 'start', 'fahren': 'drive',
            'laufen': 'run', 'arbeiten': 'work', 'funktionieren': 'function',
            'erreichen': 'reach', 'erkennen': 'recognize', 'erkennung': 'recognition',
            'überwachen': 'monitor', 'kontrollieren': 'control', 'regeln': 'regulate',
            'messen': 'measure', 'prüfen': 'check', 'testen': 'test', 'kalibrieren': 'calibrate',
            
            # Basic adjectives and adverbs
            'gut': 'good', 'schlecht': 'bad', 'groß': 'large', 'klein': 'small',
            'hoch': 'high', 'niedrig': 'low', 'lang': 'long', 'kurz': 'short',
            'breit': 'wide', 'schmal': 'narrow', 'dick': 'thick', 'dünn': 'thin',
            'stark': 'strong', 'schwach': 'weak', 'schnell': 'fast', 'langsam': 'slow',
            'neu': 'new', 'alt': 'old', 'jung': 'young', 'früh': 'early', 'spät': 'late',
            'richtig': 'correct', 'falsch': 'wrong', 'wahr': 'true', 'sicher': 'safe',
            'gefährlich': 'dangerous', 'wichtig': 'important', 'notwendig': 'necessary',
            'möglich': 'possible', 'unmöglich': 'impossible', 'einfach': 'simple',
            'schwierig': 'difficult', 'leicht': 'light', 'schwer': 'heavy',
            'warm': 'warm', 'kalt': 'cold', 'heiß': 'hot', 'kühl': 'cool',
            'trocken': 'dry', 'nass': 'wet', 'sauber': 'clean', 'schmutzig': 'dirty',
            'leer': 'empty', 'voll': 'full', 'offen': 'open', 'geschlossen': 'closed',
            'aktiv': 'active', 'passiv': 'passive', 'automatisch': 'automatic',
            'manuell': 'manual', 'elektrisch': 'electric', 'mechanisch': 'mechanical',
            'digital': 'digital', 'analog': 'analog', 'normal': 'normal',
            'maximal': 'maximum', 'minimal': 'minimum', 'optimal': 'optimal',
            'konstant': 'constant', 'variabel': 'variable', 'stabil': 'stable',
            'instabil': 'unstable', 'linear': 'linear', 'dynamisch': 'dynamic',
            'statisch': 'static', 'kontinuierlich': 'continuous', 'diskret': 'discrete',
            
            # Numbers and quantities
            'null': 'zero', 'eins': 'one', 'zwei': 'two', 'drei': 'three', 'vier': 'four',
            'fünf': 'five', 'sechs': 'six', 'sieben': 'seven', 'acht': 'eight', 'neun': 'nine',
            'zehn': 'ten', 'hundert': 'hundred', 'tausend': 'thousand', 'million': 'million',
            'erste': 'first', 'zweite': 'second', 'dritte': 'third', 'letzte': 'last',
            'alle': 'all', 'jede': 'each', 'einige': 'some', 'viele': 'many', 'wenige': 'few',
            'mehr': 'more', 'weniger': 'less', 'genug': 'enough', 'zu viel': 'too much',
            'anzahl': 'number', 'menge': 'amount', 'summe': 'sum', 'total': 'total',
            
            # Technical terms - General
            'wert': 'value', 'parameter': 'parameter', 'variable': 'variable',
            'konstante': 'constant', 'faktor': 'factor', 'koeffizient': 'coefficient',
            'verhältnis': 'ratio', 'prozent': 'percent', 'grad': 'degree',
            'einheit': 'unit', 'maß': 'measure', 'größe': 'size', 'dimension': 'dimension',
            'bereich': 'range', 'grenze': 'limit', 'schwelle': 'threshold',
            'minimum': 'minimum', 'maximum': 'maximum', 'durchschnitt': 'average',
            'mittelwert': 'mean value', 'median': 'median', 'standardabweichung': 'standard deviation',
            'toleranz': 'tolerance', 'abweichung': 'deviation', 'fehler': 'error',
            'genauigkeit': 'accuracy', 'präzision': 'precision', 'auflösung': 'resolution',
            'kalibrierung': 'calibration', 'justierung': 'adjustment', 'einstellung': 'setting',
            'konfiguration': 'configuration', 'parameter': 'parameter', 'option': 'option',
            'modus': 'mode', 'zustand': 'state', 'status': 'status', 'bedingung': 'condition',
            'kriterium': 'criterion', 'regel': 'rule', 'vorschrift': 'regulation',
            'norm': 'standard', 'spezifikation': 'specification', 'anforderung': 'requirement',
            
            # Technical terms - Measurement and Control
            'messung': 'measurement', 'sensor': 'sensor', 'detektor': 'detector',
            'fühler': 'sensor', 'geber': 'transmitter', 'wandler': 'converter',
            'verstärker': 'amplifier', 'filter': 'filter', 'regler': 'controller',
            'steuerung': 'control', 'regelung': 'regulation', 'überwachung': 'monitoring',
            'diagnose': 'diagnosis', 'prüfung': 'test', 'kontrolle': 'control',
            'inspektion': 'inspection', 'wartung': 'maintenance', 'service': 'service',
            'reparatur': 'repair', 'austausch': 'replacement', 'erneuerung': 'renewal',
            'signal': 'signal', 'impuls': 'pulse', 'frequenz': 'frequency',
            'amplitude': 'amplitude', 'phase': 'phase', 'spannung': 'voltage',
            'strom': 'current', 'leistung': 'power', 'energie': 'energy',
            'widerstand': 'resistance', 'kapazität': 'capacity', 'induktivität': 'inductance',
            
            # Technical terms - Time and Process
            'zeit': 'time', 'dauer': 'duration', 'periode': 'period', 'zyklus': 'cycle',
            'intervall': 'interval', 'verzögerung': 'delay', 'pause': 'pause',
            'start': 'start', 'stopp': 'stop', 'ende': 'end', 'beginn': 'beginning',
            'initialisierung': 'initialization', 'reset': 'reset', 'neustart': 'restart',
            'aktivierung': 'activation', 'deaktivierung': 'deactivation',
            'einschaltung': 'switch-on', 'ausschaltung': 'switch-off',
            'betrieb': 'operation', 'lauf': 'run', 'stillstand': 'standstill',
            'prozess': 'process', 'verfahren': 'procedure', 'methode': 'method',
            'algorithmus': 'algorithm', 'berechnung': 'calculation', 'rechnung': 'calculation',
            'simulation': 'simulation', 'modell': 'model', 'system': 'system',
            'komponente': 'component', 'element': 'element', 'teil': 'part',
            'baugruppe': 'assembly', 'modul': 'module', 'einheit': 'unit',
            
            # Automotive specific - Engine
            'motor': 'engine', 'triebwerk': 'engine', 'antrieb': 'drive',
            'zylinder': 'cylinder', 'kolben': 'piston', 'pleuel': 'connecting rod',
            'kurbelwelle': 'crankshaft', 'nockenwelle': 'camshaft', 'ventil': 'valve',
            'einlassventil': 'intake valve', 'auslassventil': 'exhaust valve',
            'zündkerze': 'spark plug', 'glühkerze': 'glow plug', 'zündung': 'ignition',
            'verbrennung': 'combustion', 'kraftstoff': 'fuel', 'benzin': 'gasoline',
            'diesel': 'diesel', 'öl': 'oil', 'schmierung': 'lubrication',
            'kühlung': 'cooling', 'kühlmittel': 'coolant', 'thermostat': 'thermostat',
            'wasserpumpe': 'water pump', 'ölpumpe': 'oil pump', 'kraftstoffpumpe': 'fuel pump',
            'einspritzung': 'injection', 'injektor': 'injector', 'düse': 'nozzle',
            'vergaser': 'carburetor', 'drosselklappe': 'throttle valve',
            'luftfilter': 'air filter', 'kraftstofffilter': 'fuel filter', 'ölfilter': 'oil filter',
            'turbolader': 'turbocharger', 'kompressor': 'compressor', 'lader': 'charger',
            'ladeluftkühler': 'intercooler', 'ansaugkrümmer': 'intake manifold',
            'abgaskrümmer': 'exhaust manifold', 'auspuff': 'exhaust', 'schalldämpfer': 'muffler',
            
            # Automotive specific - Transmission and Drivetrain
            'getriebe': 'transmission', 'schaltgetriebe': 'manual transmission',
            'automatikgetriebe': 'automatic transmission', 'kupplung': 'clutch',
            'drehmomentwandler': 'torque converter', 'differential': 'differential',
            'achse': 'axle', 'antriebswelle': 'drive shaft', 'gelenkwelle': 'propeller shaft',
            'kardanwelle': 'cardan shaft', 'rad': 'wheel', 'reifen': 'tire',
            'felge': 'rim', 'bremse': 'brake', 'bremsscheibe': 'brake disc',
            'bremstrommel': 'brake drum', 'bremsbelag': 'brake pad', 'bremsflüssigkeit': 'brake fluid',
            'lenkung': 'steering', 'lenkrad': 'steering wheel', 'lenksäule': 'steering column',
            'lenkgetriebe': 'steering gear', 'spurstange': 'tie rod', 'achsschenkel': 'steering knuckle',
            
            # Automotive specific - Electronics and Control
            'steuergerät': 'control unit', 'ecu': 'ECU', 'mikrocontroller': 'microcontroller',
            'prozessor': 'processor', 'speicher': 'memory', 'software': 'software',
            'firmware': 'firmware', 'programm': 'program', 'code': 'code',
            'datenbus': 'data bus', 'can': 'CAN', 'lin': 'LIN', 'flexray': 'FlexRay',
            'ethernet': 'Ethernet', 'kommunikation': 'communication', 'protokoll': 'protocol',
            'nachricht': 'message', 'telegramm': 'telegram', 'frame': 'frame',
            'bit': 'bit', 'byte': 'byte', 'word': 'word', 'register': 'register',
            'adresse': 'address', 'pointer': 'pointer', 'index': 'index',
            'tabelle': 'table', 'matrix': 'matrix', 'array': 'array', 'liste': 'list',
            'struktur': 'structure', 'datentyp': 'data type', 'format': 'format',
            
            # Automotive specific - Emissions and Environment
            'abgas': 'exhaust gas', 'emission': 'emission', 'schadstoff': 'pollutant',
            'katalysator': 'catalytic converter', 'kat': 'cat', 'partikelfilter': 'particle filter',
            'dpf': 'DPF', 'egr': 'EGR', 'abgasrückführung': 'exhaust gas recirculation',
            'lambda': 'lambda', 'sauerstoff': 'oxygen', 'lambdasonde': 'lambda sensor',
            'nox': 'NOx', 'stickoxid': 'nitrogen oxide', 'kohlenmonoxid': 'carbon monoxide',
            'kohlendioxid': 'carbon dioxide', 'kohlenwasserstoff': 'hydrocarbon',
            'partikel': 'particle', 'ruß': 'soot', 'regeneration': 'regeneration',
            'reinigung': 'cleaning', 'filterung': 'filtering', 'reduktion': 'reduction',
            'oxidation': 'oxidation', 'katalyse': 'catalysis', 'reaktion': 'reaction',
            
            # Common compound word components
            'temperatur': 'temperature', 'druck': 'pressure', 'geschwindigkeit': 'speed',
            'drehzahl': 'rpm', 'moment': 'torque', 'kraft': 'force', 'leistung': 'power',
            'spannung': 'voltage', 'strom': 'current', 'widerstand': 'resistance',
            'position': 'position', 'winkel': 'angle', 'stellung': 'position',
            'hub': 'stroke', 'weg': 'path', 'strecke': 'distance', 'länge': 'length',
            'breite': 'width', 'höhe': 'height', 'tiefe': 'depth', 'durchmesser': 'diameter',
            'radius': 'radius', 'umfang': 'circumference', 'fläche': 'area', 'volumen': 'volume',
            'masse': 'mass', 'gewicht': 'weight', 'dichte': 'density', 'viskosität': 'viscosity',
            
            # Status and condition words
            'aktiv': 'active', 'inaktiv': 'inactive', 'ein': 'on', 'aus': 'off',
            'offen': 'open', 'geschlossen': 'closed', 'verfügbar': 'available',
            'bereit': 'ready', 'besetzt': 'busy', 'frei': 'free', 'blockiert': 'blocked',
            'gesperrt': 'locked', 'entsperrt': 'unlocked', 'aktiviert': 'activated',
            'deaktiviert': 'deactivated', 'eingeschaltet': 'switched on', 'ausgeschaltet': 'switched off',
            'verbunden': 'connected', 'getrennt': 'disconnected', 'online': 'online', 'offline': 'offline',
            'gültig': 'valid', 'ungültig': 'invalid', 'korrekt': 'correct', 'inkorrekt': 'incorrect',
            'erfolgreich': 'successful', 'fehlgeschlagen': 'failed', 'abgebrochen': 'aborted',
            'beendet': 'finished', 'laufend': 'running', 'wartend': 'waiting', 'pausiert': 'paused',
            
            # Action words
            'starten': 'start', 'stoppen': 'stop', 'pausieren': 'pause', 'fortsetzen': 'resume',
            'initialisieren': 'initialize', 'konfigurieren': 'configure', 'einstellen': 'adjust',
            'kalibrieren': 'calibrate', 'testen': 'test', 'prüfen': 'check', 'messen': 'measure',
            'überwachen': 'monitor', 'kontrollieren': 'control', 'regeln': 'regulate',
            'steuern': 'control', 'schalten': 'switch', 'umschalten': 'toggle',
            'aktivieren': 'activate', 'deaktivieren': 'deactivate', 'sperren': 'lock',
            'entsperren': 'unlock', 'freigeben': 'enable', 'blockieren': 'block',
            'zurücksetzen': 'reset', 'löschen': 'delete', 'speichern': 'save',
            'laden': 'load', 'entladen': 'unload', 'übertragen': 'transfer',
            'senden': 'send', 'empfangen': 'receive', 'verarbeiten': 'process',
            'berechnen': 'calculate', 'auswerten': 'evaluate', 'analysieren': 'analyze',
            
            # Common technical abbreviations and their expansions
            'max': 'maximum', 'min': 'minimum', 'std': 'standard', 'nom': 'nominal',
            'typ': 'typical', 'def': 'default', 'init': 'initial', 'ref': 'reference',
            'abs': 'absolute', 'rel': 'relative', 'diff': 'differential', 'int': 'integral',
            'prop': 'proportional', 'lin': 'linear', 'log': 'logarithmic', 'exp': 'exponential',
            'pos': 'positive', 'neg': 'negative', 'dir': 'direction', 'inv': 'inverse',
            'fwd': 'forward', 'rev': 'reverse', 'up': 'up', 'down': 'down',
            'left': 'left', 'right': 'right', 'front': 'front', 'rear': 'rear',
            'top': 'top', 'bottom': 'bottom', 'side': 'side', 'center': 'center',
            
            # Error and diagnostic terms
            'fehler': 'error', 'störung': 'fault', 'defekt': 'defect', 'ausfall': 'failure',
            'unterbrechung': 'interruption', 'kurzschluss': 'short circuit', 'überlast': 'overload',
            'überhitzung': 'overheating', 'unterspannung': 'undervoltage', 'überspannung': 'overvoltage',
            'timeout': 'timeout', 'überlauf': 'overflow', 'unterlauf': 'underflow',
            'grenzwert': 'limit value', 'überschreitung': 'exceedance', 'unterschreitung': 'underrun',
            'warnung': 'warning', 'alarm': 'alarm', 'meldung': 'message', 'hinweis': 'note',
            'information': 'information', 'status': 'status', 'zustand': 'state',
            
            # Counter and counting terms
            'zähler': 'counter', 'zhler': 'counter',  # Common misspelling
            'zählung': 'count', 'anzahl': 'number', 'summe': 'sum', 'total': 'total',
            'inkrement': 'increment', 'dekrement': 'decrement', 'schritt': 'step',
            'stufe': 'stage', 'level': 'level', 'ebene': 'level', 'rang': 'rank',
            'priorität': 'priority', 'reihenfolge': 'sequence', 'ordnung': 'order',
            
            # Logical and mathematical terms
            'und': 'and', 'oder': 'or', 'nicht': 'not', 'nand': 'nand', 'nor': 'nor',
            'xor': 'xor', 'wenn': 'if', 'dann': 'then', 'sonst': 'else', 'falls': 'if',
            'gleich': 'equal', 'ungleich': 'not equal', 'größer': 'greater', 'kleiner': 'smaller',
            'plus': 'plus', 'minus': 'minus', 'mal': 'times', 'geteilt': 'divided',
            'wurzel': 'root', 'quadrat': 'square', 'kubik': 'cubic', 'potenz': 'power',
            'logarithmus': 'logarithm', 'exponential': 'exponential', 'sinus': 'sine',
            'cosinus': 'cosine', 'tangens': 'tangent', 'integral': 'integral', 'ableitung': 'derivative',
        }
        
        # Create reverse lookup for efficiency
        self.reverse_dict = {v: k for k, v in self.dictionary.items()}
    
    def translate_word(self, german_word: str) -> str:
        """
        Translate a single German word to English.
        
        Args:
            german_word: German word to translate
            
        Returns:
            English translation or original word if not found
        """
        # Try exact match first
        word_lower = german_word.lower()
        if word_lower in self.dictionary:
            return self.dictionary[word_lower]
        
        # Try without common punctuation
        clean_word = german_word.strip('.,;:!?()[]{}"\'-').lower()
        if clean_word in self.dictionary:
            return self.dictionary[clean_word]
        
        # Return original if not found
        return german_word
    
    def get_all_translations(self) -> dict:
        """Get the complete dictionary."""
        return self.dictionary.copy()
    
    def has_translation(self, german_word: str) -> bool:
        """Check if a German word has a translation."""
        return german_word.lower() in self.dictionary
    
    def get_word_count(self) -> int:
        """Get the total number of words in the dictionary."""
        return len(self.dictionary)

