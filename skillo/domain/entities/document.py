from dataclasses import dataclass, field
from typing import Any, Dict

from skillo.domain.enums import DocumentType


@dataclass
class Document:
    """Universal document entity."""

    id: str
    document_type: DocumentType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
