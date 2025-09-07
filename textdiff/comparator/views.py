import os
import json
import logging
from datetime import datetime

import jdatetime
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.utils.http import urlencode

from comparator.algorithms.comparator import TextComparator
from comparator.algorithms.preprocessing import process_text_step_by_step
from comparator.algorithms.alignment import align_texts_step_by_step , compute_levenshtein_with_path
from comparator.algorithms.report import (
    generate_comparison_report,
    save_report_to_markdown,
)
from comparator.algorithms.constants import PHONETIC_MAPPING, DEFAULT_PHONETIC
from textdiff.settings import MAX_TEXT_LENGTH, MAX_WORDS

logger = logging.getLogger(__name__)


def validate_text_length(view_func):
    def wrapper(request, *args, **kwargs):
        text1 = request.POST.get("text1", "") or request.GET.get("text1", "")
        text2 = request.POST.get("text2", "") or request.GET.get("text2", "")

        if len(text1) > MAX_TEXT_LENGTH or len(text2) > MAX_TEXT_LENGTH:
            messages.error(
                request,
                f"Text too long. Maximum allowed is {MAX_TEXT_LENGTH} characters.",
            )
            return redirect("index")

        if len(text1.split()) > MAX_WORDS or len(text2.split()) > MAX_WORDS:
            messages.error(
                request,
                f"Too many words. Maximum allowed is {MAX_WORDS} words.",
            )
            return redirect("index")

        return view_func(request, *args, **kwargs)

    return wrapper


@require_http_methods(["GET", "POST"])
def index(request):
    if request.method == "POST":
        text1 = request.POST.get("text1", "").strip()
        text2 = request.POST.get("text2", "").strip()

        if not text1 or not text2:
            messages.error(request, "Please enter both texts.")
            return render(request, "index.html", {"now": datetime.now()})

        query_string = urlencode({"text1": text1, "text2": text2})
        return redirect(reverse("compare") + f"?{query_string}")

    return render(request, "index.html", {"now": datetime.now()})


