from unittest.mock import Mock, mock_open, patch

import pytest

from skillo.domain.entities import Document
from skillo.domain.enums import DocumentType
from skillo.infrastructure.chains.cv_processing_chain import (
    LangChainCVProcessingChain,
    create_cv_processing_chain,
)
from skillo.infrastructure.chains.job_processing_chain import (
    LangChainJobProcessingChain,
    create_job_processing_chain,
)


@pytest.fixture
def mock_cv_processing_response():
    """Create mock CV processing response."""
    response = Mock()
    response.skills = ["Python", "Django", "FastAPI"]
    response.experience_years = "5+ years"
    response.education = "Computer Science degree"
    response.summary = "Experienced Python developer"
    return response


@pytest.fixture
def mock_job_processing_response():
    """Create mock Job processing response."""
    response = Mock()
    response.skills = ["Python", "Django", "React"]
    response.experience_years = "3+ years"
    response.education = "Bachelor's degree preferred"
    response.summary = "Looking for Python developer"
    return response


@pytest.fixture
def mock_normalization_response():
    """Create mock normalization response."""
    response = Mock()
    response.normalized_skills = ["python", "django", "fastapi"]
    response.normalized_experience = "senior"
    response.normalized_education = "university"
    return response


@pytest.fixture
def mock_document():
    """Create mock document."""
    return Document(
        id="test-doc-001",
        document_type=DocumentType.CV,
        content="Test CV content",
        metadata={"filename": "test_cv.pdf", "profile": "Software Developer"},
    )


@pytest.fixture
def mock_services():
    """Create mocked services for pipeline testing."""
    cv_agent = Mock()
    normalizer = Mock()
    profile_classifier = Mock()
    document_builder = Mock()
    return {
        "cv_agent": cv_agent,
        "normalizer": normalizer,
        "profile_classifier": profile_classifier,
        "document_builder": document_builder,
    }


def test_cv_processing_chain_initialization(mock_services):
    """Test CV processing chain initializes correctly."""
    chain = LangChainCVProcessingChain(
        cv_agent=mock_services["cv_agent"],
        normalizer=mock_services["normalizer"],
        profile_classifier=mock_services["profile_classifier"],
        document_builder=mock_services["document_builder"],
    )
    assert chain._cv_agent == mock_services["cv_agent"]
    assert chain._normalizer == mock_services["normalizer"]
    assert chain._profile_classifier == mock_services["profile_classifier"]
    assert chain._document_builder == mock_services["document_builder"]
    assert chain._pipeline is not None
    assert chain.CHAIN_NAME == "CV PROCESSING CHAIN"


def test_cv_processing_chain_successful_processing(
    mock_services,
    mock_cv_processing_response,
    mock_normalization_response,
    mock_document,
):
    """Test CV processing chain processes document successfully."""
    mock_services["cv_agent"].process_document.return_value = (
        mock_cv_processing_response
    )
    mock_services["normalizer"].normalize_cv_data.return_value = (
        mock_normalization_response
    )
    mock_services["profile_classifier"].classify_profile.return_value = (
        "Software Developer"
    )
    mock_services["document_builder"].build_cv_document.return_value = (
        mock_document
    )
    chain = LangChainCVProcessingChain(
        cv_agent=mock_services["cv_agent"],
        normalizer=mock_services["normalizer"],
        profile_classifier=mock_services["profile_classifier"],
        document_builder=mock_services["document_builder"],
    )
    result = chain.process_document("Test CV content", "test_cv.pdf", "cv-001")
    mock_services["cv_agent"].process_document.assert_called_once_with(
        "Test CV content"
    )
    mock_services[
        "profile_classifier"
    ].classify_profile.assert_called_once_with("Test CV content")
    mock_services["normalizer"].normalize_cv_data.assert_called_once_with(
        mock_cv_processing_response
    )
    mock_services["document_builder"].build_cv_document.assert_called_once()
    assert result == mock_document


def test_cv_processing_chain_parallel_execution(
    mock_services, mock_cv_processing_response
):
    """Test CV processing chain executes CV agent and profile classifier in parallel."""
    call_order = []

    def cv_agent_side_effect(content):
        call_order.append("cv_agent")
        return mock_cv_processing_response

    def profile_classifier_side_effect(content):
        call_order.append("profile_classifier")
        return "Software Developer"

    mock_services["cv_agent"].process_document.side_effect = (
        cv_agent_side_effect
    )
    mock_services["profile_classifier"].classify_profile.side_effect = (
        profile_classifier_side_effect
    )
    mock_services["normalizer"].normalize_cv_data.return_value = Mock()
    mock_services["document_builder"].build_cv_document.return_value = Mock()
    chain = LangChainCVProcessingChain(
        cv_agent=mock_services["cv_agent"],
        normalizer=mock_services["normalizer"],
        profile_classifier=mock_services["profile_classifier"],
        document_builder=mock_services["document_builder"],
    )
    chain.process_document("Test CV content", "test_cv.pdf", "cv-001")
    assert "cv_agent" in call_order
    assert "profile_classifier" in call_order


