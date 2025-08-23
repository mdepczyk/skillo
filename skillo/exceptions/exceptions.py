class SkilloError(Exception):
    """Base exception for all Skillo-specific errors."""
    
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)


class SkilloConfigurationError(SkilloError):
    """Configuration and environment setup errors."""
    pass


class SkilloProcessingError(SkilloError):
    """Document processing errors (PDF extraction, file handling)."""
    
    def __init__(self, details: str):
        message = f"Document processing failed: {details}"
        super().__init__(message)


class SkilloStorageError(SkilloError):
    """Vector store and database errors."""
    
    def __init__(self, details: str):
        message = f"Storage operation failed: {details}"
        super().__init__(message)


class SkilloAgentError(SkilloError):
    """AI agent and LLM coordination errors."""
    
    def __init__(self, details: str):
        message = f"Agent error: {details}"
        super().__init__(message)


class SkilloMatchingError(SkilloError):
    """CV-Job matching process errors."""
    
    def __init__(self, details: str):
        message = f"Matching failed: {details}"
        super().__init__(message)


class SkilloValidationError(SkilloError):
    """Data validation and schema errors."""
    
    def __init__(self, details: str):
        message = f"Validation failed: {details}"
        super().__init__(message)