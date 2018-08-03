"""This module encapsulates extraction of Smart Contract (SC) endpoints from
compiled source code.
"""
from mypy.nodes import FuncDef, StrExpr, ExpressionStmt
from mypy.types import AnyType

from pikciosc.models import EndPointDef, TypedNamed


def _is_valid_endpoint(def_):
    """Tells whether provided definition is a valid SC endpoint."""
    return isinstance(def_, FuncDef) and not def_.name().startswith('_')


def _check_endpoint_typing(raw_endpoint):
    """Checks that provided endpoint has return and arg types correctly set.

    :param raw_endpoint: The raw endpoint resulting from extraction.
    :type raw_endpoint: FuncDef
    """
    if not raw_endpoint.type:
        raise ValueError(
            f"line {raw_endpoint.line}: error: Required type hint or "
            f"annotation is missing for endpoint '{raw_endpoint.name()}'.")

    arguments = raw_endpoint.type.items()[0]
    if any(isinstance(arg_type, AnyType) for arg_type in arguments.arg_types):
        raise ValueError(
            f"line {raw_endpoint.line}: error: typing is missing for some "
            f"parameters in type annotation of '{raw_endpoint.name()}'.")


def _extract_parameters(raw_endpoint):
    """Extracts parameter definition from the raw endpoint.

    Type checking must have been performed before.

    :param raw_endpoint: The raw endpoint resulting from extraction.
    :type raw_endpoint: FuncDef
    :return: A mapping of each parameter to its type.
    :rtype dict
    """
    arguments = raw_endpoint.type.items()[0]
    arg_names = arguments.arg_names
    arg_types = arguments.arg_types
    return [
        TypedNamed(arg_name, arg_types[i].name)
        for i, arg_name in enumerate(arg_names)
    ]


def _extract_documentation_if_any(raw_endpoint):
    """Extracts documentation from the raw endpoint if it exists.

    The documentation is the first string expression statement of

    :param raw_endpoint: The raw endpoint resulting from extraction.
    :type raw_endpoint: FuncDef
    :return: A mapping of each parameter to its type.
    :rtype dict
    """
    string_expressions = [
        decl.expr                               # Collect all statements
        for decl in raw_endpoint.body.body      # from endpoint body
        if isinstance(decl, ExpressionStmt)     # if statement is an expression
        if isinstance(decl.expr, StrExpr)       # that has a string content
    ]
    return string_expressions[0].value if string_expressions else None


def _create_endpointdef(raw_endpoint):
    """Analyses candidate endpoint resulting from compilation and creates an
    endpoint out of it.

    Validation is performed on the raw endpoint, particularly regarding types.

    :param raw_endpoint: The raw endpoint resulting from extraction.
    :type raw_endpoint: FuncDef
    :return: The resulting Pikcio endpoint.
    :rtype EndPointDef
    """
    _check_endpoint_typing(raw_endpoint)

    return EndPointDef(
        raw_endpoint.name(),
        raw_endpoint.type.ret_type.name,
        _extract_parameters(raw_endpoint),
        _extract_documentation_if_any(raw_endpoint)
    )


def extract_endpoints(compiled_source):
    """Validates and extracts the endpoints from a compiled smart contract.

    :param compiled_source: The compiled code resulting of a mypy parse.
    :type compiled_source: MypyFile
    :return: A list of all the valid endpoints in the compiled code.
    :rtype: list[EndPointDef]
    """
    return [
        _create_endpointdef(def_)
        for def_ in compiled_source.defs
        if _is_valid_endpoint(def_)
    ]