def compare(request):
    text1 = request.GET.get("text1", "").strip()
    text2 = request.GET.get("text2", "").strip()

    if not text1 or not text2:
        messages.error(request, "No text found for comparison.")
        return redirect("index")

    # Validate text length
    if len(text1) > MAX_TEXT_LENGTH or len(text2) > MAX_TEXT_LENGTH:
        messages.error(request, f"Texts must be shorter than {MAX_TEXT_LENGTH} characters.")
        return redirect("index")
    
    # Validate word count
    word_count1 = len(text1.split())
    word_count2 = len(text2.split())
    if word_count1 > MAX_WORDS or word_count2 > MAX_WORDS:
        messages.error(request, f"Texts must contain fewer than {MAX_WORDS} words.")
        return redirect("index")

    try:
        comparator = TextComparator(text1, text2)
        processing_steps_1 = process_text_step_by_step(text1)
        processing_steps_2 = process_text_step_by_step(text2)
        alignment_steps = align_texts_step_by_step(text1, text2)

        # Standard comparison
        highlighted_std1, highlighted_std2, cost_std, ops_std = comparator.compare_texts(mode="standard")
        
        # Phonetic comparison
        highlighted_ph1, highlighted_ph2, cost_ph, ops_ph = comparator.compare_texts(mode="phonetic")
        
        # Phonetic1 comparison
        highlighted_p1, highlighted_p2, cost_p1, ops_p1 = comparator.compare_texts(mode="phonetic1")
        
        # Persian comparison
        highlighted_per1, highlighted_per2, cost_per, ops_per = comparator.compare_texts(mode="persian")

        # Create operations table for standard comparison
        operations_table = []
        for i, (w1, w2, op) in enumerate(zip(highlighted_std1, highlighted_std2, ops_std), start=1):
            if isinstance(op, tuple) and len(op) >= 3:
                op_type, _, _ = op
                if op_type == "match":
                    description = f"Words match at position {i}"
                elif op_type == "substitute":
                    description = f"Substitute '{w1}' with '{w2}' at position {i}"
                elif op_type == "insert":
                    description = f"Insert '{w2}' at position {i}"
                elif op_type == "delete":
                    description = f"Delete '{w1}' at position {i}"
                else:
                    description = f"Operation '{op_type}' at position {i}"
            else:
                description = f"Unknown operation at position {i}"

            operations_table.append({
                "num": i,
                "word1": w1,
                "word2": w2,
                "operation": str(op),
                "description": description,
            })

        # Create phonetic operations table
        phonetic_operations_table = []
        for i, (w1, w2, op) in enumerate(zip(highlighted_ph1, highlighted_ph2, ops_ph), start=1):
            if isinstance(op, tuple) and len(op) >= 3:
                op_type, _, _ = op
                if op_type == "match":
                    description = f"Phonetic match at position {i}"
                elif op_type == "substitute":
                    description = f"Phonetic substitute '{w1}' with '{w2}' at position {i}"
                elif op_type == "insert":
                    description = f"Phonetic insert '{w2}' at position {i}"
                elif op_type == "delete":
                    description = f"Phonetic delete '{w1}' at position {i}"
                else:
                    description = f"Phonetic operation '{op_type}' at position {i}"
            else:
                description = f"Unknown phonetic operation at position {i}"

            phonetic_operations_table.append({
                "num": i,
                "word1": w1,
                "word2": w2,
                "operation": str(op),
                "description": description,
            })

        # Character comparison table
        char_table = []
        max_len = max(len(text1), len(text2))
        for i in range(max_len):
            char1 = text1[i] if i < len(text1) else ""
            char2 = text2[i] if i < len(text2) else ""
            char_table.append((char1, char2))

        # Phonetic character conversion
        def get_phonetic_representation(char):
            return PHONETIC_MAPPING.get(char, DEFAULT_PHONETIC)

        def text_to_phonetic_chars(text):
            phonetic_text = []
            for char in text:
                phonetic_char = get_phonetic_representation(char)
                if phonetic_char and phonetic_char != DEFAULT_PHONETIC:
                    phonetic_text.append(phonetic_char)
                elif phonetic_char == " ":
                    phonetic_text.append(" ")
            return phonetic_text

        phonetic_chars1 = text_to_phonetic_chars(text1)
        phonetic_chars2 = text_to_phonetic_chars(text2)

        phonetic_char_table = []
        max_phonetic_len = max(len(phonetic_chars1), len(phonetic_chars2))
        for i in range(max_phonetic_len):
            char1 = phonetic_chars1[i] if i < len(phonetic_chars1) else ""
            char2 = phonetic_chars2[i] if i < len(phonetic_chars2) else ""
            phonetic_char_table.append((char1, char2))

        # Word transformation data for visualization
        word_transformation_data = []
        for i, (word1, word2, op) in enumerate(zip(highlighted_std1, highlighted_std2, ops_std)):
            if isinstance(op, tuple) and len(op) >= 3:
                op_type, _, _ = op
                operations_list = []
                if op_type == "match":
                    operations_list = ["Match"] * min(len(word1), len(word2))
                elif op_type == "substitute":
                    operations_list = ["Substitute"] * min(len(word1), len(word2))
                elif op_type == "insert":
                    operations_list = ["Insert"] * len(word2)
                elif op_type == "delete":
                    operations_list = ["Delete"] * len(word1)

                word_transformation_data.append({
                    "word1": word1,
                    "word2": word2,
                    "operations": operations_list,
                    "index": i,
                })

        # Get current time in Jalali calendar
        now_gregorian = datetime.now()
        now_jalali = jdatetime.datetime.fromgregorian(datetime=now_gregorian)
        now_jalali_str = now_jalali.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate Levenshtein distance
        distance, operations = compute_levenshtein_with_path(text1, text2)

        # Prepare context
        context = {
            "highlighted1": highlighted_std1,
            "highlighted2": highlighted_std2,
            "operations_table": operations_table,
            "total_cost": cost_std,
            "phonetic_lis1": highlighted_ph1,
            "phonetic_lis2": highlighted_ph2,
            "phonetic_operations_table": phonetic_operations_table,
            "phonetic_cost": cost_ph,

            "phonetic1_cost": cost_p1,
            "phonetic1_similarity": round(
                (1 - cost_p1 / max(len(text1.split()), len(text2.split()))) * 100, 2
            ) if max(len(text1.split()), len(text2.split())) > 0 else 100,
            "persian_lis1": highlighted_per1,
            "persian_lis2": highlighted_per2,
            "persian_cost": cost_per,
            "persian_similarity": round(
                (1 - cost_per / max(len(text1.split()), len(text2.split()))) * 100, 2
            ) if max(len(text1.split()), len(text2.split())) > 0 else 100,
            "char_table": char_table,
            "phonetic_char_table": phonetic_char_table,
            "word_transformation_data": json.dumps(word_transformation_data),
            "text1": text1,
            "text2": text2,
            "text1_word_count": word_count1,
            "text2_word_count": word_count2,
            "now": now_jalali_str,
            "max_text_length": MAX_TEXT_LENGTH,
            "max_words": MAX_WORDS,
            "processing_steps_1": processing_steps_1,
            "processing_steps_2": processing_steps_2,
            "alignment_steps": alignment_steps,
            "levenshtein_distance": distance,
            "levenshtein_operations": operations,
        }

        return render(request, "results.html", context)

    except Exception as e:
        logger.error(f"Error during comparison: {str(e)}", exc_info=True)
        messages.error(request, f"Error processing texts: {str(e)}")
        return redirect("index")



