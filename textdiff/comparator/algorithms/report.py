# report.py
from datetime import datetime
import os

def generate_comparison_report(text1, text2, highlighted_text1, highlighted_text2, operations, total_cost, mode, preprocessing1=None, preprocessing2=None):
    """
    Generates a report dictionary containing all information about comparison.
    Includes preprocessing results.
    """
    report = {
        'text1': text1,
        'text2': text2,
        'highlighted_text1': ' '.join(highlighted_text1),
        'highlighted_text2': ' '.join(highlighted_text2),
        'total_cost': total_cost,
        'operations': operations,
        'mode': mode,
        'timestamp': datetime.now().isoformat(),
        'preprocessing1': preprocessing1,
        'preprocessing2': preprocessing2
    }
    return report


def save_report_to_markdown(report):
    """
    Save the report as a Markdown file (in Persian).
    Filename includes current datetime.
    """
    from datetime import datetime
    import os

    total_ops = len(report['operations'])
    match_count = sum(1 for op in report['operations'] if len(op) > 0 and 'match' in str(op[0]).lower())
    insert_count = sum(1 for op in report['operations'] if len(op) > 0 and 'insert' in str(op[0]).lower())
    delete_count = sum(1 for op in report['operations'] if len(op) > 0 and 'delete' in str(op[0]).lower())
    substitute_count = sum(1 for op in report['operations'] if len(op) > 0 and 'substitute' in str(op[0]).lower())

    def text_bar(count):
        length = 20
        filled = int((count / total_ops) * length) if total_ops else 0
        return '█' * filled + '░' * (length - filled)

    md_content = f"""# گزارش مقایسه متون

## اطلاعات کلی
| ویژگی | مقدار |
|-------|--------|
| حالت مقایسه | `{report['mode']}` |
| زمان تولید | `{report['timestamp']}` |
| هزینه کلی | `{report['total_cost']:.2f}` |
| تعداد کل عملیات | `{total_ops}` |

## متون اصلی
**متن ۱:**  
{report['text1']}

**متن ۲:**  
{report['text2']}

## متون هایلایت‌شده
**متن ۱:**  
{report['highlighted_text1']}

**متن ۲:**  
{report['highlighted_text2']}

## خلاصه عملیات
| نوع عملیات | تعداد | درصد | نمودار |
|------------|-------|-------|---------|
| تطابق | {match_count} | {(match_count/total_ops*100 if total_ops else 0):.1f}% | {text_bar(match_count)} |
| درج | {insert_count} | {(insert_count/total_ops*100 if total_ops else 0):.1f}% | {text_bar(insert_count)} |
| حذف | {delete_count} | {(delete_count/total_ops*100 if total_ops else 0):.1f}% | {text_bar(delete_count)} |
| جایگزینی | {substitute_count} | {(substitute_count/total_ops*100 if total_ops else 0):.1f}% | {text_bar(substitute_count)} |
| **مجموع** | {total_ops} | 100% | {'█'*20} |

## جزئیات عملیات
| گام | عملیات |
|-----|---------|
"""
    for i, op in enumerate(report['operations']):
        md_content += f"| {i+1} | `{op}` |\n"

    def render_preprocessing(pre, title):
        if not pre:
            return ""
        block = f"\n## پیش‌پردازش {title}\n"
        block += f"- متن اصلی: {pre['original_text']}\n"
        block += f"- متن تمیز شده: {pre['cleaned_text']}\n"
        block += f"- متن آوایی: {pre['phonetic_text']}\n"
        block += "\n### جزئیات کلمات\n"
        block += "| کلمه | تمیز شده | آوایی | حروف حذف‌شده | موقعیت‌های واو ساکت |\n"
        block += "|-------|-----------|-------|----------------|----------------------|\n"
        for word in pre['word_details']:
            block += f"| {word['original']} | {word['cleaned']} | {word['phonetic']} | {','.join(word['removed_chars']) if word['removed_chars'] else '-'} | {word['silent_vav_positions']} |\n"
        return block

    md_content += render_preprocessing(report.get("preprocessing1"), "متن ۱")
    md_content += render_preprocessing(report.get("preprocessing2"), "متن ۲")

    md_content += f"\n---\n*این گزارش به صورت خودکار تولید شد - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    os.makedirs('reports', exist_ok=True)

    # نام فایل شامل تاریخ و زمان
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"comparison_report_{timestamp_str}.md"
    filepath = os.path.join('reports', filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    return filepath
