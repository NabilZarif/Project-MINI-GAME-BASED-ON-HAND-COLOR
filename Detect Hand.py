import cv2
import numpy as np

def hitung_jari(kontur):
    # Menggunakan Convex Hull dan Convexity Defects untuk menghitung jumlah jari yang terangkat
    hull = cv2.convexHull(kontur, returnPoints=False)
    if len(hull) > 3:
        defects = cv2.convexityDefects(kontur, hull)
        if defects is not None:
            jumlah_jari = 0
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i].flatten()
                start = tuple(kontur[s][0])
                end = tuple(kontur[e][0])
                far = tuple(kontur[f][0])
                
                # Menggunakan aturan kosinus untuk mencari sudut antar sela jari
                a = np.linalg.norm(np.array(start) - np.array(far))
                b = np.linalg.norm(np.array(end) - np.array(far))
                c = np.linalg.norm(np.array(start) - np.array(end))
                
                sudut = np.arccos((a**2 + b**2 - c**2) / (2 * a * b))
                
                # Jika sudut kurang dari 90 derajat, itu berarti ada sela antara jari
                if sudut <= np.pi / 2:
                    jumlah_jari += 1
            
            # Jumlah jari biasanya adalah jumlah sela + 1 (misal 4 sela = 5 jari)
            if jumlah_jari > 0:
                return jumlah_jari + 1
            else:
                return 0
    return 0

def main():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1) 
        h, w, c = frame.shape
        
        # --- 1. PREPROCESSING (Segmentasi Warna Kulit) ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # --- 2. TRIK: BLOKIR BAGIAN ATAS LAYAR (Tempat wajah berada) ---
        # Kita buat 40% bagian atas layar menjadi hitam agar tidak terdeteksi
        batas_atas = int(h * 0.45) # Anda bisa mengubah 0.45 (45%) sesuai kebutuhan
        mask[0:batas_atas, 0:w] = 0
        
        # Gambarkan garis pembatas di layar untuk panduan (Opsional)
        cv2.line(frame, (0, batas_atas), (w, batas_atas), (0, 0, 255), 2)
        cv2.putText(frame, "Area Wajah (Diabaikan)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "Area Tangan (Terdeteksi)", (10, batas_atas + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Operasi morfologi untuk membersihkan noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 100)
        
        # --- 3. MENCARI KONTUR TANGAN ---
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            kontur_terbesar = max(contours, key=cv2.contourArea)
            
            # Filter luas agar tangan yang dideteksi cukup besar
            if cv2.contourArea(kontur_terbesar) > 3000:
                cv2.drawContours(frame, [kontur_terbesar], -1, (0, 255, 0), 2)
                
                # --- 4. MENCARI PUSAT TANGAN (Untuk Posisi) ---
                M = cv2.moments(kontur_terbesar)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    cv2.circle(frame, (cx, cy), 7, (255, 0, 0), -1)
                    
                    titik_pusat_x_rel = cx / w
                    if titik_pusat_x_rel < 0.35:
                        posisi = "KIRI"
                    elif titik_pusat_x_rel > 0.65:
                        posisi = "KANAN"
                    else:
                        posisi = "TENGAH"
                        
                    # --- 5. DETEKSI KEPALAN ---
                    jumlah_jari_terbuka = hitung_jari(kontur_terbesar)
                    mengepal = (jumlah_jari_terbuka == 0)
                    
                    status_aksi = "JATUHKAN!" if mengepal else "Tahan"

                    cv2.putText(frame, f"Posisi: {posisi}", (20, batas_atas + 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    
                    warna_teks_aksi = (0, 0, 255) if mengepal else (0, 255, 0)
                    cv2.putText(frame, f"Aksi: {status_aksi}", (20, batas_atas + 120), cv2.FONT_HERSHEY_SIMPLEX, 1, warna_teks_aksi, 2)
                    cv2.putText(frame, f"Jari: {jumlah_jari_terbuka}", (20, batas_atas + 170), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow('Prototipe Deteksi Tangan Tetris', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
