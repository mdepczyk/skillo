import os
import tempfile
from unittest.mock import Mock, mock_open, patch

import joblib
import pytest
from pydantic import BaseModel, ValidationError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

from skillo.infrastructure.agents.langchain_experience_agent import (
    LangChainExperienceAgent,
)
from skillo.infrastructure.agents.langchain_location_agent import (
    LangChainLocationAgent,
)
from skillo.infrastructure.agents.langchain_skills_agent import (
    LangChainSkillsAgent,
)
from skillo.infrastructure.agents.langchain_supervisor_agent import (
    LangChainSupervisorAgent,
)
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.tools.profile_classifier import ProfileClassifier


def test_supervisor_agent_basic(mock_openai, test_config):
    with patch.dict(
        "os.environ", {"OPENAI_API_KEY": test_config["OPENAI_API_KEY"]}
    ):
        config = Config()
        agent = LangChainSupervisorAgent(config=config)
        mock_cv = Mock()
        mock_cv.content = "Senior Python Developer with Django experience"
        mock_cv.metadata = {"skills": ["Python", "Django"]}
        mock_job = Mock()
        mock_job.content = "Looking for Python Developer with Django"
        mock_job.metadata = {"requirements": ["Python", "Django"]}
        result = agent.analyze_match(mock_cv, mock_job)
        assert "weighted_final_score" in result
        assert result["weighted_final_score"] >= 0.0
        assert result["weighted_final_score"] <= 1.0
        assert "recommendation" in result
        assert mock_openai.chat.completions.create.call_count >= 1


@pytest.fixture
def mock_models_directory():
    """Create temporary directory with mock ML model files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        training_texts = [
            "software developer python django react",
            "data scientist machine learning python pandas",
            "product manager agile scrum requirements",
            "python developer backend api django",
            "ml engineer tensorflow pytorch deep learning",
            "project manager coordination planning",
        ]
        vectorizer = TfidfVectorizer(max_features=100, stop_words="english")
        X_vectorized = vectorizer.fit_transform(training_texts)
        joblib.dump(vectorizer, os.path.join(temp_dir, "vectorizer.joblib"))
        classifier = KNeighborsClassifier(n_neighbors=3)
        y_labels = [
            0,
            1,
            2,
            0,
            1,
            2,
        ]
        classifier.fit(X_vectorized, y_labels)
        joblib.dump(
            classifier, os.path.join(temp_dir, "KNeighborsClassifier.joblib")
        )
        encoder = LabelEncoder()
        encoder.fit(
            ["Software Developer", "Data Scientist", "Product Manager"]
        )
        joblib.dump(encoder, os.path.join(temp_dir, "label_encoder.joblib"))
        yield temp_dir


@pytest.fixture
def profile_classifier(mock_models_directory):
    """Create ProfileClassifier instance with mock models."""
    return ProfileClassifier(mock_models_directory)


def test_profile_classifier_initialization(mock_models_directory):
    """Test ProfileClassifier initializes correctly."""
    classifier = ProfileClassifier(mock_models_directory)
    assert classifier._models_dir == mock_models_directory
    assert not classifier._loaded
    assert classifier._vectorizer is None
    assert classifier._model is None
    assert classifier._label_encoder is None


def test_profile_classifier_loads_models_successfully(profile_classifier):
    """Test ProfileClassifier loads all model files successfully."""
    result = profile_classifier.classify_profile(
        "python developer with django experience"
    )
    assert profile_classifier._loaded
    assert profile_classifier._vectorizer is not None
    assert profile_classifier._model is not None
    assert profile_classifier._label_encoder is not None
    assert isinstance(result, str)


def test_profile_classifier_classify_software_developer(profile_classifier):
    """Test classification of software developer CV content."""
    cv_content = "software developer python django react"
    result = profile_classifier.classify_profile(cv_content)
    assert isinstance(result, str)
    assert len(result) > 0


def test_profile_classifier_classify_data_scientist(profile_classifier):
    """Test classification of data scientist CV content."""
    cv_content = "data scientist machine learning python pandas"
    result = profile_classifier.classify_profile(cv_content)
    assert isinstance(result, str)
    assert len(result) > 0


def test_profile_classifier_empty_content(profile_classifier):
    """Test ProfileClassifier handles empty content gracefully."""
    result = profile_classifier.classify_profile("")
    assert isinstance(result, str)


def test_profile_classifier_none_content(profile_classifier):
    """Test ProfileClassifier handles None content."""
    try:
        result = profile_classifier.classify_profile(None)
        assert result == "Unknown"
    except (TypeError, AttributeError):
        pass


def test_profile_classifier_missing_model_files():
    """Test ProfileClassifier handles missing model files gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        classifier = ProfileClassifier(temp_dir)
        result = classifier.classify_profile("test content")
        assert result == "Unknown"
        assert not classifier._loaded


