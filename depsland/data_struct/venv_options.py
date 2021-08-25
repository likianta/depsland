from dataclasses import dataclass  # noqa

from ..path_struct import src_struct
from ..typehint import Union


@dataclass
class VenvOptions:
    name: str  # project or application name, suggest snake case
    venv_id: str
    requirements: Union[list[str], str]
    
    @property
    def venv_name(self):
        return f'{self.name}_{self.venv_id}'
    
    @property
    def venv_path(self):
        return f'{src_struct.venvlinks}/{self.venv_name}'
