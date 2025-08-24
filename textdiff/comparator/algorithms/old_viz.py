import json
import logging
from typing import Dict, List, Optional
import os

# مسیر نصب Graphviz
graphviz_path = r"C:\Program Files\Graphviz\bin"

# اضافه کردن مسیر به PATH محیط Python
os.environ["PATH"] += os.pathsep + graphviz_path

# حالا import graphviz
from graphviz import Digraph

try:
    from logs_setting import get_logger
except ImportError:

    def get_logger(
        name: str, log_file: str = "app.log", level=logging.DEBUG
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger


logger = get_logger(__name__, "visualization.log")


def visualize_word_operations(
    word1: str,
    word2: str,
    operations: list[str],
    filename: str,
    format: str = "png",
    enhanced: bool = True,
):
    try:
        logger.info(
            f"Starting visualization for word transformation: '{word1}' → '{word2}'"
        )
        logger.debug(f"Operations: {operations}")
        logger.debug(f"Output format: {format}, Enhanced: {enhanced}")

        if format == "json":
            return _create_word_json_visualization(word1, word2, operations, filename)

        if enhanced:
            return _create_enhanced_word_visualization(
                word1, word2, operations, filename, format
            )
        else:
            return _create_basic_word_visualization(
                word1, word2, operations, filename, format
            )

    except Exception as e:
        logger.error(f"Error in visualize_word_operations: {str(e)}", exc_info=True)
        raise


def _create_word_json_visualization(
    word1: str, word2: str, operations: list[tuple], filename: str
):
    # تبدیل operations از tuple به string
    str_operations = []
    for op in operations:
        if op[0] == 'match':
            str_operations.append(f"Match:{op[1]}:{op[2]}")
        elif op[0] == 'substitute':
            str_operations.append(f"Substitute:{op[1]}:{op[2]}")
        elif op[0] == 'delete':
            str_operations.append(f"Delete:{op[1]}")
        elif op[0] == 'insert':
            str_operations.append(f"Insert:{op[1]}")
    
    data = {
        "word1": word1,
        "word2": word2,
        "operations": str_operations,
        "nodes": [],
        "edges": [],
        "metadata": {
            "length1": len(word1),
            "length2": len(word2),
            "operations_count": len(operations),
        },
    }

    for i, ch in enumerate(word1):
        data["nodes"].append({
            "id": f"src{i}",
            "label": ch,
            "type": "source",
            "color": "lightblue",
            "position": i,
        })

    for j, ch in enumerate(word2):
        data["nodes"].append({
            "id": f"tgt{j}",
            "label": ch,
            "type": "target",
            "color": "lightgreen",
            "position": j,
        })

    src_idx = 0
    tgt_idx = 0
    op_count = 0

    for op in operations:
        op_type = op[0]
        op_data = {"id": f"op{op_count}", "type": op_type, "description": str(op)}

        if op_type == "match":
            char1 = word1[src_idx] if src_idx < len(word1) else ""
            char2 = word2[tgt_idx] if tgt_idx < len(word2) else ""
            op_data.update({
                "from": f"src{src_idx}",
                "to": f"tgt{tgt_idx}",
                "chars": [char1, char2],
                "color": "green",
            })
            data["edges"].append(op_data)
            src_idx += 1
            tgt_idx += 1

        elif op_type == "substitute":
            char1 = word1[src_idx] if src_idx < len(word1) else ""
            char2 = word2[tgt_idx] if tgt_idx < len(word2) else ""
            op_data.update({
                "from": f"src{src_idx}",
                "to": f"tgt{tgt_idx}",
                "chars": [char1, char2],
                "color": "orange",
            })
            data["edges"].append(op_data)
            src_idx += 1
            tgt_idx += 1

        elif op_type == "delete":
            del_id = f"del{src_idx}"
            data["nodes"].append({
                "id": del_id,
                "label": "X",
                "type": "delete",
                "color": "red",
                "position": src_idx,
            })
            op_data.update({"from": f"src{src_idx}", "to": del_id, "color": "red"})
            data["edges"].append(op_data)
            src_idx += 1

        elif op_type == "insert":
            ins_id = f"ins{tgt_idx}"
            inserted_char = word2[tgt_idx]
            data["nodes"].append({
                "id": ins_id,
                "label": inserted_char,
                "type": "insert",
                "color": "green",
                "position": tgt_idx,
            })
            op_data.update({"from": ins_id, "to": f"tgt{tgt_idx}", "color": "green"})
            data["edges"].append(op_data)
            tgt_idx += 1

        op_count += 1

    json_filename = f"{filename}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"JSON visualization saved to: {json_filename}")
    return json_filename


def _create_enhanced_word_visualization(
    word1: str, word2: str, operations: list[tuple], filename: str, format: str
):
    """
    ایجاد ویژوال‌سازی پیشرفته برای تبدیل کلمات با استفاده از گراف
    """
    dot = Digraph(comment=f"Word transformation: {word1} → {word2}")
    dot.attr(rankdir="LR", splines="ortho", fontname="Arial")

    # ایجاد زیرگراف برای کلمه منبع
    with dot.subgraph(name="cluster_source") as c:
        c.attr(style="filled", fillcolor="aliceblue", color="lightgray", label="Source Word")
        for i, ch in enumerate(word1):
            c.node(
                f"src{i}",
                ch,
                shape="circle",
                style="filled",
                fillcolor="lightblue",
                fontname="Arial",
                fontsize="14",
            )

    # ایجاد زیرگراف برای کلمه هدف
    with dot.subgraph(name="cluster_target") as c:
        c.attr(style="filled", fillcolor="honeydew", color="lightgray", label="Target Word")
        for j, ch in enumerate(word2):
            c.node(
                f"tgt{j}",
                ch,
                shape="circle",
                style="filled",
                fillcolor="lightgreen",
                fontname="Arial",
                fontsize="14",
            )

    op_count = 0
    stats = {"matches": 0, "substitutes": 0, "deletes": 0, "inserts": 0}

    # پردازش هر عملیات
    for op in operations:
        op_type, i, j = op
        
        if op_type == "match":
            char1 = word1[i] if i < len(word1) else ""
            char2 = word2[j] if j < len(word2) else ""
            dot.edge(
                f"src{i}",
                f"tgt{j}",
                label=f"Match ({char1}→{char2})",
                color="green",
                fontcolor="green",
                style="bold",
                penwidth="2",
            )
            stats["matches"] += 1

        elif op_type == "substitute":
            old_char = word1[i] if i < len(word1) else ""
            new_char = word2[j] if j < len(word2) else ""
            dot.edge(
                f"src{i}",
                f"tgt{j}",
                label=f"Substitute ({old_char}→{new_char})",
                color="orange",
                fontcolor="orange",
                style="dashed",
                penwidth="2",
            )
            stats["substitutes"] += 1

        elif op_type == "delete":
            char_to_delete = word1[i] if i < len(word1) else ""
            dot.node(
                f"del{op_count}",
                "🗑️",
                shape="diamond",
                style="filled",
                fillcolor="red",
                fontsize="16",
                fontname="Arial",
            )
            dot.edge(
                f"src{i}",
                f"del{op_count}",
                label=f"Delete ({char_to_delete})",
                color="red",
                fontcolor="red",
            )
            stats["deletes"] += 1

        elif op_type == "insert":
            inserted_char = word2[j] if j < len(word2) else ""
            dot.node(
                f"ins{op_count}",
                f"➕{inserted_char}",
                shape="diamond",
                style="filled",
                fillcolor="green",
                fontsize="14",
                fontname="Arial",
            )
            dot.edge(
                f"ins{op_count}",
                f"tgt{j}",
                label=f"Insert ({inserted_char})",
                color="green",
                fontcolor="green",
            )
            stats["inserts"] += 1

        op_count += 1

    # ایجاد عنوان با آمار عملیات
    title = (
        f"Transformation '{word1}' to '{word2}'\n"
        f"Operations: {len(operations)} | "
        f"Matches: {stats['matches']} | Substitutes: {stats['substitutes']}\n"
        f"Deletes: {stats['deletes']} | Inserts: {stats['inserts']}"
    )

    dot.attr(label=title, fontsize="12", fontname="Arial")
    dot.format = format
    output_file = dot.render(filename, cleanup=True)

    logger.info(f"Enhanced visualization saved to: {output_file}")
    return output_file


def _calculate_word_operations_stats(operations: list[tuple]) -> dict:
    """
    محاسبه آمار عملیات انجام شده
    """
    stats = {"matches": 0, "substitutes": 0, "deletes": 0, "inserts": 0}
    
    for op in operations:
        op_type, _, _ = op
        if op_type == "match":
            stats["matches"] += 1
        elif op_type == "substitute":
            stats["substitutes"] += 1
        elif op_type == "delete":
            stats["deletes"] += 1
        elif op_type == "insert":
            stats["inserts"] += 1
    
    return stats


from typing import Dict, List
from graphviz import Digraph
import logging

logger = logging.getLogger(__name__)


def _create_basic_word_visualization(
    word1: str, word2: str, operations: List[tuple], filename: str, format: str
):
    """
    Create a basic visualization of word transformation using Graphviz.
    operations: list of tuples like ('match', i, j), ('substitute', i, j), ('delete', i), ('insert', j)
    """
    dot = Digraph(comment=f"Word transformation: {word1} → {word2}")
    dot.attr(rankdir="LR")

    # Source word nodes
    for i, ch in enumerate(word1):
        dot.node(f"src{i}", ch, shape="box", style="filled", fillcolor="lightblue")

    # Target word nodes
    for j, ch in enumerate(word2):
        dot.node(f"tgt{j}", ch, shape="box", style="filled", fillcolor="lightgreen")

    src_idx = 0
    tgt_idx = 0
    for op in operations:
        op_type = op[0]

        if op_type == "match":
            dot.edge(f"src{src_idx}", f"tgt{tgt_idx}", label="match", color="black")
            src_idx += 1
            tgt_idx += 1

        elif op_type == "substitute":
            dot.edge(f"src{src_idx}", f"tgt{tgt_idx}", label="substitute", color="orange")
            src_idx += 1
            tgt_idx += 1

        elif op_type == "delete":
            dot.node(f"del{src_idx}", "[X]", shape="ellipse", style="filled", fillcolor="red")
            dot.edge(f"src{src_idx}", f"del{src_idx}", label="delete", color="red")
            src_idx += 1

        elif op_type == "insert":
            dot.node(f"ins{tgt_idx}", "[ ]", shape="ellipse", style="filled", fillcolor="green")
            dot.edge(f"ins{tgt_idx}", f"tgt{tgt_idx}", label="insert", color="green")
            tgt_idx += 1

    dot.format = format
    output_file = dot.render(filename, cleanup=True)

    logger.info(f"Basic visualization saved to: {output_file}")
    return output_file


def _calculate_word_operations_stats(operations: List[tuple]) -> Dict[str, int]:
    """
    Calculate statistics of word operations.
    operations: list of tuples like ('match', i, j), ('substitute', i, j), ('delete', i), ('insert', j)
    """
    stats = {"matches": 0, "substitutes": 0, "deletes": 0, "inserts": 0}
    for op in operations:
        op_type = op[0]
        if op_type == "match":
            stats["matches"] += 1
        elif op_type == "substitute":
            stats["substitutes"] += 1
        elif op_type == "delete":
            stats["deletes"] += 1
        elif op_type == "insert":
            stats["inserts"] += 1
    return stats



def visualize_sentence(
    words1: list[str],
    words2: list[str],
    operations: Optional[List[Dict]] = None,
    filename: str = "sentence_visualization",
    format: str = "png",
    enhanced: bool = True,
):
    try:
        logger.info(f"Starting sentence visualization for {len(words1)} vs {len(words2)} words")
        logger.debug(f"Words1: {words1}")
        logger.debug(f"Words2: {words2}")

        if format == "json":
            return _create_sentence_json_visualization(words1, words2, operations, filename)

        if enhanced:
            return _create_enhanced_sentence_visualization(
                words1, words2, operations, filename, format
            )
        else:
            return _create_basic_sentence_visualization(words1, words2, filename, format)

    except Exception as e:
        logger.error(f"Error in visualize_sentence: {str(e)}", exc_info=True)
        raise


def _create_sentence_json_visualization(
    words1: list[str], words2: list[str], operations: Optional[List[Dict]], filename: str
):
    data = {
        "sentence1": " ".join(words1),
        "sentence2": " ".join(words2),
        "words1": words1,
        "words2": words2,
        "operations": operations or [],
        "nodes": [],
        "edges": [],
        "metadata": {
            "word_count1": len(words1),
            "word_count2": len(words2),
            "alignment_type": "basic" if operations is None else "detailed",
        },
    }

    for i, word in enumerate(words1):
        data["nodes"].append(
            {
                "id": f"w1_{i}",
                "label": word,
                "type": "source",
                "color": "lightblue",
                "position": i,
            }
        )

    for j, word in enumerate(words2):
        data["nodes"].append(
            {
                "id": f"w2_{j}",
                "label": word,
                "type": "target",
                "color": "lightgreen",
                "position": j,
            }
        )

    if operations:
        for op in operations:
            op_data = op.copy()
            data["edges"].append(op_data)
    else:
        min_len = min(len(words1), len(words2))
        for k in range(min_len):
            data["edges"].append(
                {
                    "from": f"w1_{k}",
                    "to": f"w2_{k}",
                    "type": "alignment",
                    "label": "alignment",
                    "color": "black",
                }
            )

        for i in range(min_len, len(words1)):
            data["edges"].append(
                {
                    "from": f"w1_{i}",
                    "to": f"del_{i}",
                    "type": "delete",
                    "label": "delete",
                    "color": "red",
                }
            )

        for j in range(min_len, len(words2)):
            data["edges"].append(
                {
                    "from": f"ins_{j}",
                    "to": f"w2_{j}",
                    "type": "insert",
                    "label": "insert",
                    "color": "green",
                }
            )

    json_filename = f"{filename}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Sentence JSON visualization saved to: {json_filename}")
    return json_filename


