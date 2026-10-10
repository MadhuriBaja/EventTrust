
"""Evidence-led event research for EventTrust.

Search results are leads, not verified facts. Event identity is checked
separately from general text relevance to reduce false matches.
"""

import re
from typing import Any
from urllib.parse import urlparse

from app.models.event import EventProfile
from app.services.serpapi_service import serpapi_service


class ResearchService:
    """Collect, classify, and summarize public event research leads."""

    SEARCH_GROUPS = (
        (
            "event_details",
            '"{event}" {organizer} official event agenda date venue',
        ),
        (
            "organizer_history",
            '"{organizer}" past events attendee feedback',
        ),
        (
            "location",
            '"{venue}" address directions event venue',
        ),
        (
            "past_reviews",
            '"{event}" attendee reviews previous edition experiences',
        ),
        (
            "audience_fit",
            '"{event}" agenda topics who should attend benefits',
        ),
    )

    STOP_WORDS = {
        "the", "and", "for", "with", "from", "event", "events",
        "review", "reviews", "attendee", "attendees", "experience",
        "experiences", "past", "official", "about", "what", "when",
        "where", "who", "should", "their", "this", "that", "your",
        "into", "have", "will", "are", "was", "its", "not",
    }

    GENERIC_EVENT_WORDS = {
        "ai", "tech", "technology", "conference", "conferences",
        "summit", "summits", "event", "events", "festival",
        "fest", "expo", "exhibition", "meetup", "meet", "forum",
        "workshop", "workshops", "convention", "symposium",
        "annual", "international", "global", "the",
    }

    def __init__(self, search_client: Any = None) -> None:
        self.search_client = search_client or serpapi_service

    @staticmethod
    def _clean(value: Any) -> str:
        if not isinstance(value, str):
            return ""
        return value.strip()

    @classmethod
    def _tokens(cls, value: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9]+", value.lower())
            if len(token) > 2 and token not in cls.STOP_WORDS
        }

    @staticmethod
    def _normalized_words(value: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", value.lower())

    @classmethod
    def _event_identity_matches(
        cls,
        text: str,
        event_name: str,
    ) -> bool:
        """Require the event's distinguishing name phrase in the result.

        A trailing year is optional. Generic terms alone are not reliable
        event identifiers.
        """
        result_words = cls._normalized_words(text)
        name_words = cls._normalized_words(event_name)

        if not result_words or not name_words:
            return False

        core_words = list(name_words)
        if core_words and re.fullmatch(r"(19|20)\d{2}", core_words[-1]):
            core_words.pop()

        if not core_words:
            return False

        def contains_phrase(phrase: list[str]) -> bool:
            if not phrase or len(phrase) > len(result_words):
                return False

            width = len(phrase)
            return any(
                result_words[index:index + width] == phrase
                for index in range(len(result_words) - width + 1)
            )

        if contains_phrase(core_words):
            return True

        distinctive_words = [
            word for word in core_words
            if word not in cls.GENERIC_EVENT_WORDS and len(word) > 2
        ]

        if len(distinctive_words) < 2:
            return False

        result_word_set = set(result_words)
        return (
            len(set(distinctive_words) & result_word_set)
            == len(set(distinctive_words))
        )

    @classmethod
    def _relevance(
        cls,
        text: str,
        event_name: str,
        organizer: str,
        venue: str,
    ) -> tuple[str, int]:
        """Score text overlap, not event trust or safety."""
        haystack = cls._tokens(text)
        event_tokens = cls._tokens(event_name)
        organizer_tokens = cls._tokens(organizer)
        venue_tokens = cls._tokens(venue)

        score = 0
        event_overlap = len(event_tokens & haystack)

        if event_tokens:
            score += round(70 * event_overlap / len(event_tokens))

        if organizer_tokens:
            score += round(
                20 * len(organizer_tokens & haystack)
                / len(organizer_tokens)
            )

        if venue_tokens:
            score += round(
                10 * len(venue_tokens & haystack)
                / len(venue_tokens)
            )

        if event_tokens and event_overlap == len(event_tokens):
            score = max(score, 70)

        if score >= 70:
            return "high", min(score, 100)
        if score >= 35:
            return "medium", min(score, 100)
        return "low", min(score, 100)

    @staticmethod
    def _valid_url(url: str) -> bool:
        parsed = urlparse(url)
        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )

    @staticmethod
    def _domain(url: str) -> str:
        return urlparse(url).netloc.lower().removeprefix("www.")

    @classmethod
    def _looks_like_attendee_review(
        cls,
        text: str,
        domain: str,
    ) -> bool:
        """Identify review-like wording without claiming authenticity."""
        lower = text.lower()

        review_phrases = (
            "i attended",
            "i went to",
            "my experience",
            "attendee review",
            "attendee feedback",
            "attendees said",
            "attendees discuss their experience",
            "attendees discuss their experiences",
            "experience at",
            "was crowded",
            "was valuable",
            "was disappointing",
            "would recommend",
            "would not recommend",
            "learned a lot",
        )

        review_platforms = (
            "reddit.com",
            "trustpilot.com",
            "eventbrite.",
            "meetup.com",
            "facebook.com",
            "google.com/maps",
            "quora.com",
        )

        return (
            any(phrase in lower for phrase in review_phrases)
            or any(site in domain for site in review_platforms)
        )

    @staticmethod
    def _finding_category(category: str) -> str:
        return {
            "event_details": "event",
            "organizer_history": "organizer_history",
            "location": "venue",
            "past_reviews": "public_reviews",
            "audience_fit": "audience_fit",
        }.get(category, category)

    def build_report(
        self,
        event_name: str,
        event_profile: EventProfile | None = None,
    ) -> dict[str, Any]:
        """Build a structured decision brief with traceable evidence leads."""
        profile = event_profile or EventProfile()
        name = self._clean(profile.event_name) or self._clean(event_name)
        organizer = self._clean(profile.organizer)
        venue = self._clean(profile.venue)

        if not name:
            return {
                "event_name": None,
                "assessment": "insufficient_evidence",
                "summary": "An event name is required to research this event.",
                "findings": [],
                "searches_completed": 0,
                "searches_failed": 0,
                "limitations": ["No event name was provided."],
            }

        findings: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        searches_completed = 0
        searches_failed = 0
        failed_categories: list[str] = []

        for category, template in self.SEARCH_GROUPS:
            if category == "organizer_history" and not organizer:
                continue
            if category == "location" and not venue:
                continue

            query = template.format(
                event=name,
                organizer=organizer,
                venue=venue,
            )

            try:
                response = self.search_client.search(query)
                searches_completed += 1
            except Exception:
                searches_failed += 1
                failed_categories.append(category)
                continue

            if not isinstance(response, dict):
                continue

            results = response.get("organic_results", []) or []
            if not isinstance(results, list):
                continue

            for result in results:
                if not isinstance(result, dict):
                    continue

                title = self._clean(result.get("title"))
                url = self._clean(result.get("link"))
                snippet = self._clean(result.get("snippet"))

                if not self._valid_url(url):
                    continue

                normalized_url = url.split("#", 1)[0].rstrip("/").lower()
                if normalized_url in seen_urls:
                    continue
                seen_urls.add(normalized_url)

                text = f"{title} {snippet}".strip()
                identity_match = self._event_identity_matches(text, name)

                relevance, score = self._relevance(
                    text,
                    name,
                    organizer,
                    venue,
                )

                # A high text-overlap score cannot override a failed
                # event-identity check.
                if not identity_match:
                    relevance = "low"
                    score = min(score, 34)

                domain = self._domain(url)
                review_like = (
                    identity_match
                    and category == "past_reviews"
                    and self._looks_like_attendee_review(text, domain)
                )

                findings.append({
                    "category": self._finding_category(category),
                    "title": title or "Untitled source",
                    "url": url,
                    "snippet": (
                        snippet or "No descriptive snippet was provided."
                    ),
                    "relevance": relevance,
                    "relevance_score": score,
                    "source_domain": domain,
                    "review_status": (
                        "review_like_not_verified"
                        if review_like
                        else "not_independently_verified"
                    ),
                    "evidence_type": (
                        "possible_attendee_review"
                        if review_like
                        else "general_search_lead"
                    ),
                })

        relevant_findings = [
            item for item in findings
            if item["relevance"] in {"high", "medium"}
        ]
        relevant_findings.sort(
            key=lambda item: (
                item["relevance"] != "high",
                -item["relevance_score"],
            )
        )

        review_findings = [
            item for item in relevant_findings
            if item["category"] == "public_reviews"
            and item["evidence_type"] == "possible_attendee_review"
        ]
        event_sources = [
            item for item in relevant_findings
            if item["category"] == "event"
        ]
        location_sources = [
            item for item in relevant_findings
            if item["category"] == "venue"
        ]
        audience_sources = [
            item for item in relevant_findings
            if item["category"] == "audience_fit"
        ]

        limitations = [
            "Event identity matching uses names in search-result titles and snippets; it is not independent verification.",
            "Search snippets may be incomplete, outdated, promotional, or misleading.",
            "Review-like wording does not prove that a source is an authentic attendee review.",
            "No source in this report is independently authenticated by this service.",
        ]

        if not review_findings:
            limitations.append(
                "No plausible attendee-review leads were found for the "
                "matched event results. This does not mean the event has no reviews."
            )

        if not location_sources:
            limitations.append(
                "The venue address and travel details have not been established "
                "by relevant location sources."
            )

        if not audience_sources:
            limitations.append(
                "Audience suitability could not be established from matched "
                "agenda or topic sources."
            )

        if failed_categories:
            limitations.append(
                "Some searches failed: " + ", ".join(failed_categories) + "."
            )

        if not relevant_findings:
            assessment = "insufficient_evidence"
            summary = (
                "There is not enough relevant evidence to assess this event yet. "
                "Check the official event page and organizer details before "
                "making a registration decision."
            )
        else:
            assessment = "investigate_further"
            summary = (
                f"Found {len(relevant_findings)} potentially relevant source "
                f"leads for {name}. These leads are not a safety verdict; "
                "review the original sources and remaining gaps before deciding."
            )

        reviews_summary = (
            f"Found {len(review_findings)} matched, review-like source lead(s). "
            "Open the original pages to confirm that they describe real "
            "attendees and this event or a previous edition."
            if review_findings
            else "No matched attendee-review evidence was established. "
                 "The available results are not enough to summarize past "
                 "attendee experiences."
        )

        audience_summary = (
            "Matched sources mention event topics or audience information. "
            "Review the linked agenda and speaker details to decide whether "
            "the content fits your goals; audience fit is not confirmed."
            if audience_sources
            else "Audience fit is undetermined because matched agenda or "
                 "audience evidence was not found."
        )

        worth_attending = {
            "recommendation": "not_enough_evidence",
            "summary": (
                "There is not enough reliable evidence yet to recommend "
                "attending or skipping the event."
            ),
            "potential_benefits": [],
            "potential_drawbacks": [
                "The quality of attendee feedback and the event's practical "
                "value have not been established."
            ],
        }

        return {
            "event_name": name,
            "organizer": organizer or None,
            "venue": venue or None,
            "event_date": profile.event_date,
            "event_source_url": profile.source_url,
            "registration_url": profile.registration_url,
            "description": profile.description,
            "speakers": profile.speakers,
            "assessment": assessment,
            "summary": summary,
            "event_overview": {
                "description": profile.description,
                "date": profile.event_date,
                "organizer": organizer or None,
                "speakers": profile.speakers,
                "source_url": profile.source_url,
                "registration_url": profile.registration_url,
            },
            "location_details": {
                "venue_name": venue or None,
                "address": None,
                "status": "venue_name_only" if venue else "not_found",
                "source_urls": [
                    item["url"] for item in location_sources
                ],
                "note": "A venue name alone does not establish the full address.",
            },
            "past_reviews": {
                "status": (
                    "possible_reviews_found"
                    if review_findings
                    else "not_found"
                ),
                "summary": reviews_summary,
                "sources": review_findings,
            },
            "audience_fit": {
                "status": (
                    "needs_manual_confirmation"
                    if audience_sources
                    else "insufficient_evidence"
                ),
                "summary": audience_summary,
                "source_urls": [
                    item["url"] for item in audience_sources
                ],
                "likely_audiences": [],
            },
            "worth_attending": worth_attending,
            "findings": relevant_findings,
            "excluded_low_relevance_count": (
                len(findings) - len(relevant_findings)
            ),
            "searches_completed": searches_completed,
            "searches_failed": searches_failed,
            "relevant_findings": len(relevant_findings),
            "limitations": limitations,
        }


research_service = ResearchService()