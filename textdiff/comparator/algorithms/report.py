# report.py
from datetime import datetime
import os

def generate_comparison_report(text1, text2, highlighted_text1, highlighted_text2, operations, total_cost, mode):
    """
    Generates a report dictionary containing all information about comparison.
    """
    report = {
        'text1': text1,
        'text2': text2,
        'highlighted_text1': ' '.join(highlighted_text1),
        'highlighted_text2': ' '.join(highlighted_text2),
        'total_cost': total_cost,
        'operations': operations,
        'mode': mode,
        'timestamp': datetime.now().isoformat()
    }
    return report

def save_report_to_markdown(report, filename="comparison_report.md"):
    """
    Save the report as a Markdown file with emoji-based highlights and summary.
    """
    # شمارش انواع عملیات
    total_ops = len(report['operations'])

    # فرض بر این است که اولین عنصر tuple نوع عملیات است
    match_count = sum(1 for op in report['operations'] if len(op) > 0 and 'match' in str(op[0]).lower())
    insert_count = sum(1 for op in report['operations'] if len(op) > 0 and 'insert' in str(op[0]).lower())
    delete_count = sum(1 for op in report['operations'] if len(op) > 0 and 'delete' in str(op[0]).lower())
    substitute_count = sum(1 for op in report['operations'] if len(op) > 0 and 'substitute' in str(op[0]).lower())

    
    # نمودار متنی ساده
    def text_bar(count):
        length = 20  # طول ماکزیمم نمودار
        filled = int((count / total_ops) * length) if total_ops else 0
        return '*' * filled + '-' * (length - filled)

    md_content = f"""# 📊 Comparison Report

## 📋 Metadata
| Parameter | Value |
|-----------|-------|
| **Mode** | `{report['mode']}` |
| **Timestamp** | `{report['timestamp']}` |
| **Total Cost** | `{report['total_cost']:.2f}` |
| **Total Operations** | `{total_ops}` |

## 📝 Original Texts

**Text 1:**  
{report['text1']}

**Text 2:**  
{report['text2']}

## 🔹 Highlighted Texts (Emoji)
Legend: 🔴 Delete | 🟢 Match | 🔵 Insert | 🟡 Substitute

**Text 1 Highlighted:**  
{report['highlighted_text1']}

**Text 2 Highlighted:**  
{report['highlighted_text2']}

## 📊 Operations Summary
| Operation | Count | Percentage | Visual |
|-----------|-------|-----------|--------|
| Match 🔢 | {match_count} | {(match_count/total_ops*100 if total_ops else 0):.1f}% | {text_bar(match_count)} |
| Insert ➕ | {insert_count} | {(insert_count/total_ops*100 if total_ops else 0):.1f}% | {text_bar(insert_count)} |
| Delete ➖ | {delete_count} | {(delete_count/total_ops*100 if total_ops else 0):.1f}% | {text_bar(delete_count)} |
| Substitute 🟡 | {substitute_count} | {(substitute_count/total_ops*100 if total_ops else 0):.1f}% | {text_bar(substitute_count)} |
| **Total** | {total_ops} | 100% | {'*'*20} |

## 📝 Detailed Operations
| Step | Operation |
|------|-----------|
"""
    # اضافه کردن عملیات جزئی
    for i, op in enumerate(report['operations']):
        md_content += f"| {i+1} | `{op}` |\n"

    md_content += f"\n---\n*Report generated automatically - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    # ایجاد پوشه reports اگر وجود ندارد
    os.makedirs('reports', exist_ok=True)
    
    # ذخیره فایل
    filepath = os.path.join('reports', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return filepath

# === نسخه وب برای Django ===
from django.http import FileResponse

def download_report(report):
    """
    Generate Markdown report and return as downloadable file in Django.
    """
    filename = f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = save_report_to_markdown(report, filename)
    return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
