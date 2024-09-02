# Mosys Printer

Mosys Printer adalah aplikasi yang menggabungkan GUI berbasis PyQt5 untuk desain dan manajemen struk dengan server Flask untuk menangani permintaan cetak. Aplikasi ini memudahkan proses pembuatan, pengelolaan, dan pencetakan struk untuk berbagai kebutuhan bisnis.

## Fitur

- GUI intuitif untuk desain template struk
- Preview real-time dari template struk
- Pemilihan dan manajemen printer yang mudah
- Server Flask untuk menangani permintaan cetak melalui HTTP
- Mendukung berbagai ukuran kertas dan tata letak yang dapat disesuaikan

## Persyaratan Sistem

- Windows 10 atau yang lebih baru
- Python 3.7+
- Printer termal yang kompatibel dan driver wajib terinstall

## Instalasi

1. Clone repositori ini:

   ```
   git clone https://github.com/dypras666/sedotphp_printer_server.git
   ```

2. Masuk ke direktori proyek:

   ```
   cd sedotphp_printer_server
   ```

3. Instal dependensi yang diperlukan:

   ```
   pip install -r requirements.txt
   ```

4. Pastikan file konfigurasi `mosys.json` dan `receipt_template.json` ada di direktori proyek. Jika tidak ada, aplikasi akan membuatnya secara otomatis saat pertama kali dijalankan.

## Penggunaan

1. Jalankan aplikasi dengan perintah:

   ```
   python app_launcher.py
   ```

2. Gunakan GUI untuk mendesain template struk Anda.

3. Pilih printer yang diinginkan dari opsi yang tersedia.

4. Gunakan endpoint server Flask untuk mengirim permintaan cetak.

## API Endpoints

Server berjalan di `http://localhost:1717` dan menyediakan endpoint berikut:

1. **GET /printers**

   - Deskripsi: Mendapatkan daftar printer yang tersedia
   - Respons: Array nama printer

2. **POST /set_printer**

   - Deskripsi: Mengatur printer aktif
   - Body: JSON dengan `printer_name`
   - Contoh:
     ```json
     {
       "printer_name": "Nama Printer Anda"
     }
     ```

3. **POST /print**

   - Deskripsi: Mencetak struk
   - Body: Form-data dengan field berikut:
     - `nama_toko`: Nama toko (string)
     - `alamat_toko`: Alamat toko (string)
     - `no_hp`: Nomor telepon toko (string)
     - `nama_kasir`: Nama kasir (string)
     - `tanggal`: Tanggal dan waktu transaksi (string, format: "YYYY-MM-DD HH:MM:SS")
     - `items`: Daftar item yang dibeli (JSON string array)
     - `notes`: Catatan tambahan (string, opsional)
   - Contoh `items`:
     ```json
     [
       {
         "nama_produk": "Produk A",
         "qty": 2,
         "satuan": "pcs",
         "harga": 10000,
         "diskon": 1000,
         "total_harga": 19000
       },
       {
         "nama_produk": "Produk B",
         "qty": 1,
         "satuan": "pcs",
         "harga": 15000,
         "diskon": 0,
         "total_harga": 15000
       }
     ]
     ```

4. **POST /update_template**
   - Deskripsi: Memperbarui template struk
   - Body: JSON dengan field template yang ingin diperbarui

## Postman Collection

Untuk memudahkan pengujian API, kami menyediakan Postman collection. Anda dapat mengimpor file `postman_collection.txt` ke Postman Anda untuk mulai menguji endpoint API.

Cara menggunakan Postman collection:

1. Buka Postman
2. Klik "Import" di bagian atas
3. Pilih "Raw text" dan salin isi dari file `postman_collection.txt`
4. Klik "Continue" dan kemudian "Import"
5. Anda sekarang memiliki collection Mosys Printer di Postman Anda

## Struktur Proyek

```
sedotphp_printer_server/
│
├── app_launcher.py         # Script utama untuk menjalankan aplikasi
├── icon.ico                # Ikon aplikasi
├── LICENSE                 # File lisensi
├── main.py                 # Script utama GUI
├── mosys.json              # File konfigurasi aplikasi
├── postman_collection.txt  # Koleksi Postman untuk testing API
├── readme.md               # File README (dokumen ini)
├── receipt_template.json   # Template struk default
├── receipt_template.py     # Modul pengelolaan template struk
└── requirements.txt        # Daftar dependensi Python
```

## Membangun Executable

Untuk membuat executable standalone:

1. Pastikan PyInstaller terinstal:

   ```
   pip install pyinstaller
   ```

2. Jalankan perintah berikut:

   ```
   pyinstaller --onefile --windowed --icon=icon.ico --name="Mosys Printer" app_launcher.py
   ```

3. Temukan executable di direktori `dist`.

## Kontribusi

Kontribusi selalu diterima! Silakan ajukan Pull Request.

## Pengembang

- **Kurniawan**
- Instagram: [@sedotphp](https://instagram.com/sedotphp)

## Repositori

:star: Beri bintang dan :fork_and_knife: fork repositori ini di GitHub:

[https://github.com/dypras666/sedotphp_printer_server](https://github.com/dypras666/sedotphp_printer_server)

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT - lihat file [LICENSE](LICENSE) untuk detailnya.
