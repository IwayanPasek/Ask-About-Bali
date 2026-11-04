# Ask About Bali

Aplikasi web berbasis AI untuk membantu wisatawan mancanegara, wisatawan domestik,
dan masyarakat Bali memperoleh informasi tentang Bali secara lebih mudah, spesifik,
dan sesuai kebutuhan.

Aplikasi ini hanya menyediakan informasi terkait Bali dan kebutuhan wisatawan di Bali.
Pertanyaan di luar cakupan Bali ditolak dengan penjelasan yang jelas.

## Tech Stack

Status **pakai** = sudah ada di kode dan berjalan · **rencana** = target tahap
berikutnya. Rincian lengkap ada di [`docs/proposal.md`](docs/proposal.md).

| Komponen | Teknologi | Versi | Status |
| --- | --- | --- | --- |
| Frontend | Vue 3 (`<script setup>`) + Vite + TypeScript | 3.5.44 / 8.3.5 / 6.0.3 | pakai |
| Backend | Python + FastAPI | 3.14.7 / 0.162.0 | pakai |
| AI | Google Gemini — `gemini-3.5-flash-lite` | google-genai 2.34.0 | pakai |
| Image & Web Search | Google Programmable Search Engine (Custom Search JSON API) | — | pakai |
| Peta | Google Maps Places API (New) v1 — Text Search | — | pakai |
| Database | TiDB Cloud (MySQL-compatible) — usage log anonim saja | SQLAlchemy 2.1.8 / PyMySQL 1.2.3 | pakai |
| Hosting | Vercel — frontend static + backend Python serverless | — | rencana |

## Struktur Project

```
ask-about-bali/
├── frontend/        # Vue 3 (Vite) — UI chat, ganti bahasa, card gambar/lokasi/sumber
├── backend/         # FastAPI — endpoint /api/ask, /api/health
│   ├── app/
│   │   ├── routers/ # ask.py
│   │   ├── services/# gemini, image_search, web_search, maps, prompts, usage_log
│   │   └── db/      # model + session TiDB Cloud
│   └── scripts/     # init_db.py, smoke_test.py
├── docs/            # Dokumentasi per tahap
├── .env.example     # Daftar environment variable (tanpa nilai rahasia)
├── .gitignore
└── README.md
```

## Environment Variable

Salin `.env.example` menjadi `.env` di root project lalu isi nilainya:

```bash
cp .env.example .env
```

| Variable | Sumber | Dipakai oleh |
| --- | --- | --- |
| `GEMINI_API_KEY` | Google AI Studio | `/api/ask` — jawaban teks |
| `GEMINI_MODEL_ID` | — (default `gemini-3.5-flash-lite`) | model Gemini |
| `GOOGLE_SEARCH_API_KEY` | Google Cloud Console → Custom Search JSON API | image & web search |
| `GOOGLE_SEARCH_ENGINE_ID` | Google Programmable Search Engine | image & web search |
| `GOOGLE_MAPS_API_KEY` | Google Cloud Console → Places API (New) | place lookup |
| `TIDB_HOST` / `TIDB_PORT` / `TIDB_USER` / `TIDB_PASSWORD` / `TIDB_DATABASE` | TiDB Cloud → tab Connect | usage log anonim |
| `SESSION_HASH_SALT` | nilai acak buatan sendiri | hash session id pada usage log |

File `.env` sudah masuk `.gitignore` dan tidak boleh di-commit.

## Menjalankan Backend

```bash
cd backend
python -m venv .venv
```

Aktifkan virtual environment:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Pasang dependency lalu jalankan:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend berjalan di `http://127.0.0.1:8000`, dokumentasi API di `http://127.0.0.1:8000/docs`.

Membuat tabel usage log (sekali saja, setelah kredensial TiDB diisi):

```bash
python -m scripts.init_db
```

## Menjalankan Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend berjalan di `http://localhost:5173`. Permintaan ke `/api` diproksi ke backend
lokal (`http://127.0.0.1:8000`) oleh Vite.

## Pengujian

```bash
cd backend
python -m scripts.smoke_test
```

Seluruh layanan eksternal dipalsukan, jadi tidak ada panggilan API berbayar dan
tidak ada baris yang ditulis ke database.

## API

### `POST /api/ask`

```json
{
  "question": "Ceritakan tentang Tanah Lot di Bali",
  "language": "id",
  "category": "places"
}
```

Respons:

```json
{
  "status": "answered",
  "answer": "Tanah Lot adalah pura ikonik di Bali.",
  "language": "id",
  "category": "places",
  "model_id": "gemini-3.5-flash-lite",
  "images": [
    {
      "title": "Tanah Lot",
      "image_url": "https://…",
      "thumbnail_url": "https://…",
      "source_name": "www.bali.com",
      "source_url": "https://…"
    }
  ],
  "locations": [
    {
      "place_id": "ChIJ…",
      "name": "Tanah Lot Temple",
      "address": "Jl. Goa Lempeh, Canggu, Bali",
      "latitude": -8.6212,
      "longitude": 115.087,
      "maps_url": "https://…"
    }
  ],
  "sources": [
    {
      "title": "Tanah Lot opening hours",
      "link": "https://…",
      "snippet": "Open daily from 6am to 7pm.",
      "source_name": "www.bali.com"
    }
  ],
  "search_tip": "Cari 'Tanah Lot opening hours' di Google."
}
```

`status` berisi `answered`, `out_of_scope` (pertanyaan di luar Bali), atau `not_found`
(data tidak ditemukan pada sistem).

Field `images`, `locations`, dan `sources` hanya terisi bila jawaban relevan dan
layanan terkait berhasil. Kegagalan masing-masing layanan dilaporkan terpisah lewat
`location_error` dan `web_search_error`, tanpa merusak `answer`.

Header opsional `X-Session-Id` boleh dikirim; nilainya di-hash server sebelum
disimpan ke usage log anonim.

### `GET /api/health`

```bash
curl http://127.0.0.1:8000/api/health
```

Mengembalikan status aplikasi, daftar service yang sudah terkonfigurasi, status
koneksi database (`database_reachable`), dan environment variable yang masih belum
diisi.

## Dokumentasi

| Dokumen | Isi |
| --- | --- |
| [`docs/image-search.md`](docs/image-search.md) | Image search via Google PSE |
| [`docs/places-search.md`](docs/places-search.md) | Place lookup via Google Maps Places API |
| [`docs/web-search.md`](docs/web-search.md) | Web search via Google PSE |
| [`docs/usage-log.md`](docs/usage-log.md) | Usage log anonim di TiDB Cloud |
