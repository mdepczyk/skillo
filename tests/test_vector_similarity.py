from unittest.mock import Mock, patch

import pytest

from skillo.domain.entities.document import Document
from skillo.domain.enums import DocumentType
from skillo.domain.exceptions import SkilloRepositoryError
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.repositories.chroma_document_repository import (
    ChromaDocumentRepository,
)


@pytest.fixture
def mock_config():
    """Create mock config for ChromaDB tests."""
    config = Mock(spec=Config)
    config.OPENAI_API_KEY = "test-key-123"
    config.EMBEDDING_MODEL = "text-embedding-3-small"
    config.CHROMA_DB_PATH = "./test_chroma_db"
    config.COLLECTION_NAME = "test_documents"
    return config


@pytest.fixture
def sample_cv_document():
    """Create sample CV document for testing."""
    return Document(
        id="test-cv-001",
        document_type=DocumentType.CV,
        content="Senior Python Developer with 5+ years experience in Django and FastAPI.",
        metadata={
            "filename": "senior_python_dev.pdf",
            "skills": ["Python", "Django", "FastAPI"],
            "name": "John Doe",
        },
    )


@pytest.fixture
def sample_job_document():
    """Create sample Job document for testing."""
    return Document(
        id="test-job-001",
        document_type=DocumentType.JOB,
        content="Looking for Python Developer with Django experience. Remote work available.",
        metadata={
            "filename": "python_job.pdf",
            "company": "TechCorp",
            "requirements": ["Python", "Django"],
        },
    )


def test_chroma_repository_initialization(mock_config):
    """Test ChromaDocumentRepository initializes correctly."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ) as mock_chroma,
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ) as mock_embeddings,
        patch("os.makedirs"),
    ):
        repo = ChromaDocumentRepository(mock_config)
        mock_embeddings.assert_called_once_with(
            api_key=mock_config.OPENAI_API_KEY,
            model=mock_config.EMBEDDING_MODEL,
        )
        mock_chroma.assert_called_once()
        assert repo.config == mock_config


def test_add_document_successfully(mock_config, sample_cv_document):
    """Test adding document to vector database successfully."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ) as mock_chroma,
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ),
        patch("os.makedirs"),
    ):
        mock_vectorstore = Mock()
        mock_chroma.return_value = mock_vectorstore
        repo = ChromaDocumentRepository(mock_config)
        result = repo.add_document(sample_cv_document)
        mock_vectorstore.add_documents.assert_called_once()
        call_args = mock_vectorstore.add_documents.call_args
        langchain_docs = call_args[0][0]
        assert len(langchain_docs) == 1
        langchain_doc = langchain_docs[0]
        assert langchain_doc.page_content == sample_cv_document.content
        assert langchain_doc.metadata["document_id"] == sample_cv_document.id
        assert (
            langchain_doc.metadata["document_type"]
            == sample_cv_document.document_type.value
        )
        assert result is True


def test_add_document_failure(mock_config, sample_cv_document):
    """Test handling of document add failure."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ) as mock_chroma,
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ),
        patch("os.makedirs"),
    ):
        mock_vectorstore = Mock()
        mock_vectorstore.add_documents.side_effect = Exception(
            "Database error"
        )
        mock_chroma.return_value = mock_vectorstore
        repo = ChromaDocumentRepository(mock_config)
        with pytest.raises(SkilloRepositoryError):
            repo.add_document(sample_cv_document)


def test_find_similar_documents_success(mock_config, sample_job_document):
    """Test finding similar documents successfully."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ) as mock_chroma,
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ),
        patch("os.makedirs"),
    ):
        mock_result1 = Mock()
        mock_result1.metadata = {
            "document_id": "cv-001",
            "document_type": "cv",
            "filename": "python_dev.pdf",
        }
        mock_result1.page_content = "Python Developer CV"
        mock_result2 = Mock()
        mock_result2.metadata = {
            "document_id": "cv-002",
            "document_type": "cv",
            "filename": "java_dev.pdf",
        }
        mock_result2.page_content = "Java Developer CV"
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [
            mock_result1,
            mock_result2,
        ]
        mock_chroma.return_value = mock_vectorstore
        repo = ChromaDocumentRepository(mock_config)
        results = repo.find_similar_documents(
            query="Looking for Python developer",
            doc_type=DocumentType.CV,
            limit=5,
        )
        mock_vectorstore.similarity_search.assert_called_once_with(
            query="Looking for Python developer",
            k=5,
            filter={"document_type": "cv"},
        )
        assert len(results) == 2
        assert all(isinstance(doc, Document) for doc in results)
        assert results[0].id == "cv-001"
        assert results[0].document_type == DocumentType.CV
        assert results[0].content == "Python Developer CV"


