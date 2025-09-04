import os
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from skillo.domain.entities import Document
from skillo.domain.enums import DocumentType
from skillo.domain.exceptions import SkilloProcessingError
from skillo.infrastructure.processing.base_processor import (
    BaseDocumentProcessor,
)
from skillo.infrastructure.processing.cv_processor import CVDocumentProcessor
from skillo.infrastructure.processing.document_processor import (
    DocumentProcessor,
)
from skillo.infrastructure.processing.job_processor import JobDocumentProcessor


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = Mock()
    config.CV_UPLOAD_DIR = "./uploads/cvs"
    config.JOB_UPLOAD_DIR = "./uploads/jobs"
    return config


@pytest.fixture
def mock_pdf_file():
    """Create mock PDF file."""
    pdf_file = Mock()
    pdf_file.name = "test_document.pdf"
    pdf_file.read.return_value = b"fake_pdf_content"
    pdf_file.seek.return_value = None
    pdf_file.getbuffer.return_value = b"fake_pdf_buffer"
    return pdf_file


@pytest.fixture
def mock_cv_chain():
    """Create mock CV processing chain."""
    chain = Mock()
    mock_document = Document(
        id="cv-test-001",
        document_type=DocumentType.CV,
        content="Test CV content",
        metadata={"filename": "test_cv.pdf", "profile": "Software Developer"},
    )
    chain.invoke.return_value = mock_document
    return chain


@pytest.fixture
def mock_job_chain():
    """Create mock Job processing chain."""
    chain = Mock()
    mock_document = Document(
        id="job-test-001",
        document_type=DocumentType.JOB,
        content="Test job content",
        metadata={"filename": "test_job.pdf"},
    )
    chain.invoke.return_value = mock_document
    return chain


def test_document_processor_initialization(
    mock_config, mock_cv_chain, mock_job_chain
):
    """Test DocumentProcessor initializes correctly."""
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    assert processor.config == mock_config
    assert processor._cv_processor is not None
    assert processor._job_processor is not None
    assert isinstance(processor._cv_processor, CVDocumentProcessor)
    assert isinstance(processor._job_processor, JobDocumentProcessor)


@patch("fitz.open")
def test_document_processor_extract_text_from_pdf_success(
    mock_fitz_open, mock_config, mock_cv_chain, mock_job_chain, mock_pdf_file
):
    """Test successful PDF text extraction."""
    mock_doc = MagicMock()
    mock_page = Mock()
    mock_page.get_text.return_value = "Test PDF content extracted from page"
    mock_page.get_links.return_value = []
    mock_doc.__len__.return_value = 1
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz_open.return_value = mock_doc
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    result = processor.extract_text_from_pdf(mock_pdf_file)
    assert "Test PDF content extracted from page" in result
    mock_fitz_open.assert_called_once()
    mock_doc.close.assert_called_once()


@patch("fitz.open")
def test_document_processor_extract_text_with_links(
    mock_fitz_open, mock_config, mock_cv_chain, mock_job_chain, mock_pdf_file
):
    """Test PDF text extraction with link enhancement."""
    mock_doc = MagicMock()
    mock_page = Mock()
    mock_page.get_text.return_value = "Contact me at LinkedIn"
    mock_page.get_links.return_value = [
        {
            "uri": "https://linkedin.com/in/johndoe",
            "from": {"x0": 10, "y0": 10, "x1": 50, "y1": 20},
        }
    ]
    mock_page.get_textbox.return_value = "LinkedIn"
    mock_doc.__len__.return_value = 1
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz_open.return_value = mock_doc
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    result = processor.extract_text_from_pdf(mock_pdf_file)
    assert "https://linkedin.com/in/johndoe" in result


@patch("fitz.open")
def test_document_processor_extract_text_pdf_error(
    mock_fitz_open, mock_config, mock_cv_chain, mock_job_chain, mock_pdf_file
):
    """Test PDF extraction error handling."""
    mock_fitz_open.side_effect = Exception("PDF is corrupted")
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    with pytest.raises(SkilloProcessingError, match="PDF extraction failed"):
        processor.extract_text_from_pdf(mock_pdf_file)


def test_document_processor_generate_document_id(
    mock_config, mock_cv_chain, mock_job_chain
):
    """Test document ID generation."""
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    content = "This is test content for document ID generation"
    filename = "test_document.pdf"
    doc_id = processor.generate_document_id(content, filename)
    assert isinstance(doc_id, str)
    assert len(doc_id) == 32
    doc_id2 = processor.generate_document_id(content, filename)
    assert doc_id == doc_id2


@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_document_processor_save_uploaded_file_cv(
    mock_file_open,
    mock_makedirs,
    mock_config,
    mock_cv_chain,
    mock_job_chain,
    mock_pdf_file,
):
    """Test saving uploaded CV file."""
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    file_path = processor.save_uploaded_file(
        mock_pdf_file, DocumentType.CV.value
    )
    mock_makedirs.assert_called_once_with("./uploads/cvs", exist_ok=True)
    mock_file_open.assert_called_once()
    assert file_path == os.path.join("./uploads/cvs", "test_document.pdf")