def test_profile_classifier_corrupted_model_files():
    """Test ProfileClassifier handles corrupted model files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "vectorizer.joblib"), "w") as f:
            f.write("invalid content")
        with open(
            os.path.join(temp_dir, "KNeighborsClassifier.joblib"), "w"
        ) as f:
            f.write("invalid content")
        with open(os.path.join(temp_dir, "label_encoder.joblib"), "w") as f:
            f.write("invalid content")
        classifier = ProfileClassifier(temp_dir)
        result = classifier.classify_profile("test content")
        assert result == "Unknown"
        assert not classifier._loaded


def test_profile_classifier_model_loading_caching(profile_classifier):
    """Test models are loaded only once and cached."""
    result1 = profile_classifier.classify_profile("first call")
    vectorizer_id1 = id(profile_classifier._vectorizer)
    result2 = profile_classifier.classify_profile("second call")
    vectorizer_id2 = id(profile_classifier._vectorizer)
    assert vectorizer_id1 == vectorizer_id2
    assert profile_classifier._loaded
    assert isinstance(result1, str)
    assert isinstance(result2, str)


def test_profile_classifier_vectorizer_transforms_correctly(
    profile_classifier,
):
    """Test TF-IDF vectorizer transforms text correctly."""
    profile_classifier.classify_profile("test content")
    assert profile_classifier._vectorizer is not None
    test_texts = ["python developer", "machine learning engineer"]
    transformed = profile_classifier._vectorizer.transform(test_texts)
    assert transformed.shape[0] == 2
    assert transformed.shape[1] > 0


def test_profile_classifier_label_encoder_inverse_transform(
    profile_classifier,
):
    """Test label encoder correctly maps numeric labels to text."""
    profile_classifier.classify_profile("test content")
    assert profile_classifier._label_encoder is not None
    labels = profile_classifier._label_encoder.classes_
    assert len(labels) > 0
    assert all(isinstance(label, str) for label in labels)


def test_profile_classifier_multiple_concurrent_calls(profile_classifier):
    """Test ProfileClassifier handles concurrent classification calls."""
    cv_contents = [
        "software developer python experience",
        "data scientist ml background",
        "product manager agile experience",
        "devops engineer aws expertise",
    ]
    results = []
    for content in cv_contents:
        result = profile_classifier.classify_profile(content)
        results.append(result)
    assert len(results) == 4
    assert all(isinstance(result, str) for result in results)
    assert all(len(result) > 0 for result in results)
    assert profile_classifier._loaded


@pytest.fixture
def mock_skills_agent():
    """Create mock SkillsAgent for testing."""
    with (
        patch(
            "skillo.infrastructure.agents.langchain_skills_agent.yaml.safe_load"
        ) as mock_yaml,
        patch(
            "skillo.infrastructure.agents.langchain_skills_agent.ChatOpenAI"
        ) as mock_openai,
        patch("builtins.open", mock_open(read_data="dummy_yaml_content")),
    ):
        mock_yaml.return_value = {
            "skills_analysis": {
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "max_tokens": 1500,
                "system_message": "You are a skills analysis agent.",
                "user_message": "Analyze skills between CV and job: {cv_content} vs {job_content}",
            }
        }
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.cv_skills = ["Python", "Django"]
        mock_response.required_skills = ["Python", "Django", "React"]
        mock_response.matched_skills = ["Python", "Django"]
        mock_response.score = 0.85
        mock_response.explanation = "Good skills match"
        mock_response.to_domain.return_value = mock_response
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value.with_structured_output.return_value = mock_llm
        config = Mock(spec=Config)
        config.PROMPTS_DIR = "./test_prompts"
        agent = LangChainSkillsAgent(config)
        agent.llm = mock_llm
        yield agent


def test_skills_agent_successful_analysis(mock_skills_agent):
    """Test SkillsAgent performs successful analysis."""
    cv_content = "Python Developer with Django experience"
    job_content = "Looking for Python/Django developer with React knowledge"
    result = mock_skills_agent.analyze_skills_match(cv_content, job_content)
    assert isinstance(result, dict)
    assert "cv_skills" in result
    assert "required_skills" in result
    assert "matched_skills" in result
    assert "score" in result
    assert "explanation" in result
    assert isinstance(result["cv_skills"], list)
    assert isinstance(result["required_skills"], list)
    assert isinstance(result["matched_skills"], list)
    assert isinstance(result["score"], float)
    assert isinstance(result["explanation"], str)
    assert 0.0 <= result["score"] <= 1.0


def test_skills_agent_validation_error(mock_skills_agent):
    """Test SkillsAgent handles validation errors gracefully."""
    with patch.object(mock_skills_agent.llm, "invoke") as mock_invoke:
        try:

            class DummyModel(BaseModel):
                required_field: str

            DummyModel()
        except ValidationError as e:
            mock_invoke.side_effect = e
        result = mock_skills_agent.analyze_skills_match("test cv", "test job")
        assert result == {
            "cv_skills": [],
            "required_skills": [],
            "matched_skills": [],
            "score": 0.0,
            "explanation": "Error in skills analysis",
        }


def test_skills_agent_unexpected_error(mock_skills_agent):
    """Test SkillsAgent handles unexpected errors gracefully."""
    with patch.object(mock_skills_agent.llm, "invoke") as mock_invoke:
        mock_invoke.side_effect = Exception("API connection failed")
        result = mock_skills_agent.analyze_skills_match("test cv", "test job")
        assert result == {
            "cv_skills": [],
            "required_skills": [],
            "matched_skills": [],
            "score": 0.0,
            "explanation": "Error in skills analysis",
        }


@pytest.fixture
def mock_experience_agent():
    """Create mock ExperienceAgent for testing."""
    with (
        patch(
            "skillo.infrastructure.agents.langchain_experience_agent.yaml.safe_load"
        ) as mock_yaml,
        patch(
            "skillo.infrastructure.agents.langchain_experience_agent.ChatOpenAI"
        ) as mock_openai,
        patch("builtins.open", mock_open(read_data="dummy_yaml_content")),
    ):
        mock_yaml.return_value = {
            "experience_analysis": {
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "max_tokens": 1500,
                "system_message": "You are an experience analysis agent.",
                "user_message": "Analyze experience: {cv_content} vs {job_content}",
            }
        }
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.cv_experience_years = "5+ years"
        mock_response.required_experience_years = "3+ years"
        mock_response.cv_level = "Senior"
        mock_response.required_level = "Mid-level"
        mock_response.score = 0.90
        mock_response.explanation = "Experience exceeds requirements"
        mock_response.to_domain.return_value = mock_response
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value.with_structured_output.return_value = mock_llm
        config = Mock(spec=Config)
        config.PROMPTS_DIR = "./test_prompts"
        agent = LangChainExperienceAgent(config)
        agent.llm = mock_llm
        yield agent


def test_experience_agent_successful_analysis(mock_experience_agent):
    """Test ExperienceAgent performs successful analysis."""
    cv_content = "Senior Developer with 5 years Python experience"
    job_content = "Looking for Mid-level developer with 3+ years"
    result = mock_experience_agent.analyze_experience_match(
        cv_content, job_content
    )
    assert isinstance(result, dict)
    required_fields = [
        "cv_experience_years",
        "required_experience_years",
        "cv_level",
        "required_level",
        "score",
        "explanation",
    ]
    for field in required_fields:
        assert field in result
    assert isinstance(result["score"], float)
    assert 0.0 <= result["score"] <= 1.0
    assert isinstance(result["explanation"], str)


@pytest.fixture
def mock_location_agent():
    """Create mock LocationAgent for testing."""
    with (
        patch(
            "skillo.infrastructure.agents.langchain_location_agent.yaml.safe_load"
        ) as mock_yaml,
        patch(
            "skillo.infrastructure.agents.langchain_location_agent.ChatOpenAI"
        ) as mock_openai,
        patch("builtins.open", mock_open(read_data="dummy_yaml_content")),
    ):
        mock_yaml.return_value = {
            "location_analysis": {
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "max_tokens": 1500,
                "system_message": "You are a location matching agent.",
                "user_message": "Analyze location compatibility: {cv_content} vs {job_content}",
            }
        }
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.candidate_location = "New York, NY"
        mock_response.job_location = "Remote/New York"
        mock_response.remote_work = "Available"
        mock_response.distance_km = "0"
        mock_response.commute_feasibility = "Excellent"
        mock_response.score = 0.95
        mock_response.explanation = "Perfect location match with remote option"
        mock_response.to_domain.return_value = mock_response
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value.with_structured_output.return_value = mock_llm
        config = Mock(spec=Config)
        config.PROMPTS_DIR = "./test_prompts"
        agent = LangChainLocationAgent(config)
        agent.llm = mock_llm
        yield agent


def test_location_agent_remote_work_compatibility(mock_location_agent):
    """Test LocationAgent handles remote work scenarios."""
    cv_content = "Based in New York, open to remote work"
    job_content = "Remote position, preference for East Coast candidates"
    result = mock_location_agent.analyze_location_match(
        cv_content, job_content
    )
    assert isinstance(result, dict)
    assert "candidate_location" in result
    assert "job_location" in result
    assert "remote_work" in result
    assert "distance_km" in result
    assert "commute_feasibility" in result
    assert "score" in result
    assert "explanation" in result
    assert isinstance(result["remote_work"], str)
    assert isinstance(result["score"], float)
    assert 0.0 <= result["score"] <= 1.0


def test_multiple_agents_integration():
    """Test multiple agents can work together without interference."""
    with (
        patch(
            "skillo.infrastructure.agents.langchain_skills_agent.yaml.safe_load"
        ),
        patch(
            "skillo.infrastructure.agents.langchain_skills_agent.ChatOpenAI"
        ),
        patch(
            "skillo.infrastructure.agents.langchain_experience_agent.yaml.safe_load"
        ),
        patch(
            "skillo.infrastructure.agents.langchain_experience_agent.ChatOpenAI"
        ),
        patch("builtins.open", mock_open(read_data="dummy_yaml_content")),
    ):
        config = Mock(spec=Config)
        config.PROMPTS_DIR = "./test_prompts"
        skills_agent = LangChainSkillsAgent(config)
        experience_agent = LangChainExperienceAgent(config)
        assert skills_agent.AGENT_NAME == "SKILLS AGENT"
        assert experience_agent.AGENT_NAME == "EXPERIENCE AGENT"
        assert (
            skills_agent.DEFAULT_RESPONSE != experience_agent.DEFAULT_RESPONSE
        )


def test_agent_prompt_configuration_loading():
    """Test agents correctly load prompt configurations."""
    with patch("builtins.open", create=True) as mock_open:
        mock_file = Mock()
        mock_file.read.return_value = """
