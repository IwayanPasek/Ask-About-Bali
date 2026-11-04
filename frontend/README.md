# Frontend — Ask About Bali

Sisi klien dari **Ask About Bali**: web app satu halaman (chat) yang
bertanya ke backend dan menampilkan jawaban beserta foto, lokasi, dan sumber
web.

| | |
| --- | --- |
| Framework | Vue 3.5.44 (`<script setup>`) |
| Build tool | Vite 8.3.5 |
| Bahasa | TypeScript 6.0.3 |
| Type check | vue-tsc 3.3.14 |
| Runtime | Node.js 24.19.0 |
| Styling | CSS murni dengan custom properties (tanpa framework CSS) |

Lihat [`../docs/proposal.md`](../docs/proposal.md) untuk proposal utama proyek
dan [`../README.md`](../README.md) untuk cara menjalankan backend.

## Menjalankan

```bash
npm install
npm run dev
```

Frontend berjalan di `http://localhost:5173`. Permintaan ke `/api` diproksi ke
backend lokal (`http://127.0.0.1:8000`) oleh Vite — ganti targetnya lewat
environment variable `VITE_DEV_API_TARGET` bila perlu.

## Build

```bash
npm run build     # vue-tsc -b lalu vite build, output ke dist/
npm run preview   # menyajikan hasil build secara lokal
```

Hasil build (`dist/`) tidak di-commit.

## Struktur

| Path | Isi |
| --- | --- |
| `src/App.vue` | Kerangka halaman |
| `src/components/` | Hero, input pertanyaan, daftar percakapan, card gambar/lokasi/sumber |
| `src/composables/` | `useAsk` (state percakapan), `useI18n` (ID/EN) |
| `src/api/` | Client HTTP, endpoint ask, session id browser |
| `src/i18n/` | Pesan bilingual dan daftar kategori |
| `src/types.ts` | Bentuk data API |

## Catatan

- Session id dibuat acak di `src/api/session.ts` dan dikirim sebagai header
  `X-Session-Id`. Backend menghash-nya sebelum menyimpan, jadi ini bukan
  identitas dan tidak ada data pribadi.
- Tidak ada framework CSS dan tidak ada state management library; state
  percakapan memakai `ref` dari Vue.
