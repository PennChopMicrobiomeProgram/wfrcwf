from dataclasses import dataclass, field
from pathlib import Path

class Filetype:
    pass

@dataclass
class SuffixedFiletype(Filetype):
    name: str
    suffix: str
    alt_suffixes: list[str] = field(default_factory=list)

    def gather(self, dir: Path):
        fps = list(dir.iterdir())
        for fp in fps:
            if fp.endswith(self.suffix):
                

@dataclass
class SuffixedFiletypeBundle(Filetype):
    name: str
    components: tuple[SuffixedFiletype, ...]
    
class FiletypeRegistry(dict):
    def register(self, t):
        self[t.name] = t

@dataclass
class FileSource:
    dir: Path
    filetype: Filetype

    def gather(self):
        filepaths = list(self.dir.iterdir())
