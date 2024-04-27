from tree_sitter import Language
# import tree_sitter_python
# import tree_sitter_bash
# import tree_sitter_javascript
# import tree_sitter_typescript
# import tree_sitter_html
# import tree_sitter_css
# import tree_sitter_java
# import tree_sitter_c
# import tree_sitter_cpp
# import tree_sitter_make
# import tree_sitter_go
import subprocess
import logging
import os

dc_dir = os.path.join(str(os.getenv("HOME")), ".dc")

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
f_handler = logging.FileHandler('.dc.log')
f_handler.setLevel(logging.ERROR)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
LOG.addHandler(f_handler)

grammar_repos = {
    'python': 'https://github.com/tree-sitter/tree-sitter-python',
    'bash': 'https://github.com/tree-sitter/tree-sitter-bash',
    'javascript': 'https://github.com/tree-sitter/tree-sitter-javascript',
    'typescript': 'https://github.com/tree-sitter/tree-sitter-typescript',
    'html': 'https://github.com/tree-sitter/tree-sitter-html',
    'css': 'https://github.com/tree-sitter/tree-sitter-css',
    'java': 'https://github.com/tree-sitter/tree-sitter-java',
    'c': 'https://github.com/tree-sitter/tree-sitter-c',
    'cpp': 'https://github.com/tree-sitter/tree-sitter-cpp'
    # 'makefile': 'https://github.com/tree-sitter-grammars/tree-sitter-make'
}

# grammar_repos = {
#     'python': tree_sitter_python.language(),
#     'go': tree_sitter_go.language(),
#     'bash': tree_sitter_bash.language(),
#     'javascript': tree_sitter_javascript.language(),
#     'typescript': tree_sitter_typescript.language(),
#     'html': tree_sitter_html.language(),
#     'css': tree_sitter_css.language(),
#     'java': tree_sitter_java.language(),
#     'c': tree_sitter_c.language(),
#     'cpp': tree_sitter_cpp.language(),
#     'makefile': tree_sitter_make.language()
# }

def clone_grammar(language_name, grammar_url, grammars_dir='tree-sitter-grammars'):
    """
    Clones a Tree-sitter grammar repository into a local directory.
    
    :param language_name: The name of the language (e.g., 'python').
    :param grammar_url: The URL of the grammar repository.
    :param grammars_dir: The directory to clone the grammar repositories into.
    """
    # Ensure the grammars directory exists
    os.makedirs(grammars_dir, exist_ok=True)
    
    # Define the path for the local grammar repository
    grammar_path = os.path.join(grammars_dir, language_name)
    
    # Clone the repository if it doesn't already exist
    if not os.path.exists(grammar_path):
        print(f"Cloning {language_name} grammar repository...")
        subprocess.run(["git", "clone", grammar_url, grammar_path], check=True)
    else:
        LOG.info(f"Grammar repository for {language_name} already exists.")
    
    return grammar_path

def get_tree_sitter_parser(language):
    """
    Fetches the Tree-sitter parser shared object file for the specified
    language.
    
    :param language: The language to build the parser for (e.g., 'python').
    :param dc_dir: Domain Catcher runtime path
    """
    # Ensure the build directory exists
    os.makedirs(dc_dir, exist_ok=True)
    # Ensure the parsers directory exists
    parsers_dir = os.path.join(dc_dir, "parsers")
    os.makedirs(parsers_dir, exist_ok=True)
    grammar_dir = os.path.join(dc_dir, "tree-sitter-grammars")
    os.makedirs(grammar_dir, exist_ok=True)

    so_file_path = os.path.join(parsers_dir, f"{language}.so")

    # Check tree-sitter parser already exists else clone grammar
    if not os.path.exists(so_file_path):
        # Clone the grammar repository for the specified language
        grammar_repo_url = grammar_repos.get(language)
        if grammar_repo_url:
            grammar_path = clone_grammar(language, grammar_repo_url, grammar_dir)
        else:
            LOG.warn(f"No grammar repository found for language: {language}")
            return None
        
        # Build the shared library
        Language.build_library(
            so_file_path,
            [grammar_path],
        )
        
        # print(f"Built parser shared object file at {so_file_path}")
        LOG.info(f"Built parser shared object file at {so_file_path}")
    else:
        # print(f"Parser for {language} already exists.")
        LOG.info(f"Parser for {language} already exists.")
    
    return Language(so_file_path, language)

# def get_tree_sitter_parser(language):
#     """
#     Fetches the Tree-sitter parser shared object file for the specified
#     language.
#     
#     :param language: The language to build the parser for (e.g., 'python').
#     :param dc_dir: Domain Catcher runtime path
#     """
#     
#     return Language(grammar_repos[language], language)
