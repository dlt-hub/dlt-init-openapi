from dataclasses import dataclass, field
from typing import List


@dataclass
class SecurityScheme:

    type: str
    scheme: str
    name: str
    location: str

    detected_secret_names: List[str] = field(default_factory=list)
    detected_auth_vars: str = ""

    @property
    def supported(self) -> bool:
        if self.type == "apiKey":
            return True
        elif self.type == "http" and self.scheme == "basic":
            return True
        elif self.type == "http" and self.scheme == "bearer":
            return True
        return False
