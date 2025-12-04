"""
Background job execution using ThreadPoolExecutor.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class JobRunner:
    """
    Handles asynchronous job execution in background threads.
    Follows Single Responsibility Principle - only manages job execution.
    """

    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit_job(self, job_func: Callable, *args, **kwargs):
        """
        Submit a job to be executed in the background.

        Args:
            job_func: The function to execute
            *args, **kwargs: Arguments to pass to the function
        """
        future = self._executor.submit(job_func, *args, **kwargs)

        # Add error callback for logging
        def log_exception(fut):
            try:
                fut.result()
            except Exception as e:
                logger.error(f"Job execution failed: {str(e)}", exc_info=True)

        future.add_done_callback(log_exception)
        return future

    def shutdown(self, wait: bool = True):
        """Shutdown the executor gracefully."""
        self._executor.shutdown(wait=wait)
