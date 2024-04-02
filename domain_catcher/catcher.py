import tree_sitter
import os
import fnmatch
import logging
from urllib.parse import urlparse
from domain_catcher.parsers import get_tree_sitter_parser

LOG = logging.getLogger(__name__)
extension_to_language = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.html': 'html',
    '.css': 'css',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.bash': 'bash',
    '.sh': 'bash'
}


class DomainCatcher:

    def __init__( self ):
        self.files_list = []
        self.file_to_language = {}
        self.languages = []
        self.parser = {}

    def discover_files(self, targets, recursive=False):
        included_globs = ["*.py", "*.bash", "*.sh"]
        excluded_path_globs = []
        files_list = set()
        excluded_files = set()

        for fname in targets:
            # if this is a directory and recursive is set, find all files
            if os.path.isdir(fname):
                if recursive:
                    new_files, newly_excluded = _get_files_from_dir(
                        fname,
                        included_globs=included_globs,
                        excluded_path_strings=excluded_path_globs,
                    )
                    files_list.update(new_files)
                    excluded_files.update(newly_excluded)
                else:
                    LOG.warning(
                        "Skipping directory (%s), use -r flag to "
                        "scan contents",
                        fname,
                    )

            else:
                # if the user explicitly mentions a file on command line,
                # we'll scan it, regardless of whether it's in the included
                # file types list
                if _is_file_included(
                    fname,
                    included_globs,
                    excluded_path_globs,
                    enforce_glob=False,
                ):
                    if fname != "-":
                        fname = os.path.join(".", fname)
                    files_list.add(fname)
                else:
                    excluded_files.add(fname)

        self.files_list = sorted(files_list)

    def extract_urls_from_file(self, filename):
        with open(filename, "rb") as fdata:
            source_code = fdata.read().decode()
        language = self.file_to_language[filename]
        tree = self.parser[language].parse(bytes(source_code, "utf8"))
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

    def detect_languages(self):
        """
        Detects programming languages based on a list of filenames.

        :return: A set containing the detected languages.
        """
        languages = set()
        for filename in self.files_list:
            _, ext = os.path.splitext(filename)
            language = extension_to_language.get(ext)
            self.file_to_language[filename] = language
            if language:
                languages.add(language)
        self.languages = sorted(languages)

    def set_parsers(self):
        for language in self.languages:
            LANGUAGE = get_tree_sitter_parser(language)
            self.parser[language] = tree_sitter.Parser()
            self.parser[language].set_language(LANGUAGE)

    def run(self):
        urls = []
        for filename in self.files_list:
            urls.extend(self.extract_urls_from_file(filename))
        return urls

def _get_files_from_dir(
    files_dir, included_globs=None, excluded_path_strings=None
):
    if not included_globs:
        included_globs = ["*.py"]
    if not excluded_path_strings:
        excluded_path_strings = []

    files_list = set()
    excluded_files = set()

    for root, _, files in os.walk(files_dir):
        for filename in files:
            path = os.path.join(root, filename)
            if _is_file_included(path, included_globs, excluded_path_strings):
                files_list.add(path)
            else:
                excluded_files.add(path)

    return files_list, excluded_files


def _is_file_included(
    path, included_globs, excluded_path_strings, enforce_glob=True
):
    """Determine if a file should be included based on filename

    This utility function determines if a file should be included based
    on the file name, a list of parsed extensions, excluded paths, and a flag
    specifying whether extensions should be enforced.

    :param path: Full path of file to check
    :param parsed_extensions: List of parsed extensions
    :param excluded_paths: List of paths (globbing supported) from which we
        should not include files
    :param enforce_glob: Can set to false to bypass extension check
    :return: Boolean indicating whether a file should be included
    """
    return_value = False

    # if this is matches a glob of files we look at, and it isn't in an
    # excluded path
    if _matches_glob_list(path, included_globs) or not enforce_glob:
        if not _matches_glob_list(path, excluded_path_strings) and not any(
            x in path for x in excluded_path_strings
        ):
            return_value = True

    return return_value

def _matches_glob_list(filename, glob_list):
    for glob in glob_list:
        if fnmatch.fnmatch(filename, glob):
            return True
    return False


