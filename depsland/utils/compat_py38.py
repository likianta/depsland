"""
compatibilities list:
    python  feature
    3.9     removeprefix
    3.9     removesufffix
    3.9     list[int]
    3.9     int | None
    3.11    typing.Self
"""


def remove_suffix(name: str, suffix: str) -> str:
    return name[:-len(suffix)]


def substitute_suffix(name: str, old: str, new: str) -> str:
    return name[:-len(old)] + new
