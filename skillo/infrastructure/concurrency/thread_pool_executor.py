from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, List, Optional

from skillo.domain.services.interfaces import ParallelExecutionService


class ThreadPoolParallelExecutor(ParallelExecutionService):
    """ThreadPool-based parallel execution service."""

    def __init__(self, max_workers: int = 5):
        """Initialize with max workers."""
        self._max_workers = max_workers

    def execute_tasks_with_progress(
        self,
        tasks: List[Any],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Any]:
        """Execute tasks in parallel with progress tracking."""
        if not tasks:
            return []

        results = []
        completed_count = 0
        total_count = len(tasks)

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_task = {executor.submit(task): task for task in tasks}

            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                except Exception:
                    continue
                finally:
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total_count)

        return results
