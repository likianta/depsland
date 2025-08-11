import streamlit as st
import streamlit_canary as sc
import typing as t
from lk_utils import fs
from streamlit_tree_select import tree_select as st_tree_select

_state = sc.session.get_state(15, default={})


def main(root: str):
    if root not in _state:
        _state[root] = Tree(root)
        _state[f'{root}:cache:checked'] = []
        _state[f'{root}:cache:expanded'] = []
    tree: Tree = _state[root]
    x = st_tree_select(
        tree.freeze(),
        check_model='leaf',
        no_cascade=False,
        checked=_state[f'{root}:cache:checked'],
        expanded=_state[f'{root}:cache:expanded'],
    )
    print(x, ':vl')
    if changes := tree.expand(x['expanded']):
        # expand checks
        temp = []
        for p in x['checked']:
            if p in changes:
                # temp.append(p)
                temp.extend('{}/{}'.format(p, n) for n in changes[p])
            else:
                temp.append(p)
        # print('{} -> {}'.format(len(x['checked']), len(temp)), temp, ':vl')
        _state[f'{root}:cache:checked'] = temp
        _state[f'{root}:cache:expanded'] = x['expanded']
        st.rerun()


class Tree:
    def __init__(self, root: str) -> None:
        self._parent_root = fs.parent(root)
        self._data = {
            fs.basename(root): {
                # TODO: replace this key with "abspath"?
                'parent': self._parent_root,
                'type': 1,
                'children': self.mount(root, recursive=1),
                'mounted': True
            }
        }
        self._frozen = None
        self._mounted_cache = set()
    
    def expand(self, paths: t.Iterable[str]) -> dict:
        new_mounted = {}
        for p in paths:
            if p not in self._mounted_cache:
                node = self._path_to_node(p)
                if not node['mounted']:
                    print('dynamic mounting', p)
                    node['children'] = self.mount(p)
                    node['mounted'] = True
                    new_mounted[p] = tuple(node['children'].keys())
                self._mounted_cache.add(p)
        if new_mounted:
            self._frozen = None
        return new_mounted
    
    def freeze(self) -> list:
        if self._frozen is None:
            def recursive_freeze(xdict: dict):
                out = []
                for k, v in xdict.items():
                    x = {
                        'label': k if v['mounted'] else k + ' (...)',
                        'value': v['parent'] + '/' + k,
                    }
                    if v['type'] == 1:
                        x['children'] = recursive_freeze(v['children'])
                    out.append(x)
                return out
            
            self._frozen = recursive_freeze(self._data)
            self._frozen[0]['label'] += ' (root)'
        return self._frozen
    
    def mount(self, folder: str, recursive: int = 0) -> dict:
        """
        params:
            recursive: the recursion depth.
        returns:
            {name, xdict, ...}
                xdict: {
                    'parent': str dirpath,
                    'type': 0 | 1,  # 0 for file, 1 for dir
                    'children': {name: xdict, ...},  # only dir has this key.
                    'mounted': bool,  # for file, this value is always True.
                }
        """
        out = {}
        for d in fs.find_dirs(folder):
            out[d.name] = {
                'parent': folder,
                'type': 1,
                'children':
                    dict(self.mount(d.path, recursive - 1))
                    if recursive else {},
                'mounted': bool(recursive),
            }
        for f in fs.find_files(folder):
            out[f.name] = {
                'parent': folder,
                'type': 0,
                'mounted': True,
            }
        return out
    
    def _path_to_node(self, path: str) -> dict:
        key_chain = path.removeprefix(self._parent_root + '/').split('/')
        nodes: t.Dict[str, dict] = self._data
        for k in key_chain[:-1]:
            nodes = nodes[k]['children']
        return nodes[key_chain[-1]]
