"""Agent processing related exceptions."""


class LLMResponseError(Exception):
    """Language model failed to generate valid response."""

    def __init__(
        self,
        agent_name: str = "",
        prompt_length: int = 0,
        original_error: str = "",
    ):
        message = f"LLM failed to respond for {agent_name} agent (prompt: {prompt_length} chars): {original_error}"
        super().__init__(message)


class PromptLoadingError(Exception):
    """Failed to load agent prompt configuration from YAML."""

    def __init__(
        self,
        prompt_file: str = "",
        prompt_key: str = "",
        original_error: str = "",
    ):
        message = f"Cannot load prompt '{prompt_key}' from file '{prompt_file}.yaml': {original_error}"
        super().__init__(message)


class AgentProcessingError(Exception):
    """Agent failed to process input data into structured output."""

    def __init__(
        self,
        agent_name: str = "",
        input_type: str = "",
        original_error: str = "",
    ):
        message = f"{agent_name} agent failed to process {input_type} data: {original_error}"
        super().__init__(message)


class StructuredOutputError(Exception):
    """Agent returned invalid or incomplete structured output."""

    def __init__(
        self,
        agent_name: str = "",
        expected_fields: str = "",
        original_error: str = "",
    ):
        message = f"{agent_name} agent output missing required fields ({expected_fields}): {original_error}"
        super().__init__(message)


class AgentCoordinationError(Exception):
    """Supervisor agent failed to coordinate sub-agents."""

    def __init__(self, failed_agents: str = "", original_error: str = ""):
        message = f"Supervisor failed coordinating agents ({failed_agents}): {original_error}"
        super().__init__(message)
