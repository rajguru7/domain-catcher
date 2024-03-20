# Implementation

## Discover files
Get the source code for which analysis has to be done

## Generate AST
* Use Treesitter because you want to extend to other languages too.
* If I use the Python `ast` module that'll work only for parsing python source
  code AST
* Similar reasons as given at:
  <https://github.com/github/semantic/blob/main/docs/why-tree-sitter.md#why-we-use-tree-sitter>

### Determine Programming Language
Use appropriate language detection to determine which language analysers to run
on which files.

## Analyse AST 

Get executable URLs

## Report

Reference Links

[Python AST module](https://docs.python.org/3/library/ast.html)
[Missing AST docs](https://greentreesnakes.readthedocs.io/en/latest/)
