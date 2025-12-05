"""
Job service for orchestrating the job workflow.
"""
import logging
from typing import Dict
from core.job_store import JobStore
from core.job_runner import JobRunner
from services.linkedin_scraper_service import LinkedInScraperService
from services.model_service import ModelService

logger = logging.getLogger(__name__)


class JobService:
    """
    Orchestrates job execution workflow.
    Follows Dependency Inversion - depends on abstractions (injected dependencies).
    """

    def __init__(
        self,
        job_store: JobStore,
        job_runner: JobRunner,
        scraper_service: LinkedInScraperService,
        model_service: ModelService
    ):
        self.job_store = job_store
        self.job_runner = job_runner
        self.scraper_service = scraper_service
        self.model_service = model_service

    def create_and_execute_job(self, job_id: str, job_data: Dict) -> str:
        """
        Create a job and execute it in the background.

        Args:
            job_id: Unique job identifier
            job_data: Job input data (name, cell_number, linkedin_account)

        Returns:
            Job ID
        """
        # Create job in store
        self.job_store.create_job(job_id)

        # Submit background execution
        self.job_runner.submit_job(self._execute_job, job_id, job_data)

        return job_id

    def get_job_status(self, job_id: str) -> Dict:
        """
        Get job status and result.

        Args:
            job_id: Job identifier

        Returns:
            Dict containing status and result (if complete)
        """
        job = self.job_store.get_job(job_id)

        if not job:
            return None

        response = {"status": job.status}

        if job.status == "complete" and job.result:
            response["result"] = job.result
        elif job.status == "failed" and job.error:
            response["error"] = job.error

        return response

    def _execute_job(self, job_id: str, job_data: Dict):
        """
        Execute the job workflow in background.

        Args:
            job_id: Job identifier
            job_data: Job input data
        """
        try:
            logger.info(f"Starting job execution: {job_id}")

            # Step 1: Scrape LinkedIn profile using RapidAPI
            linkedin_profile = self.scraper_service.scrape(job_data["linkedin_account"])

            # Step 2: Map LinkedIn profile to model input format
            model_input = self.scraper_service.map_to_model_input(linkedin_profile)

            # Step 3: Run model prediction (includes raw_profile in explanation)
            model_result = self.model_service.predict(model_input)

            # Update job as complete with model result directly
            self.job_store.update_job_status(job_id, "complete", result=model_result)
            logger.info(f"Job completed successfully: {job_id}")

        except Exception as e:
            logger.error(f"Job failed: {job_id}, error: {str(e)}", exc_info=True)
            self.job_store.update_job_status(job_id, "failed", error=str(e))
