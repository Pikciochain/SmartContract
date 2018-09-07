"""Contains the logic of parsing Pikcio Smart Contract.

It provides entrypoints to validate a Smart Contract and generate its
interface.
"""
import json
import logging
from argparse import ArgumentParser

from mypy.build import parse, Options
from mypy.errors import CompileError

from pikciosc.models import ContractInterface
from pikciosc.parse.endpoint import extract_endpoints
from pikciosc.parse.storage import extract_storage_vars


def parse_string(source, filename):
    """Parses provided source code and returns its interface if successful.

    Raises an exception otherwise.

    :param source: The source code of the contract to parse.
    :type source: str
    :param filename: The name of the file the contract comes from.
    :type filename: str
    :return: The generated interface.
    :rtype: ContractInterface
    """
    logging.debug('Compiling source_code...')
    compiled = parse(source, filename, '__main__', None, options=Options())
    logging.debug('Done.')

    logging.debug('Extracting Storage variables...')
    variable_constants = extract_storage_vars(compiled)
    logging.debug('Done.')

    logging.debug('Extracting endpoints...')
    endpoints = extract_endpoints(compiled)
    logging.debug('Done.')

    logging.debug('Building interface...')
    contract_name = filename.split('.')[0]
    interface = ContractInterface(contract_name, variable_constants, endpoints)
    logging.debug('Done.')

    return interface


def parse_file_cli(source_path):
    """Parses provided source code in a file to generate a contract interface.

    If the code cannot be parsed or code fails to validate, interface won't be
    generated and an error message will be forwarded in the returned object.

    :param source_path: Path to the file containing the code.
    :type source_path: str
    :return: A dictionary encapsulating a parsing result.
    :rtype: dict
    """
    with open(source_path) as fd:
        code = fd.read()
    try:
        sc_interface = parse_string(code, 'submitted_code')
        return sc_interface.to_dict()
    except (CompileError, ValueError, NotImplementedError) as e:
        logging.error(e)
        return {'error': str(e)}


def _parse_args():
    """Loads the arguments from the command line."""
    parser = ArgumentParser(description='Pikcio Smart Contract Parsing '
                                        'module.')
    parser.add_argument("file", type=str, help='source code file to parse')
    parser.add_argument("-i", "--indent", type=int,
                        help='If positive, prettify the output json with tabs')
    parser.add_argument("-o", "--output", type=str, dest='output',
                        help='Path to the generated interface.')
    known_args, _ = parser.parse_known_args()
    return known_args.file, known_args.indent, known_args.output


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    args_file, indent, output_path = _parse_args()
    result = json.dumps(parse_file_cli(args_file), indent=indent)
    if output_path:
        with open(output_path, 'w') as outfile:
            outfile.write(result)
    print(result)
