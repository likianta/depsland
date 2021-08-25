from depsland.typehint import TName


def normalize_name(name: str) -> TName:
    """ Normalize name. """
    # return name.lower().replace('_', '-')
    return name.lower().replace('-', '_')


def normalize_version(version_rng: str):
    """ Normalize verison (only for internal purpose).
    
    Returns:
        ''
        'latest'
        '1.0'
        '1.0.*'
    """
    if ',' in version_rng or '!' in version_rng:
        return ''
    elif version_rng in ('', '*', '==*'):
        return 'latest'
    elif version_rng.startswith('=='):
        return version_rng.removeprefix('==')
    else:
        return ''
