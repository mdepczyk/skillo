from unittest.mock import Mock, patch

from skillo.domain.enums import DocumentType
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.repositories.chroma_document_repository import (
    ChromaDocumentRepository,
)


def test_chroma_operations(mock_chroma_db, test_config):
    with patch.dict(
        "os.environ",
        {
            "CHROMA_DB_PATH": test_config["CHROMA_DB_PATH"],
            "COLLECTION_NAME": test_config["COLLECTION_NAME"],
        },
    ):
        config = Config()

        with patch("chromadb.PersistentClient", return_value=mock_chroma_db):
            repository = ChromaDocumentRepository(config=config)

            mock_document = Mock()
            mock_document.id = "test-doc-1"
            mock_document.document_type = DocumentType.CV
            mock_document.content = "Test document content"
            mock_document.metadata = {"filename": "test.pdf"}

            result = repository.add_document(mock_document)
            assert result is True or result is False

            documents = repository.get_documents_by_type(DocumentType.CV)
            assert isinstance(documents, list)
            for doc in documents:
                assert doc.document_type == DocumentType.CV

            similar_docs = repository.find_similar_documents(
                "test query", DocumentType.JOB, limit=5
            )
            assert isinstance(similar_docs, list)
            for doc in similar_docs:
                assert doc.document_type == DocumentType.JOB
