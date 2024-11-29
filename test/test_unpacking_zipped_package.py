import os
import sys

from lk_utils import p, fs

from depsland.utils import init_target_tree
from depsland.utils import make_temp_dir
from depsland.utils import ziptool
from depsland.venv.target_venv.indexer import analyze_records


def confirm(prompt: str) -> None:
    if input(prompt + ' ') == 'x':
        sys.exit()


p0 = p('qmlease-3.0.5a6.zip')
p1 = make_temp_dir()
ziptool.extract_file(p0, '{}/{}'.format(p1, 'qmlease'))
p2 = '{}/{}/3.0.5a6'.format(p1, 'qmlease')
p3 = '{}/{}/RECORD'.format(p2, 'qmlease-3.0.5a6.dist-info')

relfiles = tuple(analyze_records(p3))
print(relfiles, ':l')

reldirs = set()
for p in relfiles:
    if p.startswith('../'):
        reldirs.add('bin')
    else:
        if '/' in p:
            reldirs.add(p.rsplit('/', 1)[0])
print(sorted(reldirs), ':l')
# confirm('continue?')
p4 = '{}/new_root'.format(p1)
init_target_tree(p4, reldirs)
print(
    'created target tree',
    [fs.relpath(x, p4) for x in fs.findall_dir_paths(p4)],
    ':l'
)
confirm('continue?')

for p in relfiles:
    if p.startswith('../'):
        print(p)
        continue
        # file_i = '{}/{}'.format(p2, p)
        # file_o = '{}/bin/{}'.format(p4, fs.basename(p))
    else:
        file_i = '{}/{}'.format(p2, p)
        file_o = '{}/{}'.format(p4, p)
    # note that `file_i` is from record file, which may not exist, we
    # should check its validity.
    if os.path.isfile(file_i):
        print(':v2i', 'copy', p)
        fs.copy_file(file_i, file_o)
    else:
        print(':v3i', 'skip', p)

confirm('finish?')

# pox unittests/test_unpacking_zipped_package.py
