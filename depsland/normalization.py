import re

from .data_struct.special_versions import LATEST


def normalize_raw_name(raw_name: str):
    # https://pip.pypa.io/en/stable/cli/pip_install/#requirement-specifiers
    # note: use quotes around specifiers in the shell when using '>', '<', etc.
    return (
        raw_name
            .lower()
            # .replace(' ', '')
            .replace('(', '')
            .replace(')', '')
            .strip()
    )


def normalize_name(name: str):
    """ Normalize name. """
    # return name.lower().replace('_', '-')
    return name.lower().replace('-', '_')


def normalize_version_spec(version_spec: str):
    """ Normalize verison specifier. """
    version_spec = version_spec.replace(' ', '')
    if ';' in version_spec:  # e.g. ">=0.15.2;extra=='uvloop'"
        version_spec = version_spec.split(';')[0]
    
    if version_spec in ('', '*', '==*'):
        return LATEST
    
    if version_spec.startswith('['):  # e.g. '[toml]>=5.0.2'
        if version_spec.endswith(']'):
            return LATEST
        else:
            version_spec = version_spec.split(']')[-1]
    
    return re.search(r'[-.,><=!\w]+', version_spec).group()
