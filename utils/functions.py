from typing import Any


def get_reversed_id(object_: Any) -> str:
    # Note: `get_reversed_id` allows to create unique identifiers.
    # It reverses object's id to make it more distinguishable.
    # CPython-specific function.
    return str(id(object_))[::-1]
