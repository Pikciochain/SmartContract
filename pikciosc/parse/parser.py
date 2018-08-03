"""Contains the logic of parsing Pikcio Smart Contract.

It provides entrypoints to validate a Smart Contract and generate its
interface.
"""
import logging
from os import path

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


def _build_parse_result(contract_interface=None, error=None):
    """Builds a response to a parse() call.

    :param contract_interface: In case of successful parsing, the contract
        interface definition
    :type contract_interface: ContractInterface
    :param error: In case of failure, the error message.
    :type error: str
    :return: A dictionary encapsulating a parsing result.
    :rtype: dict
    """
    return contract_interface.to_dict() if error is None else {'error': error}


def parse_string_cli(source, filename='submitted_code'):
    """Parses provided source code to generate a contract interface.

    If the code cannot be parsed or code fails to validate, interface won't be
    generated and an error message will be forwarded in the returned object.

    :param source: The source code of the contract to parse.
    :type source: str
    :param filename: Optional name of the submitted file containing the code.
    :type filename: str
    :return: A dictionary encapsulating a parsing result.
    :rtype: dict
    """
    try:
        result = parse_string(source, filename)
        return _build_parse_result(contract_interface=result)
    except (CompileError, ValueError, NotImplementedError) as e:
        logging.error(e)
        return _build_parse_result(error=str(e))


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
    return parse_string_cli(code, path.basename(source_path))
