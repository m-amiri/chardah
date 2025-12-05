"""
LinkedIn scraper service using RapidAPI.
"""
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Education:
    """LinkedIn education entry."""
    school: str
    degree: str
    field_of_study: str
    start_month: Optional[str]
    start_year: Optional[int]
    end_month: Optional[str]
    end_year: Optional[int]
    date_range: str
    school_id: Optional[str] = None
    school_linkedin_url: Optional[str] = None


@dataclass
class Experience:
    """LinkedIn work experience entry."""
    company: str
    title: str
    start_month: Optional[int]
    start_year: Optional[int]
    end_month: Optional[int]
    end_year: Optional[int]
    duration: str
    is_current: bool
    location: Optional[str] = None
    description: Optional[str] = None
    company_id: Optional[str] = None
    company_linkedin_url: Optional[str] = None


@dataclass
class LinkedInProfile:
    """Complete LinkedIn profile data model."""
    # Basic info
    public_id: str
    first_name: str
    last_name: str
    full_name: str
    headline: str
    about: Optional[str]

    # Current position
    job_title: Optional[str]
    company: Optional[str]
    company_description: Optional[str]
    company_domain: Optional[str]
    company_employee_count: Optional[int]
    company_employee_range: Optional[str]
    company_industry: Optional[str]
    company_linkedin_url: Optional[str]
    company_website: Optional[str]
    company_year_founded: Optional[int]

    # Location
    location: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]

    # Social metrics
    connection_count: int
    follower_count: Optional[int]

    # Education and experience
    educations: List[Education]
    experiences: List[Experience]

    # Additional fields
    linkedin_url: str
    profile_image_url: Optional[str]
    is_premium: bool = False
    is_verified: bool = False


