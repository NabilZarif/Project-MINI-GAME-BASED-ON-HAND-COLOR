# usingnamespace std
import cv2
# pyrefly: ignore [missing-import]
import pygame
import sys
# Mengimpor fungsi dari file deteksi tangan milikmu
from Detect_Hand import proses_tangan 

def main():
    # Inisialisasi Pygame (Untuk jendela Tetris nanti)
    pygame.init()
    LAYAR_LEBAR, LAYAR_TINGGI = 300, 600
    screen = pygame.display.set_mode((LAYAR_LEBAR, LAYAR_TINGGI))
    pygame.display.set_caption("Tetris Kontrol Tangan")
    clock = pygame.time.Clock()

    # Inisialisasi Kamera
    cap = cv2.VideoCapture(0)

    while True:
        # --- 1. PROSES INPUT KAMERA ---
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1) # Mirror
        
        # Masukkan frame ke modul deteksi tanganmu
        posisi, mengepal, frame_visual = proses_tangan(frame)

        # --- 2. LOGIKA GAME TETRIS (Akan dikembangkan di sini) ---
        # Contoh penggunaan data dari kamera:
        # if posisi == "KIRI": 
        #     geser_balok_kiri()
        # elif mengepal == True:
        #     jatuhkan_balok()

        # --- 3. RENDER VISUAL ---
        # A. Update jendela Tetris (Pygame)
        screen.fill((0, 0, 0)) # Layar hitam sementara
        # pygame.draw... (gambar grid dan balok di sini nanti)
        pygame.display.flip()

        # B. Tampilkan jendela Kamera (OpenCV)
        cv2.imshow("Kamera Kontrol", frame_visual)

        # Penutup program
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                sys.exit()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        clock.tick(30) # Batasi 30 Frame per detik

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()