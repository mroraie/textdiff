import json
import logging
import os
from typing import Dict, List, Optional, Tuple
import numpy as np

# Graphviz path - can be set via environment variable
graphviz_path = os.environ.get('GRAPHVIZ_PATH', r"C:\Program Files\Graphviz\bin")
if os.path.exists(graphviz_path):
    os.environ["PATH"] += os.pathsep + graphviz_path

try:
    from graphviz import Digraph
except ImportError:
    Digraph = None

try:
    from logs_setting import get_logger
except ImportError:
    def get_logger(name: str, log_file: str = "app.log", level=logging.DEBUG) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

logger = get_logger(__name__, "visualization.log")

def visualize_word_operations(
    word1: str,
    word2: str,
    operations: list,
    filename: str,
    output_format: str = "png",
    enhanced: bool = True,
):
    try:
        logger.info(f"Visualizing word transformation: '{word1}' → '{word2}'")
        logger.debug(f"Operations: {operations}")
        logger.debug(f"Output format: {output_format}, Enhanced: {enhanced}")

        if output_format == "json":
            return _create_word_json_visualization(word1, word2, operations, filename)

        if enhanced:
            return _create_enhanced_word_visualization(word1, word2, operations, filename, output_format)
        else:
            return _create_basic_word_visualization(word1, word2, operations, filename, output_format)

    except Exception as e:
        logger.error(f"Error in visualize_word_operations: {str(e)}", exc_info=True)
        raise

def _create_word_json_visualization(word1: str, word2: str, operations: list, filename: str):
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

def _create_enhanced_word_visualization(word1: str, word2: str, operations: list, filename: str, format: str):
    if Digraph is None:
        raise ImportError("Graphviz is not installed. Please install graphviz package.")

    dot = Digraph(comment=f"Word transformation: {word1} → {word2}")
    dot.attr(rankdir="LR", splines="ortho", fontname="Arial")

    with dot.subgraph(name="cluster_source") as c:
        c.attr(style="filled", fillcolor="aliceblue", color="lightgray", label="Source Word")
        for i, ch in enumerate(word1):
            c.node(f"src{i}", ch, shape="circle", style="filled", fillcolor="lightblue", fontname="Arial", fontsize="14")

    with dot.subgraph(name="cluster_target") as c:
        c.attr(style="filled", fillcolor="honeydew", color="lightgray", label="Target Word")
        for j, ch in enumerate(word2):
            c.node(f"tgt{j}", ch, shape="circle", style="filled", fillcolor="lightgreen", fontname="Arial", fontsize="14")

    op_count = 0
    stats = {"matches": 0, "substitutes": 0, "deletes": 0, "inserts": 0}

    for op in operations:
        op_type, i, j = op
        
        if op_type == "match":
            char1 = word1[i] if i < len(word1) else ""
            char2 = word2[j] if j < len(word2) else ""
            dot.edge(f"src{i}", f"tgt{j}", label=f"Match ({char1}→{char2})", color="green", fontcolor="green", style="bold", penwidth="2")
            stats["matches"] += 1

        elif op_type == "substitute":
            old_char = word1[i] if i < len(word1) else ""
            new_char = word2[j] if j < len(word2) else ""
            dot.edge(f"src{i}", f"tgt{j}", label=f"Substitute ({old_char}→{new_char})", color="orange", fontcolor="orange", style="dashed", penwidth="2")
            stats["substitutes"] += 1

        elif op_type == "delete":
            char_to_delete = word1[i] if i < len(word1) else ""
            dot.node(f"del{op_count}", "🗑️", shape="diamond", style="filled", fillcolor="red", fontsize="16", fontname="Arial")
            dot.edge(f"src{i}", f"del{op_count}", label=f"Delete ({char_to_delete})", color="red", fontcolor="red")
            stats["deletes"] += 1

        elif op_type == "insert":
            inserted_char = word2[j] if j < len(word2) else ""
            dot.node(f"ins{op_count}", f"➕{inserted_char}", shape="diamond", style="filled", fillcolor="green", fontsize="14", fontname="Arial")
            dot.edge(f"ins{op_count}", f"tgt{j}", label=f"Insert ({inserted_char})", color="green", fontcolor="green")
            stats["inserts"] += 1

        op_count += 1

    title = (f"Transformation '{word1}' to '{word2}'\nOperations: {len(operations)} | Matches: {stats['matches']} | Substitutes: {stats['substitutes']}\nDeletes: {stats['deletes']} | Inserts: {stats['inserts']}")
    dot.attr(label=title, fontsize="12", fontname="Arial")
    dot.format = format
    output_file = dot.render(filename, cleanup=True)

    logger.info(f"Enhanced visualization saved to: {output_file}")
    return output_file

