"use client";

import { useState } from "react";
import {
  createInvestigation,
  runResearch,
  type InvestigationResponse,
  type ResearchReport,
  type ResearchFinding,
} from "@/lib/api";

function Icon({
  name,
  size = 18,
}: {
  name: string;
  size?: number;
}) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.7,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true as const,
  };

  switch (name) {
    case "grid":
      return (
        <svg {...common}>
          <rect x="3" y="3" width="7" height="7" rx="1.5" />
          <rect x="14" y="3" width="7" height="7" rx="1.5" />
          <rect x="3" y="14" width="7" height="7" rx="1.5" />
          <rect x="14" y="14" width="7" height="7" rx="1.5" />
        </svg>
      );

    case "search":
      return (
        <svg {...common}>
          <circle cx="10.8" cy="10.8" r="6.8" />
          <path d="m16 16 4.5 4.5" />
        </svg>
      );

    case "shield":
      return (
        <svg {...common}>
          <path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z" />
          <path d="m9 12 2 2 4-4" />
        </svg>
      );

    case "activity":
      return (
        <svg {...common}>
          <path d="M3 12h4l3-8 4 16 3-8h4" />
        </svg>
      );

    case "settings":
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="3" />
          <path d="m19.4 15 .1.1 1.1.9-1.2 2.1-1.4-.5a8 8 0 0 1-1.7 1l-.3 1.5h-2.5l-.3-1.5a8 8 0 0 1-1.7-1l-1.4.5-1.2-2.1 1.1-.9a7 7 0 0 1 0-2l-1.1-.9 1.2-2.1 1.4.5a8 8 0 0 1 1.7-1l.3-1.5h2.5l.3 1.5a8 8 0 0 1 1.7 1l1.4-.5 1.2 2.1-1.1.9a7 7 0 0 1-.1 2Z" />
        </svg>
      );

    case "arrow":
      return (
        <svg {...common}>
          <path d="M5 12h14" />
          <path d="m13 6 6 6-6 6" />
        </svg>
      );

    case "link":
      return (
        <svg {...common}>
          <path d="M10 13a5 5 0 0 0 7.1 0l3-3A5 5 0 0 0 13 2.9l-1.7 1.7" />
          <path d="M14 11a5 5 0 0 0-7.1 0l-3 3A5 5 0 0 0 11 21.1l1.7-1.7" />
        </svg>
      );

    case "clock":
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v5l3 2" />
        </svg>
      );

    case "check":
      return (
        <svg {...common}>
          <path d="m5 12 4 4L19 6" />
        </svg>
      );

    case "external":
      return (
        <svg {...common}>
          <path d="M14 3h7v7" />
          <path d="m21 3-10 10" />
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
        </svg>
      );

    case "plus":
      return (
        <svg {...common}>
          <path d="M12 5v14M5 12h14" />
        </svg>
      );

    case "file":
      return (
        <svg {...common}>
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" />
          <path d="M14 2v6h6M8 13h8M8 17h8" />
        </svg>
      );

    case "globe":
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="9" />
          <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" />
        </svg>
      );

    default:
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="9" />
          <path d="M12 8v4M12 16h.01" />
        </svg>
      );
  }
}