@require_http_methods(["POST"])
def api_compare(request):
    text1 = request.POST.get("text1", "").strip()
    text2 = request.POST.get("text2", "").strip()

    if not text1 or not text2:
        return JsonResponse({"error": "Both texts are required"}, status=400)

    try:
        comparator = TextComparator(text1, text2)
        highlighted1, highlighted2, total_cost, operations = comparator.compare_texts(
            mode="standard"
        )
        report = generate_comparison_report(
            text1=text1,
            text2=text2,
            highlighted_text1=highlighted1,
            highlighted_text2=highlighted2,
            operations=operations,
            total_cost=total_cost,
        )

        return JsonResponse(
            {
                "text1": text1,
                "text2": text2,
                "highlighted_text1": report["highlighted_text1"],
                "highlighted_text2": report["highlighted_text2"],
                "total_cost": report["total_cost"],
                "operations": report["operations"],
                "similarity": round(
                    (1 - report["total_cost"] / max(len(text1), len(text2))) * 100, 2
                ),
            }
        )
    except Exception as e:
        logger.error(f"API Error: {str(e)}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@validate_text_length
def download_report_view(request):
    text1 = request.GET.get("text1", "").strip()
    text2 = request.GET.get("text2", "").strip()

    if not text1 or not text2:
        messages.error(request, "No text found for comparison.")
        return redirect("index")

    try:
        comparator = TextComparator(text1, text2)
        highlighted1, highlighted2, total_cost, operations = comparator.compare_texts(
            mode="standard"
        )

        report = generate_comparison_report(
            text1=text1,
            text2=text2,
            highlighted_text1=highlighted1,
            highlighted_text2=highlighted2,
            operations=operations,
            total_cost=total_cost,
            mode="standard",
        )

        filepath = save_report_to_markdown(report)
        filename = os.path.basename(filepath)
        return FileResponse(open(filepath, "rb"), as_attachment=True, filename=filename)

    except Exception as e:
        logger.error(
            f"Error generating downloadable report: {str(e)}", exc_info=True
        )
        messages.error(request, "Error generating report. Please try again.")
        return redirect("index")

def _generate_phonetic_graph_data(text1, text2):
    """ایجاد داده‌های گراف برای مقایسه آوایی"""
    # تبدیل متن به نمایش آوایی (فونتیک)
    phonetic1 = _convert_to_phonetic(text1)
    phonetic2 = _convert_to_phonetic(text2)
    
    # فقط از منطق کلمه استفاده می‌کنیم
    return _generate_word_graph_data(phonetic1, phonetic2)

def _generate_persian_graph_data(text1, text2):
    """ایجاد داده‌های گراف برای پردازش ویژه فارسی"""
    # پردازش ویژه برای زبان فارسی (مثلاً نرمال‌سازی)
    processed1 = _normalize_persian_text(text1)
    processed2 = _normalize_persian_text(text2)
    
    # فقط از منطق کلمه استفاده می‌کنیم
    return _generate_word_graph_data(processed1, processed2)

def _convert_to_phonetic(text):
    """تبدیل متن به نمایش آوایی (فونتیک)"""
    # اینجا باید الگوریتم تبدیل به فونتیک را پیاده‌سازی کنید
    # این یک پیاده‌سازی ساده است که باید با الگوریتم واقعی جایگزین شود
    phonetic_map = {
        'c': 'k', 'q': 'k', 'x': 'ks',
        'ph': 'f', 'gh': 'g', 'rh': 'r',
        # می‌توانید نقشه کاملتری ایجاد کنید
    }
    
    result = text.lower()
    for key, value in phonetic_map.items():
        result = result.replace(key, value)
    
    return result

def _normalize_persian_text(text):
    """نرمال‌سازی متن فارسی"""
    # نرمال‌سازی حروف فارسی (مثلاً حروف مختلف با یک شکل)
    normalization_map = {
        'ك': 'ک', 'ي': 'ی', 'ة': 'ه', 'ۀ': 'ه',
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ؤ': 'و',
        'ئ': 'ی', '': ''
    }
    
    result = text
    for key, value in normalization_map.items():
        result = result.replace(key, value)
    
    return result

def graph_view(request):
    text1 = request.GET.get('text1', '')
    text2 = request.GET.get('text2', '')
    
    context = {
        'text1': text1,
        'text2': text2,
    }
    return render(request, 'graph.html', context)


def api_graph_data(request):
    text1 = request.GET.get('text1', '')
    text2 = request.GET.get('text2', '')
    mode = request.GET.get('mode', 'standard')  # دریافت پارامتر mode
    
    try:
        if mode == 'phonetic':
            # پردازش فونتیک (آوایی)
            graph_data = _generate_phonetic_graph_data(text1, text2)
        elif mode == 'persian':
            # پردازش ویژه فارسی
            graph_data = _generate_persian_graph_data(text1, text2)
        else:
            # حالت استاندارد
            graph_data = _generate_word_graph_data(text1, text2)
        
        return JsonResponse(graph_data)
        
    except Exception as e:
        logger.error(f"Error generating graph data: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def _generate_word_graph_data(word1, word2):
    operations = _simulate_word_operations(word1, word2)
    
    nodes = []
    edges = []
    
    nodes.append({
        'id': 'source_text',
        'label': word1,
        'type': 'source_text',
        'color': '#69b3a2',
        'size': 25
    })
    
    nodes.append({
        'id': 'target_text',
        'label': word2,
        'type': 'target_text',
        'color': '#ff6b6b',
        'size': 25
    })
    
    for i, char in enumerate(word1):
        node_id = f"src_char_{i}"
        nodes.append({
            'id': node_id,
            'label': char,
            'type': 'source_char',
            'color': '#a1d99b',
            'size': 15,
            'position': i
        })
        
        edges.append({
            'source': 'source_text',
            'target': node_id,
            'label': 'contains',
            'color': '#69b3a2',
            'width': 1,
            'dashes': True
        })
    
    for j, char in enumerate(word2):
        node_id = f"tgt_char_{j}"
        nodes.append({
            'id': node_id,
            'label': char,
            'type': 'target_char',
            'color': '#fdae6b',
            'size': 15,
            'position': j
        })
        
        edges.append({
            'source': 'target_text',
            'target': node_id,
            'label': 'contains',
            'color': '#ff6b6b',
            'width': 1,
            'dashes': True
        })
    
    op_count = 0
    stats = {'matches': 0, 'substitutes': 0, 'deletes': 0, 'inserts': 0}
    
    for op in operations:
        op_type = op[0]
        i = op[1] if len(op) > 1 else None
        j = op[2] if len(op) > 2 else None
        
        op_id = f"op_{op_count}"
        op_label = _get_operation_label(op_type, word1, word2, i, j)
        op_color = _get_operation_color(op_type)
        
        if op_type == 'match':
            stats['matches'] += 1
        elif op_type == 'substitute':
            stats['substitutes'] += 1
        elif op_type == 'delete':
            stats['deletes'] += 1
        elif op_type == 'insert':
            stats['inserts'] += 1
        
        nodes.append({
            'id': op_id,
            'label': op_label,
            'type': 'operation',
            'color': op_color,
            'size': 12
        })
        
        if op_type in ['match', 'substitute']:
            edges.append({
                'source': f"src_char_{i}",
                'target': op_id,
                'label': 'from',
                'color': op_color,
                'width': 2
            })
            
            edges.append({
                'source': op_id,
                'target': f"tgt_char_{j}",
                'label': 'to',
                'color': op_color,
                'width': 2
            })
        elif op_type == 'delete':
            edges.append({
                'source': f"src_char_{i}",
                'target': op_id,
                'label': 'deleted',
                'color': op_color,
                'width': 2
            })
        elif op_type == 'insert':
            edges.append({
                'source': op_id,
                'target': f"tgt_char_{j}",
                'label': 'inserted',
                'color': op_color,
                'width': 2
            })
        
        op_count += 1
    
    stats_node = {
        'id': 'stats',
        'label': f"Conversion Statistics\nOperations count: {len(operations)}\n"
                f"Matches: {stats['matches']}\nSubstitutes: {stats['substitutes']}\n"
                f"Deletes: {stats['deletes']}\nInserts: {stats['inserts']}",
        'type': 'statistics',
        'color': '#9ecae1',
        'size': 20
    }
    nodes.append(stats_node)
    
    edges.append({
        'source': 'stats',
        'target': 'source_text',
        'label': 'analysis',
        'color': '#9ecae1',
        'width': 2,
        'dashes': [5, 5]
    })
    
    edges.append({
        'source': 'stats',
        'target': 'target_text',
        'label': 'analysis',
        'color': '#9ecae1',
        'width': 2,
        'dashes': [5, 5]
    })
    
    return {
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'text1': word1,
            'text2': word2,
            'type': 'word_comparison',
            'operations_count': len(operations),
            'stats': stats
        }
    }



def _simulate_word_operations(word1, word2):
    operations = []
    len1, len2 = len(word1), len(word2)
    i, j = 0, 0
    
    while i < len1 and j < len2:
        if word1[i] == word2[j]:
            operations.append(('match', i, j))
            i += 1
            j += 1
        else:
            operations.append(('substitute', i, j))
            i += 1
            j += 1
    
    while i < len1:
        operations.append(('delete', i))
        i += 1
    
    while j < len2:
        operations.append(('insert', j))
        j += 1
    
    return operations




def _get_operation_label(op_type, item1, item2, i, j):
    labels = {
        'match': f'Match: "{item1}" → "{item2}"',
        'substitute': f'Substitute: "{item1}" → "{item2}"',
        'delete': f'Delete: "{item1}"',
        'insert': f'Insert: "{item2}"'
    }
    return labels.get(op_type, op_type)


def _get_operation_color(op_type):
    color_map = {
        'match': '#4daf4a',
        'substitute': '#ff7f00',
        'delete': '#e41a1c',
        'insert': '#377eb8',
    }
    return color_map.get(op_type, '#999999')


# views.py
from django.shortcuts import render

def info(request):
    """
    Simple view to render the info.html template.
    """
    return render(request, 'info.html')