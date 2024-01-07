import re
import typing as t

from lk_utils import fs

from .index import Index
from .index import T as T0
from .. import normalization as norm
from ..paths import pypi as pypi_paths
from ..pip import Pip
from ..pip import pip as _default_pip
from ..venv import link_venv

__all__ = ['LocalPyPI', 'T', 'pypi']


class T(T0):
    IsNew = bool
    Path = str
    VersionSpecs = t.Iterable[norm.VersionSpec]


class LocalPyPI:
    index: Index
    pip: Pip
    
    def __init__(self, pip: Pip = _default_pip) -> None:
        self.index = Index()
        self.pip = pip
        self.update_index = self.index.update_index
    
    # -------------------------------------------------------------------------
    # main methods
    
    # TODO: rename `download_one` to `sole_download`?
    def download_one(
        self,
        pkg_id: T.PackageId,
        custom_url: str = None,
        _auto_save_index: bool = True
    ) -> T.Path:
        if custom_url:
            assert pkg_id in custom_url, (pkg_id, custom_url)
            resp = self.pip.run(
                ('download', custom_url),
                ('--no-deps', '--no-index'),
                ('-d', pypi_paths.downloads),
            )
        else:
            name, ver = self.split(pkg_id)
            resp = self.pip.download(
                name, f'=={ver}',
                no_dependency=True,
            )
        for path, _ in self._parse_pip_download_response(resp):
            if _auto_save_index:
                self.index.add_to_index(path, 0)
            return path
    
    def install_one(
        self,
        pkg_id: T.PackageId,
        path: T.Path,
        _auto_save_index: bool = True
    ) -> T.Path:
        src_path = path
        dst_path = self.get_install_path(pkg_id)
        if not fs.exists(dst_path):
            fs.make_dirs(dst_path)
        self.pip.run(
            ('install', src_path),
            ('--no-deps', '--no-index'),
            ('-t', dst_path),
        )
        if _auto_save_index:
            self.index.add_to_index(dst_path, 1)
        return dst_path
    
    def download_all(
        self, requirements_file: str
    ) -> t.Iterator[t.Tuple[T.Path, T.IsNew]]:
        resp = self.pip.download_r(requirements_file)
        yield from self._parse_pip_download_response(resp)
    
    def install_all(
        self,
        downloaded_files: t.Iterable[T.Path],
        # _skip_existed: bool = True
    ) -> t.Iterator[t.Tuple[T.PackageId, T.Path, T.IsNew]]:
        for filepath in downloaded_files:
            filename = fs.basename(filepath)
            name, version = norm.split_filename_of_package(filename)
            pkg_id = f'{name}-{version}'
            print(pkg_id, ':i2v2s')
            if fs.exists(p := self.get_install_path(pkg_id)):
                yield pkg_id, p, False
            else:
                yield pkg_id, self.install_one(pkg_id, filepath), True
    
    @staticmethod
    def linking(
        pkg_ids: t.Iterable[T.PackageId], dst_dir: T.Path, **_kwargs
    ) -> None:
        print(':d', f'linking required packages to "{dst_dir}"')
        print(':l', pkg_ids)
        link_venv(pkg_ids, dst_dir, **_kwargs)
        
    # -------------------------------------------------------------------------
    # general
    
    def exists(self, name_or_id: t.Union[T.PackageName, T.PackageId]) -> bool:
        return (name_or_id.rstrip('-')) in self.index
    
    def get_download_path(self, pkg_id: T.PackageId) -> T.Path:
        # FIXME: not a general way
        return self.index[pkg_id][0]
    
    def get_install_path(self, pkg_id: T.PackageId) -> T.Path:
        return '{}/{}/{}'.format(pypi_paths.installed, *self.split(pkg_id))
    
    @staticmethod
    def split(pkg_id: T.PackageId) -> t.Tuple[T.PackageName, T.ExactVersion]:
        return pkg_id.split('-', 1)  # noqa
    
    # def _find_dependencies(self, pkg_id: str) -> t.Iterator[T.PackageId]:
    #     from .insight import analyze_metadata
    #     dir0 = self.index[pkg_id][1]
    #     for name in os.listdir(dir0):
    #         if name.endswith('.dist-info'):
    #             dir1 = f'{dir0}/{name}'
    #             if os.path.exists(x := f'{dir1}/METADATA'):
    #                 yield from analyze_metadata(x, self.name_2_versions)
    #             break
    #     else:
    #         raise Exception(f'cannot find dist-info for {pkg_id}')
    
    @staticmethod
    def _parse_pip_download_response(
        resp: str
    ) -> t.Iterator[t.Tuple[T.Path, bool]]:
        """
        how do we extract the downloaded file path from the raw response?
            the raw response from `pip download` command. something like:
                1.
                    Collecting lk-utils==2.6.0b9
                      Downloading <some_url> (16 kB)
                    Saved <some_relpath_or_abspath_dir>/lk_utils-2.6.0b9-py3 \
                    -none-any.whl
                    Successfully downloaded lk-utils
                2.
                    Collecting lk-utils==2.6.0b9
                      File was already downloaded <abspath>/lk_utils-2.6.0-py3 \
                      -none-any.whl
                    Successfully downloaded lk-utils
                3.
                    Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                    Collecting argsense
                      Using cached https://pypi.tuna.tsinghua.edu.cn/packages \
                      /5f/e4/e6eb339f09106a3fd0947cec58275bd5b00c78367db6acf39 \
                      b49a7393fa0/argsense-0.5.2-py3-none-any.whl (26 kB)
                    Saved <some_relpath_or_abspath_dir>/argsense-0.5.2-py3 \
                    -none-any.whl
                    Successfully downloaded argsense
                    [notice] A new release of pip is available: 23.2 -> 23.2.1
                    [notice] To update, run: pip install --upgrade pip
            we can use regex to parse the line which starts with 'Saved ...' \
            or 'File was already downloaded ...'.
        
        note:
            the yielt path's letter case may be un-uniform in windows.
        """
        # for pattern in (
        #     re.compile(r'File was already downloaded (.+)'),
        #     re.compile(r'Saved (.+)')
        # ):
        #     yield from map(fs.abspath, pattern.findall(resp))
        for p in re.compile(r'File was already downloaded (.+)').findall(resp):
            yield fs.abspath(p), False
        for p in re.compile(r'Saved (.+)').findall(resp):
            yield fs.abspath(p), True


pypi = LocalPyPI()
