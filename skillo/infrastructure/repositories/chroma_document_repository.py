import os
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document as LangChainDocument
from langchain_openai import OpenAIEmbeddings

from skillo.domain.entities import Document
from skillo.domain.enums import DocumentType
from skillo.domain.exceptions import SkilloRepositoryError
from skillo.domain.repositories import DocumentRepository
from skillo.infrastructure.config.settings import Config


class QueryConstants:
    """Document repository query constants."""

    DEFAULT_SIMILARITY_LIMIT = 10


class ChromaDocumentRepository(DocumentRepository):
    """Chroma document repository implementation."""

    def __init__(self, config: Config) -> None:
        """Initialize with config."""
        self.config = config
        self.embeddings = OpenAIEmbeddings(
            api_key=self.config.OPENAI_API_KEY,  # type: ignore
            model=self.config.EMBEDDING_MODEL,
        )
        self._initialize_vectorstore()

    def _initialize_vectorstore(self) -> None:
        """Initialize Chroma vectorstore."""
        try:
            os.makedirs(self.config.CHROMA_DB_PATH, exist_ok=True)

            self.vectorstore = Chroma(
                collection_name=self.config.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=self.config.CHROMA_DB_PATH,
            )

        except Exception as e:
            path = self.config.CHROMA_DB_PATH
            error_msg = f"Failed to init vector store at '{path}': {str(e)}"
            raise SkilloRepositoryError(error_msg)

    def add_document(self, document: Document) -> bool:
        """Add document to vector store."""
        try:
            langchain_doc = LangChainDocument(
                page_content=document.content,
                metadata={
                    "document_id": document.id,
                    "document_type": document.document_type.value,
                    **document.metadata,
                },
            )

            self.vectorstore.add_documents([langchain_doc])
            return True

        except Exception as e:
            raise SkilloRepositoryError(
                f"Failed to add document {document.id}: {str(e)}"
            )

    def get_documents_by_type(self, doc_type: DocumentType) -> List[Document]:
        """Get documents by type."""
        try:
            results = self.vectorstore.get(
                where={"document_type": doc_type.value}
            )

            documents = []
            for i, document_content in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                doc = Document(
                    id=metadata["document_id"],
                    document_type=DocumentType(metadata["document_type"]),
                    content=document_content,
                    metadata={
                        k: v
                        for k, v in metadata.items()
                        if k not in ["document_id", "document_type"]
                    },
                )
                documents.append(doc)

            return documents

        except Exception as e:
            raise SkilloRepositoryError(
                f"Failed to get documents by type {doc_type}: {str(e)}"
            )

    def find_similar_documents(
        self,
        query: str,
        doc_type: DocumentType,
        limit: int = QueryConstants.DEFAULT_SIMILARITY_LIMIT,
    ) -> List[Document]:
        """Find documents similar to the query text."""
        try:
            results = self.vectorstore.similarity_search(
                query=query, k=limit, filter={"document_type": doc_type.value}
            )

            documents = []
            for result in results:
                doc = Document(
                    id=result.metadata["document_id"],
                    document_type=DocumentType(
                        result.metadata["document_type"]
                    ),
                    content=result.page_content,
                    metadata={
                        k: v
                        for k, v in result.metadata.items()
                        if k not in ["document_id", "document_type"]
                    },
                )
                documents.append(doc)

            return documents

        except Exception as e:
            raise SkilloRepositoryError(
                f"Failed to find similar documents: {str(e)}"
            )
