# constants.py

# Sets of characters - اضافه کردن علائم حرکتی به SET_A
SET_A = set("ـ،؛؟!«»…َُِّْ")  # کاراکترهای قابل چشم‌پوشی در پاک‌سازی (شامل علائم حرکتی)
SET_B = set("ابپتثجچحخدذرزسشصضطظعغفقکگلمنوهی")  # حروف اصلی برای هزینه‌ها

# Costs
IGNORE_COST = 0           # هزینه برای کاراکترهای قابل چشم‌پوشی
SUBSTITUTE_COST = 1       # هزینه جایگزینی بین کاراکترهای مشابه
OTHER_COST = 2            # هزینه سایر جایگزینی‌ها یا حذف/درج

# Colors for HTML highlighting - اضافه کردن رنگ بنفش برای علائم حرکتی
VAV_COLOR = "blue"        # رنگ حرف 'و'
NEW_COLOR = "green"       # رنگ درج جدید
DIACRITIC_COLOR = "purple"  # رنگ بنفش برای علائم حرکتی

# Diacritic marks (علائم حرکتی)
DIACRITICS = set("َُِّْ")  # فتحه، ضمه، کسره، تشدید، سکون

# Alef variants (ا و مشابه‌ها)
ALEF_VARIANTS = set("اآإأ")  # شامل الف معمولی و الف با حرکات

# Enhanced Phonetic Mapping (English representation)
PHONETIC_MAPPING = {
    # Persian letters
    'ا': 'a', 'آ': 'a', 'أ': 'a', 'إ': 'a',
    'ب': 'b', 
    'پ': 'p',
    'ت': 't', 'ط': 't',
    'ث': 's', 'س': 's', 'ص': 's',
    'ج': 'j',
    'چ': 'ch',
    'ح': 'h', 'ه': 'h', 'ة': 'h', 'ۀ': 'h',
    'خ': 'kh',
    'د': 'd',
    'ذ': 'z', 'ز': 'z', 'ض': 'z', 'ظ': 'z',
    'ر': 'r',
    'ژ': 'zh',
    'ش': 'sh',
    'ع': '', 'غ': 'gh', 'ق': 'gh',
    'ف': 'f',
    'ک': 'k', 'ك': 'k',
    'گ': 'g',
    'ل': 'l',
    'م': 'm',
    'ن': 'n',
    'و': 'v', 'ؤ': 'v',
    'ی': 'y', 'ي': 'y', 'ئ': 'y', 'ى': 'y',
    
    # Diacritics and other characters - علائم حرکتی بدون هزینه
    'َ': '', 'ُ': '', 'ِ': '', 'ّ': '', 'ْ': '', 
    'ً': 'an', 'ٌ': 'on', 'ٍ': 'en', 'ٰ': 'a',
    'ء': '', '': ' ',
    
    # Numbers
    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
    '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
    
    # Punctuation (keep as is)
    ' ': ' ', '.': '.', ',': ',', '؛': ';', '؟': '?',
    '!': '!', '«': '"', '»': '"', '…': '...', 'ـ': '-'
}

# Vowels for phonetic analysis
VOWELS = {'ا', 'آ', 'و', 'ی', 'ى', 'ع', 'أ', 'إ'}

# Similar sounding groups for phonetic comparison
PHONETIC_GROUPS = {
    's': {'ث', 'س', 'ص'},
    'z': {'ذ', 'ز', 'ض', 'ظ'},
    't': {'ت', 'ط'},
    'h': {'ح', 'ه', 'ة', 'ۀ'},
    'gh': {'غ', 'ق'},
    'a': {'ا', 'آ', 'أ', 'إ', 'ع'},
    'y': {'ی', 'ي', 'ئ', 'ى'},
    'v': {'و', 'ؤ'}
}

# Default character for unknown characters
DEFAULT_PHONETIC = '?'