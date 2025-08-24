# comparator.py

from comparator.algorithms.preprocessing import clean_word, convert_to_phonetic, validate_text_length
from comparator.algorithms.alignment import align_words, levenshtein_with_path
from comparator.algorithms.highlighting import highlight_aligned_words
from comparator.algorithms.visualization import visualize_word_operations, visualize_sentence
from comparator.algorithms.report import generate_comparison_report
from comparator.algorithms.constants import DIACRITICS, IGNORE_COST, DIACRITIC_COLOR
from django.contrib import messages
from django.shortcuts import redirect, render
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# از settings مقادیر پیش‌فرض میگیریم
MAX_TEXT_LENGTH = 10000
MAX_WORDS = 2000

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


@validate_text_length
def compare(request):
    """Main comparison view with detailed per-character operation table"""
    text1 = request.GET.get("text1", "").strip()
    text2 = request.GET.get("text2", "").strip()

    if not text1 or not text2:
        messages.error(request, "No text found for comparison.")
        return redirect("index")

    try:
        comparator = TextComparator(text1, text2)

        # ===== Standard comparison =====
        highlighted_std1, highlighted_std2, cost_std, ops_std = comparator.compare_texts(mode="standard")

        # ===== Phonetic comparison =====
        highlighted_ph1, highlighted_ph2, cost_ph, ops_ph = comparator.compare_texts(mode="phonetic")

        # ===== Phonetic1 / char-level comparison =====
        highlighted_p1, highlighted_p2, cost_p1, ops_p1 = comparator.compare_texts(mode="phonetic1")

        # ===== Persian char-level comparison =====
        highlighted_per1, highlighted_per2, cost_per, ops_per = comparator.compare_texts(mode="persian")

        # ===== Build detailed operations table for standard comparison =====
        operations_table = []
        for i, (w1, w2, op) in enumerate(zip(highlighted_std1, highlighted_std2, ops_std), start=1):
            if isinstance(op, tuple) and len(op) >= 3:
                op_type, cost, _ = op
                if op_type == 'match':
                    description = f"Words match at position {i}"
                elif op_type == 'substitute':
                    description = f"Substitute '{w1}' with '{w2}' at position {i} (cost: {cost})"
                elif op_type == 'insert':
                    description = f"Insert '{w2}' at position {i} (cost: {cost})"
                elif op_type == 'delete':
                    description = f"Delete '{w1}' at position {i} (cost: {cost})"
                else:
                    description = f"Operation '{op_type}' at position {i} (cost: {cost})"
            else:
                description = f"Unknown operation at position {i}"

            operations_table.append({
                "num": i,
                "word1": w1,
                "word2": w2,
                "operation": str(op),
                "description": description
            })

        # ===== Build character comparison table =====
        char_table = []
        max_len = max(len(text1), len(text2))
        
        for i in range(max_len):
            char1 = text1[i] if i < len(text1) else ""
            char2 = text2[i] if i < len(text2) else ""
            
            # تعیین کلاس CSS برای علائم حرکتی
            class1 = "diacritic" if char1 in DIACRITICS else ""
            class2 = "diacritic" if char2 in DIACRITICS else ""
            
            char_table.append((char1, char2, class1, class2))

        # تاریخ و زمان فعلی
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        context = {
            # Standard
            "highlighted1": highlighted_std1,
            "highlighted2": highlighted_std2,
            "operations_table": operations_table,
            "total_cost": cost_std,
            "similarity": round((1 - cost_std / max(len(text1.split()), len(text2.split()))) * 100, 2),

            # Phonetic
            "phonetic_lis1": highlighted_ph1,
            "phonetic_lis2": highlighted_ph2,
            "phonetic_cost": cost_ph,
            "phonetic_similarity": round((1 - cost_ph / max(len(text1.split()), len(text2.split()))) * 100, 2),

            # Phonetic1 / char-level
            "phonetic1_lis1": highlighted_p1,
            "phonetic1_lis2": highlighted_p2,
            "phonetic1_cost": cost_p1,
            "phonetic1_similarity": round((1 - cost_p1 / max(len(text1.split()), len(text2.split()))) * 100, 2),

            # Persian char-level
            "persian_lis1": highlighted_per1,
            "persian_lis2": highlighted_per2,
            "persian_cost": cost_per,
            "persian_similarity": round((1 - cost_per / max(len(text1.split()), len(text2.split()))) * 100, 2),

            # Character comparison tables
            "char_table": char_table,

            # Original texts
            "text1": text1,
            "text2": text2,

            # Meta
            "text1_word_count": len(text1.split()),
            "text2_word_count": len(text2.split()),
            "now": now_str,
            "max_text_length": MAX_TEXT_LENGTH,
            "max_words": MAX_WORDS,
            
            # Constants for template
            "diacritic_color": DIACRITIC_COLOR,
        }

        return render(request, "results.html", context)

    except Exception as e:
        logger.error(f"Error during comparison: {str(e)}", exc_info=True)
        messages.error(request, "Error processing texts. Please check your input.")
        return redirect("index")