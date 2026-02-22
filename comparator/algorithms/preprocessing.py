import logging
from comparator.algorithms.constants import SET_A, ALEF_VARIANTS, PHONETIC_MAPPING, VOWELS, DIACRITICS
from comparator.algorithms.logs_setting import get_logger
from django.contrib import messages
from django.shortcuts import redirect
from textdiff.settings import MAX_TEXT_LENGTH, MAX_WORDS

logger = get_logger(__name__, 'preprocessing.log')


def log_function_call(func):
    def wrapper(*args, **kwargs):
        logger.debug(f"Entering {func.__name__} with args: {args}, kwargs: {kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__} with result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper


@log_function_call
def clean_word(word: str) -> tuple[str, list[str]]:
    logger.info(f"Cleaning word: '{word}'")
    
    removed_chars = []
    cleaned_chars = []

    for c in word:
        if c in (SET_A - {' ', 'ـ'}):
            removed_chars.append(c)
        else:
            cleaned_chars.append(c)

    cleaned_word = ''.join(cleaned_chars)
    
    logger.info(f"Cleaned word: '{cleaned_word}', removed chars: {removed_chars}")
    return cleaned_word, removed_chars


@log_function_call
def get_removed_chars(word: str) -> list[str]:
    logger.info(f"Getting removed chars from word: '{word}'")
    
    result = [c for c in word if c in (SET_A - {' ', 'ـ'})]
    logger.info(f"Removed chars: {result}")
    return result


@log_function_call
def is_diacritic(char: str) -> bool:
    return char in DIACRITICS


@log_function_call
def is_phonetically_silent_vav(word: str, pos: int) -> bool:
    logger.info(f"Checking silent vav in word: '{word}' at position: {pos}")
    
    if not isinstance(word, str):
        logger.warning(f"Received non-string input: {word} (type: {type(word)})")
        return False

    if pos >= len(word) or word[pos] != 'و':
        logger.debug(f"Position {pos} is not 'و' or out of bounds")
        return False

    if word.startswith("خوا") and pos == 1:
        logger.debug("Silent vav detected in 'خوا' pattern")
        return True

    if pos > 0 and word[pos - 1] in {'خ', 'ح', 'غ', 'ع'}:
        if pos + 1 < len(word) and word[pos + 1] in {'ا', 'و', 'ی'}:
            logger.debug("Silent vav detected after specific consonants")
            return True

    logger.debug("Vav is not silent")
    return False


@log_function_call
def convert_to_phonetic(text: str) -> str:
    logger.info(f"Converting to phonetic: '{text}'")
    
    phonetic = []
    length = len(text)
    
    i = 0
    while i < length:
        char = text[i]
        
        if char == 'و':
            if i > 0 and text[i-1] in {'خ', 'ح', 'غ', 'ع'}:
                logger.debug(f"Converting 'و' to 'u' at position {i}")
                phonetic.append('u')
            else:
                logger.debug(f"Converting 'و' to 'v' at position {i}")
                phonetic.append('v')
        
        elif i+1 < length and char == text[i+1] and char in PHONETIC_MAPPING:
            logger.debug(f"Handling double letter '{char}' at position {i}")
            phonetic.append(PHONETIC_MAPPING[char]*2)
            i += 1
        
        elif char in DIACRITICS:
            logger.debug(f"Ignoring diacritic '{char}' at position {i}")
            phonetic.append('')
        else:
            mapped_char = PHONETIC_MAPPING.get(char, char)
            if char != mapped_char:
                logger.debug(f"Mapping '{char}' to '{mapped_char}' at position {i}")
            phonetic.append(mapped_char)
        
        i += 1
    
    result = ''.join(phonetic)
    logger.info(f"Phonetic conversion result: '{result}'")
    return result


@log_function_call
def validate_text_length(view_func):
    def wrapper(request, *args, **kwargs):
        logger.info(f"Validating text length for request: {request.method}")
        
        # Get text from both POST and GET parameters
        text1 = request.POST.get("text1", "") or request.GET.get("text1", "")
        text2 = request.POST.get("text2", "") or request.GET.get("text2", "")

        logger.debug(f"Text1 length: {len(text1)}, Text2 length: {len(text2)}")
        logger.debug(f"Text1 word count: {len(text1.split())}, Text2 word count: {len(text2.split())}")

        if len(text1) > MAX_TEXT_LENGTH or len(text2) > MAX_TEXT_LENGTH:
            error_msg = f"Text too long. Maximum allowed is {MAX_TEXT_LENGTH} characters."
            logger.warning(error_msg)
            messages.error(request, error_msg)
            return redirect("index")

        if len(text1.split()) > MAX_WORDS or len(text2.split()) > MAX_WORDS:
            error_msg = f"Too many words. Maximum allowed is {MAX_WORDS} words."
            logger.warning(error_msg)
            messages.error(request, error_msg)
            return redirect("index")

        logger.info("Text validation passed")
        return view_func(request, *args, **kwargs)
    
    return wrapper


@log_function_call
def process_text_step_by_step(text: str) -> dict:
    logger.info(f"Processing text step by step: '{text}'")
    
    cleaned_words = []
    removed_chars_list = []
    for word in text.split():
        cleaned_word, removed_chars = clean_word(word)
        cleaned_words.append(cleaned_word)
        removed_chars_list.append(removed_chars)
    
    cleaned_text = ' '.join(cleaned_words)
    phonetic_text = convert_to_phonetic(cleaned_text)
    
    word_details = []
    for i, word in enumerate(cleaned_text.split()):
        silent_vav_positions = []
        for pos in range(len(word)):
            if word[pos] == 'و' and is_phonetically_silent_vav(word, pos):
                silent_vav_positions.append(pos)
        
        phonetic_word = convert_to_phonetic(word)
        
        word_details.append({
            'original': word,
            'cleaned': word,
            'phonetic': phonetic_word,
            'silent_vav_positions': silent_vav_positions,
            'removed_chars': removed_chars_list[i]
        })
    
    result = {
        'original_text': text,
        'cleaned_text': cleaned_text,
        'phonetic_text': phonetic_text,
        'word_details': word_details
    }
    
    logger.info(f"Step-by-step processing completed for text: '{text}'")
    return result


logger.info("preprocessing.py module imported successfully")