function formatDate(value?: string | null): string {
  if (!value) return "Not confirmed";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatAssessment(value?: string | null): string {
  if (!value) return "Assessment pending";

  return value
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function getAssessmentClass(value?: string | null): string {
  const assessment = (value || "").toLowerCase();

  if (
    assessment.includes("verified") ||
    assessment.includes("trustworthy") ||
    assessment.includes("low risk")
  ) {
    return "assessment-positive";
  }

  if (
    assessment.includes("high risk") ||
    assessment.includes("suspicious") ||
    assessment.includes("unsafe")
  ) {
    return "assessment-caution";
  }

  return "assessment-review";
}

/**
 * ResearchFinding does not guarantee a `score` property.
 * Use only optional metadata that is explicitly checked here.
 */
function getRelevanceLevel(finding: ResearchFinding): string {
  const extra = finding as ResearchFinding & {
    relevance?: unknown;
    relevance_score?: unknown;
  };

  const value = String(extra.relevance ?? "").toLowerCase();

  if (value.includes("high")) return "high";
  if (value.includes("low")) return "low";

  const score = Number(extra.relevance_score ?? 0);

  if (score >= 70) return "high";
  if (score > 0 && score < 30) return "low";

  return "medium";
}

function getDisplayDomain(value?: string | null): string {
  if (!value) return "Source";

  try {
    return new URL(value).hostname.replace(/^www\./, "");
  } catch {
    return value;
  }
}

function FindingCard({ finding }: { finding: ResearchFinding }) {
  const level = getRelevanceLevel(finding);

  const extra = finding as ResearchFinding & {
    category?: string;
    source_url?: string;
    url?: string;
    source?: string;
    relevance_score?: number;
  };

  const sourceUrl =
    extra.source_url || extra.url || extra.source || "";

  const score =
    typeof extra.relevance_score === "number"
      ? extra.relevance_score
      : null;

  return (
    <article className="finding-card">
      <div className="finding-topline">
        <span className="finding-category">
          {extra.category || "Research finding"}
        </span>

        <span className={`relevance-label relevance-${level}`}>
          <span className="relevance-dot" />
          {level} relevance
        </span>
      </div>

      <h3 className="finding-title">
        {finding.title || "Untitled finding"}
      </h3>

      <p className="finding-snippet">
        {finding.snippet ||
          "No additional description was provided for this finding."}
      </p>

      <div className="finding-bottom">
        <div className="finding-meta">
          <Icon name="globe" size={14} />
          <span>{getDisplayDomain(sourceUrl)}</span>

          {score !== null && (
            <>
              <span className="meta-separator">·</span>
              <span>Score {score}</span>
            </>
          )}
        </div>

        {sourceUrl && (
          <a
            className="result-link"
            href={sourceUrl}
            target="_blank"
            rel="noreferrer"
          >
            Open source <Icon name="external" size={14} />
          </a>
        )}
      </div>
    </article>
  );
}

export default function Home() {
  const [eventName, setEventName] = useState("");
  const [eventUrl, setEventUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [researchError, setResearchError] = useState("");

  const [investigation, setInvestigation] =
    useState<InvestigationResponse | null>(null);

  const [researchReport, setResearchReport] =
    useState<ResearchReport | null>(null);

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setErrorMessage("");
    setResearchError("");
    setInvestigation(null);
    setResearchReport(null);

    const name = eventName.trim();
    const url = eventUrl.trim();

    if (!name && !url) {
      setErrorMessage(
        "Enter an event name or event URL to begin."
      );
      return;
    }

    if (url) {
      try {
        const parsedUrl = new URL(url);

        if (
          !["http:", "https:"].includes(parsedUrl.protocol)
        ) {
          setErrorMessage(
            "Please enter a valid HTTP or HTTPS event URL."
          );
          return;
        }
      } catch {
        setErrorMessage(
          "Please enter a valid event URL, including https://."
        );
        return;
      }
    }

    setIsLoading(true);

    try {
      const result = await createInvestigation({
        event_name: name || undefined,
        event_url: url || undefined,
      });

      setInvestigation(result);

      try {
        const report = await runResearch(
          result.investigation_id
        );

        setResearchReport(report);
      } catch (error) {
        setResearchError(
          error instanceof Error
            ? error.message
            : "Research could not be completed. Please try again."
        );
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Could not start the investigation. Check that the backend is running."
      );
    } finally {
      setIsLoading(false);
    }
  }

  function resetInvestigation() {
    setEventName("");
    setEventUrl("");
    setErrorMessage("");
    setResearchError("");
    setInvestigation(null);
    setResearchReport(null);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  const eventProfile = investigation?.event_profile;
  const findings = researchReport?.findings ?? [];

  const sortedFindings = [...findings].sort((a, b) => {
    const order = {
      high: 0,
      medium: 1,
      low: 2,
    };

    return (
      order[
        getRelevanceLevel(a) as keyof typeof order
      ] -
      order[
        getRelevanceLevel(b) as keyof typeof order
      ]
    );
  });

  const highCount = findings.filter(
    (finding) => getRelevanceLevel(finding) === "high"
  ).length;

  const mediumCount = findings.filter(
    (finding) => getRelevanceLevel(finding) === "medium"
  ).length;

  const lowCount = findings.filter(
    (finding) => getRelevanceLevel(finding) === "low"
  ).length;

  const limitations = (
    researchReport?.limitations ?? []
  ).filter(
    (item) =>
      typeof item === "string" &&
      item.trim().length > 0
  );

  const failedSearches = (
    researchReport?.failed_searches ?? []
  ).filter(
    (item) =>
      typeof item === "string" &&
      item.trim().length > 0
  );

  const profile = eventProfile as
    | (NonNullable<typeof eventProfile> & {
        event_name?: string | null;
        organizer?: string | null;
        event_date?: string | null;
        venue?: string | null;
        registration_url?: string | null;
        source_url?: string | null;
        description?: string | null;
        speakers?: string[] | null;
      })
    | undefined;

  const assessment = researchReport?.assessment;

  const displayedEventName =
    profile?.event_name ||
    eventName.trim() ||
    "Untitled event";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#overview"
          aria-label="EventTrust home"
        >
          <span className="brand-mark">
            <Icon name="shield" size={23} />
            <span className="brand-mark-dot" />
          </span>

          <span className="brand-name">
            Event<span>Trust</span>
          </span>
        </a>

        <div className="sidebar-divider" />

        <p className="nav-caption">WORKSPACE</p>

        <nav
          className="side-nav"
          aria-label="Main navigation"
        >
          <a className="nav-item active" href="#overview">
            <Icon name="grid" />
            <span>Overview</span>
            <span className="nav-active-mark" />
          </a>

          <a className="nav-item" href="#investigate">
            <Icon name="search" />
            <span>Investigate event</span>
          </a>

          <a className="nav-item" href="#results">
            <Icon name="file" />
            <span>Research report</span>
          </a>
        </nav>

        <p className="nav-caption nav-caption-spaced">
          SYSTEM
        </p>

        <div className="side-nav">
          <div className="nav-item nav-static">
            <Icon name="activity" />
            <span>Research engine</span>
          </div>

          <div className="nav-item nav-static">
            <Icon name="shield" />
            <span>Evidence review</span>
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <span className="live-dot" />

            <div>
              <strong>Workspace ready</strong>
              <span>Event intelligence</span>
            </div>
          </div>

          <div className="sidebar-footer">
            <span className="sidebar-footer-mark">ET</span>

            <div>
              <strong>EventTrust</strong>
              <span>Research workspace</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-panel" id="overview">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Workspace</span>
            <span className="crumb-slash">/</span>
            <strong>Overview</strong>
          </div>

          <div className="topbar-right">
            <span className="environment-pill">
              <span className="live-dot" />
              Local environment
            </span>

            <div
              className="avatar"
              aria-label="EventTrust workspace"
            >
              ET
            </div>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome-row">
            <div className="welcome-copy">
              <div className="eyebrow">
                <span className="eyebrow-line" />
                EVENT INTELLIGENCE PLATFORM
              </div>

              <h1>
                Trust, backed by
                <br className="mobile-break" />{" "}
                <span>evidence.</span>
              </h1>

              <p className="hero-copy">
                Investigate events, discover supporting
                sources, and review the available evidence
                before you decide to trust an event.
              </p>

              <div className="hero-points">
                <span>
                  <Icon name="check" size={15} />
                  Source-linked findings
                </span>

                <span>
                  <Icon name="check" size={15} />
                  Evidence-first review
                </span>
              </div>
            </div>

            <div
              className="hero-emblem"
              aria-hidden="true"
            >
              <div className="emblem-orbit orbit-one" />
              <div className="emblem-orbit orbit-two" />
              <div className="emblem-orbit orbit-three" />

              <div className="emblem-core">
                <Icon name="shield" size={48} />
              </div>

              <span className="emblem-node node-one" />
              <span className="emblem-node node-two" />
              <span className="emblem-node node-three" />
              <span className="emblem-node node-four" />
            </div>
          </section>

          <section
            className="metrics-grid"
            aria-label="Workspace overview"
          >
            <article className="metric-card">
              <div className="metric-top">
                <span className="metric-icon cyan">
                  <Icon name="search" />
                </span>

                <span className="metric-trend">
                  WORKSPACE
                </span>
              </div>

              <div className="metric-value">01</div>

              <div className="metric-label">
                Investigation workspace
              </div>

              <div className="metric-foot">
                Start with an event name or URL
              </div>
            </article>

            <article className="metric-card">
              <div className="metric-top">
                <span className="metric-icon blue">
                  <Icon name="globe" />
                </span>

                <span className="metric-trend">
                  RESEARCH
                </span>
              </div>

              <div className="metric-value">
                {researchReport
                  ? findings.length
                      .toString()
                      .padStart(2, "0")
                  : "--"}
              </div>

              <div className="metric-label">
                Research findings
              </div>

              <div className="metric-foot">
                {researchReport
                  ? "Findings returned for this investigation"
                  : "Sources are reviewed after research"}
              </div>
            </article>

            <article className="metric-card">
              <div className="metric-top">
                <span className="metric-icon violet">
                  <Icon name="shield" />
                </span>

                <span className="metric-trend">
                  ASSESSMENT
                </span>
              </div>

              <div className="metric-value metric-value-text">
                {researchReport ? "Ready" : "Evidence"}
              </div>

              <div className="metric-label">
                Evidence review
              </div>

              <div className="metric-foot">
                {researchReport
                  ? "Review the assessment and its sources"
                  : "No unsupported trust guarantees"}
              </div>
            </article>
          </section>

          <section
            className="workspace-grid"
            id="investigate"
          >
            <article className="panel investigation-panel">
              <div className="panel-heading">
                <div className="panel-icon">
                  <Icon name="search" size={19} />
                </div>

                <div>
                  <p className="section-kicker">
                    START AN INVESTIGATION
                  </p>

                  <h2>Investigate an event</h2>

                  <p className="panel-subtitle">
                    Give us a starting point. We’ll gather the
                    available event details and research
                    evidence.
                  </p>
                </div>
              </div>

              <form
                className="investigation-form"
                onSubmit={handleSubmit}
              >
                <div className="form-field">
                  <label htmlFor="eventName">
                    Event name{" "}
                    <span className="optional-label">
                      OPTIONAL
                    </span>
                  </label>

                  <input
                    id="eventName"
                    type="text"
                    placeholder="e.g. AI Systems Summit"
                    value={eventName}
                    onChange={(event) =>
                      setEventName(event.target.value)
                    }
                    autoComplete="off"
                  />

                  <p className="field-hint">
                    Add the name to help identify the right
                    event.
                  </p>
                </div>

                <div className="field-divider">
                  <span>AND / OR</span>
                </div>

                <div className="form-field">
                  <label htmlFor="eventUrl">
                    Event URL{" "}
                    <span className="optional-label">
                      OPTIONAL
                    </span>
                  </label>

                  <div className="url-input-wrap">
                    <span className="url-input-icon">
                      <Icon name="link" size={17} />
                    </span>

                    <input
                      id="eventUrl"
                      type="url"
                      placeholder="https://example.com/event"
                      value={eventUrl}
                      onChange={(event) =>
                        setEventUrl(event.target.value)
                      }
                      autoComplete="url"
                    />
                  </div>

                  <p className="field-hint">
                    Paste the official page or event
                    registration link.
                  </p>
                </div>

                {errorMessage && (
                  <div
                    className="error-banner"
                    role="alert"
                  >
                    <span className="error-symbol">!</span>
                    <span>{errorMessage}</span>
                  </div>
                )}

                <button
                  className="primary-button"
                  type="submit"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <span className="spinner" />
                      Research in progress...
                    </>
                  ) : (
                    <>
                      Begin investigation
                      <Icon name="arrow" size={18} />
                    </>
                  )}
                </button>

                <div className="form-security">
                  <Icon name="shield" size={15} />

                  <span>
                    Research supports your decision; it does
                    not guarantee an event’s legitimacy.
                  </span>
                </div>
              </form>
            </article>

            <article className="panel activity-panel">
              <div className="panel-heading compact-heading">
                <div className="panel-icon muted-icon">
                  <Icon name="activity" size={19} />
                </div>

                <div>
                  <p className="section-kicker">
                    HOW IT WORKS
                  </p>

                  <h2>Research workflow</h2>

                  <p className="panel-subtitle">
                    From event details to evidence you can
                    review.
                  </p>
                </div>
              </div>

              <div className="flow-list">
                <div className="flow-step">
                  <div className="flow-marker complete">
                    <Icon name="check" size={15} />
                  </div>

                  <div className="flow-content">
                    <strong>Identify the event</strong>
                    <p>
                      Use the event name or registration URL.
                    </p>
                  </div>

                  <span className="flow-state ready">
                    STEP 01
                  </span>
                </div>

                <div className="flow-connector" />

                <div className="flow-step">
                  <div className="flow-marker">
                    <Icon name="globe" size={15} />
                  </div>

                  <div className="flow-content">
                    <strong>Gather evidence</strong>
                    <p>
                      Search for details and related sources.
                    </p>
                  </div>

                  <span className="flow-state">
                    STEP 02
                  </span>
                </div>

                <div className="flow-connector" />

                <div className="flow-step">
                  <div className="flow-marker">
                    <Icon name="file" size={15} />
                  </div>

                  <div className="flow-content">
                    <strong>Review findings</strong>
                    <p>
                      Inspect source links and research
                      limitations.
                    </p>
                  </div>

                  <span className="flow-state">
                    STEP 03
                  </span>
                </div>
              </div>

              <div className="notice-card">
                <span className="notice-icon">
                  <Icon name="shield" size={18} />
                </span>

                <div>
                  <strong>Evidence over assumptions</strong>

                  <p>
                    Missing information is not proof of fraud.
                    Always review the source material and
                    confirm critical details directly.
                  </p>
                </div>
              </div>

              <div className="activity-foot">
                <span className="live-dot" />
                <span>Ready when you are</span>
              </div>
            </article>
          </section>

          <section
            className="results-section"
            id="results"
          >
            <div className="results-heading">
              <div>
                <p className="section-kicker">
                  INVESTIGATION OUTPUT
                </p>

                <h2>Research report</h2>

                <p className="results-description">
                  Event details, assessment, source-linked
                  findings, and limitations in one place.
                </p>
              </div>

              {(investigation || researchReport) && (
                <button
                  className="secondary-button"
                  type="button"
                  onClick={resetInvestigation}
                >
                  <Icon name="plus" size={16} />
                  New investigation
                </button>
              )}
            </div>

            {!investigation &&
              !researchReport &&
              !isLoading && (
                <div className="empty-state">
                  <div className="empty-icon">
                    <Icon name="file" size={28} />
                  </div>

                  <div className="empty-state-content">
                    <h3>Your report will appear here</h3>

                    <p>
                      Enter an event name or URL above to
                      begin. Your report will appear here
                      after the research workflow completes.
                    </p>
                  </div>

                  <a
                    className="text-link"
                    href="#investigate"
                  >
                    Start an investigation{" "}
                    <Icon name="arrow" size={16} />
                  </a>
                </div>
              )}

            {isLoading && (
              <div className="loading-state">
                <span className="loading-ring" />

                <div>
                  <h3>Investigating your event</h3>

                  <p>
                    Gathering event details and researching
                    available evidence. This may take a
                    little while.
                  </p>
                </div>
              </div>
            )}

            {investigation && (
              <article className="case-result">
                <div className="case-header">
                  <div className="case-symbol">
                    <Icon name="file" size={23} />
                  </div>

                  <div className="case-heading-copy">
                    <p className="section-kicker">
                      EVENT RECORD
                    </p>

                    <h3 className="case-title">
                      {displayedEventName}
                    </h3>

                    <p className="case-subtitle">
                      Investigation ID:{" "}
                      <code>
                        {investigation.investigation_id}
                      </code>
                    </p>
                  </div>

                  <span className="record-badge">
                    <span className="live-dot" />
                    Record created
                  </span>
                </div>

                {profile?.description && (
                  <p className="case-description">
                    {profile.description}
                  </p>
                )}

                <div className="case-fields">
                  <div className="case-field">
                    <span>Organizer</span>
                    <strong>
                      {profile?.organizer || "Not confirmed"}
                    </strong>
                  </div>

                  <div className="case-field">
                    <span>Event date</span>
                    <strong>
                      {formatDate(profile?.event_date)}
                    </strong>
                  </div>

                  <div className="case-field">
                    <span>Venue</span>
                    <strong>
                      {profile?.venue || "Not confirmed"}
                    </strong>
                  </div>

                  <div className="case-field">
                    <span>Research status</span>
                    <strong>
                      {researchReport
                        ? "Research completed"
                        : researchError
                          ? "Research needs attention"
                          : "Preparing report"}
                    </strong>
                  </div>
                </div>

                {(
                  profile?.registration_url ||
                  profile?.source_url ||
                  eventUrl
                ) && (
                  <div className="source-row">
                    <span className="source-row-icon">
                      <Icon name="link" size={16} />
                    </span>

                    <div className="source-row-content">
                      <span>Event source</span>

                      <a
                        href={
                          profile?.registration_url ||
                          profile?.source_url ||
                          eventUrl
                        }
                        target="_blank"
                        rel="noreferrer"
                      >
                        {getDisplayDomain(
                          profile?.registration_url ||
                            profile?.source_url ||
                            eventUrl
                        )}

                        <Icon name="external" size={14} />
                      </a>
                    </div>
                  </div>
                )}

                {profile?.speakers &&
                  profile.speakers.length > 0 && (
                    <div className="speakers-block">
                      <span className="field-label">
                        Speakers
                      </span>

                      <div className="speaker-tags">
                        {profile.speakers.map(
                          (speaker, index) => (
                            <span
                              className="speaker-tag"
                              key={`${speaker}-${index}`}
                            >
                              {speaker}
                            </span>
                          )
                        )}
                      </div>
                    </div>
                  )}
              </article>
            )}

            {researchError && (
              <div
                className="error-banner research-error"
                role="alert"
              >
                <span className="error-symbol">!</span>

                <div>
                  <strong>
                    Research could not be completed
                  </strong>

                  <p>{researchError}</p>
                </div>
              </div>
            )}

            {researchReport && (
              <>
                <section className="research-panel">
                  <div className="report-summary">
                    <div className="report-summary-top">
                      <div>
                        <p className="section-kicker">
                          CURRENT ASSESSMENT
                        </p>

                        <h3>
                          {formatAssessment(assessment)}
                        </h3>
                      </div>

                      <span
                        className={`assessment-label ${getAssessmentClass(
                          assessment
                        )}`}
                      >
                        <Icon name="shield" size={16} />
                        Evidence review
                      </span>
                    </div>

                    <p className="report-summary-copy">
                      The assessment reflects the evidence
                      currently available in this report. It
                      is not a guarantee of legitimacy or a
                      definitive fraud determination.
                    </p>
                  </div>

                  <div className="report-counts">
                    <div className="report-count-card">
                      <span className="report-count-icon count-total">
                        <Icon name="file" size={17} />
                      </span>

                      <div>
                        <strong className="report-count-value">
                          {findings.length}
                        </strong>

                        <span className="report-count-label">
                          Total findings
                        </span>
                      </div>
                    </div>

                    <div className="report-count-card">
                      <span className="report-count-icon count-high">
                        <span className="relevance-dot" />
                      </span>

                      <div>
                        <strong className="report-count-value">
                          {highCount}
                        </strong>

                        <span className="report-count-label">
                          High relevance
                        </span>
                      </div>
                    </div>

                    <div className="report-count-card">
                      <span className="report-count-icon count-medium">
                        <span className="relevance-dot" />
                      </span>

                      <div>
                        <strong className="report-count-value">
                          {mediumCount}
                        </strong>

                        <span className="report-count-label">
                          Medium relevance
                        </span>
                      </div>
                    </div>

                    <div className="report-count-card">
                      <span className="report-count-icon count-low">
                        <span className="relevance-dot" />
                      </span>

                      <div>
                        <strong className="report-count-value">
                          {lowCount}
                        </strong>

                        <span className="report-count-label">
                          Low relevance
                        </span>
                      </div>
                    </div>
                  </div>
                </section>

                <section className="findings-section">
                  <div className="findings-heading">
                    <div>
                      <p className="section-kicker">
                        SOURCE-BACKED RESEARCH
                      </p>

                      <h3>Findings</h3>

                      <p>
                        Review each item and open its source
                        to verify the original context.
                      </p>
                    </div>

                    <span className="findings-total">
                      {findings.length}{" "}
                      {findings.length === 1
                        ? "finding"
                        : "findings"}
                    </span>
                  </div>

                  {sortedFindings.length > 0 ? (
                    <div className="research-findings">
                      {sortedFindings
                        .filter(
                          (finding) =>
                            getRelevanceLevel(finding) !==
                            "low"
                        )
                        .map((finding, index) => (
                          <FindingCard
                            finding={finding}
                            key={`${finding.title}-${index}`}
                          />
                        ))}

                      {sortedFindings.some(
                        (finding) =>
                          getRelevanceLevel(finding) ===
                          "low"
                      ) && (
                        <details className="low-relevance-details">
                          <summary>
                            <span>
                              Show low-relevance findings (
                              {lowCount})
                            </span>

                            <span className="details-chevron">
                              ⌄
                            </span>
                          </summary>

                          <div className="low-relevance-list">
                            {sortedFindings
                              .filter(
                                (finding) =>
                                  getRelevanceLevel(
                                    finding
                                  ) === "low"
                              )
                              .map((finding, index) => (
                                <FindingCard
                                  finding={finding}
                                  key={`low-${finding.title}-${index}`}
                                />
                              ))}
                          </div>
                        </details>
                      )}
                    </div>
                  ) : (
                    <div className="no-findings">
                      <span className="empty-icon">
                        <Icon name="search" size={23} />
                      </span>

                      <div>
                        <h4>No findings were returned</h4>

                        <p>
                          The research workflow did not
                          return findings for this
                          investigation. Check the
                          limitations below before drawing
                          conclusions.
                        </p>
                      </div>
                    </div>
                  )}
                </section>

                {(limitations.length > 0 ||
                  failedSearches.length > 0) && (
                  <details className="limitations-panel">
                    <summary>
                      <span className="limitations-summary-icon">
                        <Icon name="activity" size={17} />
                      </span>

                      <span className="limitations-summary-copy">
                        <strong>Research limitations</strong>

                        <small>
                          Review unavailable searches and
                          evidence gaps.
                        </small>
                      </span>

                      <span className="limitations-count">
                        {limitations.length +
                          failedSearches.length}{" "}
                        items
                      </span>

                      <span className="details-chevron">
                        ⌄
                      </span>
                    </summary>

                    <div className="limitations-content">
                      {limitations.length > 0 && (
                        <div>
                          <h4>Limitations</h4>

                          <ul>
                            {limitations.map(
                              (item, index) => (
                                <li key={`limitation-${index}`}>
                                  {item}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}

                      {failedSearches.length > 0 && (
                        <div>
                          <h4>
                            Searches that did not complete
                          </h4>

                          <ul>
                            {failedSearches.map(
                              (item, index) => (
                                <li key={`failed-${index}`}>
                                  {item}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  </details>
                )}

                <div className="result-disclaimer">
                  <Icon name="shield" size={18} />

                  <p>
                    <strong>Use independent judgment.</strong>{" "}
                    Findings depend on available sources and
                    search coverage. An absence of evidence
                    is not proof that an event is
                    fraudulent, and positive evidence is
                    not a guarantee that it is safe.
                  </p>
                </div>
              </>
            )}
          </section>

          <footer className="page-footer">
            <div className="footer-brand">
              <span className="footer-brand-icon">
                <Icon name="shield" size={15} />
              </span>

              <span>EventTrust</span>
            </div>

            <span className="footer-separator">·</span>
            <span>Evidence-led event research</span>

            <span className="footer-right">
              Built for clearer decisions
            </span>
          </footer>
        </div>
      </main>
    </div>
  );
}