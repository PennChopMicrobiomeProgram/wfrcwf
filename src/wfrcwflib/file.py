from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

class Filetype:
    pass

@dataclass
class SuffixedFiletype(Filetype):
    name: str
    suffix: str
    alt_suffixes: list[str] = field(default_factory=list)

    def gather(self, dir: Path) -> dict[str, Path]:
        fps = list(dir.iterdir())
        fs = {}
        for fp in fps:
            if any([str(fp).endswith(suffix) for suffix in [self.suffix, *self.alt_suffixes]]):
                fs[self.stem(fp)] = fp
        
        return fs

    def stem(self, fp: Path) -> str:
        stem = str(fp.name)
        for suffix in [self.suffix, *self.alt_suffixes]:
            if stem.endswith(suffix):
                return stem[:-len(suffix)]
                

@dataclass
class SuffixedFiletypeBundle(Filetype):
    name: str
    components: tuple[SuffixedFiletype, ...]

    def gather(self, dir: Path) -> dict[SuffixedFiletype, list[Path]]:
        bundles: dict[str, list[Optional[Path]]] = {}
        for i, component in enumerate(self.components):
            for name, fp in component.gather(dir).items():
                old_bundle = bundles.get(name, [None for _ in range(len(self.components))])
                old_bundle[i] = fp
                bundles[name] = old_bundle

        return {k: v for k, v in bundles.items() if all(v)}
    
class FiletypeRegistry(dict[str, Filetype]):
    def register(self, t: Filetype):
        self[t.name] = t

@dataclass
class FileSource:
    dir: Path
    filetype: Filetype

    def gather(self) -> list[Path]:
        return list(self.dir.iterdir())
