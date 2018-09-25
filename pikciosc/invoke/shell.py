"""This script acts as a shell to load contract to execute and call required
endpoint.
"""
import os
import json
import importlib.util
from argparse import ArgumentParser

from pikciosc.invoke.utils import inflate_cli_arguments, unserialise_vars
from pikciosc.models import CallInfo, ExecutionInfo, Variable


def _load_module(module_path):
    """Loads the module at specified path and returns it.

    :param module_path: The path to the module to load. The module is loaded in
        current context.
    :type: module_path :str
    :return: The loaded module.
    :rtype: module
    """
    module_name = os.path.basename(module_path).split('.')[0]
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Module '{module_name}' could not be found in"
                                f" path.")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _restore_storage(module, storage_vars):
    """Updates the module storage vars using the provided values.

    :param module: The module whose storage vars have to be updated.
    :type module: module
    :param storage_vars: The list of storage vars to restore.
    :type storage_vars: list[Variable]
    """
    for storage_var in storage_vars:
        setattr(module, storage_var.name, storage_var.value)


def _collect_storage(module, storage_vars):
    """Collects the current values for the provided storage_vars and returns
    them.

    :param module: The module to inspect.
    :param storage_vars: The storage vars to collect.
    :type storage_vars: list[Variable]
    :return: A dictionary of the new storage vars states.
    :rtype: list[Variable]
    """
    return [
        Variable(
            var.name,
            type(getattr(module, var.name)),
            getattr(module, var.name),
        )
        for var in storage_vars
    ]


def _call(module, endpoint_name, args):
    """Calls provided endpoint with some named arguments and return an object
    containing call info and result.

    :param module: Module to call endpoint in.
    :param endpoint_name: Name of endpoint to call.
    :type: endpoint_name: str
    :param args: Named arguments to pass to the endpoint
    :type args: list[Variable]
    :return: Call details and result.
    :rtype: CallInfo
    """
    endpoint = getattr(module, endpoint_name)
    call_info = CallInfo(endpoint_name, args)
    call_info.stop_watch.set_start()
    try:
        kwargs = {arg.name: arg.value for arg in args}
        call_info.ret_val = endpoint(**kwargs)
    except Exception as e:
        call_info.success_info.error = str(e)
    call_info.stop_watch.set_end()
    return call_info


def execute(module_path, storage_vars, endpoint_name, kwargs):
    """Calls a module endpoint after restoring storage vars.

    :param module_path: Path to module to call endpoint in.
    :type module_path: str
    :param storage_vars: The list of storage vars to restore.
    :type storage_vars: list[Variable]
    :param endpoint_name: Name of endpoint to call.
    :type: endpoint_name: str
    :param kwargs: Named arguments to pass to the endpoint
    :type kwargs: list[Variable]
    :return: Execution details and result.
    :rtype: ExecutionInfo
    """
    execution_info = ExecutionInfo(storage_vars)
    execution_info.stop_watch.set_start()

    try:
        module = _load_module(module_path)
        _restore_storage(module, storage_vars)
        execution_info.call_info = _call(module, endpoint_name, kwargs)
        execution_info.storage_after = _collect_storage(module, storage_vars)
    except Exception as e:
        execution_info.success_info.error = str(e)

    execution_info.stop_watch.set_end()
    return execution_info


def execute_cli(module_path, flat_storage_vars, endpoint_name, flat_args):
    """Calls a module endpoint after restoring storage vars.

    :param module_path: Path to module to call endpoint in.
    :type module_path: str
    :param flat_storage_vars: The list of storage vars components to inflate.
    :type flat_storage_vars: list
    :param endpoint_name: Name of endpoint to call.
    :type: endpoint_name: str
    :param flat_args: Named arguments to pass to the endpoint
    :type flat_args: list
    :return: Execution details and result.
    :rtype: dict
    """
    args = inflate_cli_arguments(flat_args)
    storage_vars = unserialise_vars(flat_storage_vars)
    execution_info = execute(module_path, storage_vars, endpoint_name, args)
    return execution_info.to_dict()


def _parse_args():
    """Loads the arguments from the command line."""
    parser = ArgumentParser(description='Pikcio Smart Contract Shell')
    parser.add_argument("script", type=str,
                        help='python script to import')
    parser.add_argument("endpoint", type=str,
                        help='endpoint to call')
    parser.add_argument("--storage", "-s", dest="storage",
                        help='Path to serialised storage vars')
    parser.add_argument("--kwargs", "-kw", dest="kwargs", nargs='*',
                        help='List of args names and values')
    parser.add_argument("-i", "--indent", type=int,
                        help='If positive, prettify the output json with tabs')
    parser.add_argument("-o", "--output", type=str, dest='output',
                        help='Path to the output file to create')
    known_args, _ = parser.parse_known_args()
    return (
        known_args.script, known_args.storage, known_args.endpoint,
        known_args.kwargs, known_args.indent, known_args.output
    )


if __name__ == '__main__':
    cli_args = _parse_args()
    output_path = cli_args[-1]
    json_result = json.dumps(execute_cli(*cli_args[:-2]), indent=cli_args[-2])
    if output_path:
        with open(output_path, 'w') as outfile:
            outfile.write(json_result)
    print(json_result)
