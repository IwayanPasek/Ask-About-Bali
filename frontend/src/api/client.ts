const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ""

export class ApiError extends Error {
  code: string
  status: number

  constructor(code: string, message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.code = code
    this.status = status
  }
}

interface ErrorEnvelope {
  error?: { code?: string; message?: string }
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
    })
  } catch {
    throw new ApiError("network_error", "Gagal terhubung ke server.", 0)
  }

  if (!response.ok) {
    let envelope: ErrorEnvelope = {}
    try {
      envelope = (await response.json()) as ErrorEnvelope
    } catch {
      // Body is not JSON; fall back to a generic message.
    }
    throw new ApiError(
      envelope.error?.code ?? "unknown_error",
      envelope.error?.message ?? `Terjadi kesalahan (${response.status}).`,
      response.status,
    )
  }

  return (await response.json()) as T
}
