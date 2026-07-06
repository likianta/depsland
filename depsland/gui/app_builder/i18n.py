"""
TODO: we may use `gettext` in the future.
"""

import typing as tp

from lk_utils import fs


def self_check():
    ch = fs.load(fs.here('languages/chinese.yaml'))
    en = fs.load(fs.here('languages/english.yaml'))
    for key in ch:
        if key not in en:
            print('missing key in english.yaml', key, ':v6')
    for key in en:
        if key not in ch:
            print('missing key in chinese.yaml', key, ':v6')


class English:
    def __init__(self, file: str = fs.here('languages/english.yaml')) -> None:
        self.__dict__.update(self._load(file))

    def _load(self, file: str) -> tp.Iterator[tp.Tuple[str, str]]:
        for k, v in fs.load(file).items():
            if '\n' in v:
                yield (
                    k,
                    v.replace('\n\n', '<temp_masked>')
                    .replace('\n', '  \n')
                    .replace('<temp_masked>', '\n\n'),
                )
            else:
                yield k, v


class Chinese(English):
    def __init__(self, file: str = fs.here('languages/chinese.yaml')) -> None:
        super().__init__(file)


# note: currently chinese is in active development.
i18n = Chinese()
