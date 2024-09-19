import os

from lk_utils import run_cmd_args


class PoetryExecutable:
    def __init__(self) -> None:
        if 'VIRTUAL_ENV' in os.environ:
            print('pop current venv', os.environ['VIRTUAL_ENV'])
            del os.environ['VIRTUAL_ENV']
    
    @staticmethod
    def run(*args, cwd: str, **kwargs) -> None:
        assert 'VIRTUAL_ENV' not in os.environ  # TEST
        run_cmd_args(
            'poetry', 'run', *args,
            cwd=cwd,
            verbose=True,
            force_term_color=True,
            ignore_return=True,
            **kwargs
        )


poetry = PoetryExecutable()