def test_cv_processing_chain_error_handling(mock_services):
    """Test CV processing chain handles errors gracefully."""
    mock_services["cv_agent"].process_document.side_effect = Exception(
        "Processing failed"
    )
    chain = LangChainCVProcessingChain(
        cv_agent=mock_services["cv_agent"],
        normalizer=mock_services["normalizer"],
        profile_classifier=mock_services["profile_classifier"],
        document_builder=mock_services["document_builder"],
    )
    with pytest.raises(Exception, match="Processing failed"):
        chain.process_document("Test CV content", "test_cv.pdf", "cv-001")


def test_cv_processing_chain_invoke_method(mock_services, mock_document):
    """Test CV processing chain invoke method works correctly."""
    processing_response = Mock()
    processing_response.skills = ["Python", "Django", "FastAPI"]
    mock_services["cv_agent"].process_document.return_value = (
        processing_response
    )
    mock_services["profile_classifier"].classify_profile.return_value = (
        "Software Developer"
    )
    mock_services["normalizer"].normalize_cv_data.return_value = Mock()
    mock_services["document_builder"].build_cv_document.return_value = (
        mock_document
    )
    chain = LangChainCVProcessingChain(
        cv_agent=mock_services["cv_agent"],
        normalizer=mock_services["normalizer"],
        profile_classifier=mock_services["profile_classifier"],
        document_builder=mock_services["document_builder"],
    )
    input_data = {
        "content": "Test CV content",
        "filename": "test_cv.pdf",
        "doc_id": "cv-001",
    }
    result = chain.invoke(input_data)
    assert result == mock_document
    mock_services["cv_agent"].process_document.assert_called_once_with(
        "Test CV content"
    )


def test_job_processing_chain_initialization():
    """Test Job processing chain initializes correctly."""
    job_agent = Mock()
    normalizer = Mock()
    document_builder = Mock()
    chain = LangChainJobProcessingChain(
        job_agent=job_agent,
        normalizer=normalizer,
        document_builder=document_builder,
    )
    assert chain._job_agent == job_agent
    assert chain._normalizer == normalizer
    assert chain._document_builder == document_builder
    assert chain._pipeline is not None
    assert chain.CHAIN_NAME == "JOB PROCESSING CHAIN"


def test_job_processing_chain_successful_processing(
    mock_job_processing_response, mock_normalization_response
):
    """Test Job processing chain processes document successfully."""
    job_agent = Mock()
    normalizer = Mock()
    document_builder = Mock()
    mock_job_document = Mock()
    job_agent.process_document.return_value = mock_job_processing_response
    normalizer.normalize_job_data.return_value = mock_normalization_response
    document_builder.build_job_document.return_value = mock_job_document
    chain = LangChainJobProcessingChain(
        job_agent=job_agent,
        normalizer=normalizer,
        document_builder=document_builder,
    )
    result = chain.process_document(
        "Test job content", "test_job.pdf", "job-001"
    )
    job_agent.process_document.assert_called_once_with("Test job content")
    normalizer.normalize_job_data.assert_called_once_with(
        mock_job_processing_response
    )
    document_builder.build_job_document.assert_called_once()
    assert result == mock_job_document


def test_job_processing_chain_error_handling():
    """Test Job processing chain handles errors gracefully."""
    job_agent = Mock()
    normalizer = Mock()
    document_builder = Mock()
    job_agent.process_document.side_effect = Exception("Job processing failed")
    chain = LangChainJobProcessingChain(
        job_agent=job_agent,
        normalizer=normalizer,
        document_builder=document_builder,
    )
    with pytest.raises(Exception, match="Job processing failed"):
        chain.process_document("Test job content", "test_job.pdf", "job-001")


