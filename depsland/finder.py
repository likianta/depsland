"""
DELETE ME
"""
from collections import defaultdict
from importlib.metadata import DistributionFinder, MetadataPathFinder
from os.path import isfile
from re import compile

from lk_logger import lk
from lk_utils import find_dirs
from lk_utils.read_and_write import load_list

from .typehint import *


def analyse_locations(pip, requirements):
    for name in requirements:
        pip.show()


class PackageFinder:
    
    def __init__(self, path: TPath):
        self.lib_root = path.replace('\\', '/')
        self.lib_dirs = set()
        self.lib_pkgs = {}
        self.pkg_deps = defaultdict(list)
        
        self._key_match = compile(r'[-\w]+')
        self._name_match = compile(r'[\w]+')
        
        self._meta_finder = MetadataPathFinder()
        
        self._indexing()
    
    def _indexing(self):
        self.lib_pkgs.update(self.list_all_packages())
    
    reindexing = _indexing
    
    def list_all_packages(self) -> TPackges:
        lk.loga('listing all packages...')
        
        out = defaultdict(dict)
        
        _used = set()
        
        for dp, dn in find_dirs(self.lib_root, suffix='.dist-info', fmt='zip'):
            if dn in self.lib_dirs:
                continue
            else:
                # lk.loga(dn)
                self.lib_dirs.add(dn)
            
            # name
            record = load_list(f'{dp}/RECORD')
            ''' f'{dp}/RECORD' content example:
                    __pycache__/six.cpython-39.pyc,,
                    six-1.16.0.dist-info/INSTALLER,sha256=zuuue4knoyJ-UwPPXg8fez
                    S7VCrXJQrAP7zeNuwvFQg,4
                    six-1.16.0.dist-info/LICENSE,sha256=i7hQxWWqOJ_cFvOkaWWtI9gq
                    3_YPI5P8J2K2MYXo5sk,1066
                    six-1.16.0.dist-info/METADATA,sha256=VQcGIFCAEmfZcl77E5riPCN
                    4v2TIsc_qtacnjxKHJoI,1795
                    six-1.16.0.dist-info/RECORD,,
                    six-1.16.0.dist-info/WHEEL,sha256=Z-nyYpwrcSqxfdux5Mbn_DQ525
                    iP7J2DG3JgGvOYyTQ,110
                    six-1.16.0.dist-info/top_level.txt,sha256=_iVH_iYEtEXnD8nYGQ
                    YpYFUvkUW9sEO1GYbkeKSAais,4
                    six.py,sha256=TOOfQi7nFGfMrIvtdr6wX4wyHH8M7aknmuLfo2cBBrM,34
                    549
                
                special cases:
                    ../../LICENSE,sha256=o_-3eZYgLX8zFLQWGhZh-5wJKsh4r0OR550wGu3
                    BWGY,1084
                
                each line consists of '{path},{sha256},{size}', we need only the
                first part of path. i.e. '__pycache__', 'six-1.16.0.dist-info',
                'six.py', etc.
            '''
            
            # key
            key = self._name_match.match(dn).group().lower()
            
            for line in record:  # type: str
                # (A)
                # if line.startswith('../'):
                #     #   '../../LICENSE,sha256=o_-3eZYgLX8zFLQWGhZh-5wJKsh4r0OR55
                #     #   0wGu3BWGY,1084'
                #     lk.logt('[D4611]', 'skip', line)
                #     continue
                # (B)
                line = line.lstrip('./')
                #   '../../LICENSE,sha256=o_-3eZYgLX8zFLQWGhZh-5wJKsh4r0OR550wGu
                #   3BWGY,1084' -> 'LICENSE,sha256=o_-3eZYgLX8zFLQWGhZh-5wJKsh4r
                #   0OR550wGu3BWGY,1084'
                
                if '/' in line:
                    basename = line.split('/')[0]
                else:
                    basename = line.split(',')[0]
                '''
                    '__pycache__/six.cpython-39.pyc,,' -> '__pycache__'
                    'six-1.16.0.dist-info/INSTALLER,sha256=zuuue4knoyJ-UwPPXg8fe
                     zS7VCrXJQrAP7zeNuwvFQg,4' -> 'six-1.16.0.dist-info'
                    'six.py,sha256=TOOfQi7nFGfMrIvtdr6wX4wyHH8M7aknmuLfo2cBBrM,3
                     4549' -> 'six.py'
                '''
                if basename in ('__pycache__', 'LICENSE'):
                    continue
                elif basename == dn:
                    continue
                elif basename in _used:
                    continue
                else:
                    _used.add(basename)
                
                name = self._name_match.match(basename).group()
                ''' note: this is case sensitive
                    examples:
                        'PIL' -> 'PIL'
                        'six.py' -> 'six'
                '''
                
                out[key].update({
                    'name'  : name,
                    'deps'  : self.get_dependencies(key),
                    'path'  : (basename, dn),
                    'isfile': isfile(f'{self.lib_root}/{basename}'),
                })
        
        return out
    
    def get_dependencies(self, key: TRawName, recursive=False):
        
        def recurse(keys: List[TRawName], collector: set):
            for key in keys:
                if key in collector:
                    continue
                else:
                    collector.add(key)
                recurse(self.get_dependencies(key, recursive=False), collector)
            return collector

        key = self.normalize_name(key)

        if not recursive:
            if key not in self.pkg_deps:
                for dist in self._meta_finder.find_distributions(
                        context=DistributionFinder.Context(
                            path=[self.lib_root],
                            name=key
                        )
                ):
                    if (requires := dist.requires) is not None:
                        for r in requires:
                            self.pkg_deps[key].append(
                                self._key_match.match(r).group()
                            )
            return self.pkg_deps[key]
        else:
            return list(
                recurse(
                    self.get_dependencies(key, recursive=False),
                    set()
                )
            )
    
    def exists(self, key: TRawName) -> bool:
        key = self.normalize_name(key)
        return key in self.lib_pkgs
    
    def get_info(self, key: TRawName) -> TPackagesInfo:
        key = self.normalize_name(key)
        try:
            info = self.lib_pkgs[key]
        except KeyError:
            raise ModuleNotFoundError
        else:
            return info

    @staticmethod
    def normalize_name(key: TRawName) -> TNormName:
        return key.replace('-', '_')