def _create_basic_word_visualization(word1: str, word2: str, operations: list, filename: str, format: str):
    if Digraph is None:
        raise ImportError("Graphviz is not installed. Please install graphviz package.")

    dot = Digraph(comment=f"Word transformation: {word1} → {word2}")
    dot.attr(rankdir="LR")

    for i, ch in enumerate(word1):
        dot.node(f"src{i}", ch, shape="box", style="filled", fillcolor="lightblue")

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

def _calculate_word_operations_stats(operations: list) -> Dict[str, int]:
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
            return _create_enhanced_sentence_visualization(words1, words2, operations, filename, format)
        else:
            return _create_basic_sentence_visualization(words1, words2, filename, format)

    except Exception as e:
        logger.error(f"Error in visualize_sentence: {str(e)}", exc_info=True)
        raise

def _create_sentence_json_visualization(words1: list[str], words2: list[str], operations: Optional[List[Dict]], filename: str):
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
        data["nodes"].append({
            "id": f"w1_{i}",
            "label": word,
            "type": "source",
            "color": "lightblue",
            "position": i,
        })

    for j, word in enumerate(words2):
        data["nodes"].append({
            "id": f"w2_{j}",
            "label": word,
            "type": "target",
            "color": "lightgreen",
            "position": j,
        })

    if operations:
        for op in operations:
            op_data = op.copy()
            data["edges"].append(op_data)
    else:
        min_len = min(len(words1), len(words2))
        for k in range(min_len):
            data["edges"].append({
                "from": f"w1_{k}",
                "to": f"w2_{k}",
                "type": "alignment",
                "label": "alignment",
                "color": "black",
            })

        for i in range(min_len, len(words1)):
            data["edges"].append({
                "from": f"w1_{i}",
                "to": f"del_{i}",
                "type": "delete",
                "label": "delete",
                "color": "red",
            })

        for j in range(min_len, len(words2)):
            data["edges"].append({
                "from": f"ins_{j}",
                "to": f"w2_{j}",
                "type": "insert",
                "label": "insert",
                "color": "green",
            })

    json_filename = f"{filename}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Sentence JSON visualization saved to: {json_filename}")
    return json_filename