def test_find_similar_documents_empty_result(mock_config):
    """Test handling empty similarity search results."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ) as mock_chroma,
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ),
        patch("os.makedirs"),
    ):
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = []
        mock_chroma.return_value = mock_vectorstore
        repo = ChromaDocumentRepository(mock_config)
        results = repo.find_similar_documents(
            query="Nonexistent skill set", doc_type=DocumentType.JOB, limit=5
        )
        assert results == []


def test_find_similar_documents_query_failure(mock_config):
    """Test handling query failure."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ) as mock_chroma,
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ),
        patch("os.makedirs"),
    ):
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.side_effect = Exception(
            "Vector search failed"
        )
        mock_chroma.return_value = mock_vectorstore
        repo = ChromaDocumentRepository(mock_config)
        with pytest.raises(Exception):
            repo.find_similar_documents(
                query="test query", doc_type=DocumentType.CV, limit=5
            )


def test_get_documents_by_type_cv(mock_config):
    """Test getting documents by CV type."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ) as mock_chroma,
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ),
        patch("os.makedirs"),
    ):
        mock_vectorstore = Mock()
        mock_vectorstore.get.return_value = {
            "ids": ["cv-001", "cv-002"],
            "documents": ["Python Dev CV", "Data Scientist CV"],
            "metadatas": [
                {
                    "document_id": "cv-001",
                    "document_type": "cv",
                    "filename": "python_dev.pdf",
                },
                {
                    "document_id": "cv-002",
                    "document_type": "cv",
                    "filename": "data_scientist.pdf",
                },
            ],
        }
        mock_chroma.return_value = mock_vectorstore
        repo = ChromaDocumentRepository(mock_config)
        results = repo.get_documents_by_type(DocumentType.CV)
        mock_vectorstore.get.assert_called_once_with(
            where={"document_type": "cv"}
        )
        assert len(results) == 2
        assert all(isinstance(doc, Document) for doc in results)
        assert all(doc.document_type == DocumentType.CV for doc in results)


def test_get_documents_by_type_job(mock_config):
    """Test getting documents by Job type."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ) as mock_chroma,
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ),
        patch("os.makedirs"),
    ):
        mock_vectorstore = Mock()
        mock_vectorstore.get.return_value = {
            "ids": ["job-001"],
            "documents": ["Python Developer Job"],
            "metadatas": [
                {
                    "document_id": "job-001",
                    "document_type": "job",
                    "filename": "python_job.pdf",
                }
            ],
        }
        mock_chroma.return_value = mock_vectorstore
        repo = ChromaDocumentRepository(mock_config)
        results = repo.get_documents_by_type(DocumentType.JOB)
        mock_vectorstore.get.assert_called_once_with(
            where={"document_type": "job"}
        )
        assert len(results) == 1
        assert results[0].document_type == DocumentType.JOB
        assert results[0].id == "job-001"


def test_vectorstore_initialization_failure(mock_config):
    """Test handling vectorstore initialization failure."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ),
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ),
        patch("os.makedirs") as mock_makedirs,
    ):
        mock_makedirs.side_effect = OSError("Permission denied")
        with pytest.raises(Exception):
            ChromaDocumentRepository(mock_config)


def test_embedding_model_configuration(mock_config):
    """Test correct embedding model configuration."""
    with (
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.Chroma"
        ),
        patch(
            "skillo.infrastructure.repositories.chroma_document_repository.OpenAIEmbeddings"
        ) as mock_embeddings,
        patch("os.makedirs"),
    ):
        mock_config.EMBEDDING_MODEL = "text-embedding-ada-002"
        mock_config.OPENAI_API_KEY = "custom-api-key"
        ChromaDocumentRepository(mock_config)
        mock_embeddings.assert_called_once_with(
            api_key="custom-api-key", model="text-embedding-ada-002"
        )