class LinkedInScraperService:
    """
    LinkedIn scraper service using RapidAPI.
    Follows Interface Segregation - provides only scraping functionality.
    """

    RAPIDAPI_URL = "https://fresh-linkedin-profile-data.p.rapidapi.com/enrich-lead"

    def __init__(self, api_key: str, api_host: str = "fresh-linkedin-profile-data.p.rapidapi.com"):
        """
        Initialize the scraper service.

        Args:
            api_key: RapidAPI key
            api_host: RapidAPI host (default: fresh-linkedin-profile-data.p.rapidapi.com)
        """
        self.api_key = api_key
        self.api_host = api_host

    def scrape(self, linkedin_url: str) -> LinkedInProfile:
        """
        Scrape LinkedIn profile using RapidAPI.

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            LinkedInProfile object containing profile data

        Raises:
            Exception: If API request fails or returns invalid data
        """
        logger.info(f"Scraping LinkedIn profile: {linkedin_url}")

        headers = {
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": self.api_key
        }

        params = {
            "linkedin_url": linkedin_url
        }

        try:
            response = requests.get(
                self.RAPIDAPI_URL,
                headers=headers,
                params=params,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()

            if data.get("message") != "ok":
                raise Exception(f"API returned non-ok message: {data.get('message')}")

            profile_data = data.get("data", {})

            # Parse profile data
            profile = self._parse_profile(profile_data)

            logger.info(f"Successfully scraped profile: {profile.public_id}")
            return profile

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to scrape LinkedIn profile: {str(e)}", exc_info=True)
            raise Exception(f"LinkedIn scraping failed: {str(e)}")

    def _parse_profile(self, data: Dict) -> LinkedInProfile:
        """
        Parse RapidAPI response into LinkedInProfile object.

        Args:
            data: Raw API response data

        Returns:
            LinkedInProfile object
        """
        # Parse educations
        educations = []
        for edu in data.get("educations", []):
            educations.append(Education(
                school=edu.get("school", ""),
                degree=edu.get("degree", ""),
                field_of_study=edu.get("field_of_study", ""),
                start_month=edu.get("start_month"),
                start_year=edu.get("start_year"),
                end_month=edu.get("end_month"),
                end_year=edu.get("end_year"),
                date_range=edu.get("date_range", ""),
                school_id=edu.get("school_id"),
                school_linkedin_url=edu.get("school_linkedin_url")
            ))

        # Parse experiences
        experiences = []
        for exp in data.get("experiences", []):
            experiences.append(Experience(
                company=exp.get("company", ""),
                title=exp.get("title", ""),
                start_month=exp.get("start_month"),
                start_year=exp.get("start_year"),
                end_month=exp.get("end_month"),
                end_year=exp.get("end_year"),
                duration=exp.get("duration", ""),
                is_current=exp.get("is_current", False),
                location=exp.get("location"),
                description=exp.get("description"),
                company_id=exp.get("company_id"),
                company_linkedin_url=exp.get("company_linkedin_url")
            ))

        # Create profile object
        return LinkedInProfile(
            public_id=data.get("public_id", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            full_name=data.get("full_name", ""),
            headline=data.get("headline", ""),
            about=data.get("about"),
            job_title=data.get("job_title"),
            company=data.get("company"),
            company_description=data.get("company_description"),
            company_domain=data.get("company_domain"),
            company_employee_count=data.get("company_employee_count"),
            company_employee_range=data.get("company_employee_range"),
            company_industry=data.get("company_industry"),
            company_linkedin_url=data.get("company_linkedin_url"),
            company_website=data.get("company_website"),
            company_year_founded=data.get("company_year_founded"),
            location=data.get("location"),
            city=data.get("city"),
            state=data.get("state"),
            country=data.get("country"),
            connection_count=data.get("connection_count", 0),
            follower_count=data.get("follower_count"),
            educations=educations,
            experiences=experiences,
            linkedin_url=data.get("linkedin_url", ""),
            profile_image_url=data.get("profile_image_url"),
            is_premium=data.get("is_premium", False),
            is_verified=data.get("is_verified", False)
        )

    def map_to_model_input(self, profile: LinkedInProfile) -> Dict:
        """
        Map LinkedIn profile to model service input format.

        Args:
            profile: LinkedInProfile object

        Returns:
            Dict in the format expected by model service
        """
        # Map experiences to worked_at format
        worked_at = []
        for exp in profile.experiences:
            # Calculate start and end dates
            start_date = None
            end_date = None
            years = 0

            if exp.start_year and exp.start_month:
                start_date = f"{exp.start_year}-{exp.start_month:02d}-01"
            elif exp.start_year:
                start_date = f"{exp.start_year}-01-01"

            if exp.is_current:
                end_date = None
            elif exp.end_year and exp.end_month:
                end_date = f"{exp.end_year}-{exp.end_month:02d}-01"
            elif exp.end_year:
                end_date = f"{exp.end_year}-12-31"

            # Calculate years of experience
            if exp.start_year:
                end_year = exp.end_year if exp.end_year else datetime.now().year
                years = end_year - exp.start_year

            # Get company employee range from experience or profile
            staff_count_range = profile.company_employee_range

            # Get company industry
            company_industry = profile.company_industry if exp.company == profile.company else ""

            worked_at.append({
                "company_name": exp.company,
                "staff_count_range": staff_count_range or "",
                "company_industry": company_industry or "",
                "title": exp.title,
                "start": start_date,
                "end": end_date,
                "years": years
            })

        # Map educations to studied_at format
        studied_at = []
        for edu in profile.educations:
            # Calculate start and end dates
            start_date = None
            end_date = None

            if edu.start_year and edu.start_month:
                start_date = f"{edu.start_year}-{edu.start_month}-01"
            elif edu.start_year:
                start_date = f"{edu.start_year}-09-01"

            if edu.end_year and edu.end_month:
                end_date = f"{edu.end_year}-{edu.end_month}-01"
            elif edu.end_year:
                end_date = f"{edu.end_year}-06-30"

            studied_at.append({
                "school_name": edu.school,
                "degree_level": edu.degree,
                "field_of_study": edu.field_of_study,
                "start": start_date,
                "end": end_date
            })

        return {
            "username": profile.public_id,
            "connections": profile.connection_count,
            "worked_at": worked_at,
            "studied_at": studied_at
        }