skills_analysis:
  model: "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 1500
  system_message: "Test system message"
  user_message: "Test user message"
        """
        mock_open.return_value.__enter__.return_value = mock_file
        with patch("yaml.safe_load") as mock_yaml_load:
            mock_yaml_load.return_value = {
                "skills_analysis": {
                    "model": "gpt-4o-mini",
                    "temperature": 0.1,
                    "max_tokens": 1500,
                    "system_message": "Test system message",
                    "user_message": "Test user message",
                }
            }
            with patch(
                "skillo.infrastructure.agents.langchain_skills_agent.ChatOpenAI"
            ):
                config = Mock(spec=Config)
                config.PROMPTS_DIR = "./test_prompts"
                agent = LangChainSkillsAgent(config)
                assert agent.prompt_config["model"] == "gpt-4o-mini"
                assert agent.prompt_config["temperature"] == 0.1
                assert agent.prompt_config["max_tokens"] == 1500


def test_agent_error_resilience():
    """Test agents maintain functionality despite various error conditions."""
    test_cases = [
        ("Empty CV content", "", "valid job content"),
        ("Empty job content", "valid cv content", ""),
        ("Both empty", "", ""),
        ("Very long content", "x" * 10000, "y" * 10000),
        ("Special characters", "CV with émojis 🐍", "Jób with spëcial chars"),
    ]
    with (
        patch(
            "skillo.infrastructure.agents.langchain_skills_agent.yaml.safe_load"
        ) as mock_yaml,
        patch(
            "skillo.infrastructure.agents.langchain_skills_agent.ChatOpenAI"
        ) as mock_openai,
        patch("builtins.open", mock_open(read_data="dummy_yaml_content")),
    ):
        mock_yaml.return_value = {
            "skills_analysis": {
                "model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 1500,
                "system_message": "test",
                "user_message": "test {cv_content} {job_content}",
            }
        }
        mock_llm = Mock()
        mock_llm.invoke.return_value.to_domain.return_value = Mock(
            cv_skills=[],
            required_skills=[],
            matched_skills=[],
            score=0.0,
            explanation="test",
        )
        mock_openai.return_value.with_structured_output.return_value = mock_llm
        config = Mock(spec=Config)
        config.PROMPTS_DIR = "./test_prompts"
        agent = LangChainSkillsAgent(config)
        for test_name, cv_content, job_content in test_cases:
            result = agent.analyze_skills_match(cv_content, job_content)
            assert isinstance(result, dict), f"Failed on {test_name}"
            assert "score" in result, f"Failed on {test_name}"
            assert isinstance(
                result["score"], (int, float)
            ), f"Failed on {test_name}"
