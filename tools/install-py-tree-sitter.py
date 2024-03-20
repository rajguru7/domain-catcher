from tree_sitter import Language

Language.build_library(
    # Store the library in the `build` directory
    "build/python_language.so",
    # Include one or more languages
    ["vendor/tree-sitter-python"],
)
