from ..normalization import normalize_name, normalize_version


class Requirement:
    
    def __init__(self, raw_name: str):
        self.raw_name = raw_name
        self.name = normalize_name(raw_name)
        self.version = normalize_version(raw_name)
        
    @property
    def name_id(self):
        return self.name, self.version