def _create_enhanced_sentence_visualization(words1: list[str], words2: list[str], operations: Optional[List[Dict]], filename: str, format: str):
    if Digraph is None:
        raise ImportError("Graphviz is not installed. Please install graphviz package.")

    dot = Digraph(comment="Sentence transformation")
    dot.attr(rankdir="TB", splines="ortho", fontname="Arial")

    with dot.subgraph(name="cluster_source") as c:
        c.attr(style="filled", fillcolor="aliceblue", color="lightgray", label="Source Sentence")
        for i, word in enumerate(words1):
            fillcolor = _get_sentence_word_color(operations, i, "source")
            c.node(f"w1_{i}", word, shape="box", style="filled", fillcolor=fillcolor, fontname="Arial")

    with dot.subgraph(name="cluster_target") as c:
        c.attr(style="filled", fillcolor="honeydew", color="lightgray", label="Target Sentence")
        for j, word in enumerate(words2):
            fillcolor = _get_sentence_word_color(operations, j, "target")
            c.node(f"w2_{j}", word, shape="box", style="filled", fillcolor=fillcolor, fontname="Arial")

    if operations:
        for op in operations:
            op_type = op.get("type", "")
            if op_type == "match":
                dot.edge(f"w1_{op['src_index']}", f"w2_{op['tgt_index']}", label="Match", color="green", style="bold")
            elif op_type == "substitute":
                dot.edge(f"w1_{op['src_index']}", f"w2_{op['tgt_index']}", label=f"Substitute\n{op.get('src_word', '')}→{op.get('tgt_word', '')}", color="orange", style="dashed")
            elif op_type == "delete":
                dot.node(f"del_{op['src_index']}", "Delete", shape="ellipse", style="filled", fillcolor="red")
                dot.edge(f"w1_{op['src_index']}", f"del_{op['src_index']}", color="red")
            elif op_type == "insert":
                dot.node(f"ins_{op['tgt_index']}", "Insert", shape="ellipse", style="filled", fillcolor="green")
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
    title = (f"Sentence Transformation Analysis\nSource words: {len(words1)} | Target words: {len(words2)}\nMatches: {stats['matches']} | Substitutes: {stats['substitutes']} | Deletes: {stats['deletes']} | Inserts: {stats['inserts']}")
    dot.attr(label=title, fontsize="12")
    dot.format = format
    output_file = dot.render(filename, cleanup=True)

    logger.info(f"Enhanced sentence visualization saved to: {output_file}")
    return output_file

def _create_basic_sentence_visualization(words1: list[str], words2: list[str], filename: str, format: str):
    if Digraph is None:
        raise ImportError("Graphviz is not installed. Please install graphviz package.")

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

def _get_sentence_word_color(operations: Optional[List[Dict]], index: int, word_type: str) -> str:
    if not operations:
        return "lightblue" if word_type == "source" else "lightgreen"

    for op in operations:
        if (word_type == "source" and op.get("src_index") == index) or (word_type == "target" and op.get("tgt_index") == index):
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

def _calculate_sentence_stats(words1: list[str], words2: list[str], operations: Optional[List[Dict]]) -> Dict[str, int]:
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
    operations: list,
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
    operations: list,
    base_filename: str = "word_visualization"
) -> dict:
    results = {}

    json_file = visualize_word_operations(word1, word2, operations, f"{base_filename}_json", format="json")
    results['json'] = json_file

    basic_file = visualize_word_operations(word1, word2, operations, f"{base_filename}_basic", format="png", enhanced=False)
    results['basic'] = basic_file

    enhanced_file = visualize_word_operations(word1, word2, operations, f"{base_filename}_enhanced", format="png", enhanced=True)
    results['enhanced'] = enhanced_file

    return results

def create_all_sentence_visualizations(
    words1: list[str],
    words2: list[str],
    operations: Optional[List[Dict]] = None,
    base_filename: str = "sentence_visualization"
) -> dict:
    results = {}

    json_file = visualize_sentence(words1, words2, operations, f"{base_filename}_json", format="json")
    results['json'] = json_file

    basic_file = visualize_sentence(words1, words2, operations, f"{base_filename}_basic", format="png", enhanced=False)
    results['basic'] = basic_file

    enhanced_file = visualize_sentence(words1, words2, operations, f"{base_filename}_enhanced", format="png", enhanced=True)
    results['enhanced'] = enhanced_file

    return results

