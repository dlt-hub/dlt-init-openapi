from dataclasses import dataclass
from typing import Optional

from openapi_python_client.parser.context import OpenapiContext, SecurityScheme


@dataclass
class CredentialsProperty:
    scheme: SecurityScheme

    @property
    def supported(self) -> bool:
        if self.scheme.type == "apiKey":
            return True
        elif self.scheme.type == "http" and self.scheme.scheme == "basic":
            return True
        elif self.scheme.type == "http" and self.scheme.scheme == "bearer":
            return True
        return False

    @property
    def credentials_string(self) -> str:
        key = "password"
        """We assume one scheme for now"""
        if self.scheme.type == "apiKey":
            key = "api_key"
        elif self.scheme.type == "http" and self.scheme.scheme == "basic":
            key = "password"
        elif self.scheme.type == "http" and self.scheme.scheme == "bearer":
            key = "token"
        if key:
            return f"{key}: str = dlt.secrets.value"
        return ""

    @property
    def auth_statement(self) -> str:
        if self.scheme.type == "apiKey":
            result = f"""
        {{
            "type": "apiKey",
            "api_key": api_key,
            "name": "{self.scheme.name}",
            "location": "header"
        }}"""
            return result
        elif self.scheme.type == "http" and self.scheme.scheme == "basic":
            return """
        {
            "type": "http",
            "scheme": "basic",
            "username": "",
            "password": password,
        }"""
        elif self.scheme.type == "http" and self.scheme.scheme == "bearer":
            return """
        {
            "type": "http",
            "scheme": "bearer",
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
        instance = cls(scheme)  # type: ignore
        if not instance.supported:
            return None
        return instance
