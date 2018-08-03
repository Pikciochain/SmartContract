from pikciosc.models import Variable


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
