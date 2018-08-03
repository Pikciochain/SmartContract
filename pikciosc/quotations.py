"""This module includes features enabling to create quotes related to Smart
Contract submission."""
import os
import json
import base64
import inspect
import importlib.util
from os import environ

from pikciosc.compile import compile_source


ENV_PKC_SC_SUBMIT_CHAR_COST = 'PKC_SC_SUBMIT_CHAR_COST'
ENV_PKC_SC_EXEC_LINE_COST = 'PKC_SC_EXEC_LINE_COST'


class Quotation(object):
    """Stands for the result of a Smart Contract quotation.
    """

    def __init__(self, code_length, char_cost):
        """Creates a new Quotation form provided elements.

        :param code_length: The length of the evaluated code, once compiled and
            encoded to base 64.
            :type code_length: int
        :param char_cost: The cost of a single character.
        :type char_cost: float
        """
        self.code_length = code_length
        self.char_cost = char_cost
        self.total_price = code_length * char_cost

    def to_json(self):
        """Provides a JSON representation of this Quotation."""
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_stamp):
        """Creates a new Quotation from provided JSON string."""
        try:
            return cls.from_dict(json.loads(json_stamp))
        except (TypeError, ValueError):
            return None

    @classmethod
    def from_dict(cls, json_dct):
        try:
            return cls(
                json_dct['code_length'],
                json_dct['char_cost'],
            )
        except KeyError:
            return None


def _unit_cost(env_var):
    """Retrieves the actual cost of a single unit counted in a quotation.

    :param env_var: The environment variable holding the cost per unit value.
    :type env_var: str
    :returns: The cost of a unit (character, line), to create a quotation.
    :rtype: float
    """
    raw_unit_cost = environ.get(env_var)
    if raw_unit_cost is None:
        raise EnvironmentError("'{}' must be set in order to generate "
                               "quotes.".format(env_var))
    return float(raw_unit_cost)


def get_submit_quotation(source):
    """Creates and returns a quotation for submitting provided source code.

    The source code is compiled and encoded as base64 before quotation takes
    place.

    :param source: The source code to compile.
    :type source: str
    :return: The quotation.
    :rtype: Quotation
    """
    bytecode_path = compile_source(source)
    try:
        with open(bytecode_path, 'rb') as fd:
            code_len = len(base64.encodebytes(fd.read()))
        cost_per_char = _unit_cost(ENV_PKC_SC_SUBMIT_CHAR_COST)
        return Quotation(code_len, cost_per_char)
    finally:
        os.remove(bytecode_path)


def _load_module(module_path):
    """Loads the module at specified path and returns it.

    :param module_path: The path to the module to load. The module is loaded in
        current context.
    :type: module_path :str
    :return: The loaded module.
    :rtype: CodeType
    """
    module_name = os.path.basename(module_path).split('.')[0]
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Module '{module_name}' could not be found in"
                                f" path.")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def get_exec_quotation(compiled_file, endpoint_name):
    """Creates and returns a quotation for executing provided endpoint.

    :param compiled_file: Path to the bytecode.
    :type compiled_file: str
    :param endpoint_name: Name of executed endpoint.
    :type endpoint_name: str
    :return: The quotation.
    :rtype: Quotation
    """
    module = _load_module(compiled_file)
    endpoint = getattr(module, endpoint_name)
    # Please note that here, "lines" contains the endpoint name and comments
    # as well.
    lines, _ = inspect.getsourcelines(endpoint)

    cost_per_line = _unit_cost(ENV_PKC_SC_EXEC_LINE_COST)
    return Quotation(len(lines), cost_per_line)


def get_submit_quotation_cli(source):
    """Creates and returns a quotation for provided source code.

    The source code is compiled and encoded as base64 before quotation takes
    place.

    :param source: The source code to compile.
    :type source: str
    :return: A JSON dictionary standing for the quotation.
    :rtype: dict
    """
    quotation = get_submit_quotation(source)
    return {
        'code_len': quotation.code_length,
        'char_cost': quotation.char_cost,
        'total_price': quotation.total_price
    }
