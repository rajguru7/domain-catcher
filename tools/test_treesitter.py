from tree_sitter_languages import get_language, get_parser
from urllib.parse import urlparse

language = get_language('python')
parser = get_parser('python')

example = """
#!shebang
# License blah blah (Apache 2.0)
"This is a module docstring."

a = 1

'''This
is
not
a
multiline
comment.'''

b = 2

class Test:
    "This is a class docstring."

    'This is bogus.'

    def test(self):
        "This is a function docstring."

        "Please, no."

        return 1

c = 3
"""



filename = "./tests/test.py"
with open(filename, "rb") as fdata:
    source_code = fdata.read().decode()
tree = parser.parse(bytes(source_code, "utf8"))

# tree = parser.parse(example.encode())
node = tree.root_node
# print(node.sexp())

url_str_pattern = '(string) @url_str'
url_str_query = language.query(url_str_pattern)
url_strs = url_str_query.captures(node)
domains = []
for url_str in url_strs:
    url_node, _ = url_str
    # url = source_code[url_node.start_byte:url_node.end_byte]
    url = url_node.text.decode().strip("\"'")
    print(url)
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            domains.append([url, filename])
    except Exception as e:
        print(f"Error parsing URL: {url} in {filename}, message: {e}")
print(domains)

# stmt_str_pattern = '(expression_statement (string)) @stmt_str'
# stmt_str_query = language.query(stmt_str_pattern)
# stmt_strs = stmt_str_query.captures(node)
# stmt_str_points = set(
#     (node.start_point, node.end_point) for node, _ in stmt_strs
# )
# print(stmt_str_points)
#
# doc_str_pattern = """
#     (module . (comment)* . (expression_statement (string)) @module_doc_str)
#
#     (class_definition
#         body: (block . (expression_statement (string)) @class_doc_str))
#
#     (function_definition
#         body: (block . (expression_statement (string)) @function_doc_str))
# """
# doc_str_query = language.query(doc_str_pattern)
# doc_strs = doc_str_query.captures(node)
# doc_str_points = set(
#     (node.start_point, node.end_point) for node, _ in doc_strs
# )
#
# comment_strs = stmt_str_points - doc_str_points
# print(sorted(comment_strs))
