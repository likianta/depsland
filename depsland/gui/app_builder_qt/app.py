# if __name__ == '__main__':
#     __package__ = 'depsland.gui.app_builder_qt'

import depsland
import qmlease as q
import re
import typing as t
from lk_utils import fs
from random import randint

state = {
    'appinfo': {}
}

class Main(q.QObject):
    @q.Slot(object)
    def init_ui(self, root):
        _prj_dir = ''
        _prj_info: dict = {}
        
        @q.bind_signal(root.projectPathSubmit)
        def _load_project(path):
            if not path: return
            assert fs.isdir(path)
            assert fs.exist('{}/pyproject.toml'.format(path))
            
            nonlocal _prj_info, _prj_dir
            _prj_dir = fs.normpath(path)
            if _prj_dir not in state['appinfo']:
                state['appinfo'][_prj_dir] = {
                    'appid': _generate_appid(
                        fs.basename(_prj_dir).lower().replace('-', '_')
                    ),
                    'version': Version((0, 1, 0)),
                }
            _prj_info = state['appinfo'][_prj_dir]
            
            root['appId'] = _prj_info['appid']
            root['appName'] = fs.basename(path)
            root['appVersion'] = str(_prj_info['version'])
            root['assetsModel'] = self._scan_project_structure(_prj_dir)
            root['venvPath'] = depsland.venv.get_venv_root(_prj_dir)
        
        @q.bind_signal(root.onRegenerateId)
        def _():
            assert _prj_dir
            root['appId'] = _prj_info['appid'] = _generate_appid(
                fs.basename(_prj_dir).lower().replace('-', '_')
            )
            print('regenerated id', _prj_info['appid'])
        
        @q.bind_signal(root.onBumpVersion)
        def _():
            root['appVersion'] = _prj_info['version'].bump()
            print('new version', _prj_info['version'])
    
    @staticmethod
    def _scan_project_structure(project_root):
        def recurse(folder):
            children = []
            for d in fs.find_dirs(folder):
                children.append({
                    'type'    : 'folder',
                    'name'    : d.name,
                    'path'    : d.path,
                    'children': recurse(d.path),
                })
            for f in fs.find_files(folder):
                children.append({
                    'type'   : 'file',
                    'name'   : f.name,
                    'path'   : f.path,
                })
            return q.ListModel.from_list(
                children, ('type', 'name', 'path', 'children')
            )
        
        return q.ListModel.from_list(
            [
                {
                    'type'    : 'folder',
                    'name'    : fs.basename(project_root),
                    'path'    : project_root,
                    'children': recurse(project_root),
                }
            ]
        )

class Version:
    def __init__(
        self, base: t.Tuple[int, int, int], _alpha: int = 0, _beta: int = 0
    ) -> None:
        self._origin = (tuple(base), _alpha, _beta)
        self._base = list(base)
        self._alpha = _alpha
        self._beta = _beta
        self._current_state = ''
    
    def __str__(self) -> str:  # noqa
        match self._current_state:
            case '':
                return '{}.{}.{}'.format(*self._base)
            case 'a':
                return '{}.{}.{}a{}'.format(*self._base, self._alpha)
            case 'b':
                return '{}.{}.{}b{}'.format(*self._base, self._beta)
    
    def bump(self) -> str:
        match self._current_state:
            case '':
                self._base[2] += 1
                self._alpha = self._beta = 0
            case 'a':
                self._alpha += 1
            case 'b':
                self._beta += 1
        return str(self)
    
    def reset(self) -> str:
        self._base = list(self._origin[0])
        self._alpha, self._beta = self._origin[1:]
        return str(self)
    
    def to_alpha(self) -> str:
        self._current_state = 'a'
        return '{}.{}.{}a{}'.format(*self._base, self._alpha)
    
    def to_beta(self) -> str:
        self._current_state = 'b'
        return '{}.{}.{}b{}'.format(*self._base, self._beta)
    
    def to_formal(self) -> str:
        self._current_state = ''
        return '{}.{}.{}'.format(*self._base)

def _generate_appid(basename: str) -> str:
    assert re.fullmatch(r'[a-z]\w*[a-z]', basename), basename
    return '{}_0x{:04x}'.format(basename, randint(0, 0xFFFF))

if __name__ == '__main__':
    q.app.register(Main())
    q.app.run(fs.xpath('qml/Main.qml'))
