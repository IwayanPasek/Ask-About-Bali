import { ref } from "vue"

import { ApiError } from "../api/client"
import { sendQuestion } from "../api/ask"
import { useI18n } from "./useI18n"
import { CATEGORIES } from "../i18n/categories"
import type { AnswerEntry } from "../types"

const entries = ref<AnswerEntry[]>([])
const pending = ref(false)
const error = ref<string | null>(null)

let nextId = 1

export function useAsk() {
  const { locale, t } = useI18n()

  async function ask(question: string, categoryId: string | null): Promise<void> {
    const text = question.trim()
    if (!text || pending.value) return

    const category = CATEGORIES.find((item) => item.id === categoryId)
    const entry: AnswerEntry = {
      id: nextId++,
      question: text,
      categoryId,
      categoryLabel: category ? t(category.label) : null,
      status: "answered",
      answer: "",
      images: [],
      locations: [],
      locationError: null,
      sources: [],
      searchTip: null,
      webSearchError: null,
      error: null,
    }
    entries.value.push(entry)
    error.value = null
    pending.value = true

    try {
      const response = await sendQuestion({
        question: text,
        language: locale.value,
        category: categoryId,
      })
      entry.status = response.status
      entry.answer = response.answer
      entry.images = response.images ?? []
      entry.locations = response.locations ?? []
      entry.locationError = response.location_error ?? null
      entry.sources = response.sources ?? []
      entry.searchTip = response.search_tip ?? null
      entry.webSearchError = response.web_search_error ?? null
    } catch (err) {
      if (err instanceof ApiError) {
        entry.error = err.message
      } else {
        entry.error = t("ask.genericError")
      }
      error.value = entry.error
    } finally {
      pending.value = false
    }
  }

  function clear(): void {
    entries.value = []
    error.value = null
  }

  return { entries, pending, error, ask, clear }
}
