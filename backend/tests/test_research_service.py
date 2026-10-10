
from app.models.event import EventProfile
from app.services.research_service import ResearchService


class FakeSearchClient:
    def __init__(self, responses=None, fail_queries=None):
        self.responses = responses or {}
        self.fail_queries = fail_queries or []
        self.queries = []

    def search(self, query):
        self.queries.append(query)

        if any(term in query for term in self.fail_queries):
            raise RuntimeError("Simulated search failure")

        return self.responses.get(query, {"organic_results": []})


def test_report_includes_relevant_source_linked_findings():
    client = FakeSearchClient(
        responses={
            '"AI Systems Summit 2026" Example Organizer official event agenda date venue': {
                "organic_results": [
                    {
                        "title": "AI Systems Summit 2026",
                        "link": "https://example.org/event",
                        "snippet": (
                            "AI Systems Summit 2026 is organized by "
                            "Example Organizer."
                        ),
                    }
                ]
            },
            '"AI Systems Summit 2026" attendee reviews previous edition experiences': {
                "organic_results": [
                    {
                        "title": "AI Systems Summit 2026 attendee discussion",
                        "link": "https://example.net/discussion",
                        "snippet": (
                            "Attendees discuss their experience at "
                            "AI Systems Summit 2026."
                        ),
                    }
                ]
            },
        }
    )

    service = ResearchService(search_client=client)
    report = service.build_report(
        "AI Systems Summit 2026",
        EventProfile(
            event_name="AI Systems Summit 2026",
            organizer="Example Organizer",
        ),
    )

    assert report["assessment"] == "investigate_further"
    assert report["searches_completed"] == 4
    assert len(report["findings"]) == 2
    assert report["findings"][0]["url"] == "https://example.org/event"
    assert report["findings"][0]["relevance"] == "high"
    assert report["findings"][0]["review_status"] == "not_independently_verified"
    assert report["findings"][1]["category"] == "public_reviews"
    assert report["relevant_findings"] == 2
    assert report["past_reviews"]["status"] == "possible_reviews_found"
    assert report["worth_attending"]["recommendation"] == "not_enough_evidence"
    assert report["limitations"]


def test_report_handles_no_search_results():
    service = ResearchService(search_client=FakeSearchClient())

    report = service.build_report("Unknown Event")

    assert report["assessment"] == "insufficient_evidence"
    assert report["findings"] == []
    assert report["searches_failed"] == 0
    assert "not enough relevant" in report["summary"].lower()
    assert report["past_reviews"]["status"] == "not_found"
    assert report["audience_fit"]["status"] == "insufficient_evidence"


def test_report_handles_search_failure():
    client = FakeSearchClient(
        fail_queries=["Unknown Event"]
    )
    service = ResearchService(search_client=client)

    report = service.build_report("Unknown Event")

    assert report["assessment"] == "insufficient_evidence"
    assert report["searches_failed"] == 3
    assert report["findings"] == []
    assert any(
        "failed" in item.lower()
        for item in report["limitations"]
    )


def test_report_skips_venue_and_organizer_search_when_unknown():
    client = FakeSearchClient()
    service = ResearchService(search_client=client)

    service.build_report("Unknown Event")

    assert len(client.queries) == 3
    assert all("past events attendee feedback" not in q for q in client.queries)
    assert all("address directions event venue" not in q for q in client.queries)


def test_unrelated_result_is_excluded_from_primary_findings():
    client = FakeSearchClient(
        responses={
            '"AI Systems Summit 2026" attendee reviews previous edition experiences': {
                "organic_results": [
                    {
                        "title": "Cooking Festival",
                        "link": "https://example.org/cooking",
                        "snippet": "Food, music, and a weekend market.",
                    }
                ]
            }
        }
    )

    report = ResearchService(search_client=client).build_report(
        "AI Systems Summit 2026"
    )

    assert report["findings"] == []
    assert report["relevant_findings"] == 0
    assert report["excluded_low_relevance_count"] == 1
    assert report["assessment"] == "insufficient_evidence"


def test_duplicate_urls_are_removed():
    duplicate_result = {
        "title": "AI Systems Summit 2026",
        "link": "https://example.org/event",
        "snippet": "AI Systems Summit 2026 technology conference.",
    }
    client = FakeSearchClient(
        responses={
            '"AI Systems Summit 2026" Example Organizer official event agenda date venue': {
                "organic_results": [duplicate_result]
            },
            '"AI Systems Summit 2026" attendee reviews previous edition experiences': {
                "organic_results": [
                    {
                        **duplicate_result,
                        "link": "https://example.org/event/",
                    }
                ]
            },
        }
    )

    report = ResearchService(search_client=client).build_report(
        "AI Systems Summit 2026",
        EventProfile(organizer="Example Organizer"),
    )

    assert len(report["findings"]) == 1


def test_review_like_source_is_not_claimed_as_verified():
    client = FakeSearchClient(
        responses={
            '"AI Systems Summit 2026" attendee reviews previous edition experiences': {
                "organic_results": [
                    {
                        "title": "My experience at AI Systems Summit 2026",
                        "link": "https://example.net/my-experience",
                        "snippet": (
                            "I attended AI Systems Summit 2026 and learned "
                            "a lot from the speakers."
                        ),
                    }
                ]
            }
        }
    )

    report = ResearchService(search_client=client).build_report(
        "AI Systems Summit 2026"
    )

    assert len(report["findings"]) == 1
    assert report["findings"][0]["evidence_type"] == "possible_attendee_review"
    assert report["findings"][0]["review_status"] == "review_like_not_verified"
    assert report["past_reviews"]["status"] == "possible_reviews_found"