# highlighting.py

from comparator.algorithms.preprocessing import clean_word, convert_to_phonetic
from comparator.algorithms.constants import ALEF_VARIANTS, SET_B, SUBSTITUTE_COST, OTHER_COST, VAV_COLOR, NEW_COLOR

def highlight_differences(word1: str, word2: str, phonetic_mode: bool=False) -> tuple[list[str], list[str], list[str]]:
    """
    Compare two words and generate highlighted versions showing differences.

    Args:
        word1: First word
        word2: Second word
        phonetic_mode: Whether to use phonetic comparison

    Returns:
        Tuple: (highlighted_word1, highlighted_word2, operations_list)
    """
    if not word1 or not word2:
        if word1:
            return [f'<span style="color:red">{word1}</span>'], ['[X]'], [f"Delete: '{word1}'"]
        else:
            return [' '], [f'<span style="color:green">{word2}</span>'], [f"Insert: '{word2}'"]

    if phonetic_mode:
        w1 = convert_to_phonetic(clean_word(word1)[0])
        w2 = convert_to_phonetic(clean_word(word2)[0])
    else:
        w1 = clean_word(word1)[0]
        w2 = clean_word(word2)[0]

    from .alignment import levenshtein_with_path
    _, path = levenshtein_with_path(w1, w2)

    highlighted1 = []
    highlighted2 = []
    operations = []
    i = j = 0

    for op in path:
        if op[0] == 'match':
            highlighted1.append(word1[i] if i < len(word1) else "")
            highlighted2.append(word2[j] if j < len(word2) else "")
            operations.append(f"Match: '{word1[i] if i < len(word1) else ''}'")
            i += 1
            j += 1
        elif op[0] == 'substitute':
            ch1 = word1[i] if i < len(word1) else ""
            ch2 = word2[j] if j < len(word2) else ""
            if ch1 in ALEF_VARIANTS and ch2 in ALEF_VARIANTS:
                highlighted1.append(ch1)
                highlighted2.append(f'<span style="color:blue">{ch2}</span>')
                operations.append(f"Alef variant substitution: '{ch1}' → '{ch2}'")
            else:
                cost = SUBSTITUTE_COST if (ch1 in SET_B and ch2 in SET_B) else OTHER_COST
                color = 'purple' if cost == SUBSTITUTE_COST else 'orange'
                highlighted1.append(ch1)
                highlighted2.append(f'<span style="color:{color}">{ch2}</span>')
                operations.append(f"Substitute: '{ch1}' with '{ch2}' (Cost: {cost})")
            i += 1
            j += 1
        elif op[0] == 'delete':
            ch = word1[i] if i < len(word1) else ""
            highlighted1.append(f'<span style="color:red">{ch}</span>')
            highlighted2.append('[X]')
            operations.append(f"Delete: '{ch}'")
            i += 1
        elif op[0] == 'insert':
            ch = word2[j] if j < len(word2) else ""
            highlighted1.append('[X]')
            if ch == 'و' and not phonetic_mode:
                highlighted2.append(f'<span style="color:{VAV_COLOR}">{ch}</span>')
            else:
                highlighted2.append(f'<span style="color:green">{ch}</span>')
            operations.append(f"Insert: '{ch}'")
            j += 1

    return highlighted1, highlighted2, operations

def highlight_aligned_words(aligned_words1: list[str], aligned_words2: list[str], 
                          aligned_pairs: list[tuple], phonetic_mode: bool=False) -> tuple[list[str], list[str], list[str]]:
    """
    Highlight differences for lists of aligned words.

    Args:
        aligned_words1: Aligned words from text1 (may contain "_" for gaps)
        aligned_words2: Aligned words from text2 (may contain "_" for gaps)
        aligned_pairs: List of tuples (index1, index2)
        phonetic_mode: Use phonetic comparison

    Returns:
        highlighted_words1, highlighted_words2, operations_list
    """
    highlighted_words1 = []
    highlighted_words2 = []
    operations_texts = []

    for i, j in aligned_pairs:
        # بررسی صحیح برای None و اندیس‌های معتبر
        if i is not None and i < len(aligned_words1) and aligned_words1[i] != "_":
            w1 = aligned_words1[i]
        else:
            w1 = ""
        
        if j is not None and j < len(aligned_words2) and aligned_words2[j] != "_":
            w2 = aligned_words2[j]
        else:
            w2 = ""
        
        h1, h2, ops = highlight_differences(w1, w2, phonetic_mode)
        highlighted_words1.append(''.join(h1))
        highlighted_words2.append(''.join(h2))
        operations_texts.extend(ops)

    return highlighted_words1, highlighted_words2, operations_texts