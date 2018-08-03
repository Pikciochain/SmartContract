""" This module describes an example of a Pikcio contrat.
Version: 0.1
Author: Pikcio
"""
_RATE_1 = 0.4  # Internal rate. Not saved
_RATE_2 = 0.2  # Internal rate. Not saved
last_rate = 0.3  # last given rate. Updated after each call
other_var = "test"


def _get_previous_rate():  # Internal helper function
    return last_rate or 0.0


def compute_rate(amount):  # endpoint 1
    # type: (float) -> float
    global last_rate
    last_rate = _RATE_1 * amount if amount < 200 else _RATE_2 * amount
    return last_rate


def reset_last_rate() -> None:  # endpoint 2
    global last_rate
    last_rate = None


def more_complex_endpoint(a: str, b:int, c:list) -> str:
    pass


def more_complex_endpoint_py2(a, b, c):
    # type: (str, int, list[int]) -> str
    """Documentation of my method. It is more complicated"""
    return "test"
