"""
Job controller for handling HTTP requests.
"""
import uuid
from flask import Blueprint, request, jsonify
from services.job_service import JobService
from utils.validators import JobRequestValidator

# Create Blueprint
job_bp = Blueprint('job', __name__)

# This will be injected by the app factory
job_service: JobService = None


def init_controller(service: JobService):
    """
    Initialize controller with dependencies.
    Follows Dependency Inversion - controller depends on service abstraction.
    """
    global job_service
    job_service = service


@job_bp.route('/job', methods=['POST'])
def create_job():
    """
    POST /job
    Create a new background job.

    Request body:
    {
        "name": "string",
        "cell_number": "989127638825",
        "linkedin_account": "https://linkedin.com/in/...."
    }

    Response:
    {
        "job_id": "<uuid>"
    }
    """
    try:
        # Get JSON data
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        # Validate input
        errors = JobRequestValidator.validate(data)
        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 400

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Create and execute job
        job_service.create_and_execute_job(job_id, data)

        return jsonify({"job_id": job_id}), 202

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@job_bp.route('/job/<job_id>', methods=['GET'])
def get_job(job_id: str):
    """
    GET /job/<job_id>
    Get job status and result.

    Response:
    {
        "status": "inprogress | complete | failed",
        "result": { ... }  # only if status = complete
    }
    """
    try:
        # Get job status
        job_status = job_service.get_job_status(job_id)

        if not job_status:
            return jsonify({"error": "Job not found"}), 404

        return jsonify(job_status), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
