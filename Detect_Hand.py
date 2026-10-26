# usingnamespace std
import cv2
import numpy as np

def hitung_jari(kontur):
    """Mendeteksi lekukan antar jari menggunakan Convexity Defects"""
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
                # Sela jari membentuk sudut lancip (< 90 derajat)
                if sudut <= np.pi / 2:
                    jumlah_jari += 1
            
            if jumlah_jari > 0:
                return jumlah_jari + 1
    return 0

def proses_tangan(frame):
    """
    Memproses frame kamera untuk mendeteksi sarung tangan merah di seluruh area layar.
    Mengembalikan: posisi (str), mengepal (bool), frame_visual
    """
    h, w, c = frame.shape
    posisi = "TENGAH"
    mengepal = False
    
    # 1. Konversi BGR ke HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 2. Segmentasi Warna Merah (Dua Rentang HSV)
    lower_red1 = np.array([0, 120, 70], dtype=np.uint8)
    upper_red1 = np.array([10, 255, 255], dtype=np.uint8)
    
    lower_red2 = np.array([170, 120, 70], dtype=np.uint8)
    upper_red2 = np.array([180, 255, 255], dtype=np.uint8)
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    # 3. Pembersihan Noise Morfologi
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 4. Ekstraksi Kontur Sarung Tangan
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        kontur_terbesar = max(contours, key=cv2.contourArea)
        # Ambang batas luas kontur agar serpihan kecil diabaikan
        if cv2.contourArea(kontur_terbesar) > 2500:
            cv2.drawContours(frame, [kontur_terbesar], -1, (0, 255, 0), 2)
            
            M = cv2.moments(kontur_terbesar)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cx, cy), 7, (255, 0, 0), -1)
                
                # Menentukan Posisi Kiri / Tengah / Kanan
                titik_pusat_x_rel = cx / w
                if titik_pusat_x_rel < 0.35:
                    posisi = "KIRI"
                elif titik_pusat_x_rel > 0.65:
                    posisi = "KANAN"
                else:
                    posisi = "TENGAH"
                    
                # Deteksi Kepalan
                jumlah_jari = hitung_jari(kontur_terbesar)
                mengepal = (jumlah_jari == 0)
                
                status_aksi = "JATUHKAN!" if mengepal else "Tahan"
                cv2.putText(frame, f"Posisi: {posisi}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.putText(frame, f"Aksi: {status_aksi}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255) if mengepal else (0, 255, 0), 2)
                cv2.putText(frame, f"Jari Terbuka: {jumlah_jari}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    return posisi, mengepal, frame

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    print("Menguji deteksi sarung tangan merah (Layar Penuh)...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        posisi, mengepal, frame_visual = proses_tangan(frame)
        
        cv2.imshow("Test Sarung Tangan Merah", frame_visual)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()