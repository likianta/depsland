from dataclasses import dataclass  # noqa

from ..path_struct import src_struct
from ..typehint import List
from ..typehint import TRequirement


@dataclass
class VenvOptions:
    name: str  # project or application name, suggest snake case
    venv_id: str
    requirements: List[TRequirement]
    
    @property
    def venv_name(self):
        return f'{self.name}_{self.venv_id}'
    
    @property
    def venv_path(self):
        return f'{src_struct.venvlinks}/{self.venv_name}'
