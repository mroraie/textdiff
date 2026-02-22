"""
Unit tests for text comparison algorithms.

This module contains comprehensive unit tests for:
- Preprocessing functions (cleaning, phonetic conversion)
- Text comparison algorithms
- Alignment algorithms
- Highlighting functions
- Report generation
"""

from django.test import TestCase, RequestFactory
from django.contrib.messages import get_messages
from unittest.mock import Mock, patch

from comparator.algorithms.preprocessing import (
    clean_word,
    get_removed_chars,
    is_diacritic,
    is_phonetically_silent_vav,
    convert_to_phonetic,
    process_text_step_by_step,
    validate_text_length,
)
from comparator.algorithms.comparator import TextComparator
from comparator.algorithms.alignment import (
    levenshtein_with_path,
    align_words,
    align_words_with_similarity,
    create_alignment_matrix,
    calculate_similarity_score,
    align_texts_step_by_step,
    compute_levenshtein_with_path,
)
from comparator.algorithms.highlighting import (
    highlight_differences,
    highlight_aligned_words,
)
from comparator.algorithms.report import (
    generate_comparison_report,
    save_report_to_markdown,
)
from comparator.algorithms.constants import DIACRITICS, PHONETIC_MAPPING


class PreprocessingTests(TestCase):
    """Tests for preprocessing functions"""

    def test_clean_word_removes_diacritics(self):
        """Test that clean_word removes diacritics correctly"""
        word = "کتابَ"
        cleaned, removed = clean_word(word)
        self.assertIn("َ", removed)
        self.assertNotIn("َ", cleaned)

    def test_clean_word_preserves_main_chars(self):
        """Test that clean_word preserves main characters"""
        word = "سلام"
        cleaned, removed = clean_word(word)
        self.assertEqual(cleaned, "سلام")
        self.assertEqual(len(removed), 0)

    def test_clean_word_with_punctuation(self):
        """Test clean_word with punctuation"""
        word = "سلام،"
        cleaned, removed = clean_word(word)
        self.assertIn("،", removed)

    def test_get_removed_chars(self):
        """Test get_removed_chars function"""
        word = "کتابَ"
        removed = get_removed_chars(word)
        self.assertIn("َ", removed)

    def test_is_diacritic(self):
        """Test is_diacritic function"""
        self.assertTrue(is_diacritic("َ"))
        self.assertTrue(is_diacritic("ُ"))
        self.assertTrue(is_diacritic("ِ"))
        self.assertFalse(is_diacritic("ا"))
        self.assertFalse(is_diacritic("ب"))

    def test_is_phonetically_silent_vav_in_khwa(self):
        """Test silent vav detection in 'خوا' pattern"""
        self.assertTrue(is_phonetically_silent_vav("خوا", 1))
        self.assertFalse(is_phonetically_silent_vav("خوا", 0))
        self.assertFalse(is_phonetically_silent_vav("خوا", 2))

    def test_is_phonetically_silent_vav_after_consonants(self):
        """Test silent vav after specific consonants"""
        self.assertTrue(is_phonetically_silent_vav("خوا", 1))
        self.assertTrue(is_phonetically_silent_vav("حوا", 1))
        self.assertFalse(is_phonetically_silent_vav("بوا", 1))

    def test_is_phonetically_silent_vav_invalid_input(self):
        """Test silent vav with invalid input"""
        self.assertFalse(is_phonetically_silent_vav("سلام", 0))
        self.assertFalse(is_phonetically_silent_vav(None, 0))
        self.assertFalse(is_phonetically_silent_vav("", 0))

    def test_convert_to_phonetic_basic(self):
        """Test basic phonetic conversion"""
        text = "سلام"
        phonetic = convert_to_phonetic(text)
        self.assertIsInstance(phonetic, str)
        self.assertGreater(len(phonetic), 0)

    def test_convert_to_phonetic_vav_conversion(self):
        """Test vav conversion in phonetic"""
        text = "خوا"
        phonetic = convert_to_phonetic(text)
        # Should convert و to 'u' after خ
        self.assertIn('u', phonetic or '')

    def test_convert_to_phonetic_diacritics_ignored(self):
        """Test that diacritics are ignored in phonetic conversion"""
        text = "کتابَ"
        phonetic = convert_to_phonetic(text)
        # Diacritics should not appear in phonetic output
        for diacritic in DIACRITICS:
            self.assertNotIn(diacritic, phonetic)

    def test_process_text_step_by_step(self):
        """Test process_text_step_by_step function"""
        text = "سلام دنیا"
        result = process_text_step_by_step(text)
        
        self.assertIn('original_text', result)
        self.assertIn('cleaned_text', result)
        self.assertIn('phonetic_text', result)
        self.assertIn('word_details', result)
        
        self.assertEqual(result['original_text'], text)
        self.assertIsInstance(result['word_details'], list)
        self.assertGreater(len(result['word_details']), 0)

    def test_process_text_step_by_step_empty(self):
        """Test process_text_step_by_step with empty text"""
        text = ""
        result = process_text_step_by_step(text)
        self.assertEqual(result['original_text'], "")
        self.assertEqual(result['cleaned_text'], "")


