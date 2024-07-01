from lk_utils import fs

from depsland import paths

print(paths.pypi.snapdep)
for f in fs.find_files(paths.pypi.snapdep):
    if f.name != '.gitkeep':
        print(f.name, ':i')
        fs.remove_file(f.path)

# pox sidework/doctor/clean_snapdep_files.py
