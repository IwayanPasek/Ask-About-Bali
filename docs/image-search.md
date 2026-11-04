# Image Search — Google Programmable Search Engine

Dokumen ini menjelaskan alur image search yang ditambahkan pada tahap image search.
Web search dan Google Maps belum diimplementasikan.

## Alur

1. Pengguna mengirim pertanyaan ke `POST /api/ask`.
2. Backend memanggil Gemini (`gemini-3.5-flash-lite`) dengan system prompt yang memaksa
   model mengembalikan JSON berisi:
   - `status` — `answered` / `out_of_scope` / `not_found`
   - `answer` — teks jawaban untuk pengguna
   - `needs_image` — `true` hanya bila foto pendukung benar-benar membantu
   - `image_query` — frasa pencarian Bahasa Inggris (mis. `Tanah Lot temple Bali`)
3. Backend memanggil Custom Search JSON API dengan `searchType=image` memakai
   `image_query` tersebut.
4. Backend memfilter hasil agar tetap dalam konteks Bali, lalu mengembalikan gambar
   beserta sumbernya.

## File terkait

| File | Peran |
| --- | --- |
| `backend/app/services/prompts.py` | System prompt Gemini + aturan `needs_image` / `image_query` |
| `backend/app/services/gemini.py` | Pemanggilan Gemini, structured output, penanganan error kuota |
| `backend/app/services/image_search.py` | Panggilan Custom Search JSON API + filter konteks Bali |
| `backend/app/routers/ask.py` | Penyatuan jawaban teks dan gambar |
| `frontend/src/components/ImageCard.vue` | Card gambar + atribusi sumber |

## Aturan yang dijaga

- **Gambar hanya untuk konteks Bali.** `image_search.py` menyaring hasil dengan daftar
  penanda Bali (`BALI_HINTS`: bali, ubud, uuluwatu, canggu, sanur, nusa penida, …).
  Hasil yang tidak cocok dibuang.
- **Tidak ada gambar atau tautan yang dikarang.** Yang dikirim ke klien hanya hasil
  asli dari Google, lengkap dengan `source_name` dan `source_url`.
- **Kegagalan image search tidak merusak jawaban teks.** `search_images()` mengembalikan
  list kosong saat gagal, dan router menangkap exception apa pun. Field `answer` tetap
  berisi jawaban penuh.
- **API key tidak pernah sampai ke klien.** `GOOGLE_SEARCH_API_KEY` hanya dipakai
  server-side pada permintaan ke Google.

## Kendala pada model

- `needs_image` hanya `true` untuk pertanyaan yang memang butuh foto (tempat,
  pura, pantai, pemandangan, aktivitas, transportasi, jenis akomodasi).
- Pertanyaan murni faktual, aturan, dokumen, biaya, atau adat menghasilkan
  `needs_image: false`, sehingga card gambar tidak muncul.
- Pertanyaan di luar scope Bali selalu `needs_image: false`, sehingga tidak ada gambar
  yang lolos ke frontend.

## Environment variable

```
GOOGLE_SEARCH_API_KEY=
GOOGLE_SEARCH_ENGINE_ID=
GOOGLE_SEARCH_MAX_RESULTS=6
GOOGLE_SEARCH_TIMEOUT_SECONDS=8
GOOGLE_SEARCH_COUNTRY=id
```

## Cara menguji

1. Isi `GEMINI_API_KEY`, `GOOGLE_SEARCH_API_KEY`, dan `GOOGLE_SEARCH_ENGINE_ID` di `.env`.
2. Jalankan backend dan frontend.
3. Kirim pertanyaan yang butuh gambar, misalnya:
   - `Ceritakan tentang Pura Tanah Lot di Bali` → teks jawaban + card gambar.
   - `Berapa biaya tiket masuk Taman Garuda di Bali` → teks saja, tanpa gambar.
4. Cek atribut `<img>` pada card: `src` memakai `thumbnail_url`, dan caption berisi
   tautan ke `source_url`.
