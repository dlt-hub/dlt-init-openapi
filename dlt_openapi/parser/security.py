from dataclasses import dataclass


@dataclass
class SecurityScheme:

    type: str
    scheme: str
    name: str
    location: str

    detected_secret_name: str = ""
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
