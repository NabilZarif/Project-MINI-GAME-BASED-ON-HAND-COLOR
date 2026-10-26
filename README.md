# 🎮 Tetris Kontrol Gestur Tangan (Hand Gesture Controlled Tetris)
### Proyek Evaluasi Tengah Semester (ETS) - Pengolahan Citra dan Video (PCV)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5.0%2B-red?style=for-the-badge&logo=opencv&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6%2B-green?style=for-the-badge&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-orange?style=for-the-badge&logo=numpy&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

---

## 📌 Ringkasan Proyek

**Tetris Kontrol Gestur Tangan** adalah implementasi modern dari permainan klasik Tetris yang diintegrasikan dengan teknologi **Computer Vision (Pengolahan Citra Digital)** secara *real-time*. Pemain dapat mengontrol pergerakan balok Tetris hanya menggunakan gestur tangan dan sarung tangan berwarna merah di depan webcam tanpa memerlukan keyboard atau controller fisik.

Proyek ini mendemonstrasikan penerapan teknik segmentasi warna pada ruang warna HSV, operasi morfologi, ekstraksi kontur, perhitungan *moments*, serta analisis *convexity defects* untuk membaca posisi dan kepalan tangan pemain.

---

## 🚀 Fitur Utama

- **🎮 Kontrol Gestur Tangan Real-time**: Menggunakan webcam untuk mendeteksi sarung tangan merah sebagai input kendali balok secara responsif.
  - **Geser Kiri / Kanan**: Memindahkan balok ke samping.
  - **Mengepal (Fist)**: Menjatuhkan balok seketika (*Hard Drop*).
- **🖥️ Halaman Awal (Landing Page) Interaktif**:
  - Tampilan menu bergaya *retro-arcade* yang elegan dan responsif.
  - Panel **Status Deteksi (Live)** yang menampilkan status koneksi webcam, posisi tangan, dan status kepalan secara langsung sebelum permainan dimulai.
  - Tombol **Start Game** dan **Exit** yang interaktif dengan efek *hover* dan navigasi kursor mouse.
- **🚪 Sinkronisasi Penutupan Dua Jendela (Synchronized Exit)**: Tombol Exit atau penutupan jendela manapun (Pygame maupun kamera OpenCV) akan menutup kedua jendela secara bersih tanpa meninggalkan proses menggantung di latar belakang.
- **🧱 Mekanika Tetris Lengkap**:
  - Mengadopsi sistem **7-Bag Randomizer** standar resmi Tetris untuk pengacakan balok yang adil.
  - *Ghost Piece* (bayangan balok transparan) untuk membantu akurasi penempatan balok.
  - Sistem perhitungan skor bertingkat (*leveling* & *line clearing score*).
  - Pratinjau balok berikutnya (*Next Piece Preview*).
  - Mekanisme *wall-kick* rotasi balok.
- **⌨️ Kontrol Hibrida (Keyboard Fallback)**: Pemain tetap dapat menggunakan keyboard (panah/WASD dan Spasi) sebagai kontrol alternatif atau pelengkap.

---

## 🔬 Pipeline Pengolahan Citra (Computer Vision)

Modul deteksi pada `Detect_Hand.py` bekerja melalui tahapan berikut:

```
[Frame Kamera] 
       │
       ▼
1. Mirroring (cv2.flip)
       │
       ▼
2. Konversi Ruang Warna (BGR ke HSV)
       │
       ▼
3. Segmentasi Warna Merah (Dual-Range Thresholding HSV)
       │
       ▼
4. Pembersihan Derau (Morfologi: cv2.MORPH_OPEN & cv2.MORPH_CLOSE)
       │
       ▼
5. Deteksi Kontur Terbesar (cv2.findContours)
       │
       ▼
6. Kalkulasi Titik Pusat (Image Moments cx, cy) ➔ Posisi Kiri / Tengah / Kanan
       │
       ▼
7. Analisis Convex Hull & Convexity Defects ➔ Hitung Lekukan Jari (Mengepal vs Terbuka)
```

1. **Segmentasi Warna Merah (HSV)**: Karena warna merah berada di dua ujung spektrum nilai Hue (0–10 dan 170–180), thresholding dilakukan menggunakan dua rentang dan digabungkan dengan operasi bitwise OR.
2. **Operasi Morfologi**: Menggunakan kernel elips untuk menghilangkan noise bintik kecil dan menutup celah pada kontur sarung tangan.
3. **Penentuan Posisi**: Titik berat ($c_x = \frac{M_{10}}{M_{00}}$) dihitung terhadap lebar frame untuk mengklasifikasikan posisi tangan (`KIRI` jika $< 0.35$, `KANAN` jika $> 0.65$, dan `TENGAH`).
4. **Deteksi Kepalan Tangan**: Menghitung jumlah sudut lancip ($< 90^\circ$) pada celah antar jari melalui *Convexity Defects*. Jika tidak ada lekukan jari terdeteksi, sistem menandainya sebagai kepalan (*fist*).

---

## 🛠️ Teknologi & Pustaka

