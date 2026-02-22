# comparator.py

from comparator.algorithms.preprocessing import convert_to_phonetic, clean_word, MAX_TEXT_LENGTH, MAX_WORDS
from comparator.algorithms.alignment import align_words
from comparator.algorithms.highlighting import highlight_aligned_words

from comparator.algorithms.constants import DIACRITICS, IGNORE_COST, DIACRITIC_COLOR

class TextComparator:
    """
    Central class to orchestrate text comparison pipeline:
    1. Preprocessing
    2. Alignment (word-level)
    3. Highlight differences
    4. Visualization
    5. Generate report
    """
    def __init__(self, text1: str, text2: str):
        # Validate text length using settings
        if len(text1) > MAX_TEXT_LENGTH or len(text2) > MAX_TEXT_LENGTH:
            raise ValueError(f"Texts must be shorter than {MAX_TEXT_LENGTH} characters.")
        
        # Validate word count using settings
        words1_list = text1.strip().split()
        words2_list = text2.strip().split()
        if len(words1_list) > MAX_WORDS or len(words2_list) > MAX_WORDS:
            raise ValueError(f"Texts must contain fewer than {MAX_WORDS} words.")
        
        self.text1 = text1
        self.text2 = text2
        self.words1 = words1_list
        self.words2 = words2_list

    def _calculate_word_cost(self, word1: str, word2: str) -> int:
        """Calculate cost between two words with diacritic support"""
        cost = 0
        max_len = max(len(word1), len(word2))
        
        for i in range(max_len):
            char1 = word1[i] if i < len(word1) else ''
            char2 = word2[i] if i < len(word2) else ''
            
            # هزینه صفر برای علائم حرکتی
            if char1 in DIACRITICS or char2 in DIACRITICS:
                cost += IGNORE_COST
            elif char1 == char2:
                cost += 0
            else:
                cost += 1  # هزینه جایگزینی
                
        return cost

    def compare_texts(self, mode="standard"):
        """Compare the two texts and return highlighted versions + operations + cost"""

        # تبدیل متن‌ها به حالت مناسب
        if mode == "phonetic":
            words1 = [convert_to_phonetic(w) for w in self.words1]
            words2 = [convert_to_phonetic(w) for w in self.words2]
        elif mode == "persian":
            # حالت persian: فقط تمیز کردن بدون تبدیل آوایی
            words1 = [clean_word(w)[0] for w in self.words1]
            words2 = [clean_word(w)[0] for w in self.words2]
        else:
            # حالت standard: بدون تغییر
            words1 = self.words1
            words2 = self.words2

        # Align words
        aligned1, aligned2, operations, total_cost = align_words(words1, words2)

        # ایجاد aligned_pairs برای فراخوانی صحیح highlight
        # باید از اندیس‌های واقعی در لیست‌های اصلی استفاده کنیم
        aligned_pairs = []
        idx1 = 0  # اندیس در لیست اصلی words1
        idx2 = 0  # اندیس در لیست اصلی words2
        
        for w1, w2 in zip(aligned1, aligned2):
            if w1 != "_" and w2 != "_":
                # هر دو کلمه وجود دارند - match یا substitute
                aligned_pairs.append((idx1, idx2))
                idx1 += 1
                idx2 += 1
            elif w1 != "_":
                # فقط w1 وجود دارد - delete
                aligned_pairs.append((idx1, None))
                idx1 += 1
            elif w2 != "_":
                # فقط w2 وجود دارد - insert
                aligned_pairs.append((None, idx2))
                idx2 += 1
            # اگر هر دو "_" باشند، هیچ کاری نمی‌کنیم

        # Highlight words
        highlighted1, highlighted2, _ = highlight_aligned_words(
            aligned1, aligned2, aligned_pairs, phonetic_mode=(mode=="phonetic")
        )

        return highlighted1, highlighted2, total_cost, operations

    def compare_all_modes(self):
        """Compare texts in all available modes"""
        results = {}
        
        modes = ["standard", "phonetic", "persian"]
        for mode in modes:
            highlighted1, highlighted2, total_cost, operations = self.compare_texts(mode=mode)
            results[mode] = {
                "highlighted1": highlighted1,
                "highlighted2": highlighted2,
                "total_cost": total_cost,
                "operations": operations
            }
        
        return results