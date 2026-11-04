# Web Search — Google Programmable Search Engine

Dokumen ini menjelaskan alur web search yang ditambahkan pada tahap web
search. Backend memakai Custom Search JSON API yang sama dengan image
search, tetapi tanpa `searchType=image`.

## Alur

1. Pengguna mengirim pertanyaan ke `POST /api/ask`.
2. Gemini mengembalikan `needs_web_search` dan `web_query` — frasa pencarian
   Bahasa Inggris, misalnya `Tanah Lot temple opening hours`.
3. Backend memanggil Custom Search JSON API dengan `web_query` tersebut.
4. Backend memfilter hasil agar tetap dalam konteks Bali, lalu mengembalikan
   `sources` beserta tautan aslinya.

## Field respons

| Field | Tipe | Keterangan |
| --- | --- | --- |
| `title` | string | Judul hasil |
| `link` | string | URL asli hasil |
| `snippet` | string | Cuplikan deskripsi dari Google |
| `source_name` | string | Nama domain sumber |

## search_tip

Selain `sources`, Gemini juga mengembalikan `search_tip`: satu kalimat
praktis berisi cara memverifikasi informasi secara mandiri, misalnya
`Cari 'Tanah Lot opening hours' di Google`. Tips ini ditampilkan di frontend
di bawah jawaban, dan tetap ada meskipun web search gagal.

## Aturan yang dijaga

- **Tidak ada tautan yang dikarang.** Hanya URL asli dari Google yang dikirim.
- **Kegagalan web search tidak merusak jawaban teks.** Kegagalan dikembalikan
  sebagai `web_search_error`, sementara `answer` tetap utuh.
- **Hasil difilter ke konteks Bali.** `web_search.py` memakai daftar penanda
  Bali (`BALI_HINTS`), termasuk `go.id` dan `.bali` untuk sumber resmi.
- **API key tidak pernah sampai ke klien.**

## Environment variable

Variable-nya sama dengan image search:

```
GOOGLE_SEARCH_API_KEY=
GOOGLE_SEARCH_ENGINE_ID=
GOOGLE_SEARCH_MAX_RESULTS=6
GOOGLE_SEARCH_TIMEOUT_SECONDS=8
GOOGLE_SEARCH_COUNTRY=id
```

## Cara menguji

1. Isi `GOOGLE_SEARCH_API_KEY` dan `GOOGLE_SEARCH_ENGINE_ID` di `.env`.
2. Jalankan backend dan frontend.
3. Kirim pertanyaan yang perlu data terbaru, misalnya
   `Jam buka Pura Tanah Lot berapa?`.
4. Daftar sumber web harus muncul di bawah jawaban, disertai tips verifikasi.
