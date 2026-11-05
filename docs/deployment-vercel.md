# Deploy ke Vercel

Dokumen ini menjelaskan cara mendeploy **Ask About Bali** ke Vercel.

Arsitekturnya: **dua project Vercel** dari satu repo Git.

| Project | Root Directory | Isi | Hasil |
| --- | --- | --- | --- |
| `ask-about-bali-web` | `frontend` | Vue 3 (Vite) — build statis | Halaman web |
| `ask-about-bali-api` | `backend` | FastAPI — satu serverless function | API `/api/*` |

Kedua project memakai domain sendiri, jadi frontend memanggil API lewat
domain backend. Ini necessitated CORS — lihat bagian *Environment variable*.

---

## 1. Yang sudah disiapkan di repo

| Berkas | Isi |
| --- | --- |
| `backend/index.py` | Entrypoint Vercel. Mengekspor objek `app` (FastAPI) yang ditangkai Vercel sebagai satu function. |
| `backend/vercel.json` | `maxDuration: 60` detik untuk function. |
| `backend/.python-version` | Memilih Python 3.13 di Vercel. |
| `backend/requirements.txt` | Dependency backend. Dipakai juga untuk `pip install` lokal. |
| `frontend/vercel.json` | Rewrite SPA ke `index.html`. |
| `frontend/vite.config.ts` | `envDir` diarahkan ke root repo, jadi satu file `.env` melayani frontend dan backend. |

> Nama `backend/app/main.py` diganti menjadi `backend/app/api.py` supaya tidak
> bentrok dengan nama entrypoint yang dipesan Vercel (`app.py`, `index.py`,
> `main.py`, `server.py`, `wsgi.py`, `asgi.py`). Dua kandidat entrypoint di
> folder yang sama membuat Vercel tidak bisa menentukan yang mana yang dipakai.

---

## 2. Deploy backend (API)

### 2.1 Buat project

Di dashboard Vercel: **Add New → Project**, pilih repo `Ask-About-Bali`, lalu
atur:

| Pengaturan | Nilai |
| --- | --- |
| Framework Preset | **FastAPI** |
| Root Directory | `backend` |
| Build Command | (kosongkan — preset FastAPI sudah menangani) |
| Output Directory | (kosongkan) |

Penting: **Root Directory wajib `backend`**. Isi repo di luar folder itu tidak
ikut ter-deploy.

### 2.2 Environment variable

Tambahkan di **Settings → Environment Variables** (berlaku untuk Production,
Preview, dan Development):

```
GEMINI_API_KEY=<isi>
GEMINI_MODEL_ID=gemini-3.5-flash-lite
GEMINI_TIMEOUT_SECONDS=30
GEMINI_MAX_OUTPUT_TOKENS=900

GOOGLE_SEARCH_API_KEY=<isi>
GOOGLE_SEARCH_ENGINE_ID=<isi>
GOOGLE_SEARCH_MAX_RESULTS=6
GOOGLE_SEARCH_TIMEOUT_SECONDS=8
GOOGLE_SEARCH_COUNTRY=id

GOOGLE_MAPS_API_KEY=<isi>
GOOGLE_MAPS_TIMEOUT_SECONDS=8
GOOGLE_MAPS_MAX_RESULTS=5
GOOGLE_MAPS_LANGUAGE=id
GOOGLE_MAPS_REGION=ID

TIDB_HOST=<isi>
TIDB_PORT=4000
TIDB_USER=<isi>
TIDB_PASSWORD=<isi>
TIDB_DATABASE=<isi>
TIDB_CA_CERT_CONTENT=<isi PEM, lihat 2.3>
SESSION_HASH_SALT=<isi, nilai acak>

CORS_ORIGINS=https://<domain-frontend-anda>
ENVIRONMENT=production
```

`CORS_ORIGINS` diisi dengan domain frontend setelah project web selesai
dideploy. Bisa diisi lebih dari satu, dipisah koma.

### 2.3 Sertifikat CA TiDB

Folder `backend/certs/` ada di `.gitignore`, jadi **tidak ikut ter-deploy**.
Karena itu, sertifikat CA diberikan sebagai teks lewat `TIDB_CA_CERT_CONTENT`:

