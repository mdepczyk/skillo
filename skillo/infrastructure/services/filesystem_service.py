"""File system service implementation."""

import os
from typing import Optional


class FileSystemService:
    """Concrete implementation of file system operations."""

    def read_file(self, file_path: str) -> Optional[bytes]:
        """Read file content as bytes."""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception:
            return None

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        return os.path.exists(file_path)

    def join_path(self, *parts: str) -> str:
        """Join path components."""
        return os.path.join(*parts)
