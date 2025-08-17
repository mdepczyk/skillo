from unittest.mock import Mock, patch

import pytest

from skillo.application.dto import DocumentDto
from skillo.domain.enums import DocumentType


@pytest.fixture
def mock_openai():
    with patch("openai.OpenAI") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            '{"overall_score": 0.85, "recommendation": "RECOMMENDED"}'
        )

        mock_instance.chat.completions.create.return_value = mock_response
        yield mock_instance


@pytest.fixture
def sample_cv():
    return DocumentDto(
        id="test-cv-1",
        document_type=DocumentType.CV,
        content="Senior Python Developer with 5 years experience. Expert in Django, FastAPI, PostgreSQL.",
        metadata={
            "filename": "cv_python_senior.pdf",
            "upload_date": "2024-01-01",
        },
    )


@pytest.fixture
def sample_job():
    return DocumentDto(
        id="test-job-1",
        document_type=DocumentType.JOB,
        content="Looking for Python Developer. Requirements: Django, FastAPI, 3+ years experience.",
        metadata={
            "filename": "job_python_dev.pdf",
            "upload_date": "2024-01-01",
        },
    )


@pytest.fixture
def test_config():
    return {
        "OPENAI_API_KEY": "test-key-123",
        "CHROMA_DB_PATH": "./test_chroma_db",
        "COLLECTION_NAME": "test_documents",
        "EMBEDDING_MODEL": "text-embedding-3-small",
        "MIN_MATCH_SCORE": 0.7,
        "TOP_CANDIDATES_COUNT": 5,
        "AGENT_WEIGHTS": {
            "location": 0.15,
            "skills": 0.30,
            "experience": 0.25,
            "preferences": 0.10,
            "education": 0.20,
        },
    }


@pytest.fixture
def mock_chroma_db():
    with patch("chromadb.Client") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance

        mock_collection = Mock()
        mock_instance.get_or_create_collection.return_value = mock_collection

        mock_collection.add.return_value = None
        mock_collection.get.return_value = {
            "ids": ["test-doc-1"],
            "documents": ["Sample document content"],
            "metadatas": [
                {
                    "document_id": "test-doc-1",
                    "document_type": "cv",
                    "filename": "test.pdf",
                }
            ],
        }
        mock_collection.query.return_value = {
            "ids": [["test-doc-1"]],
            "distances": [[0.3]],
            "documents": [["Sample document content"]],
            "metadatas": [
                [
                    {
                        "document_id": "test-job-1",
                        "document_type": "job",
                        "filename": "test.pdf",
                    }
                ]
            ],
        }

        yield mock_instance
