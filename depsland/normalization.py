def normalize_raw_name(raw_name: str):
    # https://pip.pypa.io/en/stable/cli/pip_install/#requirement-specifiers
    # note: use quotes around specifiers in the shell when using '>', '<', etc.
    return (
        raw_name
            .lower()
            # .replace(' ', '')
            .replace('(', '')
            .replace(')', '')
            .split(';', 1)[0]
            .strip()
    )


def normalize_name(name: str):
    """ Normalize name. """
    # return name.lower().replace('_', '-')
    return name.lower().replace('-', '_')


def normalize_version_spec(version_spec: str):
    """ Normalize verison specifier. """
    if version_spec in ('', '*', '==*'):
        return '*'
    elif version_spec.startswith('['):  # e.g. '[all]'
        return '*'
    else:
        return version_spec
