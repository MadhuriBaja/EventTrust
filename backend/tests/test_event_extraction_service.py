from app.services.event_extraction_service import EventExtractionService


def test_extract_from_url_extracts_title_and_description(monkeypatch):
    """Test extracting title and description from an event webpage."""

    html = """
    <html>
        <head>
            <title>AI Systems Summit 2026</title>
            <meta
                name="description"
                content="A technology summit for AI professionals."
            >
        </head>
        <body>
            <h1>AI Systems Summit 2026</h1>
        </body>
    </html>
    """

    class MockResponse:
        text = html
        url = "https://example.com/event"

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "app.services.event_extraction_service.httpx.get",
        mock_get,
    )

    service = EventExtractionService()

    result = service.extract_from_url(
        "https://example.com/event"
    )

    assert result.event_name == "AI Systems Summit 2026"
    assert result.source_url == "https://example.com/event"
    assert result.description == "A technology summit for AI professionals."
    assert result.organizer is None
    assert result.event_date is None
    assert result.venue is None
    assert result.speakers == []
    assert result.registration_url is None


def test_extract_from_url_uses_og_title_when_page_title_missing(monkeypatch):
    """Test extracting Open Graph title when normal title is missing."""

    html = """
    <html>
        <head>
            <meta property="og:title" content="Tech Conference 2026">
        </head>
        <body>
            <h1>Tech Conference 2026</h1>
        </body>
    </html>
    """

    class MockResponse:
        text = html
        url = "https://example.com/conference"

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "app.services.event_extraction_service.httpx.get",
        mock_get,
    )

    service = EventExtractionService()

    result = service.extract_from_url(
        "https://example.com/conference"
    )

    assert result.event_name == "Tech Conference 2026"
    assert result.source_url == "https://example.com/conference"


def test_extract_from_url_uses_og_description_when_meta_description_missing(
    monkeypatch,
):
    """Test extracting Open Graph description when normal description is missing."""

    html = """
    <html>
        <head>
            <title>Developer Meetup 2026</title>
            <meta
                property="og:description"
                content="A meetup for software developers."
            >
        </head>
        <body>
            <h1>Developer Meetup 2026</h1>
        </body>
    </html>
    """

    class MockResponse:
        text = html
        url = "https://example.com/meetup"

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "app.services.event_extraction_service.httpx.get",
        mock_get,
    )

    service = EventExtractionService()

    result = service.extract_from_url(
        "https://example.com/meetup"
    )

    assert result.event_name == "Developer Meetup 2026"
    assert result.source_url == "https://example.com/meetup"
    assert result.description == "A meetup for software developers."


def test_extract_event_json_ld():
    """Test extracting complete event information from JSON-LD."""

    html = """
    <html>
        <head>
            <title>Fallback Title</title>

            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Event",
                "name": "AI Systems Summit 2026",
                "description": "A major AI technology summit.",
                "startDate": "2026-11-20T09:00:00+05:30",
                "organizer": {
                    "@type": "Organization",
                    "name": "Tech Events India"
                },
                "location": {
                    "@type": "Place",
                    "name": "Hyderabad Convention Centre"
                },
                "performer": [
                    {
                        "@type": "Person",
                        "name": "Dr. Ravi Kumar"
                    },
                    {
                        "@type": "Person",
                        "name": "Anita Sharma"
                    }
                ],
                "offers": {
                    "@type": "Offer",
                    "url": "https://example.com/register"
                }
            }
            </script>
        </head>
    </html>
    """

    soup = EventExtractionService

    from bs4 import BeautifulSoup

    parsed_html = BeautifulSoup(html, "html.parser")

    result = soup._extract_event_json_ld(parsed_html)

    assert result is not None
    assert result["event_name"] == "AI Systems Summit 2026"
    assert result["organizer"] == "Tech Events India"
    assert result["event_date"] == "2026-11-20T09:00:00+05:30"
    assert result["venue"] == "Hyderabad Convention Centre"
    assert result["speakers"] == [
        "Dr. Ravi Kumar",
        "Anita Sharma",
    ]
    assert result["registration_url"] == "https://example.com/register"
    assert result["description"] == "A major AI technology summit."


def test_extract_from_url_builds_complete_event_profile(monkeypatch):
    """Test that JSON-LD data is stored in EventProfile."""

    html = """
    <html>
        <head>
            <title>Fallback Event Title</title>

            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Event",
                "name": "Tech Conference 2026",
                "description": "Technology conference.",
                "startDate": "2026-12-15",
                "organizer": {
                    "@type": "Organization",
                    "name": "Example Technologies"
                },
                "location": {
                    "@type": "Place",
                    "name": "HICC Hyderabad"
                },
                "performer": {
                    "@type": "Person",
                    "name": "Priya Rao"
                },
                "offers": {
                    "@type": "Offer",
                    "url": "https://example.com/tickets"
                }
            }
            </script>
        </head>
    </html>
    """

    class MockResponse:
        text = html
        url = "https://example.com/tech-conference"

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "app.services.event_extraction_service.httpx.get",
        mock_get,
    )

    service = EventExtractionService()

    result = service.extract_from_url(
        "https://example.com/tech-conference"
    )

    assert result.event_name == "Tech Conference 2026"
    assert result.organizer == "Example Technologies"
    assert result.event_date == "2026-12-15"
    assert result.venue == "HICC Hyderabad"
    assert result.speakers == ["Priya Rao"]
    assert result.registration_url == "https://example.com/tickets"
    assert result.source_url == "https://example.com/tech-conference"
    assert result.description == "Technology conference."