export type Locale = "id" | "en"

export type AskStatus = "answered" | "out_of_scope" | "not_found"

export interface AskImage {
  title: string
  image_url: string
  thumbnail_url: string
  source_name: string
  source_url: string
}

export interface AskLocation {
  place_id: string
  name: string
  address: string
  latitude: number
  longitude: number
  maps_url: string
}

export interface AskSource {
  title: string
  link: string
  snippet: string
  source_name: string
}

export interface AskResponse {
  status: AskStatus
  answer: string
  language: string
  category: string | null
  model_id: string
  images: AskImage[]
  locations: AskLocation[]
  location_error: string | null
  sources: AskSource[]
  search_tip: string | null
  web_search_error: string | null
}

export interface AskRequest {
  question: string
  language: Locale
  category?: string | null
}

export interface AnswerEntry {
  id: number
  question: string
  categoryId: string | null
  categoryLabel: string | null
  status: AskStatus
  answer: string
  images: AskImage[]
  locations: AskLocation[]
  locationError: string | null
  sources: AskSource[]
  searchTip: string | null
  webSearchError: string | null
  error: string | null
}
