from .packge_info import PackageInfo
from .requester import Requester
from .requirement import Requirement
from .venv_options import VenvOptions

# class Name:
#     raw_name: str
#     norm_name: str
#     # real_name: str
#
#     @property
#     def name(self):
#         return self.norm_name
#
#     @property
#     def name_u(self):
#         # name in snake case format
#         return self.name.replace('-', '_')
#
#
# class Requirement(Name):
#     version: 'Version'
#
#     @property
#     def name_v(self):
#         # name with version
#         return self.norm_name, self.version.norm_ver
#
#
# class Version:
#     sem_ver: str
#     norm_ver: str
#     serial_ver: tuple[int, ...]
#
#     @property
#     def version(self):
#         return self.norm_ver
