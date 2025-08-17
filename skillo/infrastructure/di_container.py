from dependency_injector import containers, providers

from skillo.application import (
    ExportToCSV,
    GetDocumentList,
    GetDocumentStats,
    MatchCVToJobs,
    MatchJobToCVs,
    ResetDatabase,
    UploadDocument,
)
from skillo.domain.events import (
    DomainEventPublisher,
)
from skillo.domain.services import ServiceContainer
from skillo.infrastructure.agents import (
    LangChainCVProcessingAgent,
    LangChainJobProcessingAgent,
    LangChainNormalizationAgent,
)
from skillo.infrastructure.agents.langchain_supervisor_agent import (
    LangChainSupervisorAgent,
)
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.logger import logger
from skillo.infrastructure.processing.document_processor import (
    DocumentProcessor,
)
from skillo.infrastructure.repositories.chroma_document_repository import (
    ChromaDocumentRepository,
)
from skillo.infrastructure.repositories.chroma_management_repository import (
    ChromaManagementRepository,
)
from skillo.infrastructure.tools.profile_classifier import ProfileClassifier


class DIContainer(containers.DeclarativeContainer):
    """Application dependency injection container."""

    config = providers.Singleton(Config)

    event_publisher = providers.Singleton(DomainEventPublisher)

    logger = providers.Object(logger)

    document_repository = providers.Singleton(
        ChromaDocumentRepository,
        config=config,
    )

    management_repository = providers.Singleton(
        ChromaManagementRepository,
        document_repository=document_repository,
    )

    profile_classifier = providers.Singleton(ProfileClassifier)

    cv_processing_agent = providers.Singleton(
        LangChainCVProcessingAgent,
        profile_classifier=profile_classifier,
        config=config,
    )

    job_processing_agent = providers.Singleton(
        LangChainJobProcessingAgent,
        config=config,
    )

    normalization_agent = providers.Singleton(
        LangChainNormalizationAgent,
        config=config,
    )

    supervisor_agent = providers.Singleton(
        LangChainSupervisorAgent,
        config=config,
    )

    document_processor = providers.Singleton(
        DocumentProcessor,
        config=config,
        cv_agent=cv_processing_agent,
        job_agent=job_processing_agent,
        normalizer=normalization_agent,
    )

    match_cv_to_jobs = providers.Factory(
        MatchCVToJobs,
        document_repository=document_repository,
        supervisor_agent=supervisor_agent,
        top_candidates_count=config().TOP_CANDIDATES_COUNT,
        min_match_score=config().MIN_MATCH_SCORE,
        event_publisher=event_publisher,
    )

    match_job_to_cvs = providers.Factory(
        MatchJobToCVs,
        document_repository=document_repository,
        supervisor_agent=supervisor_agent,
        top_candidates_count=config().TOP_CANDIDATES_COUNT,
        min_match_score=config().MIN_MATCH_SCORE,
        event_publisher=event_publisher,
    )

    upload_document = providers.Factory(
        UploadDocument,
        document_repository=document_repository,
        event_publisher=event_publisher,
    )

    get_document_stats = providers.Factory(
        GetDocumentStats,
        document_repository=document_repository,
    )

    get_document_list = providers.Factory(
        GetDocumentList,
        document_repository=document_repository,
        cv_upload_dir=config().CV_UPLOAD_DIR,
        job_upload_dir=config().JOB_UPLOAD_DIR,
    )

    reset_database = providers.Factory(
        ResetDatabase,
        management_repository=management_repository,
        event_publisher=event_publisher,
    )

    export_to_csv = providers.Factory(
        ExportToCSV,
        management_repository=management_repository,
        event_publisher=event_publisher,
    )


def create_container() -> DIContainer:
    """Create DI container."""
    container = DIContainer()
    return container


class ServiceContainerAdapter(ServiceContainer):
    """ServiceContainer adapter for DIContainer."""

    def __init__(self, di_container: DIContainer):
        self._container = di_container

    def upload_document(self):
        return self._container.upload_document()

    def get_document_list(self):
        return self._container.get_document_list()

    def get_document_stats(self):
        return self._container.get_document_stats()

    def match_cv_to_jobs(self):
        return self._container.match_cv_to_jobs()

    def match_job_to_cvs(self):
        return self._container.match_job_to_cvs()

    def reset_database(self):
        return self._container.reset_database()

    def export_to_csv(self):
        return self._container.export_to_csv()

    def logger(self):
        return self._container.logger()

    def config(self):
        return self._container.config()

    def document_processor(self):
        return self._container.document_processor()
