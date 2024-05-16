from dataclasses import dataclass
from typing import Optional

from dlt_openapi.parser.context import OpenapiContext


@dataclass
class CredentialsProperty:

    type: str
    scheme: str
    name: str
    location: str

    @property
    def supported(self) -> bool:
        if self.type == "apiKey":
            return True
        elif self.type == "http" and self.scheme == "basic":
            return True
        elif self.type == "http" and self.scheme == "bearer":
            return True
        return False

    @property
    def credentials_string(self) -> str:
        key = "password"
        """We assume one scheme for now"""
        if self.type == "apiKey":
            key = "api_key"
        elif self.type == "http" and self.scheme == "basic":
            key = "password"
        elif self.type == "http" and self.scheme == "bearer":
            key = "token"
        if key:
            return f"{key}: str = dlt.secrets.value"
        return ""

    @property
    def auth_statement(self) -> str:
        if self.type == "apiKey":
            result = f"""
        {{
            "type": "api_key",
            "api_key": api_key,
            "name": "{self.name}",
            "location": "{self.location}"
        }}"""
            return result
        elif self.type == "http" and self.scheme == "basic":
            return """
        {
            "type": "http_basic",
            "username": "username",
            "password": password,
        }"""
        elif self.type == "http" and self.scheme == "bearer":
            return """
        {
            "type": "bearer",
            "token": token,
        }"""
        return ""

    @classmethod
    def from_context(cls, context: OpenapiContext) -> Optional["CredentialsProperty"]:
        """Create property from global definition"""
        """TODO: make nested defs work"""

        if not context.spec.components or not context.spec.components.securitySchemes:
            return None
        scheme = list(context.spec.components.securitySchemes.values())[0]
        instance = cls(name=scheme.name, type=scheme.type, scheme=scheme.scheme, location=scheme.security_scheme_in)
        if not instance.supported:
            return None
        return instance
