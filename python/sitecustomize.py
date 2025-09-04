# https://github.com/python/cpython/issues/93875#issuecomment-2487890248
# print('setting up customized site')
import os
import sys
sys.path[0:0] = ['.', 'lib', 'src', '.venv']
if p := os.environ.get('DEPSLAND_SEARCH_PATHS'):
    sys.path.extend(p.split(os.pathsep))
