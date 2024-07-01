from lk_utils import fs

from depsland import paths

print(paths.pypi.snapdep)
if input('^ are you sure to clean up this folder? ') == 'y':
    fs.remove_tree(paths.pypi.snapdep)
    fs.copy_tree(fs.xpath('_empty_folder_template'), paths.pypi.snapdep)

# pox sidework/doctor/clean_snapdep_files.py
