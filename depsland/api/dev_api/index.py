def view_index(dir_i: str = None) -> None:
    from ...pypi.insight import overview
    overview(dir_i)
