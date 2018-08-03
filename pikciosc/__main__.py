"""This module makes the pikciosc package executable.
You can call it from CLI to use its features. See README.
"""
import json
import logging
from argparse import ArgumentParser

from pikciosc.parse import parse_file_cli
from pikciosc.quotations import get_submit_quotation_cli
from pikciosc.compile import compile_file


def compile_file_adapter(args_file):
    return {'output_file':  compile_file(args_file, f'{args_file}c')}


_SVC_MAP = {
    'parse': parse_file_cli,
    'quote': get_submit_quotation_cli,
    'compile': compile_file_adapter,
}


def _parse_args():
    """Loads the arguments from the command line."""
    parser = ArgumentParser(description='Pikcio Smart Contract package.')
    parser.add_argument("service", choices=_SVC_MAP.keys(),
                        help='Name of service to use')
    parser.add_argument("-f", "--file", dest="file", type=str,
                        help='source code file to submit')
    parser.add_argument("-i", "--indent", type=int,
                        help='If positive, prettify the output json with tabs')
    known_args, _ = parser.parse_known_args()
    return known_args.service, known_args.file, known_args.indent


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    service, args_file, indent = _parse_args()
    result = _SVC_MAP[service](args_file)
    print(json.dumps(result, indent=indent))