class TextComparatorTests(TestCase):
    """Tests for TextComparator class"""

    def test_text_comparator_init(self):
        """Test TextComparator initialization"""
        text1 = "سلام"
        text2 = "سلامت"
        comparator = TextComparator(text1, text2)
        
        self.assertEqual(comparator.text1, text1)
        self.assertEqual(comparator.text2, text2)
        self.assertIsInstance(comparator.words1, list)
        self.assertIsInstance(comparator.words2, list)

    def test_calculate_word_cost_identical(self):
        """Test word cost calculation for identical words"""
        comparator = TextComparator("test", "test")
        cost = comparator._calculate_word_cost("سلام", "سلام")
        self.assertEqual(cost, 0)

    def test_calculate_word_cost_different(self):
        """Test word cost calculation for different words"""
        comparator = TextComparator("test", "test")
        cost = comparator._calculate_word_cost("سلام", "سلامت")
        self.assertGreater(cost, 0)

    def test_compare_texts_standard_mode(self):
        """Test text comparison in standard mode"""
        text1 = "سلام دنیا"
        text2 = "سلامت دنیا"
        comparator = TextComparator(text1, text2)
        
        highlighted1, highlighted2, cost, operations = comparator.compare_texts(mode="standard")
        
        self.assertIsInstance(highlighted1, list)
        self.assertIsInstance(highlighted2, list)
        self.assertIsInstance(cost, (int, float))
        self.assertIsInstance(operations, list)

    def test_compare_texts_phonetic_mode(self):
        """Test text comparison in phonetic mode"""
        text1 = "سلام"
        text2 = "سلام"
        comparator = TextComparator(text1, text2)
        
        highlighted1, highlighted2, cost, operations = comparator.compare_texts(mode="phonetic")
        
        self.assertIsInstance(highlighted1, list)
        self.assertIsInstance(highlighted2, list)
        self.assertIsInstance(cost, (int, float))

    def test_compare_all_modes(self):
        """Test compare_all_modes function"""
        text1 = "سلام"
        text2 = "سلامت"
        comparator = TextComparator(text1, text2)
        
        results = comparator.compare_all_modes()
        
        self.assertIn("standard", results)
        self.assertIn("phonetic", results)
        self.assertIn("persian", results)
        
        for mode, result in results.items():
            self.assertIn("highlighted1", result)
            self.assertIn("highlighted2", result)
            self.assertIn("total_cost", result)
            self.assertIn("operations", result)


