from depsland.verspec import _minor_fix_version_form  # noqa

for raw in (
        '335',  # pywin32
        '1.7',  # crcmod
        '2.5.0b18',  # lk-utils
        '0.12.0.post2',  # hidapi
        '6.4.0.1',  # pyside6
        '21.7b0',  # <unknown>
):
    print(raw, _minor_fix_version_form(raw), ':s')
