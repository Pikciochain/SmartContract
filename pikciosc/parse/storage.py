"""This module encapsulates extraction of Smart Contract (SC) storage variables
from compiled source code.
"""
from mypy.nodes import AssignmentStmt, NameExpr, Expression, FloatExpr, \
    IntExpr, StrExpr, UnicodeExpr, BytesExpr, ListExpr, RefExpr, SetExpr, \
    TupleExpr, DictExpr

from pikciosc.models import Variable

_MYPY_PY_TYPE_MAPPING = {
    FloatExpr: (float, 'value'),
    IntExpr: (int, 'value'),
    StrExpr: (str, 'value'),
    UnicodeExpr: (str, 'value'),
    BytesExpr: (bytes, 'value'),
    ListExpr: (list, 'items'),
    SetExpr: (set, 'items'),
    TupleExpr: (tuple, 'items'),
    DictExpr: (dict, 'items'),
}
"""Maps a supported mypy type to its python counterpart and to the attribute of
 the expression to use to collect the value."""

_STORAGE_FORBIDDEN_TYPES_MAPPINGS = {
    RefExpr: ('fullname', "'{}' is a reference and cannot be used as a "
                          "storage var initializer."),
    NameExpr: ('name', "'{}' is a name expression and cannot be used as a "
                       "storage var initializer.")
}
"""Maps an unsupported mypy type to the attribute of the expression to use to 
collect the value and to an error message format."""


def _is_expression_valid_storage_var_name(expr):
    """Check whether an expression is a valid name for a storage var.

    :param expr: The expression to check.
    :type expr: Expression
    :return: True if the expression is a valid storage name declaration.
    :rtype: bool
    """
    return isinstance(expr, NameExpr) and not expr.name.startswith('_')


def _create_storage_var(lvalue, rvalue):
    """Examines the provided rvalue to deduce the actual value and type of a
    storage variable assignation.

    :param rvalue: Value assigned to a storage variable.
    :type rvalue: Expression
    :return: Value and type of the rvalue if it is supported.
    :rtype: Variable
    """
    rvalue_type = type(rvalue)

    # Check for allowed types.
    if rvalue_type in _MYPY_PY_TYPE_MAPPING:
        py_type, attr = _MYPY_PY_TYPE_MAPPING[rvalue_type]
        return Variable(lvalue.name, py_type, getattr(rvalue, attr))

    # Check for forbidden types
    if rvalue_type in _STORAGE_FORBIDDEN_TYPES_MAPPINGS:
        attr, err_fmt = _STORAGE_FORBIDDEN_TYPES_MAPPINGS[rvalue_type]
        raise ValueError(err_fmt.format(getattr(rvalue, attr)))

    # Unhandled cases
    raise NotImplementedError(
        f"line {lvalue.line}: error: Storage value {rvalue} is not allowed yet"
        f" by the Pikcio contract compiler."
    )


def extract_storage_vars(compiled_source):
    """Validates and extracts the storage variables from a compiled smart
    contract.

    :param compiled_source: The compiled code resulting of a mypy parse.
    :type compiled_source: MypyFile
    :return: A list of all the valid storage variables in the compiled code.
    :rtype: list[Variable]
    """
    return [
        _create_storage_var(lvalue, def_.rvalue)
        for def_ in compiled_source.defs
        if isinstance(def_, AssignmentStmt)
        for lvalue in def_.lvalues
        if _is_expression_valid_storage_var_name(lvalue)
    ]
