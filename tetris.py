# usingnamespace std
import cv2
import pygame
import sys
import random
import numpy as np

# Mengimpor fungsi dari file deteksi tangan
from Detect_Hand import proses_tangan 

# Config & Konstanta Game
GRID_LEBAR = 10
GRID_TINGGI = 20
UKURAN_BLOK = 30

PANEL_LEBAR = 180
LAYAR_LEBAR = GRID_LEBAR * UKURAN_BLOK + PANEL_LEBAR
LAYAR_TINGGI = GRID_TINGGI * UKURAN_BLOK

# Warna Hex / RGB
WARNA_BACKGROUND = (15, 15, 25)
WARNA_GRID = (30, 30, 45)
WARNA_PANEL = (25, 25, 40)
WARNA_TEXT = (240, 240, 240)
WARNA_BORDER = (60, 60, 90)

WARNA_TETROMINO = {
    'I': (0, 240, 240),    # Cyan
    'J': (40, 100, 240),   # Blue
    'L': (240, 160, 0),    # Orange
    'O': (240, 240, 0),    # Yellow
    'S': (0, 240, 100),    # Green
    'T': (160, 40, 240),   # Purple
    'Z': (240, 50, 50)     # Red
}

BENTUK_TETROMINO = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}

class Tetromino:
    def __init__(self, jenis):
        self.jenis = jenis
        self.bentuk = [row[:] for row in BENTUK_TETROMINO[jenis]]
        self.warna = WARNA_TETROMINO[jenis]
        self.x = GRID_LEBAR // 2 - len(self.bentuk[0]) // 2
        self.y = 0

    def putar(self):
        # Transpose & Reverse untuk rotasi 90 derajat searah jarum jam
        self.bentuk = [list(row) for row in zip(*self.bentuk[::-1])]

    def putar_balik(self):
        # Rotasi berlawanan jarum jam jika tabrakan
        for _ in range(3):
            self.putar()

