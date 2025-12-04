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
            Dict containing score, label, grade, and detailed explanation
        """
        logger.info(f"Running model prediction for: {profile_data.get('username', 'unknown')}")

        # Simulate model inference delay
        time.sleep(0.3)

        # Generate random score (0.0 - 1.0)
        score = round(random.uniform(0.5, 1.0), 2)
        label = 1 if score > 0.7 else 0

        # Random score_0_1000 (0 - 1000)
        score_0_1000 = random.randint(0, 1000)

        # Random grade (A, B, C, D, E)
        grade = random.choice(['A', 'B', 'C', 'D', 'E'])

        # Generate random feature scores
        work_score = round(random.uniform(5.0, 15.0), 1)
        edu_score = round(random.uniform(0.5, 3.0), 1)
        degree = round(random.uniform(100.0, 500.0), 1)
        total_score = round(work_score + edu_score, 1)
        pagerank = round(random.uniform(0.0, 1.0), 2)
        clustering = round(random.uniform(0.0, 1.0), 2)
        total_years_experience = round(random.uniform(1.0, 15.0), 1)
        max_company_size_score = round(random.uniform(1.0, 5.0), 1)

        # Normalized features (0.0 - 1.0)
        norm_work = round(random.uniform(0.5, 1.0), 3)
        norm_edu = round(random.uniform(0.3, 1.0), 3)
        norm_degree = round(random.uniform(0.5, 1.0), 3)

        # Random logits for model output
        logit_1 = round(random.uniform(50.0, 100.0), 2)
        logit_2 = round(random.uniform(-100.0, -20.0), 2)

        return {
            "username": profile_data.get("username", "unknown"),
            "score": score,
            "label": label,
            "grade": grade,
            "score_0_1000": score_0_1000,
            "explanation": {
                "features": {
                    "work_score": work_score,
                    "edu_score": edu_score,
                    "degree": degree,
                    "total_score": total_score,
                    "pagerank": pagerank,
                    "clustering": clustering,
                    "total_years_experience": total_years_experience,
                    "max_company_size_score": max_company_size_score
                },
                "normalized_features": {
                    "norm_work": norm_work,
                    "norm_edu": norm_edu,
                    "norm_degree": norm_degree
                },
                "raw_profile": profile_data,
                "model": "mlp_baseline",
                "logits": [logit_1, logit_2]
            }
        }
