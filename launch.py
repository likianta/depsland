from depsland import create_venv

create_venv(
    *input('packages (separated with comma): ').split(','),
    target_name=input('target dirname: '),
)
