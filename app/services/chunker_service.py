
import os
from tree_sitter import Parser
from tree_sitter_languages import get_language
from typing import List, Dict

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
    parser = _get_parser(extension)
    if not parser:
        return []
    tree = parser.parse(bytes(code, "utf-8"))
    root = tree.root_node
    chunks = []
    for node in root.children:
        if node.type in ("function_definition", "decorated_definition",
                          "class_definition", "function_declaration",
                          "method_definition"):
            chunk = code[node.start_byte:node.end_byte]
            if chunk.strip():
                chunks.append(chunk)
    return chunks

def _sliding_window(content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(content):
        chunks.append(content[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks

def chunk_file(file_path: str, content: str) -> List[Dict]:
    basename = os.path.basename(file_path)
    _, ext = os.path.splitext(basename)
    ext = ext.lower()

    if not ext:
        # no extension — Dockerfile, Makefile, LICENSE etc.
        # fall straight through to sliding window, no need to attempt tree-sitter
        return [{"content": c, "chunk_type": "sliding_window"}
                for c in _sliding_window(content)]

    function_chunks = _extract_functions(content, ext)

    if function_chunks:
        return [{"content": c, "chunk_type": "function"} for c in function_chunks]

    return [{"content": c, "chunk_type": "sliding_window"}
            for c in _sliding_window(content)]