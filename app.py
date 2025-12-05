"""
Main Flask application factory.
"""
import logging
from flask import Flask, render_template
from config import get_config
from core import JobStore, JobRunner
from services import LinkedInScraperService, ModelService, JobService
from controllers import job_bp, init_controller


def create_app(config_name: str = None) -> Flask:
    """
    Application factory pattern.
    Follows Dependency Inversion - high-level modules don't depend on low-level modules.

    Args:
        config_name: Configuration environment name

    Returns:
        Configured Flask application
    """
    # Create Flask app with UI directory configuration
    app = Flask(__name__,
                static_folder='ui/static',
                template_folder='ui/templates')

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize core components
    job_store = JobStore()
    job_runner = JobRunner(max_workers=config.MAX_WORKERS)

    # Store job_runner on app for access in teardown
    app.job_runner = job_runner

    # Initialize services
    scraper_service = LinkedInScraperService(
        api_key=config.RAPIDAPI_KEY,
        api_host=config.RAPIDAPI_HOST
    )
    model_service = ModelService(
        model_api_url=config.MODEL_API_URL
    )
    job_service = JobService(
        job_store=job_store,
        job_runner=job_runner,
        scraper_service=scraper_service,
        model_service=model_service
    )

    # Initialize controller with dependencies
    init_controller(job_service)

    # Register blueprints
    app.register_blueprint(job_bp)

    # UI Route - Index page
    @app.route('/')
    def index():
        """Serve the main UI page."""
        return render_template('index.html')

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "healthy"}, 200

    # Note: Job runner cleanup removed from teardown_appcontext as it was causing
    # premature shutdown in development mode. For production, use proper
    # process management (e.g., gunicorn with worker lifecycle hooks)

    return app


if __name__ == '__main__':
    """Run the application in development mode."""
    app = create_app('development')
    app.run(host='0.0.0.0', port=5014)