@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_document_processor_save_uploaded_file_job(
    mock_file_open,
    mock_makedirs,
    mock_config,
    mock_cv_chain,
    mock_job_chain,
    mock_pdf_file,
):
    """Test saving uploaded Job file."""
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    file_path = processor.save_uploaded_file(
        mock_pdf_file, DocumentType.JOB.value
    )
    mock_makedirs.assert_called_once_with("./uploads/jobs", exist_ok=True)
    assert file_path == os.path.join("./uploads/jobs", "test_document.pdf")


def test_document_processor_save_uploaded_file_invalid_type(
    mock_config, mock_cv_chain, mock_job_chain, mock_pdf_file
):
    """Test saving file with invalid type."""
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    with pytest.raises(
        SkilloProcessingError, match="Invalid file type 'invalid'"
    ):
        processor.save_uploaded_file(mock_pdf_file, "invalid")


@patch(
    "skillo.infrastructure.processing.document_processor.DocumentProcessor.extract_text_from_pdf"
)
@patch(
    "skillo.infrastructure.processing.document_processor.DocumentProcessor.generate_document_id"
)
def test_document_processor_process_cv_document(
    mock_gen_id,
    mock_extract_text,
    mock_config,
    mock_cv_chain,
    mock_job_chain,
    mock_pdf_file,
):
    """Test processing CV document successfully."""
    mock_extract_text.return_value = "CV content with skills and experience"
    mock_gen_id.return_value = "cv-doc-id-123"
    mock_cv_document = Document(
        id="cv-doc-id-123",
        document_type=DocumentType.CV,
        content="CV content with skills and experience",
        metadata={
            "filename": "test_document.pdf",
            "profile": "Software Developer",
        },
    )
    mock_cv_chain.invoke.return_value = mock_cv_document
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    result = processor.process_document(mock_pdf_file, DocumentType.CV.value)
    mock_extract_text.assert_called_once_with(mock_pdf_file)
    mock_gen_id.assert_called_once_with(
        "CV content with skills and experience", "test_document.pdf"
    )
    expected_input = {
        "content": "CV content with skills and experience",
        "filename": "test_document.pdf",
        "doc_id": "cv-doc-id-123",
    }
    mock_cv_chain.invoke.assert_called_once_with(expected_input)
    assert result == mock_cv_document


@patch(
    "skillo.infrastructure.processing.document_processor.DocumentProcessor.extract_text_from_pdf"
)
@patch(
    "skillo.infrastructure.processing.document_processor.DocumentProcessor.generate_document_id"
)
def test_document_processor_process_job_document(
    mock_gen_id,
    mock_extract_text,
    mock_config,
    mock_cv_chain,
    mock_job_chain,
    mock_pdf_file,
):
    """Test processing Job document successfully."""
    mock_extract_text.return_value = "Job description with requirements"
    mock_gen_id.return_value = "job-doc-id-456"
    mock_job_document = Document(
        id="job-doc-id-456",
        document_type=DocumentType.JOB,
        content="Job description with requirements",
        metadata={"filename": "test_document.pdf"},
    )
    mock_job_chain.invoke.return_value = mock_job_document
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    result = processor.process_document(mock_pdf_file, DocumentType.JOB.value)
    expected_input = {
        "content": "Job description with requirements",
        "filename": "test_document.pdf",
        "doc_id": "job-doc-id-456",
    }
    mock_job_chain.invoke.assert_called_once_with(expected_input)
    assert result == mock_job_document


@patch(
    "skillo.infrastructure.processing.document_processor.DocumentProcessor.extract_text_from_pdf"
)
def test_document_processor_process_empty_document(
    mock_extract_text,
    mock_config,
    mock_cv_chain,
    mock_job_chain,
    mock_pdf_file,
):
    """Test processing document with no text content."""
    mock_extract_text.return_value = ""
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    with pytest.raises(
        SkilloProcessingError,
        match="Empty document .* - no text could be extracted",
    ):
        processor.process_document(mock_pdf_file, DocumentType.CV.value)


def test_document_processor_process_invalid_document_type(
    mock_config, mock_cv_chain, mock_job_chain, mock_pdf_file
):
    """Test processing document with invalid type."""
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    with patch.object(
        processor, "extract_text_from_pdf", return_value="some content"
    ):
        with pytest.raises(
            SkilloProcessingError, match="Invalid file type 'invalid'"
        ):
            processor.process_document(mock_pdf_file, "invalid")


@patch(
    "skillo.infrastructure.processing.document_processor.DocumentProcessor.extract_text_from_pdf"
)
@patch(
    "skillo.infrastructure.processing.document_processor.DocumentProcessor.generate_document_id"
)
def test_document_processor_process_chain_error(
    mock_gen_id,
    mock_extract_text,
    mock_config,
    mock_cv_chain,
    mock_job_chain,
    mock_pdf_file,
):
    """Test processing document when chain fails."""
    mock_extract_text.return_value = "Valid content"
    mock_gen_id.return_value = "doc-id-123"
    mock_cv_chain.invoke.side_effect = Exception("Chain processing failed")
    processor = DocumentProcessor(mock_config, mock_cv_chain, mock_job_chain)
    with pytest.raises(SkilloProcessingError, match="Processing .* failed"):
        processor.process_document(mock_pdf_file, DocumentType.CV.value)


