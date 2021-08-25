import re

from ..normalization import normalize_name, normalize_version
from ..typehint import *


class Requirement:
    name: TName
    name_id: TNameId
    raw_name: TRawName
    version_spec: TVersionSpec  # followed PEP-440 canonical form.
    #   see `normalization.py > normalize_version`.
    _version: TVersion = ''  # the fixed specified version.
    
    #   see `self.set_fixed_version`.
    
    def __init__(self, raw_name: str):
        self.raw_name = raw_name.lower()
        name, version = self._split_name_and_version()
        self.name = normalize_name(name)
        self.version_spec = normalize_version(version)
    
    def _split_name_and_version(self):
        """
        `self.raw_name` formats:
            xxx
            xxx == 1.2
            xxx == 1.2.0
            xxx >=1.2,<2.0
            xxx (>=1.2,<2.0)
            xxx != 1.3.4.*
            xxx ~= 1.4.2
            xxx == 5.4; python_version < '2.7'
            xxx; sys_platform == 'win32'
        
        References:
            PEP-440: https://www.python.org/dev/peps/pep-0440/#version-specifiers
        """
        name = re.search(r'[-.\w]+', self.raw_name).group()
        version = (
            self.raw_name
                .removeprefix(name)
                .replace(' ', '')
                .replace('(', '')
                .replace(')', '')
                .split(';')[0]
        )
        return name, version
    
    def set_fixed_version(self, version):
        self._version = version.replace('!', 'n')
        #   '!' -> 'n': earlier explicit epoch, e.g. '1!1.1'.
        #       the fixed version will be used in making folder names but '!'
        #       is not allowed, so we convert it to 'n'.
    
    @property
    def version(self):
        assert self._version, (
            'The version is not specified, you need to call `Requirement'
            '.update_version` to update version to a specific number.',
            self.name, self.version_spec
        )
        return self._version
    
    @property
    def name_id(self):
        """
        Returns:
            examples:
                xxx-1.0
                xxx-1.0.3
                xxx-1.0.3a0
                xxx-1.0.3dev1.pre3.post5
                ...
        """
        return f'{self.name}-{self.version}'