| Kategori | Teknologi / Pustaka | Deskripsi |
| :--- | :--- | :--- |
| **Bahasa Pemrograman** | [Python 3.10+](https://www.python.org/) | Bahasa utama pengembangan game dan algoritma pengolahan citra. |
| **Computer Vision** | [OpenCV (opencv-python)](https://opencv.org/) | Menangani penangkapan video webcam, segmentasi citra, dan deteksi gestur. |
| **Game Engine / GUI** | [Pygame](https://www.pygame.org/) | Merender grafis permainan, antarmuka menu, dan penanganan event input. |
| **Komputasi Numerik** | [NumPy](https://numpy.org/) | Operasi matriks array citra dan perhitungan trigonometri vektor sudut jari. |
| **IDE & Tools** | VS Code / Git | Lingkungan pengembangan dan *version control*. |

---

## 📋 Prasyarat Sistem

Sebelum menjalankan proyek, pastikan sistem Anda memenuhi spesifikasi berikut:
- **Sistem Operasi**: Windows 10/11, macOS, atau Linux.
- **Python**: Versi 3.10 ke atas (direkomendasikan Python 3.11 – 3.13).
- **Perangkat Keras**: Kamera Web (Webcam terintegrasi atau eksternal) yang berfungsi baik.
- **Alat Pendukung**: Sarung tangan berwarna merah terang atau objek berwarna merah yang pas di tangan untuk hasil deteksi optimal.

---

## ⚙️ Panduan Instalasi & Menjalankan Aplikasi

### 1. Kloning Repositori
Buka terminal / PowerShell dan clone repositori ini:
```bash
git clone https://github.com/NabilZarif/Project-MINI-GAME-BASED-ON-HAND-COLOR.git
cd Project-MINI-GAME-BASED-ON-HAND-COLOR
```

### 2. Buat & Aktifkan Virtual Environment (Disarankan)
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Pasang Dependensi
Pasang semua pustaka yang dibutuhkan menggunakan `pip`:
```bash
pip install opencv-python pygame numpy
```

### 4. Menjalankan Aplikasi
Jalankan game Tetris dengan perintah berikut:
```bash
python tetris.py
```

*(Opsional)* Jika ingin menguji kalibrasi kamera dan deteksi sarung tangan merah secara mandiri:
```bash
python Detect_Hand.py
```

---

## 🎮 Panduan Kontrol

### 🖐️ Kontrol Gestur Tangan (Webcam)
| Gestur / Gerakan | Aksi pada Permainan |
| :--- | :--- |
| **Geser Tangan ke Kiri** | Menggeser balok 1 kolom ke kiri |
| **Geser Tangan ke Kanan** | Menggeser balok 1 kolom ke kanan |
| **Tangan Berada di Tengah** | Posisi netral / tahan posisi balok |
| **Mengepalkan Tangan (Fist)** | *Hard Drop* (Balok langsung dijatuhkan ke dasar) |

### ⌨️ Kontrol Keyboard & Mouse
| Tombol / Masukan | Aksi |
| :--- | :--- |
| **Klik Tombol "START GAME" / [ENTER] / [SPACE]** | Memulai permainan dari Halaman Awal |
| **Klik Tombol "EXIT" / [ESC] / [Q]** | Menutup kedua jendela aplikasi secara bersamaan |
| **Panah Kiri / Kanan** | Geser balok ke kiri / kanan (*Fallback*) |
| **Panah Atas / W** | Memutar rotasi balok (*Rotate*) |
| **Panah Bawah / S** | Menurunkan balok lebih cepat (*Soft Drop*) |
| **Spasi (Spacebar)** | Menjatuhkan balok langsung (*Hard Drop*) |
| **R** | Me-restart permainan (*Restart*) |
| **M / Klik "Menu Utama"** | Kembali ke Halaman Awal (Landing Page) |

---

## 📂 Struktur Direktori

```plaintext
Project-MINI-GAME-BASED-ON-HAND-COLOR/
├── .vscode/
│   └── settings.json        # Konfigurasi IDE VS Code
├── Detect_Hand.py           # Modul pengolahan citra & deteksi gestur sarung tangan (OpenCV)
├── tetris.py                # Game engine Tetris, Landing Page, dan antarmuka visual (Pygame)
├── README.md                # Dokumentasi lengkap proyek
└── .gitignore               # Daftar file yang diabaikan oleh Git
```

---

## 👤 Pengembang / Kontributor

Proyek ini disusun dan dikembangkan oleh:
- **Nama**: Moh Nabil Zarif Rofif
- **GitHub**: [@NabilZarif](https://github.com/NabilZarif)
- **Email**: mohnabilzarifrofif@gmail.com
- **Mata Kuliah**: Pengolahan Citra dan Video (PCV) - Project Batas Evaluasi Tengah Semester (ETS)

---

## 📄 Lisensi

Proyek ini didistribusikan untuk kepentingan akademis dan edukasi. Bebas digunakan, dipelajari, dan dikembangkan lebih lanjut dengan tetap mencantumkan atribusi kepada pengembang asli.