def compute_edit_distance_grid(
    text1: str,
    text2: str,
    match_cost: int = 0,
    substitute_cost: int = 1,
    delete_cost: int = 1,
    insert_cost: int = 1
) -> Dict:
    m, n = len(text1), len(text2)
    
    dp = np.zeros((m + 1, n + 1), dtype=int)
    
    for i in range(m + 1):
        dp[i, 0] = i * delete_cost
    for j in range(n + 1):
        dp[0, j] = j * insert_cost
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                match_val = dp[i - 1, j - 1] + match_cost
            else:
                match_val = dp[i - 1, j - 1] + substitute_cost
            
            delete_val = dp[i - 1, j] + delete_cost
            insert_val = dp[i, j - 1] + insert_cost
            
            dp[i, j] = min(match_val, delete_val, insert_val)
    
    nodes = []
    edges = []
    
    for i in range(m + 1):
        for j in range(n + 1):
            node_id = f"node_{i}_{j}"
            nodes.append({
                "id": node_id,
                "label": f"({i},{j})",
                "position": (i, j),
                "cost": int(dp[i, j]),
                "type": "grid_node"
            })
    
    edge_id_counter = 0
    
    for i in range(m + 1):
        for j in range(n + 1):
            current_node = f"node_{i}_{j}"
            
            if i < m:
                edge_id = f"edge_{edge_id_counter}"
                edge_id_counter += 1
                edges.append({
                    "id": edge_id,
                    "from": current_node,
                    "to": f"node_{i+1}_{j}",
                    "label": f"Del: {text1[i] if i < m else ''}",
                    "cost": delete_cost,
                    "type": "delete",
                    "color": "red"
                })
            
            if j < n:
                edge_id = f"edge_{edge_id_counter}"
                edge_id_counter += 1
                edges.append({
                    "id": edge_id,
                    "from": current_node,
                    "to": f"node_{i}_{j+1}",
                    "label": f"Ins: {text2[j] if j < n else ''}",
                    "cost": insert_cost,
                    "type": "insert",
                    "color": "green"
                })
            
            if i < m and j < n:
                edge_id = f"edge_{edge_id_counter}"
                edge_id_counter += 1
                if text1[i] == text2[j]:
                    edges.append({
                        "id": edge_id,
                        "from": current_node,
                        "to": f"node_{i+1}_{j+1}",
                        "label": f"Match: {text1[i]}",
                        "cost": match_cost,
                        "type": "match",
                        "color": "blue"
                    })
                else:
                    edges.append({
                        "id": edge_id,
                        "from": current_node,
                        "to": f"node_{i+1}_{j+1}",
                        "label": f"Sub: {text1[i]}→{text2[j]}",
                        "cost": substitute_cost,
                        "type": "substitute",
                        "color": "orange"
                    })
    
    optimal_path = []
    optimal_edges = []
    i, j = m, n
    
    while i > 0 or j > 0:
        optimal_path.insert(0, f"node_{i}_{j}")
        current_cost = dp[i, j]
        
        if i > 0 and j > 0 and text1[i-1] == text2[j-1]:
            if dp[i-1, j-1] + match_cost == current_cost:
                optimal_edges.insert(0, {
                    "from": f"node_{i-1}_{j-1}",
                    "to": f"node_{i}_{j}",
                    "type": "match",
                    "cost": match_cost
                })
                i, j = i-1, j-1
                continue
        
        if i > 0 and j > 0:
            if dp[i-1, j-1] + substitute_cost == current_cost:
                optimal_edges.insert(0, {
                    "from": f"node_{i-1}_{j-1}",
                    "to": f"node_{i}_{j}",
                    "type": "substitute",
                    "cost": substitute_cost
                })
                i, j = i-1, j-1
                continue
        
        if i > 0 and dp[i-1, j] + delete_cost == current_cost:
            optimal_edges.insert(0, {
                "from": f"node_{i-1}_{j}",
                "to": f"node_{i}_{j}",
                "type": "delete",
                "cost": delete_cost
            })
            i -= 1
            continue
        
        if j > 0 and dp[i, j-1] + insert_cost == current_cost:
            optimal_edges.insert(0, {
                "from": f"node_{i}_{j-1}",
                "to": f"node_{i}_{j}",
                "type": "insert",
                "cost": insert_cost
            })
            j -= 1
            continue
    
    optimal_path.insert(0, "node_0_0")
    
    result = {
        "nodes": nodes,
        "edges": edges,
        "optimal_path": {
            "nodes": optimal_path,
            "edges": optimal_edges,
            "total_cost": int(dp[m, n])
        },
        "metadata": {
            "text1": text1,
            "text2": text2,
            "length1": m,
            "length2": n,
            "match_cost": match_cost,
            "substitute_cost": substitute_cost,
            "delete_cost": delete_cost,
            "insert_cost": insert_cost,
            "edit_distance": int(dp[m, n])
        }
    }
    
    return result

