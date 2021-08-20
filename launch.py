from depsland import create_venv

create_venv(
    *input('packages (separated with comma): ').split(','),
    venv_name=input('target dirname: '),
)
