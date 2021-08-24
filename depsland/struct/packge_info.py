from dataclasses import dataclass  # noqa

from ..typehint import *


@dataclass
class PackageInfo:
    name: TName
    version: TVersion
    locations: TLocations
    dependencies: TDependencies