class TetrisGame:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_LEBAR)] for _ in range(GRID_TINGGI)]
        self.kantong_balok = []
        self.balok_aktif = self.balok_baru()
        self.balok_selanjutnya = self.balok_baru()
        self.skor = 0
        self.level = 1
        self.baris_dihapus = 0
        self.game_over = False

    def balok_baru(self):
        # Menggunakan sistem 7-Bag Randomizer (Standar Resmi Tetris)
        # Mengacak 7 variasi balok dalam 1 kantong agar distribusi merata
        if not self.kantong_balok:
            self.kantong_balok = list(BENTUK_TETROMINO.keys())
            random.shuffle(self.kantong_balok)
        jenis = self.kantong_balok.pop()
        return Tetromino(jenis)

    def cek_tabrakan(self, balok, offset_x=0, offset_y=0):
        for r, row in enumerate(balok.bentuk):
            for c, val in enumerate(row):
                if val:
                    new_x = balok.x + c + offset_x
                    new_y = balok.y + r + offset_y
                    if new_x < 0 or new_x >= GRID_LEBAR or new_y >= GRID_TINGGI:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x] is not None:
                        return True
        return False

    def kunci_balok(self):
        for r, row in enumerate(self.balok_aktif.bentuk):
            for c, val in enumerate(row):
                if val:
                    grid_y = self.balok_aktif.y + r
                    grid_x = self.balok_aktif.x + c
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.balok_aktif.warna

        self.hapus_baris_penuh()
        self.balok_aktif = self.balok_selanjutnya
        self.balok_selanjutnya = self.balok_baru()

        # Cek Game Over
        if self.cek_tabrakan(self.balok_aktif):
            self.game_over = True

    def hapus_baris_penuh(self):
        baris_baru = [row for row in self.grid if any(cell is None for cell in row)]
        jumlah_dihapus = GRID_TINGGI - len(baris_baru)

        if jumlah_dihapus > 0:
            for _ in range(jumlah_dihapus):
                baris_baru.insert(0, [None for _ in range(GRID_LEBAR)])
            self.grid = baris_baru
            
            # Sistem Skor
            poin = {1: 100, 2: 300, 3: 500, 4: 800}
            self.skor += poin.get(jumlah_dihapus, 100 * jumlah_dihapus) * self.level
            self.baris_dihapus += jumlah_dihapus
            self.level = (self.baris_dihapus // 10) + 1

    def geser(self, dx):
        if not self.game_over and not self.cek_tabrakan(self.balok_aktif, offset_x=dx):
            self.balok_aktif.x += dx
            return True
        return False

    def turunkan(self):
        if not self.game_over:
            if not self.cek_tabrakan(self.balok_aktif, offset_y=1):
                self.balok_aktif.y += 1
                return True
            else:
                self.kunci_balok()
                return False
        return False

    def jatuhkan_langsung(self):
        if not self.game_over:
            while not self.cek_tabrakan(self.balok_aktif, offset_y=1):
                self.balok_aktif.y += 1
            self.kunci_balok()

    def rotasi(self):
        if not self.game_over:
            self.balok_aktif.putar()
            if self.cek_tabrakan(self.balok_aktif):
                # Wall kick sederhana (coba geser 1 step kiri/kanan)
                if not self.cek_tabrakan(self.balok_aktif, offset_x=-1):
                    self.balok_aktif.x -= 1
                elif not self.cek_tabrakan(self.balok_aktif, offset_x=1):
                    self.balok_aktif.x += 1
                else:
                    self.balok_aktif.putar_balik()

def menggambar_blok(screen, x, y, warna, alpha=255):
    rect = pygame.Rect(x, y, UKURAN_BLOK, UKURAN_BLOK)
    if alpha < 255:
        s = pygame.Surface((UKURAN_BLOK, UKURAN_BLOK), pygame.SRCALPHA)
        s.fill((*warna, alpha))
        screen.blit(s, (x, y))
        pygame.draw.rect(screen, (255, 255, 255, alpha // 2), (x, y, UKURAN_BLOK, UKURAN_BLOK), 1)
    else:
        pygame.draw.rect(screen, warna, rect)
        # Bevel highlight
        pygame.draw.rect(screen, (min(255, warna[0]+50), min(255, warna[1]+50), min(255, warna[2]+50)), rect, 2)

def main():
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((LAYAR_LEBAR, LAYAR_TINGGI))
    pygame.display.set_caption("Tetris Kontrol Tangan - ETS PCV")
    clock = pygame.time.Clock()
    
    font_besar = pygame.font.SysFont("Arial", 28, bold=True)
    font_sedang = pygame.font.SysFont("Arial", 20, bold=True)
    font_kecil = pygame.font.SysFont("Arial", 16)

    cap = cv2.VideoCapture(0)
    game = TetrisGame()

    # Kontrol Timing
    kecepatan_turun = 600 # ms per langkah otomatis
    terakhir_turun = pygame.time.get_ticks()
    
    # Cooldown Gestur Tangan
    cooldown_geser = 180 # ms
    terakhir_geser = 0
    
    cooldown_jatuh = 500 # ms untuk mengepal (hard drop)
    terakhir_jatuh = 0
    mengepal_sebelumnya = False

    posisi_tangan_saat_ini = "TENGAH"
    mengepal_saat_ini = False

    print("Memulai game Tetris dengan Kontrol Tangan...")

    while True:
        waktu_sekarang = pygame.time.get_ticks()

        # --- 1. AMBIL INPUT KAMERA ---
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1) # Mirror
            posisi_tangan_saat_ini, mengepal_saat_ini, frame_visual = proses_tangan(frame)
            cv2.imshow("Kamera Kontrol (Tekan 'q' untuk keluar)", frame_visual)
        
        # --- 2. RESPON KONTROL GESTUR TANGAN ---
        if not game.game_over:
            # A. Geser Kiri / Kanan
            if waktu_sekarang - terakhir_geser > cooldown_geser:
                if posisi_tangan_saat_ini == "KIRI":
                    if game.geser(-1):
                        terakhir_geser = waktu_sekarang
                elif posisi_tangan_saat_ini == "KANAN":
                    if game.geser(1):
                        terakhir_geser = waktu_sekarang

            # B. Hard Drop jika tangan MENGEPAL
            if mengepal_saat_ini and not mengepal_sebelumnya:
                if waktu_sekarang - terakhir_jatuh > cooldown_jatuh:
                    game.jatuhkan_langsung()
                    terakhir_jatuh = waktu_sekarang
            
            mengepal_sebelumnya = mengepal_saat_ini

        # --- 3. INPUT KEYBOARD (SUPLEMEN / FALLBACK) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.geser(-1)
                elif event.key == pygame.K_RIGHT:
                    game.geser(1)
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    game.rotasi()
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    game.turunkan()
                elif event.key == pygame.K_SPACE:
                    game.jatuhkan_langsung()
                elif event.key == pygame.K_r:
                    game = TetrisGame()

        # --- 4. GRAVITASI OTOMATIS (TURUN BERKALA) ---
        leveled_speed = max(100, kecepatan_turun - (game.level - 1) * 50)
        if waktu_sekarang - terakhir_turun > leveled_speed:
            game.turunkan()
            terakhir_turun = waktu_sekarang

        # --- 5. RENDER GRAPHICS ---
        screen.fill(WARNA_BACKGROUND)

        # Gambar Grid Background & Pembatas
        grid_pix_w = GRID_LEBAR * UKURAN_BLOK
        pygame.draw.rect(screen, WARNA_PANEL, (grid_pix_w, 0, PANEL_LEBAR, LAYAR_TINGGI))
        pygame.draw.line(screen, WARNA_BORDER, (grid_pix_w, 0), (grid_pix_w, LAYAR_TINGGI), 3)

        for y in range(GRID_TINGGI):
            for x in range(GRID_LEBAR):
                pygame.draw.rect(screen, WARNA_GRID, (x * UKURAN_BLOK, y * UKURAN_BLOK, UKURAN_BLOK, UKURAN_BLOK), 1)

        # Gambar Balok Terkunci di Grid
        for y in range(GRID_TINGGI):
            for x in range(GRID_LEBAR):
                warna = game.grid[y][x]
                if warna:
                    menggambar_blok(screen, x * UKURAN_BLOK, y * UKURAN_BLOK, warna)

        # Gambar Bayangan / Ghost Piece (Tanda Balok Jatuh)
        if not game.game_over:
            ghost_y = 0
            while not game.cek_tabrakan(game.balok_aktif, offset_y=ghost_y + 1):
                ghost_y += 1
            
            for r, row in enumerate(game.balok_aktif.bentuk):
                for c, val in enumerate(row):
                    if val:
                        gx = (game.balok_aktif.x + c) * UKURAN_BLOK
                        gy = (game.balok_aktif.y + r + ghost_y) * UKURAN_BLOK
                        menggambar_blok(screen, gx, gy, game.balok_aktif.warna, alpha=80)

            # Gambar Balok Aktif
            for r, row in enumerate(game.balok_aktif.bentuk):
                for c, val in enumerate(row):
                    if val:
                        bx = (game.balok_aktif.x + c) * UKURAN_BLOK
                        by = (game.balok_aktif.y + r) * UKURAN_BLOK
                        if by >= 0:
                            menggambar_blok(screen, bx, by, game.balok_aktif.warna)

        # --- PANEL INFORMASI DI KANAN ---
        px = grid_pix_w + 15
        
        # Title
        txt_title = font_sedang.render("TETRIS", True, (0, 240, 240))
        screen.blit(txt_title, (px, 15))

        # Skor & Level
        screen.blit(font_kecil.render(f"Skor: {game.skor}", True, WARNA_TEXT), (px, 55))
        screen.blit(font_kecil.render(f"Level: {game.level}", True, WARNA_TEXT), (px, 80))
        screen.blit(font_kecil.render(f"Baris: {game.baris_dihapus}", True, WARNA_TEXT), (px, 105))

        # Preview Balok Selanjutnya
        screen.blit(font_kecil.render("Berikutnya:", True, WARNA_TEXT), (px, 145))
        box_rect = pygame.Rect(px, 170, 140, 90)
        pygame.draw.rect(screen, (35, 35, 55), box_rect)
        pygame.draw.rect(screen, WARNA_BORDER, box_rect, 1)

        b_next = game.balok_selanjutnya
        offset_nx = px + (140 - len(b_next.bentuk[0]) * UKURAN_BLOK) // 2
        offset_ny = 170 + (90 - len(b_next.bentuk) * UKURAN_BLOK) // 2
        for r, row in enumerate(b_next.bentuk):
            for c, val in enumerate(row):
                if val:
                    menggambar_blok(screen, offset_nx + c * UKURAN_BLOK, offset_ny + r * UKURAN_BLOK, b_next.warna)

        # Status Deteksi Tangan Realtime
        screen.blit(font_kecil.render("Status Tangan:", True, (255, 200, 0)), (px, 280))
        
        warna_pos = (0, 255, 0) if posisi_tangan_saat_ini != "TENGAH" else (200, 200, 200)
        screen.blit(font_kecil.render(f"Posisi: {posisi_tangan_saat_ini}", True, warna_pos), (px, 305))
        
        warna_gep = (255, 50, 50) if mengepal_saat_ini else (100, 255, 100)
        status_gep = "JATUHKAN!" if mengepal_saat_ini else "Tahan"
        screen.blit(font_kecil.render(f"Aksi: {status_gep}", True, warna_gep), (px, 330))

        # Petunjuk Kontrol
        pygame.draw.line(screen, WARNA_BORDER, (px, 365), (px + 150, 365), 1)
        screen.blit(font_kecil.render("Petunjuk:", True, (180, 180, 220)), (px, 375))
        screen.blit(font_kecil.render("• Tangan Kiri/Kanan", True, (150, 150, 170)), (px, 400))
        screen.blit(font_kecil.render("  = Geser Balok", True, (150, 150, 170)), (px, 420))
        screen.blit(font_kecil.render("• Tangan Mengepal", True, (150, 150, 170)), (px, 445))
        screen.blit(font_kecil.render("  = Hard Drop", True, (150, 150, 170)), (px, 465))
        screen.blit(font_kecil.render("• W / Panah Atas", True, (150, 150, 170)), (px, 490))
        screen.blit(font_kecil.render("  = Putar Balok", True, (150, 150, 170)), (px, 510))
        screen.blit(font_kecil.render("• 'R' = Restart Game", True, (150, 150, 170)), (px, 535))

        # Tampilan Game Over
        if game.game_over:
            overlay = pygame.Surface((LAYAR_LEBAR, LAYAR_TINGGI), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            go_txt = font_besar.render("GAME OVER", True, (255, 50, 50))
            screen.blit(go_txt, (LAYAR_LEBAR // 2 - go_txt.get_width() // 2, 230))
            
            res_txt = font_sedang.render("Tekan 'R' untuk Main Lagi", True, (240, 240, 240))
            screen.blit(res_txt, (LAYAR_LEBAR // 2 - res_txt.get_width() // 2, 280))

        pygame.display.flip()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        clock.tick(30) # 30 FPS

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()
