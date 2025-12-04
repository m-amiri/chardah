"""
Input validation utilities.
"""
import re
from typing import Dict, List


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class JobRequestValidator:
    """
    Validates job request inputs.
    Follows Single Responsibility - only validates input data.
    """

    @staticmethod
    def validate(data: Dict) -> List[str]:
        """
        Validate job request data.

        Args:
            data: Request data dictionary

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Validate 'name'
        if not data.get("name"):
            errors.append("'name' is required")
        elif not isinstance(data["name"], str) or len(data["name"].strip()) == 0:
            errors.append("'name' must be a non-empty string")

        # Validate 'cell_number'
        if not data.get("cell_number"):
            errors.append("'cell_number' is required")
        elif not isinstance(data["cell_number"], str):
            errors.append("'cell_number' must be a string")
        elif not re.match(r'^[0-9]{10,15}$', data["cell_number"]):
            errors.append("'cell_number' must be 10-15 digits")

        # Validate 'linkedin_account'
        if not data.get("linkedin_account"):
            errors.append("'linkedin_account' is required")
        elif not isinstance(data["linkedin_account"], str):
            errors.append("'linkedin_account' must be a string")
        elif not JobRequestValidator._is_valid_linkedin_url(data["linkedin_account"]):
            errors.append("'linkedin_account' must be a valid LinkedIn URL")

        return errors

    @staticmethod
    def _is_valid_linkedin_url(url: str) -> bool:
        """Check if URL is a valid LinkedIn profile URL."""
        pattern = r'^https?://(www\.)?linkedin\.com/in/[\w\-]+/?$'
        return bool(re.match(pattern, url))
