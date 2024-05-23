class DltOpenAPIException(Exception):
    pass


class DltOpenAPITerminalException(DltOpenAPIException):
    pass


class DltOpenAPINot30Exception(DltOpenAPITerminalException):
    def __init__(self, swagger_detected: bool = False) -> None:

        swagger_helper = "If this is a Swagger/OpenAPI 2.0 or earlier spec, "
        if swagger_detected:
            swagger_helper = "It looks like this is a Swagger/OpenAPI 2.0 spec, "

        convert_helper = (
            "you can convert it to an openapi 3.0 spec by going to https://editor.swagger.io/, "
            + "pasting your spec and selecting 'Edit' -> 'Convert to OpenAPI 3.0' from the Menu "
            + "and then retry with the converted file."
        )

        super().__init__(
            "The spec you selected does not appear to be an OpenAPI 3.0 spec. " + swagger_helper + convert_helper
        )


class DltInvalidSpecException(DltOpenAPITerminalException):
    def __init__(self) -> None:

        super().__init__(
            "Could not validate selected spec, please provide a valid YAML or JSON OpenAPI 3.0 or higher spec."
        )


class DltUnparseableSpecException(DltOpenAPITerminalException):
    def __init__(self) -> None:

        super().__init__("Could not parse selected spec, please provide a valid YAML or JSON document.")
