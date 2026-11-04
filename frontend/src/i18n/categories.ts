import type { MessageKey } from "./messages"

export type CategoryId =
  | "culture"
  | "places"
  | "visitor-rules"
  | "documents"
  | "transport"
  | "accommodation"
  | "facilities"
  | "familiar"

export interface Category {
  id: CategoryId
  label: MessageKey
  icon: string
  /** Example prompts, one list per locale. */
  examples: Record<"id" | "en", string[]>
}

export const CATEGORIES: Category[] = [
  {
    id: "culture",
    label: "category.culture",
    icon: "◈",
    examples: {
      id: [
        "Apa arti sembah di pura Hindu Bali?",
        "Tradisi apa yang hanya bisa dilihat di Bali?",
        "Bisakah saya ikut upacara di pura saat Nyepi?",
      ],
      en: [
        "What does the daily prayer ritual at a Balinese Hindu temple mean?",
        "Which Balinese traditions can only be seen in Bali?",
        "Can visitors join a temple ceremony during Nyepi?",
      ],
    },
  },
  {
    id: "places",
    label: "category.places",
    icon: "⛰",
    examples: {
      id: [
        "Tempat terbaik untuk melihat matahari terbenam di Bali?",
        "Rekomendasi pantai yang ramah keluarga di Bali?",
        "Mana yang lebih worthy: Ubud atau Uluwatu?",
      ],
      en: [
        "Where is the best place to watch the sunset in Bali?",
        "Which beaches in Bali are family-friendly?",
        "Which is better for a first trip, Ubud or Uluwatu?",
      ],
    },
  },
  {
    id: "visitor-rules",
    label: "category.visitorRules",
    icon: "⛩",
    examples: {
      id: [
        "Apa aturan berpakaian saat visiting pura di Bali?",
        "Apakah ada hari libur di Bali yang pantang tourists?",
        "Bolehkah memotret di dalam pura?",
      ],
      en: [
        "What are the dress code rules for visiting a Balinese temple?",
        "Are there public holidays in Bali when visitors are restricted?",
        "Am I allowed to take photos inside a temple?",
      ],
    },
  },
  {
    id: "documents",
    label: "category.documents",
    icon: "🧾",
    examples: {
      id: [
        "Dokumen apa saja yang diperlukan untuk masuk ke Bali?",
        "Berapa biaya visa on arrival di Bali?",
        "Apakah saya perlu surat keterangan kesehatan?",
      ],
      en: [
        "Which documents do I need to enter Bali?",
        "How much is the Indonesian visa on arrival?",
        "Do I need any health certificate or vaccination proof?",
      ],
    },
  },
  {
    id: "transport",
    label: "category.transport",
    icon: "⛵",
    examples: {
      id: [
        "Cara termurah bepergian dari airport Bali ke Ubud?",
        "Apakah lebih aman menyewa motor atau menyewa driver di Bali?",
        "Bagaimana cara ke Nusa Penida dari Sanur?",
      ],
      en: [
        "What is the cheapest way to get from Bali airport to Ubud?",
        "Is it safer to rent a scooter or hire a driver in Bali?",
        "How do I get from Sanur to Nusa Penida?",
      ],
    },
  },
  {
    id: "accommodation",
    label: "category.accommodation",
    icon: "⌂",
    examples: {
      id: [
        "Rekomendasi homestay yang ramah keluarga di Ubud?",
        "Berapa rata-rata harga hotel di Bali per malam?",
        "Apakah ada hostel yang bagus di Kuta?",
      ],
      en: [
        "What family-friendly homestays are there in Ubud?",
        "What is the average price of a hotel in Bali per night?",
        "Are there any good hostels near Kuta?",
      ],
    },
  },
  {
    id: "facilities",
    label: "category.facilities",
    icon: "✦",
    examples: {
      id: [
        "Apakah ada ATM dan apotek di area tourists Bali?",
        "Internet di Bali bisa diandalkan?",
        "Di mana saya bisa mencari supermarket atau laundry?",
      ],
      en: [
        "Are there ATMs and pharmacies in the tourist areas of Bali?",
        "Can I rely on internet access in Bali?",
        "Where can I find a supermarket or laundry service?",
      ],
    },
  },
  {
    id: "familiar",
    label: "category.familiar",
    icon: "🌍",
    examples: {
      id: [
        "Ada apa saja di Bali yang mirip dengan negara saya?",
        "Apakah budaya Bali mirip budaya India?",
        "Are there places in Bali that remind you of other countries?",
      ],
      en: [
        "What in Bali is similar to what I know back home?",
        "Is Balinese culture similar to Indian culture?",
        "Are there any places in Bali that remind you of other countries?",
      ],
    },
  },
]
