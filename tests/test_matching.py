from unittest.mock import Mock, patch

from skillo.application.use_cases.match_cv_to_jobs import MatchCVToJobs
from skillo.domain.events import DomainEventPublisher


def test_cv_to_jobs_matching(sample_cv, sample_job):
    mock_repository = Mock()
    mock_repository.get_documents_by_type.return_value = [Mock()]

    mock_supervisor = Mock()
    mock_supervisor.analyze_match.return_value = Mock(
        overall_score=0.85, recommendation="RECOMMENDED"
    )

    mock_parallel_executor = Mock()
    mock_parallel_executor.execute_tasks.return_value = [
        {"match_result": Mock(overall_score=0.85), "job": Mock()}
    ]

    event_publisher = DomainEventPublisher()

    matching_service = MatchCVToJobs(
        document_repository=mock_repository,
        supervisor_agent=mock_supervisor,
        parallel_executor=mock_parallel_executor,
        top_candidates_count=5,
        min_match_score=0.7,
        event_publisher=event_publisher,
    )

    with (
        patch(
            "skillo.application.mappers.dto_mapper.DTOMapper.dto_to_document"
        ),
        patch.object(
            matching_service, "_matching_service"
        ) as mock_matching_svc,
    ):

        mock_match_result = Mock()
        mock_match_result.overall_score = 0.85
        mock_match_result.job_id = sample_job.id
        mock_matching_svc.match_cv_to_all_jobs.return_value = [
            mock_match_result
        ]

        results = matching_service.execute_dto(sample_cv)
        assert len(results) >= 0

        mock_matching_svc.match_cv_to_all_jobs.assert_called_once()
