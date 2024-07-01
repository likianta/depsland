from lk_utils import fs

for d in fs.find_dirs(fs.xpath('../../temp')):
    if not d.name.startswith('.'):
        print(d.name, ':i')
        fs.remove_tree(d.path)

# pox sidework/doctor/clean_temp_folder.py