def _create_enhanced_sentence_visualization(
    words1: list[str],
    words2: list[str],
    operations: Optional[List[Dict]],
    filename: str,
    format: str,
):
    dot = Digraph(comment="Sentence transformation")
    dot.attr(rankdir="TB", splines="ortho", fontname="Arial")

    with dot.subgraph(name="cluster_source") as c:
        c.attr(style="filled", fillcolor="aliceblue", color="lightgray", label="Source Sentence")
        for i, word in enumerate(words1):
            fillcolor = _get_sentence_word_color(operations, i, "source")
            c.node(
                f"w1_{i}",
                word,
                shape="box",
                style="filled",
                fillcolor=fillcolor,
                fontname="Arial",
            )

    with dot.subgraph(name="cluster_target") as c:
        c.attr(style="filled", fillcolor="honeydew", color="lightgray", label="Target Sentence")
        for j, word in enumerate(words2):
            fillcolor = _get_sentence_word_color(operations, j, "target")
            c.node(
                f"w2_{j}",
                word,
                shape="box",
                style="filled",
                fillcolor=fillcolor,
                fontname="Arial",
            )

    if operations:
        for op in operations:
            op_type = op.get("type", "")
            if op_type == "match":
                dot.edge(
                    f"w1_{op['src_index']}",
                    f"w2_{op['tgt_index']}",
                    label="Match",
                    color="green",
                    style="bold",
                )
            elif op_type == "substitute":
                dot.edge(
                    f"w1_{op['src_index']}",
                    f"w2_{op['tgt_index']}",
                    label=f"Substitute\n{op.get('src_word', '')}→{op.get('tgt_word', '')}",
                    color="orange",
                    style="dashed",
                )
            elif op_type == "delete":
                dot.node(
                    f"del_{op['src_index']}",
                    "Delete",
                    shape="ellipse",
                    style="filled",
                    fillcolor="red",
                )
                dot.edge(f"w1_{op['src_index']}", f"del_{op['src_index']}", color="red")
            elif op_type == "insert":
                dot.node(
                    f"ins_{op['tgt_index']}",
                    "Insert",
                    shape="ellipse",
                    style="filled",
                    fillcolor="green",
                )
                dot.edge(f"ins_{op['tgt_index']}", f"w2_{op['tgt_index']}", color="green")
    else:
        min_len = min(len(words1), len(words2))
        for k in range(min_len):
            dot.edge(f"w1_{k}", f"w2_{k}", label="Alignment", color="black")

        for i in range(min_len, len(words1)):
            dot.node(f"del_{i}", "Delete", shape="ellipse", style="filled", fillcolor="red")
            dot.edge(f"w1_{i}", f"del_{i}", label="Delete", color="red")

        for j in range(min_len, len(words2)):
            dot.node(f"ins_{j}", "Insert", shape="ellipse", style="filled", fillcolor="green")
            dot.edge(f"ins_{j}", f"w2_{j}", label="Insert", color="green")

    stats = _calculate_sentence_stats(words1, words2, operations)
    title = (
        f"Sentence Transformation Analysis\n"
        f"Source words: {len(words1)} | Target words: {len(words2)}\n"
        f"Matches: {stats['matches']} | Substitutes: {stats['substitutes']} | "
        f"Deletes: {stats['deletes']} | Inserts: {stats['inserts']}"
    )

    dot.attr(label=title, fontsize="12")
    dot.format = format
    output_file = dot.render(filename, cleanup=True)

    logger.info(f"Enhanced sentence visualization saved to: {output_file}")
    return output_file


