from lk_utils import fs


def check_on_lk_utils() -> None:
    dir0 = 'chore/site_packages/lk_utils'
    files0 = []
    for f in fs.findall_files(dir0, filter=True):
        files0.append(f.relpath)
    
    files1 = []
    for k, v in fs.load(fs.xpath('./results/tree-shaking-test.yaml')).items():
        if k.startswith('lk_utils'):
            files1.append(v.split('/lk_utils/')[1])
    
    print(set(files0) - set(files1), ':l')
    #   if the difference is:
    #       {'__main__.py', 'subproc/multiprocess.py'}
    #   then it's OK
    
    if x := set(files1) - set(files0):  # this must be empty!
        print(x, ':lv4')


if __name__ == '__main__':
    # pox sidework/tree_shaking/check.py
    check_on_lk_utils()
