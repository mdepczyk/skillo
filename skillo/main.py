from typing import Any

import streamlit as st
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
from skillo.application.facades import (
    ApplicationFacade,
    ConfigFacade,
    DocumentFacade,
    MatchingFacade,
)
from skillo.application.services import ApplicationEventHandler
from skillo.application.use_cases.process_and_upload_documents import (
    ProcessUploadedDocuments,
)
from skillo.domain.events import (
    DatabaseResetEvent,
    DocumentExportCompletedEvent,
    DocumentExportFailedEvent,
    DocumentUploadedEvent,
    DocumentUploadFailedEvent,
    DomainEventPublisher,
    MatchingCompletedEvent,
    MatchingFailedEvent,
)
from skillo.domain.services import DocumentBuilder
from skillo.infrastructure.agents.langchain_supervisor_agent import (
    LangChainSupervisorAgent,
)
from skillo.infrastructure.chains import (
    create_cv_processing_chain,
    create_job_processing_chain,
)
from skillo.infrastructure.config.settings import Config
from skillo.infrastructure.execution.thread_pool_executor import (
    ThreadPoolParallelExecutor,
)
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
from skillo.infrastructure.services.filesystem_service import FileSystemService
from skillo.infrastructure.tools.profile_classifier import ProfileClassifier
from skillo.ui.app import run_ui
from skillo.ui.components.notification import StreamlitNotificationHandler


class DIContainer(containers.DeclarativeContainer):
    """DI container with dependency placeholders for Composition Root."""

    config = providers.Singleton(Config)
    logger = providers.Object(logger)

    event_publisher: providers.Dependency[Any] = providers.Dependency()
    document_builder: providers.Dependency[Any] = providers.Dependency()

    document_repository = providers.Singleton(
        ChromaDocumentRepository,
        config=config,
    )

    management_repository = providers.Singleton(
        ChromaManagementRepository,
        document_repository=document_repository,
    )

    filesystem_service = providers.Singleton(FileSystemService)

    profile_classifier = providers.Singleton(
        ProfileClassifier,
        models_dir_path=config().MODELS_DIR_PATH,
    )

    cv_processing_chain = providers.Singleton(
        create_cv_processing_chain,
        config=config,
        profile_classifier=profile_classifier,
        document_builder=document_builder,
    )

    job_processing_chain = providers.Singleton(
        create_job_processing_chain,
        config=config,
        document_builder=document_builder,
    )

    supervisor_agent = providers.Singleton(
        LangChainSupervisorAgent,
        config=config,
    )

    parallel_executor = providers.Singleton(
        ThreadPoolParallelExecutor,
        max_workers=config().MAX_WORKERS,
    )

    document_processor = providers.Singleton(
        DocumentProcessor,
        config=config,
        cv_chain=cv_processing_chain,
        job_chain=job_processing_chain,
    )

    match_cv_to_jobs = providers.Factory(
        MatchCVToJobs,
        document_repository=document_repository,
        supervisor_agent=supervisor_agent,
        parallel_executor=parallel_executor,
        top_candidates_count=config().TOP_CANDIDATES_COUNT,
        min_match_score=config().MIN_MATCH_SCORE,
        event_publisher=event_publisher,
    )

    match_job_to_cvs = providers.Factory(
        MatchJobToCVs,
        document_repository=document_repository,
        supervisor_agent=supervisor_agent,
        parallel_executor=parallel_executor,
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
        filesystem=filesystem_service,
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

    process_uploaded_documents = providers.Factory(
        ProcessUploadedDocuments,
        document_processor=document_processor,
        upload_service=upload_document,
        parallel_executor=parallel_executor,
        event_publisher=event_publisher,
    )

    document_facade = providers.Singleton(
        DocumentFacade,
        upload_service=upload_document,
        stats_service=get_document_stats,
        list_service=get_document_list,
        reset_service=reset_database,
        export_service=export_to_csv,
        document_processor=document_processor,
        process_and_upload_service=process_uploaded_documents,
        filesystem=filesystem_service,
    )

    matching_facade = providers.Singleton(
        MatchingFacade,
        cv_to_jobs_service=match_cv_to_jobs,
        job_to_cvs_service=match_job_to_cvs,
    )

    config_facade = providers.Singleton(
        ConfigFacade,
        config_service=config,
        logger_service=logger,
    )

    application_facade = providers.Singleton(
        ApplicationFacade,
        documents=document_facade,
        matching=matching_facade,
        config=config_facade,
    )


def create_container(
    domain_event_publisher: Any, document_builder: Any
) -> DIContainer:
    """Container factory with Domain services from Composition Root."""
    return DIContainer(
        event_publisher=domain_event_publisher,
        document_builder=document_builder,
    )


def setup_event_subscriptions(publisher, handler):
    """Setup all event subscriptions."""
    events = [
        MatchingCompletedEvent,
        MatchingFailedEvent,
        DocumentUploadedEvent,
        DocumentUploadFailedEvent,
        DatabaseResetEvent,
        DocumentExportCompletedEvent,
        DocumentExportFailedEvent,
    ]
    for event in events:
        publisher.subscribe(event, handler)


def main():
    """Application entry point - Composition Root."""
    if "di_container" not in st.session_state:
        domain_event_publisher = DomainEventPublisher()
        document_builder = DocumentBuilder()

        st.session_state.di_container = create_container(
            domain_event_publisher=domain_event_publisher,
            document_builder=document_builder,
        )

    di_container = st.session_state.di_container
    app_facade = di_container.application_facade()

    if not st.session_state.get("events_configured", False):
        publisher = di_container.event_publisher()
        ui_notification_handler = StreamlitNotificationHandler()
        domain_event_handler = ApplicationEventHandler(ui_notification_handler)
        setup_event_subscriptions(publisher, domain_event_handler)
        st.session_state["events_configured"] = True

    run_ui(app_facade)


if __name__ == "__main__":
    main()
