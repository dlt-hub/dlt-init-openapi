from dataclasses import dataclass


@dataclass
class SecurityScheme:

    type: str
    scheme: str
    name: str
    location: str

    detected_credentials_string: str = ""
    detected_auth_statement: str = ""

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
