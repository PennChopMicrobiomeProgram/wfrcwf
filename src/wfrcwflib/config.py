from dataclasses import dataclass, field

@dataclass
class Config:
    items: dict[str, str] = field(default_factory=dict)
    