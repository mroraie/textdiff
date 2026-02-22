import logging
from datetime import datetime
from collections import defaultdict
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from matplotlib.lines import Line2D
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


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

class TextComparator:
    """کلاس نهایی برای مقایسه متون عربی/فارسی با قابلیت‌های کامل"""
    
    def __init__(self, text1: str, text2: str):
        self.text1 = text1
        self.text2 = text2
        self.words1 = text1.strip().split()
        self.words2 = text2.strip().split()
        self.len1 = len(text1)
        self.len2 = len(text2)

        # Graph styles
        self.global_graph_style = {
            'node_size': 1200,
            'node_color': 'lightgreen',
            'font_size': 10
        }
        
        self.word_graph_style = {
            'node_size': 800,
            'node_color': 'lightblue',
            'font_size': 8
        }
        
        self.edge_styles = {
            'match': {'color': 'green', 'width': 2, 'style': 'solid'},
            'replace': {'color': 'orange', 'width': 2, 'style': 'solid'},
            'delete': {'color': 'red', 'width': 2, 'style': 'dashed'},
            'insert': {'color': 'blue', 'width': 2, 'style': 'dashed'}
        }
        
        self.node_style = {
            'node_size': 800,
            'node_color': 'lightblue',
            'alpha': 0.9,
            'edgecolors': 'darkblue',
            'linewidths': 1
        }

        self.graph = self._build_graph()

    # ------------ Core Text Processing Functions ------------
    
    @staticmethod
    def clean_word(word: str) -> str:
        """Remove ignorable characters from word"""
        return ''.join(c for c in word if c not in (SET_A - {' ', 'ـ'}))

    @staticmethod
    def is_phonetically_silent_vav(word: str, pos: int) -> bool:
        """Check if 'و' at the given position is phonetically silent in Persian"""
        
        if pos >= len(word) or word[pos] != 'و':
            return False

        # 1. Pattern for words like "خواهر", "خواستن", "خواندن" where 'و' is silent
        if word.startswith("خوا") and pos == 1:
            return True

        # 2. Classic case: when 'و' follows certain letters and is followed by vowels
        if pos > 0 and word[pos - 1] in {'خ', 'ح', 'غ', 'ع'}:
            if pos + 1 < len(word) and word[pos + 1] in {'ا', 'و', 'ی'}:
                return True

        return False

    # ------------ Comparison Algorithms ------------
    
    def levenshtein_with_path(self, s1: str, s2: str) -> tuple:
        """Calculate Levenshtein distance with operation path and custom costs"""
        len1, len2 = len(s1), len(s2)
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        operation = [[''] * (len2 + 1) for _ in range(len1 + 1)]

        # Initialize DP table
        for i in range(1, len1 + 1):
            is_final_heh = (i == len1 and s1[i-1] == 'ه')
            dp[i][0] = dp[i-1][0] + (1 if is_final_heh else OTHER_COST)
            operation[i][0] = 'delete'
            
        for j in range(1, len2 + 1):
            is_final_heh = (j == len2 and s2[j-1] == 'ه')
            dp[0][j] = dp[0][j-1] + (1 if is_final_heh else OTHER_COST)
            operation[0][j] = 'insert'

        # Fill DP table
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                ch1, ch2 = s1[i-1], s2[j-1]
                is_final_heh1 = (i == len1 and ch1 == 'ه')
                is_final_heh2 = (j == len2 and ch2 == 'ه')

                # Compute substitution cost
                if ch1 == ch2:
                    cost = 0
                elif ch1 in ALEF_VARIANTS and ch2 in ALEF_VARIANTS:
                    cost = SUBSTITUTE_COST
                elif ch1 == 'ـ' or ch2 == 'ـ':
                    cost = IGNORE_COST
                elif ch1 == 'و' or ch2 == 'و':
                    if (self.is_phonetically_silent_vav(s1, i-1) or 
                        self.is_phonetically_silent_vav(s2, j-1)):
                        cost = SUBSTITUTE_COST  # cost for silent vav
                    else:
                        cost = SUBSTITUTE_COST
                elif is_final_heh1 or is_final_heh2:
                    cost = SUBSTITUTE_COST
                else:
                    cost = SUBSTITUTE_COST if (ch1 in SET_B and ch2 in SET_B) else OTHER_COST

                # Compute transition costs
                del_cost = dp[i-1][j] + (1 if is_final_heh1 or ch1 == 'ا' else OTHER_COST)
                ins_cost = dp[i][j-1] + (1 if is_final_heh2 or ch2 == 'ا' else OTHER_COST)
                sub_cost = dp[i-1][j-1] + cost

                # Find minimum cost operation
                dp[i][j] = min(del_cost, ins_cost, sub_cost)
                
                if dp[i][j] == del_cost:
                    operation[i][j] = 'delete'
                elif dp[i][j] == ins_cost:
                    operation[i][j] = 'insert'
                else:
                    operation[i][j] = 'substitute' if cost > 0 else 'match'

        # Backtrack to find operation path
        i, j = len1, len2
        steps = []
        while i > 0 or j > 0:
            op = operation[i][j]
            if op == 'delete':
                steps.append(('delete', s1[i-1], i-1))
                i -= 1
            elif op == 'insert':
                steps.append(('insert', s2[j-1], j-1))
                j -= 1
            else:
                steps.append((op, s1[i-1], s2[j-1], i-1))
                i -= 1
                j -= 1

        steps.reverse()
        return dp[len1][len2], steps

    def align_words(self, mode: str = 'standard') -> list:
        """Align words from two texts based on specified mode"""
        similarity_matrix = defaultdict(dict)
        
        # Calculate similarity matrix
        for i, w1 in enumerate(self.words1):
            for j, w2 in enumerate(self.words2):
                if mode == 'phonetic':
                    similarity_matrix[i][j] = self.phonetic_similarity(w1, w2)
                else:
                    clean_w1 = self.clean_word(w1)
                    clean_w2 = self.clean_word(w2)
                    dist, _ = self.levenshtein_with_path(clean_w1, clean_w2)
                    max_len = max(len(clean_w1), len(clean_w2))
                    similarity = 1 - (dist / max_len) if max_len > 0 else 1
                    similarity_matrix[i][j] = similarity

        # Find best alignment pairs
        aligned_pairs = []
        used_i = set()
        used_j = set()
        
        # Sort all possible pairs by similarity
        all_pairs = []
        for i in similarity_matrix:
            for j in similarity_matrix[i]:
                all_pairs.append((similarity_matrix[i][j], i, j))
        all_pairs.sort(reverse=True, key=lambda x: x[0])

        # Select optimal pairs
        for sim, i, j in all_pairs:
            if i not in used_i and j not in used_j:
                aligned_pairs.append((i, j))
                used_i.add(i)
                used_j.add(j)

        # Add unpaired words
        for i in range(len(self.words1)):
            if i not in used_i:
                aligned_pairs.append((i, None))
        for j in range(len(self.words2)):
            if j not in used_j:
                aligned_pairs.append((None, j))

        # Final sorting
        aligned_pairs.sort(key=lambda x: (
            x[0] if x[0] is not None else float('inf'),
            x[1] if x[1] is not None else float('inf')
        ))
        
        return aligned_pairs

    def highlight_differences(self, word1: str, word2: str, phonetic_mode: bool = False) -> tuple:
        """Compare two words and generate highlighted versions as lists"""
        if not word1 or not word2:
            if word1:
                return (
                    [f'<span style="color:red">{word1}</span>'],
                    ['[X]'],
                    [f"Delete: '{word1}'"]
                )
            else:
                return (
                    [' '],
                    [f'<span style="color:green">{word2}</span>'],
                    [f"Insert: '{word2}'"]
                )

        if phonetic_mode:
            clean_w1 = self.convert_to_phonetic(self.clean_word(word1))
            clean_w2 = self.convert_to_phonetic(self.clean_word(word2))
        else:
            clean_w1 = self.clean_word(word1)
            clean_w2 = self.clean_word(word2)
            
        _, path = self.levenshtein_with_path(clean_w1, clean_w2)

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
                    
                elif ch1 == 'ـ' or ch2 == 'ـ':
                    highlighted1.append(ch1)
                    highlighted2.append(ch2)
                    operations.append("Half-space (zero cost)")
                    
                elif (i == len(word1)-1 and ch1 == 'ه') or (j == len(word2)-1 and ch2 == 'ه'):
                    color = 'teal' if ch1 == 'ه' else 'darkcyan'
                    highlighted1.append(ch1)
                    highlighted2.append(f'<span style="color:{color}">{ch2}</span>')
                    operations.append(f"Final 'ه' operation: '{ch1}' ↔ '{ch2}'")
                    
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
                cost = 1 if (i == len(word1)-1 and ch == 'ه') else OTHER_COST
                highlighted1.append(f'<span style="color:red">{ch}</span>')
                highlighted2.append('[X]')
                operations.append(f"Delete: '{ch}' (Cost: {cost})")
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

    def compare_texts(self, mode: str = 'standard') -> tuple:
        """Compare two texts and return highlighted versions and operations"""
        if mode == 'phonetic':
            return self._compare_phonetically()
        if mode == 'phonetic1':
            return self._compare_phonetically_new()
        if mode == 'persian':
            return self._compare_phonetically_new1()        
        else:
            return self._compare_standard()

    def _compare_standard(self) -> tuple:
        """Compare two texts in standard mode (character-based comparison)"""
        aligned_pairs = self.align_words('standard')

        total_cost = 0
        highlighted_words1 = []
        highlighted_words2 = []
        operations_texts = []

        for i, j in aligned_pairs:
            if i is not None and j is not None:
                clean_w1 = self.clean_word(self.words1[i])
                clean_w2 = self.clean_word(self.words2[j])
                cost, _ = self.levenshtein_with_path(clean_w1, clean_w2)
                total_cost += cost
                h1_parts, h2_parts, ops = self.highlight_differences(self.words1[i], self.words2[j], False)
                
                highlighted_words1.append(''.join(h1_parts))
                highlighted_words2.append(''.join(h2_parts))
                operations_texts.extend(ops)
                
            elif i is not None:
                cost = len(self.clean_word(self.words1[i])) * OTHER_COST
                total_cost += cost
                h1_parts, h2_parts, ops = self.highlight_differences(self.words1[i], "", False)
                highlighted_words1.append(''.join(h1_parts))
                highlighted_words2.append(''.join(h2_parts))
                operations_texts.extend(ops)
                
            else:
                cost = len(self.clean_word(self.words2[j])) * OTHER_COST
                total_cost += cost
                h1_parts, h2_parts, ops = self.highlight_differences("", self.words2[j], False)
                highlighted_words1.append(''.join(h1_parts))
                highlighted_words2.append(''.join(h2_parts))
                operations_texts.extend(ops)

        return highlighted_words1, highlighted_words2, total_cost, operations_texts

    def _compare_phonetically(self) -> tuple:
        """Compare two texts in phonetic mode (pronunciation-based comparison)"""
        aligned_pairs = self.align_words('phonetic')

        total_cost = 0
        highlighted_words1 = []
        highlighted_words2 = []
        operations_texts = []

        # Split texts into characters (including space as separator)
        chars1 = list(' '.join(self.words1))
        chars2 = list(' '.join(self.words2))

        # Get phonetic representations
        phonetic1 = self.convert_to_phonetic(self.clean_word(''.join(chars1)))
        phonetic2 = self.convert_to_phonetic(self.clean_word(''.join(chars2)))


        # Calculate edit distance at character level
        dist, path = self.levenshtein_with_path(phonetic1, phonetic2)
        
        
        
        
        
        for i, j in aligned_pairs:
            if i is not None and j is not None:
                # Both words exist - compare them
                original_w1 = self.words1[i]
                original_w2 = self.words2[j]
                phonetic1 = self.convert_to_phonetic(self.clean_word(original_w1))
                phonetic2 = self.convert_to_phonetic(self.clean_word(original_w2))
                
                cost, path = self.levenshtein_with_path(phonetic1, phonetic2)
                total_cost += cost
                
                h1_parts, h2_parts, ops = self.highlight_differences(original_w1, original_w2, True)
                
                highlighted_words1.append(''.join(h1_parts))
                highlighted_words2.append(''.join(h2_parts))
                operations_texts.extend(ops)
                
            elif i is not None:
                # Word exists only in text1 (deletion)
                original_w1 = self.words1[i]
                phonetic1 = self.convert_to_phonetic(self.clean_word(original_w1))
                cost = len(phonetic1) * OTHER_COST
                total_cost += cost

                highlighted_words1.append(f'<span style="color:red">{original_w1}</span>')
                highlighted_words2.append('[X]')
                operations_texts.append(f"Delete: '{original_w1}'")
                
            else:  # j is not None (insertion case)
                # Word exists only in text2 (insertion)
                original_w2 = self.words2[j]
                phonetic2 = self.convert_to_phonetic(self.clean_word(original_w2))
                cost = len(phonetic2) * OTHER_COST
                total_cost += cost
                
                # Keep original word in text1 as empty space
                highlighted_words1.append(' ')
                # Show inserted word in text2 with phonetic in parentheses
                highlighted_words2.append(
                    f'<span style="color:green">{original_w2}</span>'
                    f'<span style="color:gray"> ({phonetic2})</span>'
                )
                operations_texts.append(f"Insert: '{original_w2}' (phonetic: {phonetic2})")

        return highlighted_words1, highlighted_words2, total_cost, operations_texts




    def _compare_phonetically_new(self) -> tuple:
        """Compare two texts in phonetic mode with character-level operations"""
        # Split texts into characters (including space as separator)
        chars1 = list(' '.join(self.words1))
        chars2 = list(' '.join(self.words2))
        
        # Get phonetic representations
        phonetic1 = self.convert_to_phonetic(self.clean_word(''.join(chars1)))
        phonetic2 = self.convert_to_phonetic(self.clean_word(''.join(chars2)))
        
        # Calculate edit distance at character level
        dist, path = self.levenshtein_with_path(phonetic1, phonetic2)
        
        # Generate highlighted versions
        highlighted1 = []
        highlighted2 = []
        operations = []
        i = j = 0
        
        for op in path:
            if op[0] == 'match':
                highlighted1.append(phonetic1[i] if i < len(phonetic1) else '')
                highlighted2.append(phonetic2[j] if j < len(phonetic2) else '')
                operations.append(f"Match: '{chars1[i]}'")
                i += 1
                j += 1
                
            elif op[0] == 'substitute':
                ch1 = phonetic1[i] if i < len(phonetic1) else ''
                ch2 = phonetic2[j] if j < len(phonetic2) else ''
                highlighted1.append(ch1)
                highlighted2.append(f'<span style="color:orange">{ch2}</span>')
                operations.append(f"Replace: '{ch1}' with '{ch2}'")
                i += 1
                j += 1
                
            elif op[0] == 'delete':
                ch = phonetic1[i] if i < len(phonetic1) else ''
                highlighted1.append(f'<span style="color:red">{ch}</span>')
                highlighted2.append('[X]')
                operations.append(f"Delete: '{ch}'")
                i += 1
                
            elif op[0] == 'insert':
                ch = phonetic2[j] if j < len(phonetic2) else ''
                highlighted1.append('[ ]')
                highlighted2.append(f'<span style="color:green">{ch}</span>')
                operations.append(f"Insert: '{ch}'")
                j += 1

        # Reconstruct words from characters
        def reconstruct(highlighted):
            text = ''.join(highlighted)
            # Handle space formatting
            text = text.replace(' ', '&nbsp;')
            text = text.replace('[&nbsp;]', '[ ]')
            return text

        highlighted_text1 = reconstruct(highlighted1)
        highlighted_text2 = reconstruct(highlighted2)
        
        return [highlighted_text1], [highlighted_text2], dist, operations

    def _compare_phonetically_new1(self) -> tuple:
        """Compare two texts in phonetic mode with character-level operations"""
        # Split texts into characters (including space as separator)
        chars1 = list(' '.join(self.words1))
        chars2 = list(' '.join(self.words2))
        
        # Get phonetic representations
        phonetic1 = self.convert_to_phonetic(self.clean_word(''.join(chars1)))
        phonetic2 = self.convert_to_phonetic(self.clean_word(''.join(chars2)))
        
        # Calculate edit distance at character level
        dist, path = self.levenshtein_with_path(phonetic1, phonetic2)
        
        # Generate highlighted versions
        highlighted1 = []
        highlighted2 = []
        operations = []
        i = j = 0
        
        for op in path:
            if op[0] == 'match':
                highlighted1.append(chars1[i] if i < len(chars1) else '')
                highlighted2.append(chars2[j] if j < len(chars2) else '')
                operations.append(f"Match: '{chars1[i]}'")
                i += 1
                j += 1
                
            elif op[0] == 'substitute':
                ch1 = chars1[i] if i < len(chars1) else ''
                ch2 = chars2[j] if j < len(chars2) else ''
                highlighted1.append(ch1)
                highlighted2.append(f'<span style="color:orange">{ch2}</span>')
                operations.append(f"Replace: '{ch1}' with '{ch2}'")
                i += 1
                j += 1
                
            elif op[0] == 'delete':
                ch = chars1[i] if i < len(chars1) else ''
                highlighted1.append(f'<span style="color:red">{ch}</span>')
                highlighted2.append('[X]')
                operations.append(f"Delete: '{ch}'")
                i += 1
                
            elif op[0] == 'insert':
                ch = chars2[j] if j < len(chars2) else ''
                highlighted1.append('[ ]')
                highlighted2.append(f'<span style="color:green">{ch}</span>')
                operations.append(f"Insert: '{ch}'")
                j += 1

        # Reconstruct words from characters
        def reconstruct(highlighted):
            text = ''.join(highlighted)
            # Handle space formatting
            text = text.replace(' ', '&nbsp;')
            text = text.replace('[&nbsp;]', '[ ]')
            return text

        highlighted_text1 = reconstruct(highlighted1)
        highlighted_text2 = reconstruct(highlighted2)
        
        return [highlighted_text1], [highlighted_text2], dist, operations

    @staticmethod
    def convert_to_phonetic(text: str) -> str:
        """Convert Arabic/Persian text to English-friendly phonetic representation"""
        phonetic = []
        for i, char in enumerate(text):
            if char == 'و':
                if i > 0 and text[i-1] in {'خ', 'ح', 'غ', 'ع'}:
                    phonetic.append('u')
                else:
                    phonetic.append('v')
            else:
                phonetic.append(PHONETIC_MAPPING.get(char, char))
        return ''.join(phonetic)

    def phonetic_similarity(self, word1: str, word2: str) -> float:
        """Calculate phonetic similarity between two words"""
        phonetic1 = self.convert_to_phonetic(self.clean_word(word1))
        phonetic2 = self.convert_to_phonetic(self.clean_word(word2))
        
        if not phonetic1 and not phonetic2:
            return 1.0
            
        max_len = max(len(phonetic1), len(phonetic2))
        dist, _ = self.levenshtein_with_path(phonetic1, phonetic2)
        return 1 - (dist / max_len) if max_len > 0 else 1

    # ------------ Visualization Methods ------------
    
    def create_comparison_graph(self, mode: str = 'standard') -> dict:
        """Create a comprehensive comparison with graphs at different levels"""
        # 1. Global text comparison
        global_graph = self._create_global_graph(mode)
        global_image = self._draw_graph(global_graph, "Global Text Comparison", 
                                      self.global_graph_style)
        
        # 2. Word alignment
        aligned_pairs = self.align_words(mode)
        word_comparisons = []
        
        for i, j in aligned_pairs:
            if i is not None and j is not None:
                word1 = self.words1[i]
                word2 = self.words2[j]
                comparator = self._create_word_comparator(word1, word2)
                cost, path = self._find_shortest_path(comparator)
                
                # Get word graph image
                path_nodes = [(0,0)]
                for op in path:
                    if op[0] in ['match', 'replace']:
                        path_nodes.append((path_nodes[-1][0]+1, path_nodes[-1][1]+1))
                    elif op[0] == 'delete':
                        path_nodes.append((path_nodes[-1][0]+1, path_nodes[-1][1]))
                    else:  # insert
                        path_nodes.append((path_nodes[-1][0], path_nodes[-1][1]+1))
                
                word_graph = self._draw_graph(comparator, 
                                            f"Word Comparison: '{word1}' vs '{word2}'",
                                            self.word_graph_style,
                                            highlight_path=path_nodes)
                
                word_comparisons.append({
                    'word1': word1,
                    'word2': word2,
                    'cost': cost,
                    'graph_image': word_graph,
                    'operations': self._visualize_path(word1, word2, path)
                })
            elif i is not None:
                word_comparisons.append({
                    'word1': self.words1[i],
                    'word2': None,
                    'cost': len(self.clean_word(self.words1[i])) * OTHER_COST,
                    'graph_image': None,
                    'operations': [{'op': f"Delete word: '{self.words1[i]}'"}]
                })
            else:
                word_comparisons.append({
                    'word1': None,
                    'word2': self.words2[j],
                    'cost': len(self.clean_word(self.words2[j])) * OTHER_COST,
                    'graph_image': None,
                    'operations': [{'op': f"Insert word: '{self.words2[j]}'"}]
                })
        
        return {
            'global_comparison': global_image,
            'word_comparisons': word_comparisons,
            'total_cost': sum(wc['cost'] for wc in word_comparisons)
        }
    
    def _create_global_graph(self, mode: str) -> nx.DiGraph:
        """Create a graph for the global text comparison"""
        graph = nx.DiGraph()
        
        # Add nodes for each word position
        for i in range(len(self.words1) + 1):
            for j in range(len(self.words2) + 1):
                graph.add_node((i, j), pos=(i, -j))
        
        # Add edges
        for i in range(len(self.words1) + 1):
            for j in range(len(self.words2) + 1):
                if i < len(self.words1) and j < len(self.words2):
                    # Match/replace edge
                    cost = self._word_distance(self.words1[i], self.words2[j], mode)
                    edge_type = 'match' if cost == 0 else 'replace'
                    graph.add_edge(
                        (i, j), (i+1, j+1),
                        weight=cost,
                        label=f"{edge_type}({cost})",
                        **self.edge_styles[edge_type]
                    )
                
                if i < len(self.words1):
                    # Delete edge
                    cost = len(self.clean_word(self.words1[i])) * OTHER_COST
                    graph.add_edge(
                        (i, j), (i+1, j),
                        weight=cost,
                        label=f"delete({cost})",
                        **self.edge_styles['delete']
                    )
                
                if j < len(self.words2):
                    # Insert edge
                    cost = len(self.clean_word(self.words2[j])) * OTHER_COST
                    graph.add_edge(
                        (i, j), (i, j+1),
                        weight=cost,
                        label=f"insert({cost})",
                        **self.edge_styles['insert']
                    )
        
        return graph
    
    def _word_distance(self, word1: str, word2: str, mode: str) -> int:
        """Calculate distance between two words"""
        clean_w1 = self.clean_word(word1)
        clean_w2 = self.clean_word(word2)
        
        if mode == 'phonetic':
            clean_w1 = self.convert_to_phonetic(clean_w1)
            clean_w2 = self.convert_to_phonetic(clean_w2)
            
        dist, _ = self.levenshtein_with_path(clean_w1, clean_w2)
        return dist
    
    def _create_word_comparator(self, word1: str, word2: str) -> nx.DiGraph:
        """Create a graph for word-level comparison"""
        graph = nx.DiGraph()
        
        # Add nodes
        for i in range(len(word1) + 1):
            for j in range(len(word2) + 1):
                graph.add_node((i, j), pos=(i, -j))
        
        # Add edges
        for i in range(len(word1) + 1):
            for j in range(len(word2) + 1):
                if i < len(word1) and j < len(word2):
                    # Match/replace edge
                    cost = self._char_distance(word1[i], word2[j])
                    edge_type = 'match' if cost == 0 else 'replace'
                    graph.add_edge(
                        (i, j), (i+1, j+1),
                        weight=cost,
                        label=f"{edge_type}({cost})",
                        **self.edge_styles[edge_type]
                    )
                
                if i < len(word1):
                    # Delete edge
                    cost = self._delete_cost(word1[i])
                    graph.add_edge(
                        (i, j), (i+1, j),
                        weight=cost,
                        label=f"delete({cost})",
                        **self.edge_styles['delete']
                    )
                
                if j < len(word2):
                    # Insert edge
                    cost = self._insert_cost(word2[j])
                    graph.add_edge(
                        (i, j), (i, j+1),
                        weight=cost,
                        label=f"insert({cost})",
                        **self.edge_styles['insert']
                    )
        
        return graph
    
    def _char_distance(self, char1: str, char2: str) -> int:
        """Calculate distance between two characters"""

        if char1 == char2:
            return 0
        elif char1 in ALEF_VARIANTS and char2 in ALEF_VARIANTS:
            return 1
        elif (char1 in SET_B and char2 in SET_B):
            return SUBSTITUTE_COST
        else:
            return OTHER_COST
    
    def _delete_cost(self, char: str) -> int:
        """Cost to delete a character"""
        return 1 if (char == 'ه' or char == 'ا') else OTHER_COST
    
    def _insert_cost(self, char: str) -> int:
        """Cost to insert a character"""
        return 1 if (char == 'ه' or char == 'ا') else OTHER_COST
    
    def _find_shortest_path(self) -> tuple:
        """Find shortest path using Dijkstra's algorithm on the instance's graph"""
        if not hasattr(self, 'graph') or self.graph is None:
            self.graph = self._build_graph()
        
        heap = []
        # Push initial state: (total_cost, i, j, path)
        heapq.heappush(heap, (0, 0, 0, []))
        visited = set()
        
        while heap:
            current_cost, i, j, path = heapq.heappop(heap)
            
            # Skip if already visited
            if (i, j) in visited:
                continue
            visited.add((i, j))
            
            # Check if we've reached the end
            if i == self.len1 and j == self.len2:
                return current_cost, path
            
            # Explore all neighbors
            for neighbor in self.graph.neighbors((i, j)):
                edge_data = self.graph.get_edge_data((i, j), neighbor)
                new_cost = current_cost + edge_data['weight']
                
                # Determine operation type based on neighbor position
                di, dj = neighbor[0]-i, neighbor[1]-j
                if di == 1 and dj == 1:
                    op_type = 'match' if self.text1[i] == self.text2[j] else 'replace'
                    operation = (op_type, self.text1[i], self.text2[j], i, j)
                elif di == 1:
                    operation = ('delete', self.text1[i], i)
                else:  # dj == 1
                    operation = ('insert', self.text2[j], j)
                
                heapq.heappush(heap, (new_cost, neighbor[0], neighbor[1], path + [operation]))
        
        return float('inf'), []
    
    def _visualize_path(self, word1: str, word2: str, path: list) -> list:
        """Visualize the transformation steps between two words"""
        current_text = list(word1)
        steps = []
        
        for op in path:
            step = {}
            if op[0] == 'match':
                char1, char2 = op[1], op[2]  # کاراکترها را مستقیماً بگیرید
                step['op'] = f"Match '{char1}' with '{char2}'"
                step['text'] = ''.join(current_text)
                steps.append(step)
            
            elif op[0] == 'replace':
                char1, char2 = op[1], op[2]
                step['op'] = f"Replace '{char1}' with '{char2}'"
                # پیدا کردن موقعیت char1 در current_text و جایگزینی آن با char2
                if char1 in current_text:
                    idx = current_text.index(char1)
                    current_text[idx] = char2
                step['text'] = ''.join(current_text)
                steps.append(step)
            
            elif op[0] == 'delete':
                char = op[1]
                step['op'] = f"Delete '{char}'"
                if char in current_text:
                    current_text.remove(char)  # حذف اولین occurrence
                step['text'] = ''.join(current_text)
                steps.append(step)
            
            elif op[0] == 'insert':
                char = op[1]
                step['op'] = f"Insert '{char}'"
                current_text.append(char)  # یا در موقعیت خاصی insert کنید
                step['text'] = ''.join(current_text)
                steps.append(step)
        
        return steps
        
    def _draw_graph(self, graph, title, style, highlight_path=None) -> str:
        """Draw a graph and return as base64 image"""
        plt.figure(figsize=(12, 8))
        pos = nx.get_node_attributes(graph, 'pos')
        
        # Draw nodes
        nx.draw_networkx_nodes(
            graph, pos,
            node_size=style['node_size'],
            node_color=style['node_color'],
            alpha=0.9
        )
        
        # Draw edges with styles
        for edge_type, estyle in self.edge_styles.items():
            edges = [(u, v) for u, v, d in graph.edges(data=True) 
                    if d.get('operation', '').startswith(edge_type)]
            nx.draw_networkx_edges(
                graph, pos, edgelist=edges,
                edge_color=estyle['color'],
                width=estyle['width'],
                style=estyle['style'],
                arrows=True
            )
        
        # Highlight path if provided
        if highlight_path:
            path_edges = [(highlight_path[k], highlight_path[k+1]) 
                        for k in range(len(highlight_path)-1)]
            nx.draw_networkx_edges(
                graph, pos, edgelist=path_edges,
                edge_color='purple',
                width=4,
                style='solid',
                arrows=True
            )
        
        # Draw labels
        node_labels = {(i, j): f"({i},{j})" for i, j in graph.nodes()}
        nx.draw_networkx_labels(
            graph, pos,
            labels=node_labels,
            font_size=style['font_size']
        )
        
        edge_labels = nx.get_edge_attributes(graph, 'label')
        nx.draw_networkx_edge_labels(
            graph, pos,
            edge_labels=edge_labels,
            font_size=style['font_size']-2
        )
        
        plt.title(title, fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        buffer.seek(0)
        
        # Encode as base64
        return base64.b64encode(buffer.read()).decode('utf-8')

    def get_comparison_report(self, mode: str = 'standard') -> dict:
        """Generate a comprehensive comparison report"""
        # Get text comparison results
        h1, h2, cost, ops = self.compare_texts(mode)
        
        # Get graph visualizations
        graph_data = self.create_comparison_graph(mode)
        
        return {
            'text1': self.text1,
            'text2': self.text2,
            'highlighted_text1': ' '.join(h1),
            'highlighted_text2': ' '.join(h2),
            'total_cost': cost,
            'operations': ops,
            'global_graph': graph_data['global_comparison'],
            'word_graphs': graph_data['word_comparisons'],
            'mode': mode,
            'timestamp': datetime.now().isoformat()
        }


    def _build_graph(self):
        """Build the graph structure for text comparison"""
        graph = nx.DiGraph()
        
        # Add nodes with positions
        for i in range(self.len1 + 1):
            for j in range(self.len2 + 1):
                pos = (i, -j)  # Position for visualization
                graph.add_node((i, j), pos=pos)
        
        # Add edges with styles and weights
        for i in range(self.len1 + 1):
            for j in range(self.len2 + 1):
                if i < self.len1 and j < self.len2:
                    # Match/replace edge
                    cost = self._char_distance(self.text1[i], self.text2[j])
                    edge_type = 'match' if cost == 0 else 'replace'
                    graph.add_edge(
                        (i, j), (i+1, j+1),
                        weight=cost,
                        label=f"{edge_type}({cost})",
                        **self.edge_styles[edge_type]
                    )
                
                if i < self.len1:
                    # Delete edge
                    cost = self._delete_cost(self.text1[i])
                    graph.add_edge(
                        (i, j), (i+1, j),
                        weight=cost,
                        label=f"delete({cost})",
                        **self.edge_styles['delete']
                    )
                
                if j < self.len2:
                    # Insert edge
                    cost = self._insert_cost(self.text2[j])
                    graph.add_edge(
                        (i, j), (i, j+1),
                        weight=cost,
                        label=f"insert({cost})",
                        **self.edge_styles['insert']
                    )
        
        return graph

    def get_graph_image(self, highlight_path=None):
        """Generate a base64 encoded image of the graph with optional path highlighting"""
        plt.figure(figsize=(14, 10))
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, pos,
            **self.node_style
        )
        
        # Draw edges with their styles
        for edge_type, style in self.edge_styles.items():
            edges = [(u, v) for u, v, d in self.graph.edges(data=True) 
                    if d.get('operation') == edge_type]
            nx.draw_networkx_edges(
                self.graph, pos, edgelist=edges,
                edge_color=style['color'],
                width=style['width'],
                style=style['style'],
                arrows=True,
                arrowstyle='->',
                arrowsize=20
            )
        
        # Highlight the path if provided
        if highlight_path:
            path_edges = [(highlight_path[k], highlight_path[k+1]) 
                        for k in range(len(highlight_path)-1)]
            nx.draw_networkx_edges(
                self.graph, pos, edgelist=path_edges,
                edge_color='purple',
                width=4,
                style='solid',
                arrows=True,
                arrowstyle='->',
                arrowsize=25,
                alpha=0.8
            )
        
        # Draw labels
        node_labels = {(i, j): f"({i},{j})" for i, j in self.graph.nodes()}
        nx.draw_networkx_labels(
            self.graph, pos,
            labels=node_labels,
            font_size=10,
            font_color='black',
            font_weight='bold'
        )
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(
            self.graph, pos,
            edge_labels=edge_labels,
            font_size=8,
            font_color='black',
            bbox=dict(alpha=0.7)
        )
        
        plt.title(f"Text Comparison Graph\nText1: '{self.text1}'\nText2: '{self.text2}'")
        plt.grid(True, linestyle='--', alpha=0.5)
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        buffer.seek(0)
        
        # Encode as base64
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"