"""
Model service for scoring using external ML API.
"""
import logging
import requests
from typing import Dict

logger = logging.getLogger(__name__)


class ModelService:
    """
    ML model service for scoring LinkedIn profiles via HTTP API.
    Follows Single Responsibility - only handles model inference.
    """

    def __init__(self, model_api_url: str):
        """
        Initialize the model service.

        Args:
            model_api_url: URL of the model scoring API endpoint
        """
        self.model_api_url = model_api_url

    def predict(self, profile_data: Dict) -> Dict:
        """
        Generate a scoring prediction based on profile data.

        Args:
            profile_data: LinkedIn profile data in the format:
                {
                    "username": str,
                    "connections": int,
                    "worked_at": List[Dict],
                    "studied_at": List[Dict]
                }

        Returns:
            Dict containing score, label, grade, and detailed explanation

        Raises:
            Exception: If API request fails or returns invalid data
        """
        logger.info(f"Running model prediction for: {profile_data.get('username', 'unknown')}")

        headers = {
            "content-type": "application/json"
        }

        try:
            response = requests.post(
                self.model_api_url,
                json=profile_data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()

            logger.info(f"Model prediction successful for: {profile_data.get('username', 'unknown')}, score: {result.get('score')}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get model prediction: {str(e)}", exc_info=True)
            raise Exception(f"Model prediction failed: {str(e)}")
