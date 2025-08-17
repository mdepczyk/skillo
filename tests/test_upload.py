from unittest.mock import Mock, patch

from skillo.application.mappers.dto_mapper import DTOMapper
from skillo.application.use_cases.upload_document import UploadDocument
from skillo.domain.events import DomainEventPublisher


def test_document_upload_end_to_end(sample_cv):
    mock_repository = Mock()
    mock_repository.add_document.return_value = True

    event_publisher = DomainEventPublisher()

    upload_service = UploadDocument(
        document_repository=mock_repository, event_publisher=event_publisher
    )

    with patch.object(DTOMapper, "dto_to_document") as mock_mapper:
        mock_domain_doc = Mock()
        mock_domain_doc.document_type.value = "CV"
        mock_domain_doc.metadata = {"filename": "test.pdf"}
        mock_mapper.return_value = mock_domain_doc

        result = upload_service.execute_with_dto(sample_cv)

        assert result is True
        mock_repository.add_document.assert_called_once()
        mock_mapper.assert_called_once_with(sample_cv)
