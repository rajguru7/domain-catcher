import tree_sitter
from urllib.parse import urlparse

class DomainCatcher:

    def __init__( self ):
        # Load Python grammar (assuming it's already built and loaded)
        PY_LANGUAGE = tree_sitter.Language(
                '/home/killua/personal/domain-catcher/build/python_language.so',
                'python'
            )
        self.parser = tree_sitter.Parser()
        self.parser.set_language(PY_LANGUAGE)

    def extract_urls_from_file(self, filename):
        with open(filename, "rb") as fdata:
            source_code = fdata.read().decode()
        tree = self.parser.parse(bytes(source_code, "utf8"))
        root_node = tree.root_node
        urls = []

        def recursive_search(node):
            if node.type == 'string':
                value = source_code[node.start_byte:node.end_byte]
                value = value.strip("\"'")

                parsed_url = urlparse(value)
                if parsed_url.scheme and parsed_url.netloc:
                    urls.append(value)
            else:
                for child in node.children:
                    recursive_search(child)

        recursive_search(root_node)
        return urls


