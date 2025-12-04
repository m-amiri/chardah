"""
LinkedIn crawler service (dummy implementation).
"""
import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class LinkedInCrawlerService:
    """
    Dummy LinkedIn crawler service.
    Follows Interface Segregation - provides only crawling functionality.
    """

    def crawl(self, linkedin_url: str) -> Dict:
        """
        Crawl LinkedIn profile (dummy implementation).

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Dict containing profile data
        """
        logger.info(f"Crawling LinkedIn profile: {linkedin_url}")

        # Simulate network delay
        time.sleep(0.5)

        # Extract username from URL
        username = linkedin_url.rstrip('/').split('/')[-1]

        # Return dummy profile data
        return {
            "url": linkedin_url,
            "username": username,
            "name": "John Doe",
            "headline": "Software Engineer at Tech Company",
            "connections": 500,
            "experience": [
                {
                    "company": "Tech Company",
                    "title": "Senior Software Engineer",
                    "duration": "2 years"
                }
            ],
            "education": [
                {
                    "school": "University",
                    "degree": "Bachelor's in Computer Science"
                }
            ]
        }
