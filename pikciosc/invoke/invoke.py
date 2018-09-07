"""This module focused on invoking an already registered contract endpoint.
"""
import json
import logging
import os
from argparse import ArgumentParser

from pikciosc.invoke.sandbox import execute_sandbox
from pikciosc.invoke.utils import inflate_cli_arguments
from pikciosc.models import ExecutionInfo, ContractInterface


def find_script(bin_folder, contract_name):
    """Finds the script to execute based on the contract name.

    :param bin_folder: The folder containing the scripts.
    :type bin_folder: str
    :param contract_name: Name of the contract to execute.
    :type contract_name: str
    :return: Path to the script to execute, or None if nothing found.
    """
    # Look for compiled scripts first.
    for ext in ('pyc', 'py'):
        script_path = os.path.join(bin_folder, f'{contract_name}.{ext}')
        if os.path.exists(script_path):
            return script_path
    return None


def _get_contract_interface(interface_folder, contract_name):
    """Fetch contract interface from directory structure.

    :param interface_folder: Folder where interfaces are stored.
    :type interface_folder : str
    :param contract_name: Name of contract.
    :type contract_name: str
    :return: ContractInterface
    """
    file_path = os.path.join(interface_folder, f'{contract_name}.json')
    contract_interface = ContractInterface.from_file(file_path)
    if not contract_interface:
        raise FileNotFoundError(f"No interface for '{contract_name}'.")
    return contract_interface


def invoke(bin_folder, interface_folder, last_exec_info, contract_name,
           endpoint, kwargs):
    """Invoke a contract endpoint with provided arguments.

    Storage variables are restored from previous contract execution and saved
    once the execution is complete and only if it is successful.

    :param bin_folder: Path to the folder containing contract compiled scripts.
    :type bin_folder: str
    :param interface_folder: Path to the folder containing contract interfaces.
    :type interface_folder: str
    :param last_exec_info: Result of previous execution, if any.
    :type last_exec_info: ExecutionInfo
    :param contract_name: Name of the contract to execute.
    :type contract_name: str
    :param endpoint: Name of endpoint to execute.
    :type endpoint: str
    :param kwargs: List of named arguments to pass to the endpoint.
    :type kwargs: list[Variable]
    :return: the execution details.
    """
    script_path = find_script(bin_folder, contract_name)
    if not script_path:
        raise ValueError(f'No executable for contract {contract_name}.')

    interface = _get_contract_interface(interface_folder, contract_name)
    if not interface.is_supported_endpoint(endpoint):
        raise ValueError(f'Endpoint {endpoint} is invalid for contract '
                         f'{contract_name}.')

    # Acquire execution lock using "with"
    vars_ = (
        last_exec_info.storage_after if last_exec_info else
        interface.storage_vars
    )
    new_exec_info = execute_sandbox(script_path, vars_, endpoint, kwargs)
    return new_exec_info


def invoke_cli(bin_folder, interface_folder, last_exec_path, contract_name,
               endpoint, flat_kwargs):
    """Invoke a contract endpoint with provided arguments coming from cli.

    Storage variables are restored from previous contract execution and saved
    once the execution is complete and only if it is successful.

    :param bin_folder: Path to the folder containing contract compiled scripts.
    :type bin_folder: str
    :param interface_folder: Path to the folder containing contract interfaces.
    :type interface_folder: str
    :param last_exec_path: Path to the last execution, if any.
    :type last_exec_path: str
    :param contract_name: Name of the contract to execute.
    :type contract_name: str
    :param endpoint: Name of endpoint to execute.
    :type endpoint: str
    :param flat_kwargs: List of named arguments to pass to the endpoint.
    :type flat_kwargs: list
    :return: the execution details.
    """
    kwargs = inflate_cli_arguments(flat_kwargs)
    last_exec_info = ExecutionInfo.from_file(last_exec_path)
    return invoke(bin_folder, interface_folder, last_exec_info,
                  contract_name, endpoint, kwargs).to_dict()


def _parse_args():
    """Loads the arguments from the command line."""
    parser = ArgumentParser(description='Pikcio Smart Contract Invoker')
    parser.add_argument("bin_folder", type=str,
                        help='folder where python binaries are stored.')
    parser.add_argument("interface_folder", type=str,
                        help='folder where contract interfaces are stored.')
    parser.add_argument("endpoint", type=str,
                        help='endpoint to call')
    parser.add_argument("contract_name", type=str,
                        help='Name of contract to execute.')
    parser.add_argument("--kwargs", "-kw", dest="kwargs", nargs='*',
                        help='List of args names and values')
    parser.add_argument("--last_exec_path", '-le', type=str,
                        dest="last_exec_path", default='',
                        help='Path to the last execution, if any')
    parser.add_argument("-i", "--indent", type=int,
                        help='If positive, prettify the output json with tabs')
    parser.add_argument("-o", "--output", type=str, dest='output',
                        help='Path to the output file to create')
    known_args, _ = parser.parse_known_args()
    return (
        known_args.bin_folder, known_args.interface_folder,
        known_args.last_exec_path, known_args.endpoint,
        known_args.contract_name, known_args.kwargs, known_args.indent,
        known_args.output
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    args = _parse_args()
    output_path = args[-1]
    json_result = json.dumps(invoke_cli(*args[:-2]), indent=args[-2])

    if output_path:
        with open(output_path, 'w') as outfile:
            outfile.write(json_result)
    print(json_result)
