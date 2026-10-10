
export interface InvestigationInput {
  event_name: string | null;
  event_url: string | null;
}

export type InvestigationStatus = "pending" | string;

export interface EventProfile {
  event_name?: string | null;
  organizer?: string | null;
  event_date?: string | null;
  venue?: string | null;
  speakers?: string[];
  registration_url?: string | null;
  source_url?: string | null;
  description?: string | null;
}

export interface InvestigationResponse {
  investigation_id: string;
  input: InvestigationInput;
  status: InvestigationStatus;
  created_at: string;
  event_profile?: EventProfile | null;
}

export interface InvestigationCreateRequest {
  event_name?: string;
  event_url?: string;
}

export interface ResearchFinding {
  title: string;
  url: string;
  snippet?: string | null;
  category?: string | null;
  relevance?: string | null;
  relevance_score?: number | null;
  source_domain?: string | null;
  review_status?: string | null;
}

export interface ResearchReport {
  assessment?: string;
  findings?: ResearchFinding[];
  limitations?: string[];
  failed_searches?: string[];
  [key: string]: unknown;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function parseError(response: Response): Promise<string> {
  let errorMessage = `Request failed with status ${response.status}`;

  try {
    const errorBody = await response.json();

    if (typeof errorBody.detail === "string") {
      errorMessage = errorBody.detail;
    } else if (Array.isArray(errorBody.detail)) {
      errorMessage = errorBody.detail
        .map((item: { msg?: string }) => item.msg || JSON.stringify(item))
        .join(", ");
    } else if (typeof errorBody.message === "string") {
      errorMessage = errorBody.message;
    }
  } catch {
    // Keep the default error message if the response is not JSON.
  }

  return errorMessage;
}

/**
 * Creates a new EventTrust investigation.
 */
export async function createInvestigation(
  data: InvestigationCreateRequest
): Promise<InvestigationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/investigations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return (await response.json()) as InvestigationResponse;
}

/**
 * Runs public-source research for an existing investigation.
 */
export async function runResearch(
  investigationId: string
): Promise<ResearchReport> {
  const response = await fetch(
    `${API_BASE_URL}/api/investigations/${encodeURIComponent(
      investigationId
    )}/research`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return (await response.json()) as ResearchReport;
}
