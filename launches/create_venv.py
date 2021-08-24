from dataclasses import dataclass  # noqa


def main(requester: 'Requester', venv_options: 'VenvOptions'):
    pass


@dataclass
class Requester:
    name: str
    version: str
    

@dataclass
class VenvOptions:
    venv_id: str
    platform: str
    pyversion: str
    name: str
    support_versions: str
