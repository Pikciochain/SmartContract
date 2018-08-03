"""This module encapsulates the tools chose to compile the code into
bytecode.
"""
import uuid
import tempfile
from py_compile import compile

import os


def _get_temp_filename():
    """Generates a temporary unique filename.

    :rtype: str
    """
    return os.path.join(tempfile.gettempdir(), f'{str(uuid.uuid4())}.py')


def compile_file(source_file, dest_file=None):
    """Compile provided file of source code into specified location.

    :param source_file: Path to the file to compile.
    :type source_file: str
    :param dest_file: Output path of compiled code. If omitted, destination
        will match PEP requirements.
    :return: The path to the compiled file.
    :rtype: str
    """
    return compile(source_file, dest_file, optimize=2)


def compile_source(source, dest_file=None):
    """Compile provided source code into specified location.

    :param source: Source code to compile.
    :type source: str
    :param dest_file: Output path of compiled code. If omitted, destination
        will match PEP requirements.
    :return: The path to the compiled file.
    :rtype: str
    """
    temp_name = _get_temp_filename()
    try:
        with open(temp_name, 'w') as fd:
            fd.write(source)
        return compile_file(temp_name, dest_file)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)
