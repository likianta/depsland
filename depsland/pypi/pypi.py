import re
import typing as t

from lk_utils import fs

from .index import Index
from .index import T as T0
from .pip import Pip
from .pip import pip as _default_pip
from .. import normalization as norm
from ..paths import pypi as pypi_paths
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
    
    def __contains__(self, pkg_id: str) -> bool:
        return self.index.has_id(pkg_id)
    
    # -------------------------------------------------------------------------
    # main methods
    
    def download_one(
        self,
        pkg_id: T.PackageId,
        custom_url: str = None,
        _auto_save_index: bool = True
    ) -> T.Path:
        if custom_url:
            assert pkg_id in custom_url, (pkg_id, custom_url)
            resp = self.pip.download(
                custom_url, pypi_paths.downloads,
                no_dependency=True, no_index=True
            )
        else:
            name, ver = self.split(pkg_id)
            resp = self.pip.download(
                f'{name}=={ver}', pypi_paths.downloads, no_dependency=True
            )
        for path, _ in self._parse_pip_download_response(resp):
            # fix path if it's a symlink
            path = '{}/{}'.format(
                pypi_paths.downloads, fs.basename(path).lower()
            )
            assert fs.exists(path), path
            if _auto_save_index:
                self.index.add_to_index(path, 0)
            return path
    
    def install_one(
        self,
        pkg_id: T.PackageId,
        path: T.Path,
        _auto_save_index: bool = True
    ) -> T.Path:
        assert path.endswith(('.tar.gz', '.whl', '.zip')), path
        src_path = path
        dst_path = self.get_install_path(pkg_id)
        if not fs.exists(dst_path):
            fs.make_dirs(dst_path)
        try:
            self.pip.install(src_path, dst_path, no_dependency=True)
        except Exception as e:
            fs.remove_tree(dst_path)
            raise e
        if _auto_save_index:
            self.index.add_to_index(dst_path, 1)
        return dst_path
    
    def download_all(
        self, requirements_file: str, _auto_save_index: bool = True
    ) -> t.Iterator[t.Tuple[T.Path, T.IsNew]]:
        resp = self.pip.download_r(requirements_file)
        for path, isnew in self._parse_pip_download_response(resp):
            if _auto_save_index:
                self.index.add_to_index(path, 0)
                yield path, isnew
    
    def install_all(
        self,
        downloaded_files: t.Iterable[T.Path],
        _auto_save_index: bool = True,
        # _skip_existed: bool = True
    ) -> t.Iterator[t.Tuple[T.PackageId, T.Path, T.IsNew]]:
        for src_path in downloaded_files:
            src_name = fs.basename(src_path)
            name, version = norm.split_filename_of_package(src_name)
            pkg_id = f'{name}-{version}'
            print(pkg_id, ':i2v2s')
            dst_path = self.get_install_path(pkg_id)
            if fs.exists(dst_path):
                yield pkg_id, dst_path, False
            else:
                yield pkg_id, self.install_one(pkg_id, src_path, False), True
            if _auto_save_index:
                self.index.add_to_index(dst_path, 1)
    
    @staticmethod
    def linking(
        pkg_ids: t.Iterable[T.PackageId], dst_dir: T.Path, **_kwargs
    ) -> None:
        print(':d', f'linking required packages to "{dst_dir}"')
        # print(':l', pkg_ids)
        link_venv(pkg_ids, dst_dir, **_kwargs)
        
    # -------------------------------------------------------------------------
    # general
    
    # def exists(self, name_or_id: t.Union[T.PackageName, T.PackageId]) -> bool:
    #     return (name_or_id.rstrip('-')) in self.index
    
    def exists(self, package_id: T.PackageId) -> bool:
        return package_id in self.index
    
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
        yields: ((abspath, is_newly_downloaded), ...)
            abspath: normalized with regular slashes ('/').
                warning:
                    the letter case maybe varied in windows.
                    if target directory is symlinked, the response will be -
                    redirected to real source.
            is_newly_downloaded: false means got from cache which is alraedy -
            downloaded.
        
        how do we extract the downloaded file path from the raw response?
            the raw response from `pip download` command. something like:
                1.
                    Collecting lk-utils==2.6.0b9
                      Downloading <some_url> (16 kB)
                    Saved <some_relpath_or_abspath_dir>/lk_utils-2.6.0b9-py3-
                    none-any.whl
                    Successfully downloaded lk-utils
                2.
                    Collecting lk-utils==2.6.0b9
                      File was already downloaded <abspath>/lk_utils-2.6.0-py3-
                      none-any.whl
                    Successfully downloaded lk-utils
                3.
                    Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                    Collecting argsense
                      Using cached https://pypi.tuna.tsinghua.edu.cn/packages -
                      /5f/e4/e6eb339f09106a3fd0947cec58275bd5b00c78367db6acf39 -
                      b49a7393fa0/argsense-0.5.2-py3-none-any.whl (26 kB)
                    Saved <some_relpath_or_abspath_dir>/argsense-0.5.2-py3 -
                    -none-any.whl
                    Successfully downloaded argsense
                    [notice] A new release of pip is available: 23.2 -> 23.2.1
                    [notice] To update, run: pip install --upgrade pip
            we can use regex to parse the line which starts with 'Saved ...' -
            or 'File was already downloaded ...'.
        """
        for p in re.compile(r'File was already downloaded (.+)').findall(resp):
            yield fs.abspath(p), False
        for p in re.compile(r'Saved (.+)').findall(resp):
            yield fs.abspath(p), True


pypi = LocalPyPI()
