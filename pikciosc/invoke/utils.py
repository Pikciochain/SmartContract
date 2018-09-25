import itertools
import os
import pickle
import tempfile
import uuid

from pikciosc.models import Variable


def _get_temp_filename():
    """Generates a temporary unique filename.

    :rtype: str
    """
    return os.path.join(tempfile.gettempdir(), f'{str(uuid.uuid4())}.storage')


def inflate_cli_arguments(raw_args):
    """Converts the list of provided flat arguments into objects. The arguments
    list must be a concatenation of tuples (name, val).

    :param raw_args: The list of arguments.
    :type raw_args: list
    :return: The list of inflated arguments.
    :rtype: list[Variable]
    """
    if not raw_args:
        return []

    if len(raw_args) % 2:
        raise ValueError('Argument list is unbalanced. It must be a list of '
                         'tuples (name, value).')
    couples = [raw_args[i:i + 2] for i in range(0, len(raw_args), 2)]
    return [
        Variable(name, type(eval(val)), eval(val))
        for name, val in couples
    ]


def flatten_vars_for_cli(variables):
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


def serialise_vars(variables):
    """Serialise provided variables into a file.

    The file can be read using following unserialise_vars function.

    :param variables: The list of variables to save.
    :type variables: list[Variable]
    :return: The path to the created file.
    :rtype: str
    """
    filename = _get_temp_filename()
    with open(filename, 'w') as fd:
        pickle.dump(variables, fd)
    return filename


def unserialise_vars(variables_path):
    """Inflates variables previously serialised using serialise_vars.

    :param variables_path: Path to the file where the variables are stored.
    :type variables_path: str
    :return: The inflated variables. Should be a list of variables.
    :rtype: list[Variable]
    """
    with open(variables_path, 'r') as fd:
        return pickle.load(fd)
