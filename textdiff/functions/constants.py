# ------------ Constants ------------
SET_A = set(['َ', 'ُ', 'ِ', 'ّ', 'ْ', 'ً', 'ٌ', 'ٍ', '.', ',', '،', ' ', 'ـ'])  # Diacritics and punctuation
SET_B = set(['ا', 'أ', 'إ', 'آ', 'ء', 'ئ', 'ؤ', 'ة', 'ه', 'ح', 'ج', 'خ'])  # Similar-looking letters

IGNORE_COST = 0
SUBSTITUTE_COST = 1
OTHER_COST = 2

VAV_COLOR = '#800080'  # Purple color for silent 'و'
NEW_COLOR = "#FF0000"

ALEF_VARIANTS = {'ا', 'أ', 'إ', 'آ'}  # Different forms of Alef

# ------------ Phonetic Mapping ------------
PHONETIC_MAPPING = {
    # Alef variants
    'ا': 'a',  # alef
    'أ': 'a',  # hamza on alef
    'إ': 'e',  # hamza below alef
    'آ': 'aa', # alef with maddah
    
    # Hamza variants
    'ء': "'",  # hamza
    'ئ': "'e", # hamza on yeh
    'ؤ': "'o", # hamza on waw
    
    # Consonants
    'ب': 'b',
    'پ': 'p',
    'ت': 't',
    'ث': 's',
    'ج': 'j',
    'چ': 'ch',
    'ح': 'h',
    'خ': 'kh',
    'د': 'd',
    'ذ': 'z',
    'ر': 'r',
    'ز': 'z',
    'ژ': 'zh',
    'س': 's',
    'ش': 'sh',
    'ص': 's',
    'ض': 'z',
    'ط': 't',
    'ظ': 'z',
    'ع': "'",
    'غ': 'gh',
    
    # Other letters
    'ف': 'f',
    'ق': 'q',
    'ک': 'k',
    'گ': 'g',
    'ل': 'l',
    'م': 'm',
    'ن': 'n',
    'ه': 'h',
    'ة': 'h',  # ta marbuta
    'و': 'v',  # default as consonant
    'ی': 'y',
    
    # Space and half-space
    ' ': ' ',
    'ـ': '',  # half-space (silent)
}