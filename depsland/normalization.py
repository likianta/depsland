from depsland.typehint import TName


def normalize_name(name: str) -> TName:
    """ Normalize name. """
    return name.lower().replace('_', '-')


def normalize_version(version: str):
    """ Normalize verison (only for internal purpose). """
    return version.lower()
