"use client";

import { useState } from "react";
import {
  createInvestigation,
  type InvestigationResponse,
} from "@/lib/api";

export default function Home() {
  const [eventName, setEventName] = useState("");
  const [eventUrl, setEventUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const trimmedName = eventName.trim();
    const trimmedUrl = eventUrl.trim();

    if (!trimmedName && !trimmedUrl) {
      setErrorMessage("Please provide at least an event name or an event URL.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await createInvestigation({
        event_name: trimmedName || undefined,
        event_url: trimmedUrl || undefined,
      });
      setInvestigation(response);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("An unexpected error occurred while submitting the investigation.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setInvestigation(null);
    setErrorMessage(null);
    setEventName("");
    setEventUrl("");
  };

  return (
    <div style={{ minHeight: "100vh", padding: "2.5rem 1rem", display: "flex", justifyContent: "center" }}>
      <div style={{ maxWidth: "680px", width: "100%", display: "flex", flexDirection: "column", gap: "1.75rem" }}>
        {/* Header */}
        <header>
          <h1 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "0.5rem" }}>EventTrust</h1>
          <p style={{ opacity: 0.85, fontSize: "1rem", lineHeight: 1.5 }}>
            Evidence-based pre-registration investigation agent for unfamiliar technical, academic, and professional events.
          </p>
        </header>

        {/* Input Form Card */}
        <section
          style={{
            border: "1px solid rgba(128, 128, 128, 0.25)",
            borderRadius: "8px",
            padding: "1.5rem",
            display: "flex",
            flexDirection: "column",
            gap: "1.25rem",
            backgroundColor: "rgba(128, 128, 128, 0.04)",
          }}
        >
          <h2 style={{ fontSize: "1.25rem", fontWeight: 600 }}>Start an Investigation</h2>
          <p style={{ fontSize: "0.9rem", opacity: 0.8 }}>
            Enter an event name, an event URL, or both to begin verification.
          </p>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
              <label htmlFor="eventName" style={{ fontSize: "0.9rem", fontWeight: 500 }}>
                Event Name
              </label>
              <input
                id="eventName"
                type="text"
                value={eventName}
                onChange={(e) => {
                  setEventName(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                placeholder="e.g. International Conference on Machine Learning & Robotics"
                disabled={isLoading}
                style={{
                  padding: "0.6rem 0.8rem",
                  borderRadius: "6px",
                  border: "1px solid rgba(128, 128, 128, 0.4)",
                  fontSize: "0.95rem",
                  background: "transparent",
                  color: "inherit",
                }}
              />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
              <label htmlFor="eventUrl" style={{ fontSize: "0.9rem", fontWeight: 500 }}>
                Event URL
              </label>
              <input
                id="eventUrl"
                type="url"
                value={eventUrl}
                onChange={(e) => {
                  setEventUrl(e.target.value);
                  if (errorMessage) setErrorMessage(null);
                }}
                placeholder="https://example-event.org"
                disabled={isLoading}
                style={{
                  padding: "0.6rem 0.8rem",
                  borderRadius: "6px",
                  border: "1px solid rgba(128, 128, 128, 0.4)",
                  fontSize: "0.95rem",
                  background: "transparent",
                  color: "inherit",
                }}
              />
            </div>

            {/* Validation / Error State */}
            {errorMessage && (
              <div
                role="alert"
                style={{
                  backgroundColor: "rgba(239, 68, 68, 0.1)",
                  border: "1px solid rgba(239, 68, 68, 0.5)",
                  color: "#dc2626",
                  padding: "0.75rem 1rem",
                  borderRadius: "6px",
                  fontSize: "0.9rem",
                }}
              >
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              style={{
                marginTop: "0.5rem",
                padding: "0.75rem 1.25rem",
                backgroundColor: isLoading ? "#9ca3af" : "#2563eb",
                color: "#ffffff",
                border: "none",
                borderRadius: "6px",
                fontWeight: 600,
                fontSize: "0.95rem",
                cursor: isLoading ? "not-allowed" : "pointer",
                transition: "background-color 0.15s ease",
              }}
            >
              {isLoading ? "Submitting Request..." : "Investigate"}
            </button>
          </form>
        </section>

        {/* Investigation Status / Result Section */}
        {investigation && (
          <section
            aria-live="polite"
            style={{
              border: "1px solid rgba(34, 197, 94, 0.4)",
              borderRadius: "8px",
              padding: "1.5rem",
              display: "flex",
              flexDirection: "column",
              gap: "1rem",
              backgroundColor: "rgba(34, 197, 94, 0.05)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 style={{ fontSize: "1.2rem", fontWeight: 600 }}>Investigation Status</h2>
              <span
                style={{
                  backgroundColor: "#22c55e",
                  color: "#ffffff",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  padding: "0.2rem 0.6rem",
                  borderRadius: "9999px",
                  letterSpacing: "0.05em",
                }}
              >
                {investigation.status}
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem", fontSize: "0.9rem" }}>
              <div>
                <strong>Investigation ID:</strong>{" "}
                <code
                  style={{
                    backgroundColor: "rgba(128, 128, 128, 0.15)",
                    padding: "0.15rem 0.4rem",
                    borderRadius: "4px",
                    fontFamily: "monospace",
                  }}
                >
                  {investigation.investigation_id}
                </code>
              </div>

              <div>
                <strong>Event Name:</strong>{" "}
                {investigation.input.event_name ? (
                  <span>{investigation.input.event_name}</span>
                ) : (
                  <em style={{ opacity: 0.6 }}>Not provided</em>
                )}
              </div>

              <div>
                <strong>Event URL:</strong>{" "}
                {investigation.input.event_url ? (
                  <a
                    href={investigation.input.event_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "#2563eb", textDecoration: "underline" }}
                  >
                    {investigation.input.event_url}
                  </a>
                ) : (
                  <em style={{ opacity: 0.6 }}>Not provided</em>
                )}
              </div>

              <div>
                <strong>Created At:</strong> {new Date(investigation.created_at).toLocaleString()}
              </div>
            </div>

            <div
              style={{
                fontSize: "0.85rem",
                opacity: 0.75,
                borderTop: "1px solid rgba(128, 128, 128, 0.2)",
                paddingTop: "0.75rem",
              }}
            >
              Investigation request initialized. Investigation engine and evidence collection pipeline will run in subsequent stages.
            </div>

            <button
              type="button"
              onClick={handleReset}
              style={{
                alignSelf: "flex-start",
                padding: "0.5rem 1rem",
                backgroundColor: "transparent",
                color: "inherit",
                border: "1px solid rgba(128, 128, 128, 0.4)",
                borderRadius: "6px",
                fontSize: "0.85rem",
                cursor: "pointer",
                marginTop: "0.25rem",
              }}
            >
              Start Another Investigation
            </button>
          </section>
        )}
      </div>
    </div>
  );
}
