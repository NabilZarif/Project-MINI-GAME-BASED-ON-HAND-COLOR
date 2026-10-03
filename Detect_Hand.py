# usingnamespace std
import cv2
import numpy as np

def hitung_jari(kontur):
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
                
                a = np.linalg.norm(np.array(start) - np.array(far))
                b = np.linalg.norm(np.array(end) - np.array(far))
                c = np.linalg.norm(np.array(start) - np.array(end))
                
                sudut = np.arccos((a**2 + b**2 - c**2) / (2 * a * b))
                if sudut <= np.pi / 2:
                    jumlah_jari += 1
            
            if jumlah_jari > 0:
                return jumlah_jari + 1
    return 0

def proses_tangan(frame):
    """
    Menerima frame dari kamera utama (di game Tetris),
    memproses deteksi warna, dan mengembalikan kontrol.
    """
    h, w, c = frame.shape
    posisi = "TENGAH"
    mengepal = False
    
    # Preprocessing
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    # Blokir area atas
    batas_atas = int(h * 0.45)
    mask[0:batas_atas, 0:w] = 0
    cv2.line(frame, (0, batas_atas), (w, batas_atas), (0, 0, 255), 2)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.GaussianBlur(mask, (5, 5), 100)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        kontur_terbesar = max(contours, key=cv2.contourArea)
        if cv2.contourArea(kontur_terbesar) > 3000:
            cv2.drawContours(frame, [kontur_terbesar], -1, (0, 255, 0), 2)
            
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
                    
                jumlah_jari_terbuka = hitung_jari(kontur_terbesar)
                mengepal = (jumlah_jari_terbuka == 0)
                
                status_aksi = "JATUHKAN!" if mengepal else "Tahan"
                cv2.putText(frame, f"Posisi: {posisi}", (20, batas_atas + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.putText(frame, f"Aksi: {status_aksi}", (20, batas_atas + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255) if mengepal else (0, 255, 0), 2)

    return posisi, mengepal, frame