def visualize_edit_distance_grid(
    text1: str,
    text2: str,
    match_cost: int = 0,
    substitute_cost: int = 1,
    delete_cost: int = 1,
    insert_cost: int = 1,
    filename: str = "edit_distance_grid",
    format: str = "json"
) -> str:
    grid_data = compute_edit_distance_grid(
        text1, text2, match_cost, substitute_cost, delete_cost, insert_cost
    )
    
    if format == "json":
        json_filename = f"{filename}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(grid_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Grid visualization saved to: {json_filename}")
        return json_filename
    
    elif format == "graphviz" and Digraph is not None:
        return _create_grid_graphviz_visualization(grid_data, filename)
    
    else:
        raise ValueError("Unsupported format or Graphviz not available")

def _create_grid_graphviz_visualization(grid_data: Dict, filename: str) -> str:
    dot = Digraph(comment="Edit Distance Grid Graph")
    dot.attr(rankdir="TB", splines="ortho", fontname="Arial")
    
    for node in grid_data["nodes"]:
        dot.node(
            node["id"],
            f"{node['label']}\nCost: {node['cost']}",
            shape="box",
            style="filled",
            fillcolor="lightgray" if node["cost"] == 0 else "white",
            fontname="Arial",
            fontsize="10"
        )
    
    for edge in grid_data["edges"]:
        dot.edge(
            edge["from"],
            edge["to"],
            label=f"{edge['label']}\nCost: {edge['cost']}",
            color=edge.get("color", "black"),
            fontname="Arial",
            fontsize="8"
        )
    
    optimal_path = grid_data["optimal_path"]["nodes"]
    for i in range(len(optimal_path) - 1):
        from_node = optimal_path[i]
        to_node = optimal_path[i + 1]
        
        for edge in grid_data["edges"]:
            if edge["from"] == from_node and edge["to"] == to_node:
                dot.edge(
                    from_node,
                    to_node,
                    label=f"{edge['label']}\nCost: {edge['cost']}",
                    color="purple",
                    penwidth="3",
                    fontname="Arial",
                    fontsize="8"
                )
                break
    
    for node_id in optimal_path:
        dot.node(
            node_id,
            f"{node_id.replace('node_', '(').replace('_', ',')})",
            shape="box",
            style="filled",
            fillcolor="lightblue",
            fontname="Arial",
            fontsize="10",
            penwidth="2"
        )
    
    metadata = grid_data["metadata"]
    title = (f"Edit Distance Grid: '{metadata['text1']}' → '{metadata['text2']}'\n"
             f"Edit Distance: {metadata['edit_distance']} | "
             f"Costs: Match={metadata['match_cost']}, "
             f"Sub={metadata['substitute_cost']}, "
             f"Del={metadata['delete_cost']}, "
             f"Ins={metadata['insert_cost']}")
    
    dot.attr(label=title, fontsize="12", fontname="Arial")
    dot.format = "png"
    output_file = dot.render(filename, cleanup=True)
    
    logger.info(f"Grid Graphviz visualization saved to: {output_file}")
    return output_file

def create_edit_distance_visualization(
    text1: str,
    text2: str,
    costs: Optional[Dict[str, int]] = None,
    filename: str = "edit_distance",
    format: str = "json"
) -> Dict:
    if costs is None:
        costs = {
            "match": 0,
            "substitute": 1,
            "delete": 1,
            "insert": 1
        }
    
    result = compute_edit_distance_grid(
        text1, text2,
        costs["match"], costs["substitute"], costs["delete"], costs["insert"]
    )
    
    if format == "json":
        json_filename = f"{filename}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return {"json_file": json_filename, "data": result}
    
    elif format == "graphviz" and Digraph is not None:
        viz_file = _create_grid_graphviz_visualization(result, filename)
        return {"graphviz_file": viz_file, "data": result}
    
    else:
        raise ValueError("Unsupported format")