class AlignmentTests(TestCase):
    """Tests for alignment algorithms"""

    def test_levenshtein_with_path_identical(self):
        """Test Levenshtein distance for identical sequences"""
        seq1 = ["سلام", "دنیا"]
        seq2 = ["سلام", "دنیا"]
        distance, operations = levenshtein_with_path(seq1, seq2)
        
        self.assertEqual(distance, 0)
        self.assertIsInstance(operations, list)

    def test_levenshtein_with_path_different(self):
        """Test Levenshtein distance for different sequences"""
        seq1 = ["سلام"]
        seq2 = ["سلامت"]
        distance, operations = levenshtein_with_path(seq1, seq2)
        
        self.assertGreater(distance, 0)
        self.assertIsInstance(operations, list)

    def test_levenshtein_with_path_empty(self):
        """Test Levenshtein distance with empty sequences"""
        seq1 = []
        seq2 = ["سلام"]
        distance, operations = levenshtein_with_path(seq1, seq2)
        
        self.assertEqual(distance, 1)
        self.assertIsInstance(operations, list)

    def test_align_words_identical(self):
        """Test word alignment for identical texts"""
        words1 = ["سلام", "دنیا"]
        words2 = ["سلام", "دنیا"]
        aligned1, aligned2, operations, cost = align_words(words1, words2)
        
        self.assertEqual(len(aligned1), len(aligned2))
        self.assertIsInstance(operations, list)
        self.assertIsInstance(cost, (int, float))

    def test_align_words_different(self):
        """Test word alignment for different texts"""
        words1 = ["سلام"]
        words2 = ["سلامت"]
        aligned1, aligned2, operations, cost = align_words(words1, words2)
        
        self.assertEqual(len(aligned1), len(aligned2))
        self.assertGreater(cost, 0)

    def test_align_words_with_similarity(self):
        """Test word alignment with similarity threshold"""
        words1 = ["سلام", "دنیا"]
        words2 = ["سلامت", "دنیا"]
        pairs, unaligned1, unaligned2 = align_words_with_similarity(words1, words2)
        
        self.assertIsInstance(pairs, list)
        self.assertIsInstance(unaligned1, list)
        self.assertIsInstance(unaligned2, list)

    def test_create_alignment_matrix(self):
        """Test alignment matrix creation"""
        pairs = [(0, 0), (1, 1)]
        len1, len2 = 2, 2
        matrix = create_alignment_matrix(pairs, len1, len2)
        
        self.assertEqual(len(matrix), len1)
        self.assertEqual(len(matrix[0]), len2)
        self.assertEqual(matrix[0][0], 1)
        self.assertEqual(matrix[1][1], 1)

    def test_calculate_similarity_score(self):
        """Test similarity score calculation"""
        words1 = ["سلام", "دنیا"]
        words2 = ["سلام", "دنیا"]
        pairs = [(0, 0), (1, 1)]
        score = calculate_similarity_score(words1, words2, pairs)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    def test_calculate_similarity_score_empty(self):
        """Test similarity score with empty inputs"""
        words1 = []
        words2 = []
        pairs = []
        score = calculate_similarity_score(words1, words2, pairs)
        self.assertEqual(score, 1.0)

    def test_align_texts_step_by_step(self):
        """Test step-by-step text alignment"""
        text1 = "سلام دنیا"
        text2 = "سلامت دنیا"
        result = align_texts_step_by_step(text1, text2)
        
        self.assertIn('words1', result)
        self.assertIn('words2', result)
        self.assertIn('levenshtein_distance', result)
        self.assertIn('aligned_words1', result)
        self.assertIn('aligned_words2', result)
        self.assertIn('similarity_score', result)

    def test_compute_levenshtein_with_path_wrapper(self):
        """Test compute_levenshtein_with_path wrapper"""
        seq1 = ["سلام"]
        seq2 = ["سلامت"]
        distance, operations = compute_levenshtein_with_path(seq1, seq2)
        
        self.assertIsInstance(distance, int)
        self.assertIsInstance(operations, list)


