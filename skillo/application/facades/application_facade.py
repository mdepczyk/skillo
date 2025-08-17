from skillo.application.protocols import (
    ApplicationFacadeProtocol,
    ConfigProtocol,
    DocumentProtocol,
    MatchingProtocol,
)


class ApplicationFacade(ApplicationFacadeProtocol):
    """Main facade aggregating document, matching and config operations."""

    def __init__(
        self,
        documents: DocumentProtocol,
        matching: MatchingProtocol,
        config: ConfigProtocol,
    ):
        """Initialize with facade dependencies."""
        self._documents = documents
        self._matching = matching
        self._config = config

    @property
    def documents(self) -> DocumentProtocol:
        """Document operations."""
        return self._documents

    @property
    def matching(self) -> MatchingProtocol:
        """Matching operations."""
        return self._matching

    @property
    def config(self) -> ConfigProtocol:
        """Configuration operations."""
        return self._config
