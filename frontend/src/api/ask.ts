import { apiFetch } from "./client"
import { getSessionId } from "./session"
import type { AskRequest, AskResponse } from "../types"

export async function sendQuestion(payload: AskRequest): Promise<AskResponse> {
  return apiFetch<AskResponse>("/api/ask", {
    method: "POST",
    // The server hashes this before storing it; it is never used as an identity.
    headers: { "X-Session-Id": getSessionId() },
    body: JSON.stringify(payload),
  })
}