def test_cv_document_processor_initialization(mock_config, mock_cv_chain):
    """Test CVDocumentProcessor initializes correctly."""
    processor = CVDocumentProcessor(mock_config, mock_cv_chain)
    assert processor.config == mock_config
    assert processor._cv_chain == mock_cv_chain


def test_cv_document_processor_process_content_success(
    mock_config, mock_cv_chain
):
    """Test CV processor processes content successfully."""
    mock_document = Document(
        id="cv-001",
        document_type=DocumentType.CV,
        content="Test CV content",
        metadata={"filename": "test.pdf"},
    )
    mock_cv_chain.invoke.return_value = mock_document
    processor = CVDocumentProcessor(mock_config, mock_cv_chain)
    result = processor.process_document_content(
        "Test CV content", "test.pdf", "cv-001"
    )
    expected_input = {
        "content": "Test CV content",
        "filename": "test.pdf",
        "doc_id": "cv-001",
    }
    mock_cv_chain.invoke.assert_called_once_with(expected_input)
    assert result == mock_document


def test_cv_document_processor_process_content_error(
    mock_config, mock_cv_chain
):
    """Test CV processor handles processing errors."""
    mock_cv_chain.invoke.side_effect = Exception("Chain failed")
    processor = CVDocumentProcessor(mock_config, mock_cv_chain)
    with pytest.raises(
        SkilloProcessingError, match="CV document processing failed"
    ):
        processor.process_document_content(
            "Test CV content", "test.pdf", "cv-001"
        )


def test_job_document_processor_process_content_success(
    mock_config, mock_job_chain
):
    """Test Job processor processes content successfully."""
    mock_document = Document(
        id="job-001",
        document_type=DocumentType.JOB,
        content="Test job content",
        metadata={"filename": "test.pdf"},
    )
    mock_job_chain.invoke.return_value = mock_document
    processor = JobDocumentProcessor(mock_config, mock_job_chain)
    result = processor.process_document_content(
        "Test job content", "test.pdf", "job-001"
    )
    expected_input = {
        "content": "Test job content",
        "filename": "test.pdf",
        "doc_id": "job-001",
    }
    mock_job_chain.invoke.assert_called_once_with(expected_input)
    assert result == mock_document


def test_base_document_processor_abstract_method():
    """Test BaseDocumentProcessor abstract method enforcement."""
    with pytest.raises(TypeError):
        BaseDocumentProcessor(Mock())


def test_base_processor_document_id_generation(mock_config):
    """Test base processor document ID generation."""

    class TestProcessor(BaseDocumentProcessor):
        def process_document_content(
            self, content: str, filename: str, doc_id: str
        ) -> Document:
            return Mock()

    processor = TestProcessor(mock_config)
    content = "Sample document content for ID generation"
    filename = "sample.pdf"
    doc_id = processor.generate_document_id(content, filename)
    assert isinstance(doc_id, str)
    assert len(doc_id) == 32
    doc_id2 = processor.generate_document_id(content, filename)
    assert doc_id == doc_id2
    doc_id3 = processor.generate_document_id("different content", filename)
    assert doc_id != doc_id3


@patch("fitz.open")
def test_base_processor_pdf_extraction_multipage(mock_fitz_open, mock_config):
    """Test base processor handles multi-page PDFs."""

    class TestProcessor(BaseDocumentProcessor):
        def process_document_content(
            self, content: str, filename: str, doc_id: str
        ) -> Document:
            return Mock()

    mock_doc = MagicMock()
    mock_page1 = Mock()
    mock_page1.get_text.return_value = "Page 1 content"
    mock_page1.get_links.return_value = []
    mock_page2 = Mock()
    mock_page2.get_text.return_value = "Page 2 content"
    mock_page2.get_links.return_value = []
    mock_doc.__len__.return_value = 2
    mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
    mock_fitz_open.return_value = mock_doc
    processor = TestProcessor(mock_config)
    mock_pdf_file = Mock()
    mock_pdf_file.read.return_value = b"fake_pdf"
    mock_pdf_file.seek.return_value = None
    result = processor.extract_text_from_pdf(mock_pdf_file)
    assert "Page 1 content" in result
    assert "Page 2 content" in result


@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_base_processor_save_file_success(
    mock_file_open, mock_makedirs, mock_config
):
    """Test base processor saves files correctly."""

    class TestProcessor(BaseDocumentProcessor):
        def process_document_content(
            self, content: str, filename: str, doc_id: str
        ) -> Document:
            return Mock()

    processor = TestProcessor(mock_config)
    mock_file = Mock()
    mock_file.name = "test.pdf"
    mock_file.getbuffer.return_value = b"file_content"
    result = processor.save_uploaded_file(mock_file, "/test/upload/dir")
    mock_makedirs.assert_called_once_with("/test/upload/dir", exist_ok=True)
    expected_path = os.path.join("/test/upload/dir", "test.pdf")
    mock_file_open.assert_called_once_with(expected_path, "wb")
    assert result == expected_path
