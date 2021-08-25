from dataclasses import dataclass  # noqa

from ..typehint import *


@dataclass
class PackageInfo:
    name: TName
    name_id: TNameId
    version: TVersion
    locations: TLocations
    dependencies: TDependencies
