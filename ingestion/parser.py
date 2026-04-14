from tree_sitter import Parser
from tree_sitter_languages import get_language

parser = Parser()
parser.set_language(get_language("python"))

def parse_code(code: str):
    tree = parser.parse(bytes(code, "utf-8"))
    return tree.root_node