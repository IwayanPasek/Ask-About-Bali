# Usage Log Anonim — TiDB Cloud

Dokumen ini menjelaskan pencatatan penggunaan di TiDB Cloud. Tujuannya hanya
satu: memahami usage layanan agar bisa dikembangkan. **Tidak ada data pribadi.**

## Apa yang disimpan

Tabel `question_logs`, satu baris per pertanyaan:

| Kolom | Isi |
| --- | --- |
| `id` | Kunci utama auto-increment |
| `session_hash` | SHA-256 dari session id browser + salt |
| `question` | Isi pertanyaan |
| `answer` | Isi jawaban |
| `language`, `category`, `status` | Konteks jawaban |
| `model_id` | Model Gemini yang dipakai |
| `prompt_tokens`, `output_tokens`, `total_tokens` | Pemakaian token |
| `latency_ms` | Waktu proses permintaan |
| `image_count`, `location_count`, `source_count` | Jumlah lampiran |
| `created_at` | Waktu pencatatan (UTC) |

## Apa yang TIDAK disimpan

- API key, kredensial, atau konfigurasi apa pun.
- Alamat IP, user agent, atau nama pengguna.
- Session id mentah — hanya hash-nya yang disimpan.

## Anonimitas

Browser membuat session id acak (`frontend/src/api/session.ts`) dan mengirimnya
pada header `X-Session-Id`. Backend mem-hash-nya dengan SHA-256 memakai salt
dari `SESSION_HASH_SALT` sebelum menulisnya ke database.

Kalau `SESSION_HASH_SALT` tidak diisi, backend memakai salt acak per-proses.
Hash tetap tidak bisa dibalik ke session id, hanya saja hash dari dua proses
yang berbeda tidak bisa dibandingkan.

Session id berfungsi sebagai pengelompok, bukan identitas: tidak ada endpoint
yang menerima session id dan mengembalikan riwayat milik pengguna tersebut.

## Ketahanan

Penulisan log dijalankan sebagai **background task** (`BackgroundTasks` FastAPI):
respons dikirim ke pengguna terlebih dahulu, lalu log ditulis setelahnya. Jadi
database yang lambat tidak pernah menunda jawaban.

Penulisan log juga dibungkus `try/except` di `app/services/usage_log.py`. Kalau
database tidak terkonfigurasi, tidak bisa dijangkau, atau tabelnya belum ada,
permintaan pengguna **tetap berhasil** — kegagalannya hanya dicatat di log
server.

Koneksi database dibatasi `connect_timeout` 10 detik, jadi jaringan rusak tidak
bisa menggantung request.

`GET /api/health` mengembalikan `database_reachable` (`true`/`false`/`null`
bila tidak dikonfigurasi) sehingga mudah memeriksa koneksi.

## Menyiapkan database

1. Buat cluster di TiDB Cloud dan salin kredensialnya.
2. Unduh sertifikat CA (menu **Connect** → *Download CA*) dan simpan sebagai
   `backend/certs/ca.pem`.
3. Isi `TIDB_HOST`, `TIDB_PORT`, `TIDB_USER`, `TIDB_PASSWORD`,
   `TIDB_DATABASE`, dan `SESSION_HASH_SALT` di `.env`.
4. Buat tabelnya sekali:

   ```bash
   cd backend
   python -m scripts.init_db
   ```

   Script-nya idempoten — tabel yang sudah ada tidak dihapus.

## Environment variable

```
TIDB_HOST=
TIDB_PORT=4000
TIDB_USER=
TIDB_PASSWORD=
TIDB_DATABASE=
TIDB_CA_CERT_PATH=backend/certs/ca.pem
DATABASE_URL=            # alternatif, menang atas TIDB_*
SESSION_HASH_SALT=
```

Path relatif pada `TIDB_CA_CERT_PATH` diselesaikan relatif terhadap root
project, jadi nilainya sama saja dijalankan dari folder mana pun.
