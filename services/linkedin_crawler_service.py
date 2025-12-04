"""
LinkedIn crawler service (dummy implementation).
"""
import time
import random
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

        # Random companies and schools
        companies = [
            ("Snapppay", "250-500", random.randint(1, 3)),
            ("Digipay", "201-500", random.randint(1, 5)),
            ("Ofogh Kish", "201-500", random.randint(2, 10)),
            ("Tech Corp", "1000-5000", random.randint(1, 4)),
            ("Startup Inc", "11-50", random.randint(1, 3))
        ]

        schools = [
            ("Sharif University of Technology", "Bachelor"),
            ("University of Tehran", "Master"),
            ("MIT", "PhD"),
            ("Stanford University", "Bachelor"),
            ("Amirkabir University", "Master")
        ]

        # Generate random work experience (1-4 companies)
        num_companies = random.randint(1, 4)
        worked_at = [
            {
                "company_name": comp[0],
                "staff_count_range": comp[1],
                "years": comp[2]
            }
            for comp in random.sample(companies, num_companies)
        ]

        # Generate random education (1-2 schools)
        num_schools = random.randint(1, 2)
        studied_at = [
            {
                "school_name": school[0],
                "degree_level": school[1]
            }
            for school in random.sample(schools, num_schools)
        ]

        # Random connections (100-500+)
        connections = random.choice([100, 250, 500, 500])

        # Return profile data in the expected format
        return {
            "username": username,
            "connections": connections,
            "worked_at": worked_at,
            "studied_at": studied_at
        }