class HighlightingTests(TestCase):
    """Tests for highlighting functions"""

    def test_highlight_differences_identical(self):
        """Test highlighting for identical words"""
        word1 = "سلام"
        word2 = "سلام"
        h1, h2, ops = highlight_differences(word1, word2)
        
        self.assertIsInstance(h1, list)
        self.assertIsInstance(h2, list)
        self.assertIsInstance(ops, list)

    def test_highlight_differences_different(self):
        """Test highlighting for different words"""
        word1 = "سلام"
        word2 = "سلامت"
        h1, h2, ops = highlight_differences(word1, word2)
        
        self.assertIsInstance(h1, list)
        self.assertIsInstance(h2, list)
        self.assertGreater(len(ops), 0)

    def test_highlight_differences_empty(self):
        """Test highlighting with empty words"""
        word1 = ""
        word2 = "سلام"
        h1, h2, ops = highlight_differences(word1, word2)
        
        self.assertIsInstance(h1, list)
        self.assertIsInstance(h2, list)

    def test_highlight_differences_phonetic_mode(self):
        """Test highlighting in phonetic mode"""
        word1 = "سلام"
        word2 = "سلام"
        h1, h2, ops = highlight_differences(word1, word2, phonetic_mode=True)
        
        self.assertIsInstance(h1, list)
        self.assertIsInstance(h2, list)

    def test_highlight_aligned_words(self):
        """Test highlighting for aligned words"""
        aligned1 = ["سلام", "دنیا"]
        aligned2 = ["سلامت", "دنیا"]
        pairs = [(0, 0), (1, 1)]
        h1, h2, ops = highlight_aligned_words(aligned1, aligned2, pairs)
        
        self.assertIsInstance(h1, list)
        self.assertIsInstance(h2, list)
        self.assertIsInstance(ops, list)
        self.assertEqual(len(h1), len(pairs))
        self.assertEqual(len(h2), len(pairs))


