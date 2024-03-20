import argparse
import sys
import json
from domain_catcher.catcher import DomainCatcher

def main():
    """domain-catcher CLI."""

    parser = argparse.ArgumentParser(
        description="domain-catcher: a URL logger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "targets",
        metavar="target",
        type=str,
        nargs="*",
        help="source file to be tested",
    )

    args = parser.parse_args()

    if not args.targets:
        parser.print_usage()
        sys.exit(2)

    dc = DomainCatcher()

    urls = dc.extract_urls_from_file(args.targets[0])
    print(json.dumps({"urls": urls}))


if __name__ == "__main__":
    main()
