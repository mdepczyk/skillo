"""Configuration-related exceptions."""


class ConfigurationError(Exception):
    """Configuration file is missing or invalid."""

    def __init__(
        self, message: str = "Configuration file is missing or invalid"
    ):
        self.message = message
        super().__init__(self.message)


class MissingEnvironmentVariableError(Exception):
    """Required environment variable is not set."""

    def __init__(self, var_name: str = ""):
        if var_name:
            message = f"Required environment variable '{var_name}' is not set"
        else:
            message = "Required environment variable is not set"
        self.message = message
        super().__init__(self.message)
