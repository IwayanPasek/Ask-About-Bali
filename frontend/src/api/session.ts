const SESSION_STORAGE_KEY = "ask-about-bali.session-id"

/**
 * Stable, anonymous id for this browser.
 *
 * It is only used to group usage logs on the server, where it is hashed
 * before it is stored. It contains no personal data and is not a login.
 */
export function getSessionId(): string {
  try {
    const existing = localStorage.getItem(SESSION_STORAGE_KEY)
    if (existing) return existing

    const generated =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(36).slice(2)}`

    localStorage.setItem(SESSION_STORAGE_KEY, generated)
    return generated
  } catch {
    // Private mode or storage disabled: fall back to a per-request id.
    return `ephemeral-${Math.random().toString(36).slice(2)}`
  }
}
