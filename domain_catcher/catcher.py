# import tree_sitter
import os
import fnmatch
import logging
import magic
from urllib.parse import urlparse
# from domain_catcher.parsers import get_tree_sitter_parser
from tree_sitter_languages import get_language, get_parser


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
f_handler = logging.FileHandler('.dc.log')
f_handler.setLevel(logging.DEBUG)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
LOG.addHandler(f_handler)

extension_to_language = {
    '.py': 'python',
    '.js': 'javascript',
    '.go': 'go',
    '.ts': 'typescript',
    '.html': 'html',
    '.css': 'css',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.bash': 'bash',
    '.sh': 'bash',
    '.json': 'json',
    '.yaml': 'yaml'
}

class DomainCatcher:

    def __init__( self ):
        self.files_list = []
        self.file_to_language = {}
        self.languages = []
        self.parser = {}

    def discover_files(self, targets, recursive=False):
        included_globs = ["*.py", "*.go", "*.bash", "*.sh", "*.js", "*.ts",
                          "*.json", "*.yaml", "*.html", "*.css",
                          "*.java", "*.c", "*.cpp"] # TODO: typescript and cpp grammar not working properly, will have to use tree-sitter cli like nvim-treesitter does
        included_no_ext = ["shell"] #, "make", "dockerfile"] # TODO: detect dockerfile, makefile grammar not working
        excluded_path_globs = [ "*.git/*" ]
        files_list = set()
        excluded_files = set()

        for fname in targets:
            # if this is a directory and recursive is set, find all files
            if os.path.isdir(fname):
                if recursive:
                    new_files, newly_excluded = _get_files_from_dir(
                        fname,
                        included_globs=included_globs,
                        included_no_ext=included_no_ext,
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
                    included_no_ext,
                    excluded_path_globs,
                    enforce_glob=False,
                ):
                    if fname != "-":
                        fname = os.path.join(".", fname)
                    files_list.add(fname)
                else:
                    excluded_files.add(fname)

        self.files_list = sorted(files_list)
        # print(self.files_list)

    # def extract_urls_from_file(self, filename):
    #     LOG.info(f"Extracting URLs from {filename}")
    #     with open(filename, "rb") as fdata:
    #         source_code = fdata.read().decode()
    #     language = self.file_to_language[filename]
    #     tree = self.parser[language].parse(bytes(source_code, "utf8"))
    #     root_node = tree.root_node
    #     domains = []
    #
    #     def recursive_search(node):
    #         if node.type == 'string' or node.type == 'word':
    #             value = source_code[node.start_byte:node.end_byte]
    #             value = value.strip("\"'")
    #
    #             try:
    #                 parsed_url = urlparse(value)
    #             except Exception as e:
    #                 LOG.error(f"Error parsing URL: {value} in {filename}, message: {e}")
    #                 return
    #             if parsed_url.scheme and parsed_url.netloc:
    #                 domains.append([value, filename])
    #         else:
    #             for child in node.children:
    #                 recursive_search(child)
    #
    #     recursive_search(root_node)
    #     return domains

    def extract_urls_from_file(self, filename):
        LOG.info(f"Extracting URLs from {filename}")
        with open(filename, "rb") as fdata:
            source_code = fdata.read().decode()
        language = self.file_to_language[filename]
        tree = self.parser[language].parse(bytes(source_code, "utf8"))
        root_node = tree.root_node
        domains = []
        url_str_pattern = '(string) @url_str'
        try:
            url_str_query = get_language(language).query(url_str_pattern)
        except Exception as e:
            LOG.error(f"Error parsing {filename}, message: {e}")
            return [['', filename]]
        url_strs = url_str_query.captures(root_node)
        for url_str in url_strs:
            url_node, _ = url_str
            # url = source_code[url_node.start_byte:url_node.end_byte]
            url = url_node.text.decode().strip("\"'")
            # print(url)
            try:
                parsed_url = urlparse(url)
                if parsed_url.scheme and parsed_url.netloc:
                    domains.append([url, filename])
            except Exception as e:
                LOG.error(f"Error parsing URL: {url} in {filename}, message: {e}")
                return
        return domains

    def detect_languages(self):
        """
        Detects programming languages based on a list of filenames.
        """
        languages = set()
        for filename in self.files_list:
            _, ext = os.path.splitext(filename)
            language = extension_to_language.get(ext)
            # print(ext)
            if not language:
                filetype = magic.from_file(filename)
                if "shell" in filetype:
                    language = "bash"
                # elif "makefile" in filetype:
                #     language = "makefile"
            self.file_to_language[filename] = language
            if language:
                languages.add(language)
        self.languages = sorted(languages)

    def set_parsers(self):
        for language in self.languages:
            # LANGUAGE = get_tree_sitter_parser(language)
            # self.parser[language] = tree_sitter.Parser()
            # self.parser[language].set_language(LANGUAGE)
            self.parser[language] = get_parser(language)
            LOG.info(f"Parser set for {language}")

    def run(self):
        ret = {}
        ret["domains"] = []
        for filename in self.files_list:
            ret["domains"].extend(self.extract_urls_from_file(filename))
        return ret

def _get_files_from_dir(
    files_dir, included_globs=None,
    included_no_ext=None,
    excluded_path_strings=None
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
            if _is_file_included(path, included_globs, included_no_ext,
                                 excluded_path_strings):
                files_list.add(path)
            else:
                excluded_files.add(path)

    return files_list, excluded_files


def _is_file_included(
    path, included_globs, included_no_ext, excluded_path_strings, enforce_glob=True
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
    if _matches_glob_list(path, included_globs) or _matches_no_ext(path, included_no_ext) or not enforce_glob:
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

def _matches_no_ext(filename, no_ext_list):
    if not no_ext_list:
        return False
    for no_ext in no_ext_list:
        if no_ext in magic.from_file(filename):
            return True
    return False


