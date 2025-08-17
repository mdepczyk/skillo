"""Vector store related exceptions."""


class VectorStoreInitializationError(Exception):
    """Failed to initialize ChromaDB vector store."""

    def __init__(self, db_path: str = "", original_error: str = ""):
        message = (
            f"Cannot initialize ChromaDB at path '{db_path}': {original_error}"
        )
        super().__init__(message)


class DocumentStorageError(Exception):
    """Failed to store document in vector database."""

    def __init__(
        self,
        document_id: str = "",
        collection_name: str = "",
        original_error: str = "",
    ):
        message = f"Cannot store document '{document_id}' in collection '{collection_name}': {original_error}"
        super().__init__(message)


class DocumentRetrievalError(Exception):
    """Failed to retrieve documents from vector database."""

    def __init__(
        self,
        query_type: str = "",
        collection_name: str = "",
        original_error: str = "",
    ):
        message = f"Cannot retrieve {query_type} documents from collection '{collection_name}': {original_error}"
        super().__init__(message)


class EmbeddingGenerationError(Exception):
    """Failed to generate embeddings for document content."""

    def __init__(self, content_length: int = 0, original_error: str = ""):
        message = f"Cannot generate embeddings for content ({content_length} chars): {original_error}"
        super().__init__(message)


class CollectionNotFoundError(Exception):
    """ChromaDB collection does not exist."""

    def __init__(self, collection_name: str = ""):
        message = f"Collection '{collection_name}' not found in ChromaDB"
        super().__init__(message)


class SimilarityCalculationError(Exception):
    """Failed to calculate semantic similarity between texts."""

    def __init__(self, original_error: str = ""):
        message = f"Cannot calculate semantic similarity: {original_error}"
        super().__init__(message)
