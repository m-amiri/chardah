"""
In-memory job storage with thread-safe operations.
"""
import threading
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Job:
    """Represents a job in the system."""
    id: str
    status: str  # inprogress | complete | failed
    result: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None


class JobStore:
    """
    Thread-safe in-memory job storage.
    Follows Single Responsibility Principle - only manages job storage.
    """

    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def create_job(self, job_id: str) -> Job:
        """Create a new job with 'inprogress' status."""
        with self._lock:
            job = Job(id=job_id, status="inprogress")
            self._jobs[job_id] = job
            return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by ID."""
        with self._lock:
            return self._jobs.get(job_id)

    def update_job_status(self, job_id: str, status: str, result: Optional[Dict] = None, error: Optional[str] = None):
        """Update job status and optionally set result or error."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].status = status
                if result is not None:
                    self._jobs[job_id].result = result
                if error is not None:
                    self._jobs[job_id].error = error

    def job_exists(self, job_id: str) -> bool:
        """Check if a job exists."""
        with self._lock:
            return job_id in self._jobs