def _create_basic_sentence_visualization(
    words1: list[str], words2: list[str], filename: str, format: str
):
    dot = Digraph(comment="Sentence transformation")
    dot.attr(rankdir="LR")

    for i, word in enumerate(words1):
        dot.node(f"w1_{i}", word, shape="box", style="filled", fillcolor="lightblue")

    for j, word in enumerate(words2):
        dot.node(f"w2_{j}", word, shape="box", style="filled", fillcolor="lightgreen")

    min_len = min(len(words1), len(words2))
    for k in range(min_len):
        dot.edge(f"w1_{k}", f"w2_{k}", label="alignment", color="black")

    for i in range(min_len, len(words1)):
        dot.node(f"del_{i}", "[X]", shape="ellipse", style="filled", fillcolor="red")
        dot.edge(f"w1_{i}", f"del_{i}", label="delete", color="red")

    for j in range(min_len, len(words2)):
        dot.node(f"ins_{j}", "[ ]", shape="ellipse", style="filled", fillcolor="green")
        dot.edge(f"ins_{j}", f"w2_{j}", label="insert", color="green")

    dot.format = format
    output_file = dot.render(filename, cleanup=True)

    logger.info(f"Basic sentence visualization saved to: {output_file}")
    return output_file


def _get_sentence_word_color(
    operations: Optional[List[Dict]], index: int, word_type: str
) -> str:
    if not operations:
        return "lightblue" if word_type == "source" else "lightgreen"

    for op in operations:
        if (word_type == "source" and op.get("src_index") == index) or (
            word_type == "target" and op.get("tgt_index") == index
        ):
            op_type = op.get("type", "")
            if op_type == "match":
                return "lightgreen"
            elif op_type == "substitute":
                return "lightyellow"
            elif op_type == "delete":
                return "lightcoral"
            elif op_type == "insert":
                return "lightblue"

    return "lightgray" if word_type == "source" else "lightblue"


