class SkilloError(Exception):
    """Base Skillo exception."""

    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)


class SkilloConfigurationError(SkilloError):
    """Configuration error."""

    pass


class SkilloProcessingError(SkilloError):
    """Document processing error."""

    def __init__(self, details: str):
        message = f"Document processing failed: {details}"
        super().__init__(message)


class SkilloStorageError(SkilloError):
    """Storage error."""

    def __init__(self, details: str):
        message = f"Storage operation failed: {details}"
        super().__init__(message)


class SkilloAgentError(SkilloError):
    """Agent error."""

    def __init__(self, details: str):
        message = f"Agent error: {details}"
        super().__init__(message)


class SkilloMatchingError(SkilloError):
    """Matching error."""

    def __init__(self, details: str):
        message = f"Matching failed: {details}"
        super().__init__(message)


class SkilloValidationError(SkilloError):
    """Validation error."""

    def __init__(self, details: str):
        message = f"Validation failed: {details}"
        super().__init__(message)
