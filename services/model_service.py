"""
Model service for scoring (dummy implementation).
"""
import random
import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ModelService:
    """
    Dummy ML model service for scoring LinkedIn profiles.
    Follows Single Responsibility - only handles model inference.
    """

    def predict(self, profile_data: Dict) -> Dict:
        """
        Generate a scoring prediction based on profile data.

        Args:
            profile_data: LinkedIn profile data

        Returns:
            Dict containing score, label, and explanation
        """
        logger.info(f"Running model prediction for: {profile_data.get('username', 'unknown')}")

        # Simulate model inference delay
        time.sleep(0.3)

        # Generate random score
        score = round(random.uniform(0.5, 0.99), 2)
        label = 1 if score > 0.7 else 0

        # Generate random feature scores
        work_score = round(random.uniform(5.0, 15.0), 1)
        edu_score = round(random.uniform(0.5, 3.0), 1)
        degree = random.choice([15, 20, 25, 30])

        # Random important factors
        possible_factors = [
            "Worked at large companies",
            "Strong professional network",
            "Relevant industry experience",
            "Advanced degree",
            "Leadership positions",
            "Multiple certifications",
            "Active community involvement"
        ]
        important_factors = random.sample(possible_factors, k=random.randint(2, 4))

        return {
            "username": profile_data.get("username", "unknown"),
            "score": score,
            "label": label,
            "explanation": {
                "features": {
                    "work_score": work_score,
                    "edu_score": edu_score,
                    "degree": degree
                },
                "important_factors": important_factors
            }
        }