def _calculate_sentence_stats(
    words1: list[str], words2: list[str], operations: Optional[List[Dict]]
) -> Dict[str, int]:
    if operations:
        stats = {"matches": 0, "substitutes": 0, "deletes": 0, "inserts": 0}
        for op in operations:
            op_type = op.get("type", "")
            if op_type == "match":
                stats["matches"] += 1
            elif op_type == "substitute":
                stats["substitutes"] += 1
            elif op_type == "delete":
                stats["deletes"] += 1
            elif op_type == "insert":
                stats["inserts"] += 1
        return stats
    else:
        min_len = min(len(words1), len(words2))
        return {
            "matches": min_len,
            "substitutes": 0,
            "deletes": max(0, len(words1) - min_len),
            "inserts": max(0, len(words2) - min_len),
        }


def create_word_visualization(
    word1: str,
    word2: str,
    operations: list[str],
    filename: str = "word_visualization",
    format: str = "png",
    enhanced: bool = True,
):
    return visualize_word_operations(word1, word2, operations, filename, format, enhanced)


def create_sentence_visualization(
    words1: list[str],
    words2: list[str],
    operations: Optional[List[Dict]] = None,
    filename: str = "sentence_visualization",
    format: str = "png",
    enhanced: bool = True,
):
    return visualize_sentence(words1, words2, operations, filename, format, enhanced)