1. TiDB Cloud → tab **Connect** → **Download CA**.
2. Buka filenya; isinya satu blok teks PEM.
3. Tempel seluruh blok itu ke nilai `TIDB_CA_CERT_CONTENT`.

Baris `-----BEGIN CERTIFICATE-----` sampai `-----END CERTIFICATE-----` ikut
disalin. Backend menulisnya ke file sementara lalu memakainya untuk koneksi
TLS — sama seperti memakai `backend/certs/ca.pem` secara lokal.

Kalau TiDB belum dikonfigurasi, backend tetap jalan: `/api/ask` tetap menjawab,
hanya usage log tidak tercatat. `/api/health` melaporkan `database_reachable:
null`.

### 2.4 Deploy

```bash
cd backend
vercel link
vercel deploy --prod
```

Atau hubungkan repo Git di dashboard dan biarkan Vercel yang deploy otomatis
setiap push.

Cek hasilnya:

```bash
curl https://<domain-api-anda>/api/health
```

---

## 3. Deploy frontend

### 3.1 Buat project

| Pengaturan | Nilai |
| --- | --- |
| Framework Preset | **Vite** |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

### 3.2 Environment variable

```
VITE_API_BASE_URL=https://<domain-api-anda>
```

Tanpa `VITE_API_BASE_URL`, frontend akan meminta `/api/ask` ke domain sendiri,
sedangkan API berada di domain lain — hasilnya 404. Nilai ini dibaca **saat
build**, jadi kalau domain API berubah, project harus di-deploy ulang.

### 3.3 Deploy

```bash
cd frontend
vercel link
vercel deploy --prod
```

---

## 4. Menjalankan lokal seperti di Vercel

```bash
# Terminal 1 — backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.api:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Frontend memakai proxy Vite, jadi `/api` diteruskan ke
`http://127.0.0.1:8000`. Tidak perlu `VITE_API_BASE_URL` untuk pengembangan
lokal.

---

## 5. Catatan penting

### Connection pool TiDB

Backend memakai connection pool (SQLAlchemy). Di serverless, tiap instance
function punya pool sendiri, dan instance bisa shuts down kapan saja. Efeknya:
bisa muncul koneksi-yang-mati. Kode sudah mengatasinya dengan `pool_pre_ping`,
jadi koneksi rusak dideteksi dan diganti otomatis.

Kalau TiDB complains tentang jumlah koneksi, turunkan `DB_POOL_SIZE` dan
`DB_MAX_OVERFLOW` lewat environment variable.

### Background task

Usage log ditulis sebagai background task FastAPI: respons dikirim ke pengguna
terlebih dahulu, log menyusul. Di serverless, function bisa di-recycle sebelum
background task selesai — usage log sesekali hilang. Jawaban pengguna tidak
pernah terpengaruh, karena itu memang Separate Failure Domain.

### `maxDuration`

Panggilan ke Gemini bisa memakan waktu. Default `maxDuration` Vercel lebih
pendek dari yang dibutuhkan, jadi `backend/vercel.json` mengaturnya ke 60
detik. Naikkan kalau jawaban sering terpotong.

### Batas plan Hobby

Semua yang dipakai di sini (Python serverless, dua project, custom domain)
berada di plan Hobby.

---

## 6. Environment variable ringkas

| Variable | Dipakai oleh | Wajib |
| --- | --- | --- |
| `GEMINI_API_KEY` | backend | ya |
| `GOOGLE_SEARCH_API_KEY` | backend | tidak |
| `GOOGLE_SEARCH_ENGINE_ID` | backend | tidak |
| `GOOGLE_MAPS_API_KEY` | backend | tidak |
| `TIDB_*` | backend | tidak |
| `TIDB_CA_CERT_CONTENT` | backend | tidak |
| `SESSION_HASH_SALT` | backend | tidak |
| `CORS_ORIGINS` | backend | ya di produksi |
| `ENVIRONMENT` | backend | tidak |
| `VITE_API_BASE_URL` | frontend | ya di produksi |
