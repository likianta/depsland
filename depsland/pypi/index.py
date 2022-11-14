import typing as t

from lk_utils import dumps
from lk_utils import loads

from ..normalization import T as T0
from ..paths import pypi as pypi_paths


class T:
    Name = T0.Name
    NameId = str  # f'{Name}-{FixedVersion}'
    Path = str
    Version = T0.Version
    
    # indexes
    Dependencies = t.Dict[NameId, t.List[NameId]]
    Name2Versions = t.Dict[Name, t.List[Version]]
    #   t.List[...]: a sorted versions list, from new to old.
    NameId2Paths = t.Dict[Version, t.Tuple[Path, Path]]
    #   t.List[...]: tuple[downloaded_path, installed_path]
    #       notice: the paths are relative to `paths.pypi.root`
    #       why do we use relative paths?
    #       based on the experience of debugging depsland (in project mode),
    #       the abspath is not convenience for symbolic links.
    Updates = t.Dict[Name, int]


class Index:
    name_2_versions: T.Name2Versions
    name_id_2_paths: T.NameId2Paths
    dependencies: T.Dependencies
    updates: T.Updates
    
    # # update_freq = 60 * 60 * 24 * 7  # one week
    update_freq = -1
    
    def __init__(self):
        self._load_index()
        # atexit.register(self.save_index)
    
    def _load_index(self):
        self.name_2_versions = loads(pypi_paths.name_2_versions)
        self.name_id_2_paths = loads(pypi_paths.name_id_2_paths)
        self.dependencies = loads(pypi_paths.dependencies)
        self.updates = loads(pypi_paths.updates)
    
    def save_index(self) -> None:
        dumps(self.name_2_versions, pypi_paths.name_2_versions)
        dumps(self.name_id_2_paths, pypi_paths.name_id_2_paths)
        dumps(self.dependencies, pypi_paths.dependencies)
        dumps(self.updates, pypi_paths.updates)
