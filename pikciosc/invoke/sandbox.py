"""This module encapsulates features to invoke the shell script in a sandbox.
"""
import json
import logging
import os
import subprocess
import itertools
from tempfile import TemporaryFile

from pikciosc.invoke import shell
from pikciosc.models import ExecutionInfo

_CURRENT_DIR = os.path.dirname(__file__)
_PICKIO_DIR = os.path.dirname(_CURRENT_DIR)


def _flatten_vars_for_cli(variables):
    """Returns a list of strings ready to be passed to a cli parameter
    accepting variables, like --kwargs or --storage

    :param variables: The list of variables to prepare.
    :type variables: list[Variable]
    :return: an enumerable of strings
    :rtype: list[str]
    """
    flat_vars_lists = [
        [
            var.name,
            f'"{var.value}"' if isinstance(var.value, str) else
            f'b"{var.value}"' if isinstance(var.value, bytes) else
            str(var.value)
        ] for var in variables
    ]
    return itertools.chain(*flat_vars_lists)


def _docker_execute(script_path, storage_vars, endpoint, kwargs):
    """Executes provided script inside a docker container and collects its
    output.

    :param script_path: Full path to the script to execute.
    :param storage_vars: The list of storage vars to restore.
    :type storage_vars: list[Variable]
    :param endpoint: Name of endpoint to execute.
    :type endpoint: str
    :param kwargs: List of named arguments to pass to the endpoint.
    :type kwargs: list[Variable]
    :return: The resulting execution info.
    :rtype: ExecutionInfo
    """
    if not os.path.isabs(script_path):
        script_path = os.path.abspath(script_path)

    script_dir, script_name = os.path.split(script_path)

    docker_args = [
        'docker', 'run',
        '--rm',
        '--name', f'{script_name.split(".")[0]}-{endpoint}',
        '-e', 'PYTHONPATH=.',                      # shell.py uses pikciosc
        '-v', f'{_PICKIO_DIR}:/usr/src/pikciosc',  # mount pikciosc
        '-v', f'{script_dir}:/usr/src/scripts',    # mount script folder
        '-w', '/usr/src',
        'python:3.6', 'python', '/usr/src/pikciosc/invoke/shell.py',
        f'/usr/src/scripts/{script_name}', endpoint,
        '--storage', *_flatten_vars_for_cli(storage_vars),
        '--kwargs', *_flatten_vars_for_cli(kwargs),
        '--indent', '4'
    ]
    logging.debug(docker_args)

    with TemporaryFile(mode='w+') as stdout:
        subprocess.call(docker_args, stdout=stdout, stderr=stdout)
        stdout.seek(0)
        try:
            return ExecutionInfo.from_dict(json.load(stdout))
        except ValueError:
            stdout.seek(0)
            raise RuntimeError(stdout.read())


def execute_sandbox(script_path, storage_vars, endpoint, kwargs):
    """Executes provided script and endpoint in a sandbox. The behavior of this
    function depends on the value of the environment variable SANDBOX.

    :param script_path: Full path to the script to execute.
    :param storage_vars: The list of storage vars to restore.
    :type storage_vars: list[Variable]
    :param endpoint: Name of endpoint to execute.
    :type endpoint: str
    :param kwargs: List of named arguments to pass to the endpoint.
    :type kwargs: list[Variable]
    :return: The resulting execution info.
    :rtype: ExecutionInfo
    """
    if os.environ.get('SANDBOX', '').lower() == 'none':
        return shell.execute(script_path, storage_vars, endpoint, kwargs)
    return _docker_execute(script_path, storage_vars, endpoint, kwargs)
