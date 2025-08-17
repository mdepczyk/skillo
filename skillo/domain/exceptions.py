class SkilloError(Exception):
    """Base Skillo exception."""

    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)


class SkilloProcessingError(SkilloError):
    """Document processing error."""

    def __init__(self, details: str):
        message = f"Document processing failed: {details}"
        super().__init__(message)


class SkilloAgentError(SkilloError):
    """Agent error."""

    def __init__(self, details: str):
        message = f"Agent error: {details}"
        super().__init__(message)


class SkilloMatchingError(SkilloError):
    """Matching operation error."""

    def __init__(self, details: str):
        message = f"Matching operation failed: {details}"
        super().__init__(message)


class SkilloRepositoryError(SkilloError):
    """Repository operation error."""

    def __init__(self, details: str):
        message = f"Repository operation failed: {details}"
        super().__init__(message)


class SkilloAnalysisError(SkilloError):
    """Document analysis error."""

    def __init__(self, details: str):
        message = f"Document analysis failed: {details}"
        super().__init__(message)
