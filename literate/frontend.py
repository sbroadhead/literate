import argparse
from collections import defaultdict
import sys

from literate import Corpus, Config
from literate.utils import load_json


def render(infile, outfile, config, formats):
    text = infile.read()
    corpus = Corpus(text, config, formats)
    outfile.write(corpus.render())


def main():
    """
    Main application entry point.
    """

    def format(str):
        parts = str.split('=')
        if len(parts) != 2:
            raise argparse.ArgumentError('--format', 'Expected --format LANG=FILENAME')
        lang, filename = parts
        try:
            cfg = Config.load(filename)
        except (IOError, ValueError):
            raise argparse.ArgumentError('--format', 'Failed to load format file {}'.format(parts[1]))
        return lang, cfg

    def config(str):
        return Config.load(str)

    parser = argparse.ArgumentParser(description='Literate code preprocessor')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-o', dest='outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('--config', type=config)
    parser.add_argument('--format', action='append', type=format, default=[])

    args = parser.parse_args()

    formats = defaultdict(Config)
    for lang, fmt in args.format:
        formats[lang] += fmt

    render(args.infile, args.outfile, args.config, formats)