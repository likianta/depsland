from dataclasses import dataclass  # noqa


@dataclass
class Requester:
    name: str
    version: str = ''
