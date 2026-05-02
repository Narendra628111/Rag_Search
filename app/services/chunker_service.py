# app/services/chunker_service.py
from tree_sitter import Parser
from tree_sitter_languages import get_language
from typing import List, Dict

# Language map — extend as needed
SUPPORTED_LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
}

def _get_parser(extension: str) -> Parser | None:
    lang_name = SUPPORTED_LANGUAGES.get(extension)
    if not lang_name:
        return None
    parser = Parser()
    parser.set_language(get_language(lang_name))
    return parser

def _extract_functions(code: str, extension: str) -> List[str]:
    """Use tree-sitter to extract top-level function/method bodies."""
    parser = _get_parser(extension)
    if not parser:
        return []

    tree = parser.parse(bytes(code, "utf-8"))
    root = tree.root_node

    chunks = []
    for node in root.children:
        # Capture function_definition and decorated_definition for Python
        if node.type in ("function_definition", "decorated_definition",
                          "class_definition", "function_declaration",
                          "method_definition"):
            chunk = code[node.start_byte:node.end_byte]
            if chunk.strip():
                chunks.append(chunk)

    return chunks

def _sliding_window(content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Fallback: overlap-aware sliding window."""
    chunks = []
    start = 0
    while start < len(content):
        chunks.append(content[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks

def chunk_file(file_path: str, content: str) -> List[Dict]:
    """
    Returns a list of {"content": str, "chunk_type": str} dicts.
    Tries tree-sitter function extraction first, falls back to sliding window.
    """
    ext = "." + file_path.rsplit(".", 1)[-1] if "." in file_path else ""
    
    function_chunks = _extract_functions(content, ext)

    if function_chunks:
        return [{"content": c, "chunk_type": "function"} for c in function_chunks]
    
    # Fallback for .md, .txt, .json, .sql and unrecognised extensions
    return [{"content": c, "chunk_type": "sliding_window"}
            for c in _sliding_window(content)]