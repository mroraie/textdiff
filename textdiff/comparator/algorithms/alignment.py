# alignment.py
import logging
from typing import List, Tuple, Dict, Set
from collections import defaultdict
from comparator.algorithms.logs_setting import get_logger

# ایجاد logger برای این ماژول
logger = get_logger(__name__, 'alignment.log')  # بدون logging.

def levenshtein_with_path(seq1: List[str], seq2: List[str]) -> Tuple[int, List[Tuple[str, str, str]]]:
    """
    Compute Levenshtein distance with path of operations.
    Returns: (distance, operations)
    operations: list of tuples (op_type, token1, token2)
    """
    logger.info(f"Computing Levenshtein distance with path for sequences of lengths {len(seq1)} and {len(seq2)}")
    
    len1, len2 = len(seq1), len(seq2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    backtrack = [[None] * (len2 + 1) for _ in range(len1 + 1)]

    # Initialize DP table
    for i in range(len1 + 1):
        dp[i][0] = i
        backtrack[i][0] = ("delete", seq1[i - 1], "") if i > 0 else None
    for j in range(len2 + 1):
        dp[0][j] = j
        backtrack[0][j] = ("insert", "", seq2[j - 1]) if j > 0 else None

    # Fill DP table
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                backtrack[i][j] = ("match", seq1[i - 1], seq2[j - 1])
            else:
                # substitution
                sub = dp[i - 1][j - 1] + 1
                # deletion
                delete = dp[i - 1][j] + 1
                # insertion
                insert = dp[i][j - 1] + 1

                dp[i][j] = min(sub, delete, insert)
                if dp[i][j] == sub:
                    backtrack[i][j] = ("substitute", seq1[i - 1], seq2[j - 1])
                elif dp[i][j] == delete:
                    backtrack[i][j] = ("delete", seq1[i - 1], "")
                else:
                    backtrack[i][j] = ("insert", "", seq2[j - 1])

    # Backtrack to get operations
    operations = []
    i, j = len1, len2
    while i > 0 or j > 0:
        op = backtrack[i][j]
        operations.append(op)
        if op[0] == "match" or op[0] == "substitute":
            i -= 1
            j -= 1
        elif op[0] == "delete":
            i -= 1
        elif op[0] == "insert":
            j -= 1
    operations.reverse()

    logger.info(f"Levenshtein distance computed: {dp[len1][len2]}, operations count: {len(operations)}")
    return dp[len1][len2], operations


# alignment.py

from comparator.algorithms.constants import DIACRITICS, IGNORE_COST

# هزینه‌های عملیات
INSERT_COST = 2
DELETE_COST = 2
SUBSTITUTE_COST = 1

def align_words(words1, words2):
    """Align two sequences of words using dynamic programming"""
    logger.info(f"Aligning words: {len(words1)} vs {len(words2)} words")
    
    m, n = len(words1), len(words2)
    
    # Initialize DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill DP table
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j * INSERT_COST
            elif j == 0:
                dp[i][j] = i * DELETE_COST
            else:
                cost = _calculate_word_cost(words1[i-1], words2[j-1])
                dp[i][j] = min(
                    dp[i-1][j] + DELETE_COST,
                    dp[i][j-1] + INSERT_COST,
                    dp[i-1][j-1] + cost
                )
    
    # Backtrack to find alignment
    i, j = m, n
    aligned1, aligned2, operations = [], [], []
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + _calculate_word_cost(words1[i-1], words2[j-1]):
            aligned1.append(words1[i-1])
            aligned2.append(words2[j-1])
            cost = _calculate_word_cost(words1[i-1], words2[j-1])
            operations.append(('substitute' if cost > 0 else 'match', cost, cost))
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + DELETE_COST:
            aligned1.append(words1[i-1])
            aligned2.append("_")
            operations.append(('delete', DELETE_COST, DELETE_COST))
            i -= 1
        else:
            aligned1.append("_")
            aligned2.append(words2[j-1])
            operations.append(('insert', INSERT_COST, INSERT_COST))
            j -= 1
    
    result = (aligned1[::-1], aligned2[::-1], operations[::-1], dp[m][n])
    logger.info(f"Words aligned successfully. Total cost: {dp[m][n]}")
    return result

def _calculate_word_cost(word1, word2):
    """Calculate cost between two words considering diacritics"""
    logger.debug(f"Calculating cost between '{word1}' and '{word2}'")
    
    if word1 == word2:
        logger.debug("Words are identical, cost: 0")
        return 0
        
    cost = 0
    max_len = max(len(word1), len(word2))
    
    for i in range(max_len):
        char1 = word1[i] if i < len(word1) else ''
        char2 = word2[i] if i < len(word2) else ''
        
        # هزینه صفر برای علائم حرکتی
        if char1 in DIACRITICS or char2 in DIACRITICS:
            cost += IGNORE_COST
            logger.debug(f"Ignored diacritic: char1='{char1}', char2='{char2}'")
        elif char1 != char2:
            cost += SUBSTITUTE_COST
            logger.debug(f"Substitution cost added: '{char1}' != '{char2}'")
            
    logger.debug(f"Total cost calculated: {cost}")
    return cost


def align_words_with_similarity(words1: List[str], words2: List[str], 
                               similarity_threshold: float = 0.7) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """
    Align words based on similarity with threshold.
    
    Args:
        words1: First list of words
        words2: Second list of words
        similarity_threshold: Minimum similarity score for alignment
        
    Returns:
        aligned_pairs: List of (index1, index2) tuples for aligned words
        unaligned1: List of indices from words1 that couldn't be aligned
        unaligned2: List of indices from words2 that couldn't be aligned
    """
    logger.info(f"Aligning words with similarity threshold {similarity_threshold}: {len(words1)} vs {len(words2)} words")
    
    def word_similarity(w1: str, w2: str) -> float:
        """Calculate simple similarity between two words"""
        if w1 == w2:
            return 1.0
        if not w1 or not w2:
            return 0.0
        
        # Simple character-based similarity
        common_chars = len(set(w1) & set(w2))
        max_chars = max(len(set(w1)), len(set(w2)))
        similarity = common_chars / max_chars if max_chars > 0 else 0.0
        
        logger.debug(f"Similarity between '{w1}' and '{w2}': {similarity:.2f}")
        return similarity

    # Build similarity matrix
    similarity_matrix = {}
    for i, w1 in enumerate(words1):
        for j, w2 in enumerate(words2):
            similarity = word_similarity(w1, w2)
            if similarity >= similarity_threshold:
                similarity_matrix[(i, j)] = similarity

    # Greedy alignment
    aligned_pairs = []
    used_i = set()
    used_j = set()
    
    # Sort by similarity descending
    sorted_pairs = sorted(similarity_matrix.items(), key=lambda x: x[1], reverse=True)
    
    for (i, j), similarity in sorted_pairs:
        if i not in used_i and j not in used_j:
            aligned_pairs.append((i, j))
            used_i.add(i)
            used_j.add(j)
            logger.debug(f"Aligned word {i} ('{words1[i]}') with word {j} ('{words2[j]}'), similarity: {similarity:.2f}")

    # Find unaligned words
    unaligned1 = [i for i in range(len(words1)) if i not in used_i]
    unaligned2 = [j for j in range(len(words2)) if j not in used_j]

    logger.info(f"Alignment completed: {len(aligned_pairs)} pairs aligned, {len(unaligned1)} unaligned in first, {len(unaligned2)} unaligned in second")
    return aligned_pairs, unaligned1, unaligned2


def create_alignment_matrix(aligned_pairs: List[Tuple[int, int]], 
                           len1: int, len2: int) -> List[List[int]]:
    """
    Create an alignment matrix from aligned pairs.
    
    Args:
        aligned_pairs: List of (index1, index2) tuples
        len1: Length of first sequence
        len2: Length of second sequence
        
    Returns:
        matrix: 2D list where matrix[i][j] = 1 if aligned, 0 otherwise
    """
    logger.info(f"Creating alignment matrix: {len1}x{len2} with {len(aligned_pairs)} aligned pairs")
    
    matrix = [[0] * len2 for _ in range(len1)]
    for i, j in aligned_pairs:
        if i < len1 and j < len2:
            matrix[i][j] = 1
            logger.debug(f"Matrix position [{i}][{j}] set to 1")
    
    logger.info("Alignment matrix created successfully")
    return matrix

# لاگ‌گیری هنگام import ماژول
logger.info("alignment.py module imported successfully")

def align_texts_step_by_step(text1: str, text2: str) -> dict:
    """
    Align two texts step by step and return results of each alignment stage.
    
    Args:
        text1: First text to align
        text2: Second text to align
        
    Returns:
        Dictionary containing results of each alignment step
    """
    logger.info(f"Aligning texts step by step: '{text1}' and '{text2}'")
    
    # تقسیم متون به کلمات
    words1 = text1.split()
    words2 = text2.split()
    
    # مرحله 1: همترازی با الگوریتم لوناشتاین
    levenshtein_distance, levenshtein_operations = levenshtein_with_path(words1, words2)
    
    # مرحله 2: همترازی با در نظر گرفتن هزینه‌ها
    aligned1, aligned2, operations, total_cost = align_words(words1, words2)
    
    # مرحله 3: همترازی بر اساس شباهت
    similarity_pairs, unaligned1, unaligned2 = align_words_with_similarity(words1, words2)
    
    # مرحله 4: ایجاد ماتریس همترازی
    alignment_matrix = create_alignment_matrix(similarity_pairs, len(words1), len(words2))
    
    # محاسبه شباهت
    similarity_score = calculate_similarity_score(words1, words2, similarity_pairs)
    
    result = {
        'words1': words1,
        'words2': words2,
        'levenshtein_distance': levenshtein_distance,
        'levenshtein_operations': levenshtein_operations,
        'aligned_words1': aligned1,
        'aligned_words2': aligned2,
        'alignment_operations': operations,
        'alignment_cost': total_cost,
        'similarity_pairs': similarity_pairs,
        'unaligned_words1': unaligned1,
        'unaligned_words2': unaligned2,
        'alignment_matrix': alignment_matrix,
        'similarity_score': similarity_score
    }
    
    logger.info(f"Step-by-step alignment completed. Similarity: {similarity_score:.2f}")
    return result


def calculate_similarity_score(words1: List[str], words2: List[str], 
                              similarity_pairs: List[Tuple[int, int]]) -> float:
    """
    Calculate similarity score based on aligned pairs.
    
    Args:
        words1: First list of words
        words2: Second list of words
        similarity_pairs: List of aligned pairs
        
    Returns:
        Similarity score between 0 and 1
    """
    if not words1 and not words2:
        return 1.0
    
    max_len = max(len(words1), len(words2))
    if max_len == 0:
        return 1.0
    
    similarity = len(similarity_pairs) / max_len
    logger.debug(f"Similarity score calculated: {similarity:.2f} ({len(similarity_pairs)}/{max_len})")
    return similarity