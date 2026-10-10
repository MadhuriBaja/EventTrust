"""Service for extracting basic event information from an event webpage."""

import json
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from app.models.event import EventProfile


class EventExtractionService:
    """Fetches an event webpage and extracts structured event information."""

    def extract_from_url(self, event_url: str) -> EventProfile:
        """Fetch an event URL and build an EventProfile."""

        response = httpx.get(
            event_url,
            follow_redirects=True,
            timeout=15.0,
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        event_data = self._extract_event_json_ld(soup)

        title = self._extract_title(soup)
        description = self._extract_description(soup)

        if event_data:
            title = event_data.get("event_name") or title
            description = event_data.get("description") or description

        return EventProfile(
            event_name=title,
            organizer=event_data.get("organizer") if event_data else None,
            event_date=event_data.get("event_date") if event_data else None,
            venue=event_data.get("venue") if event_data else None,
            speakers=event_data.get("speakers", []) if event_data else [],
            registration_url=(
                event_data.get("registration_url")
                if event_data
                else None
            ),
            source_url=str(response.url),
            description=description,
        )

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> Optional[str]:
        """Extract the page title."""

        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            if title:
                return title

        og_title = soup.find("meta", property="og:title")

        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        return None

    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> Optional[str]:
        """Extract the page description."""

        description = soup.find(
            "meta",
            attrs={"name": "description"},
        )

        if description and description.get("content"):
            return description["content"].strip()

        og_description = soup.find(
            "meta",
            property="og:description",
        )

        if og_description and og_description.get("content"):
            return og_description["content"].strip()

        return None

    @classmethod
    def _extract_event_json_ld(
        cls,
        soup: BeautifulSoup,
    ) -> Optional[Dict[str, Any]]:
        """Extract Event information from JSON-LD structured data."""

        scripts = soup.find_all(
            "script",
            attrs={"type": "application/ld+json"},
        )

        for script in scripts:
            if not script.string:
                continue

            try:
                data = json.loads(script.string)
            except json.JSONDecodeError:
                continue

            event = cls._find_event_object(data)

            if event:
                return cls._build_event_data(event)

        return None

    @classmethod
    def _find_event_object(
        cls,
        data: Any,
    ) -> Optional[Dict[str, Any]]:
        """Find an Event object inside JSON-LD data."""

        if isinstance(data, dict):
            data_type = data.get("@type")

            if data_type == "Event":
                return data

            if isinstance(data_type, list) and "Event" in data_type:
                return data

            graph = data.get("@graph")

            if isinstance(graph, list):
                for item in graph:
                    event = cls._find_event_object(item)

                    if event:
                        return event

        elif isinstance(data, list):
            for item in data:
                event = cls._find_event_object(item)

                if event:
                    return event

        return None

    @staticmethod
    def _build_event_data(
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Convert JSON-LD Event data into EventProfile-compatible fields."""

        organizer = EventExtractionService._extract_person_or_organization(
            event.get("organizer")
        )

        venue = EventExtractionService._extract_location(
            event.get("location")
        )

        speakers = EventExtractionService._extract_speakers(
            event.get("performer")
        )

        registration_url = EventExtractionService._extract_registration_url(
            event.get("offers")
        )

        return {
            "event_name": EventExtractionService._clean_string(
                event.get("name")
            ),
            "organizer": organizer,
            "event_date": EventExtractionService._clean_string(
                event.get("startDate")
            ),
            "venue": venue,
            "speakers": speakers,
            "registration_url": registration_url,
            "description": EventExtractionService._clean_string(
                event.get("description")
            ),
        }

    @staticmethod
    def _extract_person_or_organization(
        value: Any,
    ) -> Optional[str]:
        """Extract a name from a person or organization object."""

        if isinstance(value, str):
            return value.strip() or None

        if isinstance(value, dict):
            name = value.get("name")

            if isinstance(name, str):
                return name.strip() or None

        return None

    @staticmethod
    def _extract_location(
        value: Any,
    ) -> Optional[str]:
        """Extract venue/location name from an event location."""

        if isinstance(value, str):
            return value.strip() or None

        if not isinstance(value, dict):
            return None

        name = value.get("name")

        if isinstance(name, str) and name.strip():
            return name.strip()

        address = value.get("address")

        if isinstance(address, str):
            return address.strip() or None

        if isinstance(address, dict):
            address_parts = []

            for key in (
                "streetAddress",
                "addressLocality",
                "addressRegion",
                "postalCode",
                "addressCountry",
            ):
                part = address.get(key)

                if isinstance(part, str) and part.strip():
                    address_parts.append(part.strip())

            if address_parts:
                return ", ".join(address_parts)

        return None

    @staticmethod
    def _extract_speakers(
        value: Any,
    ) -> List[str]:
        """Extract speaker names from performer data."""

        if not value:
            return []

        values = value if isinstance(value, list) else [value]

        speakers = []

        for item in values:
            name = EventExtractionService._extract_person_or_organization(
                item
            )

            if name and name not in speakers:
                speakers.append(name)

        return speakers

    @staticmethod
    def _extract_registration_url(
        value: Any,
    ) -> Optional[str]:
        """Extract a registration or ticket URL from offers data."""

        if not value:
            return None

        values = value if isinstance(value, list) else [value]

        for item in values:
            if isinstance(item, str):
                return item.strip() or None

            if isinstance(item, dict):
                url = item.get("url")

                if isinstance(url, str) and url.strip():
                    return url.strip()

        return None

    @staticmethod
    def _clean_string(
        value: Any,
    ) -> Optional[str]:
        """Convert a value into a clean string."""

        if isinstance(value, str):
            cleaned = value.strip()

            if cleaned:
                return cleaned

        return None


event_extraction_service = EventExtractionService()