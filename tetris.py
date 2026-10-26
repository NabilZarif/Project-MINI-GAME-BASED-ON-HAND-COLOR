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

def tutup_aplikasi(cap):
    """Menutup kedua window (OpenCV kamera & Pygame game) serta melepaskan resource."""
    if cap is not None and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

def gambar_tombol(surface, rect, teks, subteks, font_utama, font_sub, warna_bg, warna_border, warna_teks, hover=False):
    """Menggambar tombol modern dengan rounded corner, efek hover, dan border."""
    if hover:
        # Efek glowing border
        glow_rect = rect.inflate(4, 4)
        pygame.draw.rect(surface, (max(0, warna_border[0]//3), max(0, warna_border[1]//3), max(0, warna_border[2]//3)), glow_rect, border_radius=12)

    pygame.draw.rect(surface, warna_bg, rect, border_radius=10)
    pygame.draw.rect(surface, warna_border, rect, 2 if hover else 1, border_radius=10)

    if subteks:
        txt_surf = font_utama.render(teks, True, warna_teks)
        txt_rect = txt_surf.get_rect(center=(rect.centerx, rect.centery - 10))
        surface.blit(txt_surf, txt_rect)

        sub_surf = font_sub.render(subteks, True, (210, 210, 220))
        sub_rect = sub_surf.get_rect(center=(rect.centerx, rect.centery + 12))
        surface.blit(sub_surf, sub_rect)
    else:
        txt_surf = font_utama.render(teks, True, warna_teks)
        txt_rect = txt_surf.get_rect(center=rect.center)
        surface.blit(txt_surf, txt_rect)

def main():
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((LAYAR_LEBAR, LAYAR_TINGGI))
    pygame.display.set_caption("Tetris Kontrol Tangan - ETS PCV")
    clock = pygame.time.Clock()
    
    font_judul = pygame.font.SysFont("Arial", 44, bold=True)
    font_besar = pygame.font.SysFont("Arial", 26, bold=True)
    font_sedang = pygame.font.SysFont("Arial", 19, bold=True)
    font_kecil = pygame.font.SysFont("Arial", 15)
    font_mini = pygame.font.SysFont("Arial", 12)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Peringatan: Kamera tidak dapat dibuka. Kontrol keyboard tetap aktif.")

    game = TetrisGame()
    state = "LANDING" # "LANDING" (Halaman Utama) atau "PLAYING" (Sedang Main)
    kamera_jendela_aktif = False

    # Kontrol Timing Permainan
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

    # Definisi Tombol Landing Page
    tombol_start_rect = pygame.Rect(75, 415, 330, 56)
    tombol_exit_rect = pygame.Rect(75, 485, 330, 50)

    # Definisi Tombol Game Over
    btn_restart_rect = pygame.Rect(LAYAR_LEBAR // 2 - 130, 310, 260, 38)
    btn_menu_rect = pygame.Rect(LAYAR_LEBAR // 2 - 130, 355, 260, 38)
    btn_exit_game_rect = pygame.Rect(LAYAR_LEBAR // 2 - 130, 400, 260, 38)

    # Definisi Tombol Panel Menu (saat bermain)
    grid_pix_w = GRID_LEBAR * UKURAN_BLOK
    px = grid_pix_w + 15
    btn_panel_menu_rect = pygame.Rect(px, 555, 150, 32)

    print("Memulai Tetris dengan Landing Page & Kontrol Tangan...")

    while True:
        waktu_sekarang = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        hover_ditemukan = False

        # --- 1. AMBIL INPUT KAMERA ---
        ret = False
        if cap is not None and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1) # Mirror
                posisi_tangan_saat_ini, mengepal_saat_ini, frame_visual = proses_tangan(frame)
                cv2.imshow("Kamera Kontrol (Tekan 'q' untuk keluar)", frame_visual)
                kamera_jendela_aktif = True

        # Deteksi jika window OpenCV ditutup secara manual (tombol 'X')
        if kamera_jendela_aktif:
            try:
                if cv2.getWindowProperty("Kamera Kontrol (Tekan 'q' untuk keluar)", cv2.WND_PROP_VISIBLE) < 1:
                    tutup_aplikasi(cap)
            except Exception:
                pass

        # OpenCV waitKey untuk keyboard 'q' pada window kamera
        if cv2.waitKey(1) & 0xFF == ord('q'):
            tutup_aplikasi(cap)

        # ==============================================================
        # --- STATE A: LANDING PAGE (HALAMAN AWAL) ---
        # ==============================================================
        if state == "LANDING":
            is_hover_start = tombol_start_rect.collidepoint(mouse_pos)
            is_hover_exit = tombol_exit_rect.collidepoint(mouse_pos)
            if is_hover_start or is_hover_exit:
                hover_ditemukan = True

            # Event Handling Landing Page
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    tutup_aplikasi(cap)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if tombol_start_rect.collidepoint(event.pos):
                        state = "PLAYING"
                        game = TetrisGame()
                        terakhir_turun = pygame.time.get_ticks()
                    elif tombol_exit_rect.collidepoint(event.pos):
                        tutup_aplikasi(cap)
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = "PLAYING"
                        game = TetrisGame()
                        terakhir_turun = pygame.time.get_ticks()
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        tutup_aplikasi(cap)

            # Gambar Landing Page
            screen.fill(WARNA_BACKGROUND)

            # Dekorasi Balok Latar Belakang (Transparan)
            dekorasi_balok = [
                ('T', 35, 55),
                ('I', 385, 75),
                ('O', 40, 480),
                ('S', 390, 460)
            ]
            for jenis, dx, dy in dekorasi_balok:
                bentuk = BENTUK_TETROMINO[jenis]
                warna = WARNA_TETROMINO[jenis]
                for r, row in enumerate(bentuk):
                    for c, val in enumerate(row):
                        if val:
                            menggambar_blok(screen, dx + c * UKURAN_BLOK, dy + r * UKURAN_BLOK, warna, alpha=35)

            # Badge Header
            badge_rect = pygame.Rect(LAYAR_LEBAR // 2 - 140, 22, 280, 24)
            pygame.draw.rect(screen, (30, 35, 55), badge_rect, border_radius=12)
            pygame.draw.rect(screen, (70, 130, 180), badge_rect, 1, border_radius=12)
            txt_badge = font_mini.render("PROYEK ETS PENGOLAHAN CITRA & VIDEO", True, (120, 200, 255))
            screen.blit(txt_badge, txt_badge.get_rect(center=badge_rect.center))

            # Judul Utama TETRIS dengan Efek Bayangan
            txt_shadow = font_judul.render("TETRIS", True, (20, 50, 80))
            screen.blit(txt_shadow, txt_shadow.get_rect(center=(LAYAR_LEBAR // 2 + 3, 73 + 3)))

            txt_title = font_judul.render("TETRIS", True, (0, 240, 240))
            screen.blit(txt_title, txt_title.get_rect(center=(LAYAR_LEBAR // 2, 73)))

            txt_subjudul = font_sedang.render("HAND GESTURE CONTROL", True, (255, 215, 0))
            screen.blit(txt_subjudul, txt_subjudul.get_rect(center=(LAYAR_LEBAR // 2, 115)))

            # --- KARTU 1: STATUS DETEKSI SENSOR REALTIME ---
            card_sensor = pygame.Rect(45, 145, 390, 105)
            pygame.draw.rect(screen, (22, 22, 38), card_sensor, border_radius=10)
            pygame.draw.rect(screen, (55, 55, 85), card_sensor, 1, border_radius=10)

            txt_card1_header = font_kecil.render("STATUS KAMERA & SENSOR GESTUR", True, (200, 220, 255))
            screen.blit(txt_card1_header, (60, 155))
            pygame.draw.line(screen, (55, 55, 85), (60, 177), (415, 177), 1)

            # Status Kamera
            status_cam = "Aktif (30 FPS)" if ret else "Mencari Kamera..."
            cam_col = (0, 255, 120) if ret else (255, 100, 100)
            pygame.draw.circle(screen, cam_col, (68, 195), 5)
            screen.blit(font_mini.render(f"Kamera           : {status_cam}", True, WARNA_TEXT), (82, 187))

            # Status Posisi Tangan
            pos_col = (0, 255, 200) if posisi_tangan_saat_ini != "TENGAH" else (170, 170, 190)
            screen.blit(font_mini.render(f"Posisi Deteksi : {posisi_tangan_saat_ini}", True, pos_col), (82, 207))

            # Status Aksi Kepalan
            status_kepal = "JATUHKAN (Mengepal)" if mengepal_saat_ini else "Terbuka (Tahan)"
            kepal_col = (255, 70, 70) if mengepal_saat_ini else (100, 255, 100)
            screen.blit(font_mini.render(f"Status Gestur  : {status_kepal}", True, kepal_col), (82, 227))

            # --- KARTU 2: PANDUAN KONTROL ---
            card_ctrl = pygame.Rect(45, 265, 390, 130)
            pygame.draw.rect(screen, (22, 22, 38), card_ctrl, border_radius=10)
            pygame.draw.rect(screen, (55, 55, 85), card_ctrl, 1, border_radius=10)

            txt_card2_header = font_kecil.render("PANDUAN KONTROL PERMAINAN", True, (255, 215, 100))
            screen.blit(txt_card2_header, (60, 275))
            pygame.draw.line(screen, (55, 55, 85), (60, 297), (415, 297), 1)

            screen.blit(font_mini.render("• Tangan Kiri / Kanan   : Geser Balok ke Samping", True, (200, 200, 220)), (65, 307))
            screen.blit(font_mini.render("• Kepalkan Tangan       : Hard Drop (Balok Langsung Jatuh)", True, (200, 200, 220)), (65, 327))
            screen.blit(font_mini.render("• Tombol W / Panah Atas : Putar Rotasi Balok", True, (200, 200, 220)), (65, 347))
            screen.blit(font_mini.render("• Gunakan Sarung Tangan Merah agar deteksi akurat", True, (255, 140, 140)), (65, 367))

            # --- TOMBOL INTERAKTIF ---
            col_start_bg = (24, 160, 95) if is_hover_start else (16, 120, 70)
            col_start_border = (50, 255, 160) if is_hover_start else (30, 180, 110)
            gambar_tombol(screen, tombol_start_rect, "▶  START GAME", "Klik atau Tekan [ ENTER ]",
                         font_sedang, font_mini, col_start_bg, col_start_border, (255, 255, 255), is_hover_start)

            col_exit_bg = (175, 35, 45) if is_hover_exit else (125, 25, 35)
            col_exit_border = (255, 80, 95) if is_hover_exit else (180, 45, 55)
            gambar_tombol(screen, tombol_exit_rect, "✕  EXIT", "Tutup Game & Kamera [ ESC ]",
                         font_sedang, font_mini, col_exit_bg, col_exit_border, (255, 255, 255), is_hover_exit)

            # Footer
            txt_footer = font_mini.render("Tekan 'q' pada kamera atau tombol Exit untuk keluar.", True, (120, 120, 140))
            screen.blit(txt_footer, txt_footer.get_rect(center=(LAYAR_LEBAR // 2, 565)))

        # ==============================================================
        # --- STATE B: PLAYING (GAMEPLAY TETRIS) ---
        # ==============================================================
        elif state == "PLAYING":
            is_hover_panel_menu = btn_panel_menu_rect.collidepoint(mouse_pos)
            if is_hover_panel_menu:
                hover_ditemukan = True

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

            # --- 3. INPUT KEYBOARD & MOUSE ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    tutup_aplikasi(cap)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_panel_menu_rect.collidepoint(event.pos):
                        state = "LANDING"
                    elif game.game_over:
                        if btn_restart_rect.collidepoint(event.pos):
                            game = TetrisGame()
                        elif btn_menu_rect.collidepoint(event.pos):
                            state = "LANDING"
                        elif btn_exit_game_rect.collidepoint(event.pos):
                            tutup_aplikasi(cap)
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
                    elif event.key == pygame.K_m and game.game_over:
                        state = "LANDING"
                    elif event.key == pygame.K_ESCAPE:
                        state = "LANDING"

            # --- 4. GRAVITASI OTOMATIS (TURUN BERKALA) ---
            leveled_speed = max(100, kecepatan_turun - (game.level - 1) * 50)
            if waktu_sekarang - terakhir_turun > leveled_speed:
                game.turunkan()
                terakhir_turun = waktu_sekarang

            # --- 5. RENDER GRAPHICS GAMEPLAY ---
            screen.fill(WARNA_BACKGROUND)

            # Gambar Grid Background & Pembatas
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
            # Title
            txt_title = font_sedang.render("TETRIS", True, (0, 240, 240))
            screen.blit(txt_title, (px, 15))

            # Skor & Level
            screen.blit(font_kecil.render(f"Skor: {game.skor}", True, WARNA_TEXT), (px, 50))
            screen.blit(font_kecil.render(f"Level: {game.level}", True, WARNA_TEXT), (px, 73))
            screen.blit(font_kecil.render(f"Baris: {game.baris_dihapus}", True, WARNA_TEXT), (px, 96))

            # Preview Balok Selanjutnya
            screen.blit(font_kecil.render("Berikutnya:", True, WARNA_TEXT), (px, 130))
            box_rect = pygame.Rect(px, 152, 140, 80)
            pygame.draw.rect(screen, (35, 35, 55), box_rect)
            pygame.draw.rect(screen, WARNA_BORDER, box_rect, 1)

            b_next = game.balok_selanjutnya
            offset_nx = px + (140 - len(b_next.bentuk[0]) * UKURAN_BLOK) // 2
            offset_ny = 152 + (80 - len(b_next.bentuk) * UKURAN_BLOK) // 2
            for r, row in enumerate(b_next.bentuk):
                for c, val in enumerate(row):
                    if val:
                        menggambar_blok(screen, offset_nx + c * UKURAN_BLOK, offset_ny + r * UKURAN_BLOK, b_next.warna)

            # Status Deteksi Tangan Realtime
            screen.blit(font_kecil.render("Status Tangan:", True, (255, 200, 0)), (px, 245))
            
            warna_pos = (0, 255, 0) if posisi_tangan_saat_ini != "TENGAH" else (200, 200, 200)
            screen.blit(font_mini.render(f"Posisi: {posisi_tangan_saat_ini}", True, warna_pos), (px, 270))
            
            warna_gep = (255, 50, 50) if mengepal_saat_ini else (100, 255, 100)
            status_gep = "JATUHKAN!" if mengepal_saat_ini else "Tahan"
            screen.blit(font_mini.render(f"Aksi: {status_gep}", True, warna_gep), (px, 292))

            # Petunjuk Kontrol Singkat
            pygame.draw.line(screen, WARNA_BORDER, (px, 320), (px + 150, 320), 1)
            screen.blit(font_kecil.render("Petunjuk:", True, (180, 180, 220)), (px, 330))
            screen.blit(font_mini.render("• Tangan Kiri/Kanan", True, (150, 150, 170)), (px, 352))
            screen.blit(font_mini.render("  = Geser Balok", True, (150, 150, 170)), (px, 370))
            screen.blit(font_mini.render("• Tangan Mengepal", True, (150, 150, 170)), (px, 392))
            screen.blit(font_mini.render("  = Hard Drop", True, (150, 150, 170)), (px, 410))
            screen.blit(font_mini.render("• W / Panah Atas", True, (150, 150, 170)), (px, 432))
            screen.blit(font_mini.render("  = Putar Balok", True, (150, 150, 170)), (px, 450))
            screen.blit(font_mini.render("• 'R' = Restart", True, (150, 150, 170)), (px, 475))
            screen.blit(font_mini.render("• 'ESC' = Menu", True, (150, 150, 170)), (px, 497))

            # Tombol Menu di Panel Bawah
            gambar_tombol(screen, btn_panel_menu_rect, "Menu [ESC]", None, font_mini, font_mini,
                         (45, 50, 75) if is_hover_panel_menu else (30, 35, 55),
                         (90, 120, 180) if is_hover_panel_menu else (55, 65, 95), (255, 255, 255), is_hover_panel_menu)

            # Tampilan Game Over dengan Tombol Interaktif
            if game.game_over:
                overlay = pygame.Surface((LAYAR_LEBAR, LAYAR_TINGGI), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 215))
                screen.blit(overlay, (0, 0))
                
                go_txt = font_besar.render("GAME OVER", True, (255, 50, 50))
                screen.blit(go_txt, go_txt.get_rect(center=(LAYAR_LEBAR // 2, 190)))
                
                skor_txt = font_sedang.render(f"Skor Akhir: {game.skor}", True, (255, 215, 0))
                screen.blit(skor_txt, skor_txt.get_rect(center=(LAYAR_LEBAR // 2, 230)))

                lvl_txt = font_kecil.render(f"Level: {game.level}  |  Baris Dihapus: {game.baris_dihapus}", True, WARNA_TEXT)
                screen.blit(lvl_txt, lvl_txt.get_rect(center=(LAYAR_LEBAR // 2, 260)))

                is_hov_res = btn_restart_rect.collidepoint(mouse_pos)
                is_hov_men = btn_menu_rect.collidepoint(mouse_pos)
                is_hov_exg = btn_exit_game_rect.collidepoint(mouse_pos)
                if is_hov_res or is_hov_men or is_hov_exg:
                    hover_ditemukan = True

                gambar_tombol(screen, btn_restart_rect, "Main Lagi (R)", None, font_kecil, font_mini,
                             (24, 150, 90) if is_hov_res else (18, 110, 65),
                             (50, 255, 160) if is_hov_res else (30, 170, 100), (255, 255, 255), is_hov_res)

                gambar_tombol(screen, btn_menu_rect, "Menu Utama (M)", None, font_kecil, font_mini,
                             (35, 75, 150) if is_hov_men else (25, 55, 110),
                             (80, 150, 255) if is_hov_men else (50, 100, 190), (255, 255, 255), is_hov_men)

                gambar_tombol(screen, btn_exit_game_rect, "Keluar / Exit (ESC)", None, font_kecil, font_mini,
                             (165, 35, 45) if is_hov_exg else (120, 25, 35),
                             (255, 80, 95) if is_hov_exg else (175, 45, 55), (255, 255, 255), is_hov_exg)

        # Ubah kursor mouse menjadi telunjuk (hand) jika hover pada tombol
        if hover_ditemukan:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()
        clock.tick(30) # 30FPS

    tutup_aplikasi(cap)

if __name__ == "__main__":
    main()

