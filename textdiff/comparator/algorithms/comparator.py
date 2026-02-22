# comparator.py

from comparator.algorithms.preprocessing import convert_to_phonetic
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
        self.text1 = text1
        self.text2 = text2
        self.words1 = text1.strip().split()
        self.words2 = text2.strip().split()

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
        else:
            words1 = self.words1
            words2 = self.words2

        # Align words
        aligned1, aligned2, operations, total_cost = align_words(words1, words2)

        # ایجاد aligned_pairs برای فراخوانی صحیح highlight
        aligned_pairs = []
        for i, (w1, w2) in enumerate(zip(aligned1, aligned2)):
            if w1 != "_" and w2 != "_":
                aligned_pairs.append((i, i))
            elif w1 != "_":
                aligned_pairs.append((i, None))
            elif w2 != "_":
                aligned_pairs.append((None, i))

        # Highlight words
        highlighted1, highlighted2, _ = highlight_aligned_words(
            aligned1, aligned2, aligned_pairs, phonetic_mode=(mode=="phonetic")
        )

        return highlighted1, highlighted2, total_cost, operations

    def compare_all_modes(self):
        """Compare texts in all available modes"""
        results = {}
        
        modes = ["standard", "phonetic", "phonetic1", "persian"]
        for mode in modes:
            highlighted1, highlighted2, total_cost, operations = self.compare_texts(mode=mode)
            results[mode] = {
                "highlighted1": highlighted1,
                "highlighted2": highlighted2,
                "total_cost": total_cost,
                "operations": operations
            }
        
        return results