def create_all_word_visualizations(
    word1: str,
    word2: str,
    operations: list[str],
    base_filename: str = "word_visualization"
) -> dict:
    """
    Create all types of visualizations for a word pair:
    - JSON
    - Basic Graph
    - Enhanced Graph
    
    Returns a dictionary with filenames.
    """
    results = {}

    # JSON
    json_file = visualize_word_operations(word1, word2, operations, f"{base_filename}_json", format="json")
    results['json'] = json_file

    # Basic Graph
    basic_file = visualize_word_operations(word1, word2, operations, f"{base_filename}_basic", format="png", enhanced=False)
    results['basic'] = basic_file

    # Enhanced Graph
    enhanced_file = visualize_word_operations(word1, word2, operations, f"{base_filename}_enhanced", format="png", enhanced=True)
    results['enhanced'] = enhanced_file

    return results


def create_all_sentence_visualizations(
    words1: list[str],
    words2: list[str],
    operations: Optional[List[Dict]] = None,
    base_filename: str = "sentence_visualization"
) -> dict:
    """
    Create all types of visualizations for a sentence pair:
    - JSON
    - Basic Graph
    - Enhanced Graph
    
    Returns a dictionary with filenames.
    """
    results = {}

    # JSON
    json_file = visualize_sentence(words1, words2, operations, f"{base_filename}_json", format="json")
    results['json'] = json_file

    # Basic Graph
    basic_file = visualize_sentence(words1, words2, operations, f"{base_filename}_basic", format="png", enhanced=False)
    results['basic'] = basic_file

    # Enhanced Graph
    enhanced_file = visualize_sentence(words1, words2, operations, f"{base_filename}_enhanced", format="png", enhanced=True)
    results['enhanced'] = enhanced_file

    return results
