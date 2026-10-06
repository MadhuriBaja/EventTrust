export interface InvestigationInput {
  event_name: string | null;
  event_url: string | null;
}

export type InvestigationStatus = "pending" | string;

export interface InvestigationResponse {
  investigation_id: string;
  input: InvestigationInput;
  status: InvestigationStatus;
  created_at: string;
}

export interface InvestigationCreateRequest {
  event_name?: string;
  event_url?: string;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Sends a request to the FastAPI backend to create a new investigation.
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
    let errorMessage = `Request failed with status ${response.status}`;
    try {
      const errorBody = await response.json();
      if (typeof errorBody.detail === "string") {
        errorMessage = errorBody.detail;
      } else if (Array.isArray(errorBody.detail)) {
        errorMessage = errorBody.detail
          .map((item: { msg?: string }) => item.msg || JSON.stringify(item))
          .join(", ");
      }
    } catch {
      // Use default fallback error message
    }
    throw new Error(errorMessage);
  }

  return response.json();
}
