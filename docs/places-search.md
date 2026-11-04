# Place Search — Google Maps Places API

Dokumen ini menjelaskan alur pencarian lokasi yang ditambahkan pada tahap
place lookup. Backend memakai **Places API (New) v1 — Text Search**, dengan
filter koordinat agar hasil tidak pernah keluar dari Bali.

## Alur

1. Pengguna mengirim pertanyaan ke `POST /api/ask`.
2. Gemini mengembalikan `needs_location` dan `location_query` — nama tempat
   yang spesifik, misalnya `Tanah Lot Temple` (tanpa kata "Bali" tambahan).
3. Backend memanggil `POST https://places.googleapis.com/v1/places:searchText`
   dengan `X-Goog-Api-Key` dan `X-Goog-FieldMask` (hanya field yang dipakai).
4. Backend membuang hasil yang koordinatnya di luar kotak Bali, lalu
   mengembalikan `locations`.

## Batas koordinat Bali

```
min_lat = -8.85   max_lat = -8.05
min_lng = 114.40  max_lng = 115.80
```

Ini mencakup Bali dan Nusa Penida/Nusa Lembongan. Hasil di luar kotak ini
dibuang, sehingga pencarian dengan nama yang ambigu tidak pernah menampilkan
tempat di Jawa atau negara lain.

## Aturan yang dijaga

- **Tidak ada lokasi yang dikarang.** Nama, alamat, dan koordinat selalu
  berasal dari respons Google.
- **Kegagalan place lookup tidak merusak jawaban teks.** `MapsLookupError`
  ditangkap di router dan dikembalikan sebagai `location_error` — pesan
  singkat yang aman untuk pengguna, tanpa detail teknis.
- **API key tidak pernah sampai ke klien.** `GOOGLE_MAPS_API_KEY` hanya
  dipakai server-side. Peta di frontend memakai embed Google Maps klasik yang
  tidak memerlukan API key.

## Field respons

| Field | Tipe | Keterangan |
| --- | --- | --- |
| `place_id` | string | ID tempat dari Google |
| `name` | string | Nama tampilan |
| `address` | string | Alamat ringkas |
| `latitude` / `longitude` | float | Koordinat |
| `maps_url` | string | Tautan "Buka di Google Maps" |

## Environment variable

```
GOOGLE_MAPS_API_KEY=
GOOGLE_MAPS_TIMEOUT_SECONDS=8
GOOGLE_MAPS_MAX_RESULTS=5
GOOGLE_MAPS_LANGUAGE=id
GOOGLE_MAPS_REGION=ID
```

## Cara menguji

1. Isi `GOOGLE_MAPS_API_KEY` di `.env` dan aktifkan **Places API (New)** pada
   project Google Cloud Anda.
2. Jalankan backend dan frontend.
3. Kirim pertanyaan seperti `Ceritakan tentang Pura Tanah Lot di Bali`.
4. Card lokasi harus muncul dengan peta tertanam dan tautan ke Google Maps.