def test_job_processing_chain_document_builder_parameters():
    """Test Job processing chain passes correct parameters to document builder."""
    job_agent = Mock()
    normalizer = Mock()
    document_builder = Mock()
    mock_job_document = Mock()
    processing_response = Mock()
    processing_response.skills = ["Python", "React"]
    normalization_response = Mock()
    job_agent.process_document.return_value = processing_response
    normalizer.normalize_job_data.return_value = normalization_response
    document_builder.build_job_document.return_value = mock_job_document
    chain = LangChainJobProcessingChain(
        job_agent=job_agent,
        normalizer=normalizer,
        document_builder=document_builder,
    )
    chain.process_document("Test job content", "test_job.pdf", "job-001")
    document_builder.build_job_document.assert_called_once_with(
        doc_id="job-001",
        filename="test_job.pdf",
        processing_response=processing_response,
        normalization_response=normalization_response,
        profile=None,
    )


def test_cv_processing_chain_factory_function():
    """Test CV processing chain factory function."""
    with (
        patch(
            "skillo.infrastructure.chains.cv_processing_chain.LangChainCVProcessingAgent"
        ) as mock_cv_agent_class,
        patch(
            "skillo.infrastructure.chains.cv_processing_chain.LangChainNormalizationAgent"
        ) as mock_normalizer_class,
        patch("builtins.open", mock_open(read_data="dummy_yaml_content")),
    ):
        mock_config = Mock()
        mock_profile_classifier = Mock()
        mock_document_builder = Mock()
        mock_cv_agent = Mock()
        mock_normalizer = Mock()
        mock_cv_agent_class.return_value = mock_cv_agent
        mock_normalizer_class.return_value = mock_normalizer
        chain = create_cv_processing_chain(
            mock_config, mock_profile_classifier, mock_document_builder
        )
        mock_cv_agent_class.assert_called_once_with(mock_config)
        mock_normalizer_class.assert_called_once_with(mock_config)
        assert isinstance(chain, LangChainCVProcessingChain)


def test_job_processing_chain_factory_function():
    """Test Job processing chain factory function."""
    with (
        patch(
            "skillo.infrastructure.chains.job_processing_chain.LangChainJobProcessingAgent"
        ) as mock_job_agent_class,
        patch(
            "skillo.infrastructure.chains.job_processing_chain.LangChainNormalizationAgent"
        ) as mock_normalizer_class,
        patch("builtins.open", mock_open(read_data="dummy_yaml_content")),
    ):
        mock_config = Mock()
        mock_document_builder = Mock()
        mock_job_agent = Mock()
        mock_normalizer = Mock()
        mock_job_agent_class.return_value = mock_job_agent
        mock_normalizer_class.return_value = mock_normalizer
        chain = create_job_processing_chain(mock_config, mock_document_builder)
        mock_job_agent_class.assert_called_once_with(mock_config)
        mock_normalizer_class.assert_called_once_with(mock_config)
        assert isinstance(chain, LangChainJobProcessingChain)


def test_pipeline_langchain_integration():
    """Test that pipelines correctly use LangChain RunnableParallel and RunnableLambda."""
    cv_agent = Mock()
    normalizer = Mock()
    profile_classifier = Mock()
    document_builder = Mock()
    chain = LangChainCVProcessingChain(
        cv_agent=cv_agent,
        normalizer=normalizer,
        profile_classifier=profile_classifier,
        document_builder=document_builder,
    )
    assert chain._pipeline is not None
    assert hasattr(chain._pipeline, "invoke")


def test_cv_processing_pipeline_data_flow():
    """Test CV processing pipeline data flow through stages."""
    cv_agent = Mock()
    normalizer = Mock()
    profile_classifier = Mock()
    document_builder = Mock()
    processing_response = Mock()
    processing_response.skills = ["Python", "Django"]
    normalization_response = Mock()
    final_document = Mock()
    cv_agent.process_document.return_value = processing_response
    normalizer.normalize_cv_data.return_value = normalization_response
    profile_classifier.classify_profile.return_value = "Software Developer"
    document_builder.build_cv_document.return_value = final_document
    chain = LangChainCVProcessingChain(
        cv_agent=cv_agent,
        normalizer=normalizer,
        profile_classifier=profile_classifier,
        document_builder=document_builder,
    )
    result = chain.process_document("Test content", "test.pdf", "doc-001")
    cv_agent.process_document.assert_called_once_with("Test content")
    profile_classifier.classify_profile.assert_called_once_with("Test content")
    normalizer.normalize_cv_data.assert_called_once_with(processing_response)
    build_call = document_builder.build_cv_document.call_args
    assert build_call[1]["doc_id"] == "doc-001"
    assert build_call[1]["filename"] == "test.pdf"
    assert build_call[1]["processing_response"] == processing_response
    assert build_call[1]["normalization_response"] == normalization_response
    assert build_call[1]["profile"] == "Software Developer"
    assert result == final_document