class ReportTests(TestCase):
    """Tests for report generation functions"""

    def test_generate_comparison_report(self):
        """Test comparison report generation"""
        text1 = "سلام"
        text2 = "سلامت"
        highlighted1 = ["سلام"]
        highlighted2 = ["سلامت"]
        operations = [("substitute", "لام", "لامت")]
        cost = 1
        
        report = generate_comparison_report(
            text1, text2, highlighted1, highlighted2, operations, cost, "standard"
        )
        
        self.assertIn('text1', report)
        self.assertIn('text2', report)
        self.assertIn('highlighted_text1', report)
        self.assertIn('highlighted_text2', report)
        self.assertIn('total_cost', report)
        self.assertIn('operations', report)
        self.assertIn('mode', report)
        self.assertIn('timestamp', report)

    def test_save_report_to_markdown(self):
        """Test saving report to markdown file"""
        report = {
            'text1': 'سلام',
            'text2': 'سلامت',
            'highlighted_text1': 'سلام',
            'highlighted_text2': 'سلامت',
            'total_cost': 1,
            'operations': [('substitute', 'لام', 'لامت')],
            'mode': 'standard',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        filepath = save_report_to_markdown(report)
        
        self.assertIsInstance(filepath, str)
        self.assertIn('reports', filepath)
        self.assertIn('.md', filepath)
        
        # Clean up
        import os
        if os.path.exists(filepath):
            os.remove(filepath)
        if os.path.exists('reports') and not os.listdir('reports'):
            os.rmdir('reports')


class ValidationTests(TestCase):
    """Tests for validation decorator"""

    def setUp(self):
        """Set up test fixtures"""
        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.test import RequestFactory
        
        self.factory = RequestFactory()
        # Add middleware to support messages
        self.middleware = MessageMiddleware(lambda req: None)
        self.session_middleware = SessionMiddleware(lambda req: None)

    @patch('comparator.algorithms.preprocessing.MAX_TEXT_LENGTH', 100)
    @patch('comparator.algorithms.preprocessing.MAX_WORDS', 50)
    def test_validate_text_length_valid(self):
        """Test validation with valid text length"""
        @validate_text_length
        def test_view(request):
            return "OK"
        
        request = self.factory.post('/', {'text1': 'سلام', 'text2': 'دنیا'})
        self.session_middleware.process_request(request)
        self.middleware.process_request(request)
        result = test_view(request)
        self.assertEqual(result, "OK")

    @patch('comparator.algorithms.preprocessing.MAX_TEXT_LENGTH', 5)
    @patch('comparator.algorithms.preprocessing.MAX_WORDS', 50)
    @patch('comparator.algorithms.preprocessing.messages')
    @patch('comparator.algorithms.preprocessing.redirect')
    def test_validate_text_length_too_long(self, mock_redirect, mock_messages):
        """Test validation with text too long"""
        mock_redirect.return_value = "REDIRECT"
        
        @validate_text_length
        def test_view(request):
            return "OK"
        
        request = self.factory.post('/', {
            'text1': 'این یک متن خیلی طولانی است',
            'text2': 'دنیا'
        })
        self.session_middleware.process_request(request)
        self.middleware.process_request(request)
        result = test_view(request)
        # Should redirect, not return "OK"
        self.assertNotEqual(result, "OK")
        mock_redirect.assert_called_once()

    @patch('comparator.algorithms.preprocessing.MAX_TEXT_LENGTH', 100)
    @patch('comparator.algorithms.preprocessing.MAX_WORDS', 2)
    @patch('comparator.algorithms.preprocessing.messages')
    @patch('comparator.algorithms.preprocessing.redirect')
    def test_validate_text_length_too_many_words(self, mock_redirect, mock_messages):
        """Test validation with too many words"""
        mock_redirect.return_value = "REDIRECT"
        
        @validate_text_length
        def test_view(request):
            return "OK"
        
        request = self.factory.post('/', {
            'text1': 'این یک متن با کلمات زیاد است',
            'text2': 'دنیا'
        })
        self.session_middleware.process_request(request)
        self.middleware.process_request(request)
        result = test_view(request)
        # Should redirect, not return "OK"
        self.assertNotEqual(result, "OK")
        mock_redirect.assert_called_once()

    @patch('comparator.algorithms.preprocessing.MAX_TEXT_LENGTH', 100)
    @patch('comparator.algorithms.preprocessing.MAX_WORDS', 50)
    def test_validate_text_length_get_request(self):
        """Test validation with GET request"""
        @validate_text_length
        def test_view(request):
            return "OK"
        
        request = self.factory.get('/', {'text1': 'سلام', 'text2': 'دنیا'})
        self.session_middleware.process_request(request)
        self.middleware.process_request(request)
        result = test_view(request)
        self.assertEqual(result, "OK")


class IntegrationTests(TestCase):
    """Integration tests for complete workflows"""

    def test_full_comparison_workflow(self):
        """Test complete text comparison workflow"""
        text1 = "سلام دنیا"
        text2 = "سلامت دنیا"
        
        # Step 1: Preprocessing
        processed1 = process_text_step_by_step(text1)
        processed2 = process_text_step_by_step(text2)
        
        # Step 2: Comparison
        comparator = TextComparator(text1, text2)
        highlighted1, highlighted2, cost, operations = comparator.compare_texts()
        
        # Step 3: Alignment
        alignment_result = align_texts_step_by_step(text1, text2)
        
        # Step 4: Report
        report = generate_comparison_report(
            text1, text2, highlighted1, highlighted2, operations, cost, "standard",
            processed1, processed2
        )
        
        # Verify all steps completed
        self.assertIsNotNone(processed1)
        self.assertIsNotNone(processed2)
        self.assertIsNotNone(highlighted1)
        self.assertIsNotNone(highlighted2)
        self.assertIsNotNone(alignment_result)
        self.assertIsNotNone(report)

    def test_phonetic_comparison_workflow(self):
        """Test complete phonetic comparison workflow"""
        text1 = "سلام"
        text2 = "سلام"
        
        # Preprocessing
        processed1 = process_text_step_by_step(text1)
        phonetic1 = processed1['phonetic_text']
        
        # Comparison in phonetic mode
        comparator = TextComparator(text1, text2)
        highlighted1, highlighted2, cost, operations = comparator.compare_texts(mode="phonetic")
        
        # Verify phonetic processing
        self.assertIsNotNone(phonetic1)
        self.assertIsInstance(cost, (int, float))
        self.assertIsInstance(operations, list)
