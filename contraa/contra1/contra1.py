import pygame
import random
import sys
import math
import traceback
import os

# ============================================================
# =================== CONFIGURACIÓN GLOBAL ===================
# ============================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

NIVEL_ANCHO = 7000

GRAVEDAD = 0.8
PLAYER_GRAVEDAD = 0.6
SALTAR_FUERZA = -14
VELOCIDAD_JUGADOR = 5
VELOCIDAD_BALA = 9
VELOCIDAD_ENEMIGO = 2

MAX_REPETICIONES = 3
ENEMIGOS_PARA_DISPARAR = 5
MAX_ENEMIGOS_EN_PANTALLA = 10

# ============================================================
# ========================= COLORES ==========================
# ============================================================

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 100, 255)
MORADO = (180, 0, 255)
AMARILLO = (255, 255, 0)
GRIS = (90, 90, 90)
CIAN = (0, 255, 255) # Para Spread Gun
NARANJA = (255, 165, 0) # Para Machine Gun

# ============================================================
# ======================= INICIALIZAR ========================
# ============================================================

try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
except:
    pass
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    AUDIO_ENABLED = True
except:
    AUDIO_ENABLED = False
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("CONTRA - NIVEL 1")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 26)
font_small = pygame.font.SysFont("consolas", 18)
font_big = pygame.font.SysFont("consolas", 72)
font_title = pygame.font.SysFont("consolas", 48)
# ============================================================
# ========================== ESTADOS =========================
# ============================================================

ESTADO_MENU = 0
ESTADO_JUGANDO = 1
ESTADO_GAME_OVER = 2

# ============================================================
# ========================= CONTROLES ========================
# ============================================================

CONTROLES_J1 = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "salto": pygame.K_1,      # Botón A (Saltar)
    "disparo": pygame.K_2,    # Botón B (Disparar)
    "start": pygame.K_RETURN, # Start
    "select": pygame.K_RSHIFT # Select
}

CONTROLES_J2 = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "up": pygame.K_w,
    "down": pygame.K_s,
    "salto": pygame.K_k,      # Botón A
    "disparo": pygame.K_l,    # Botón B
    "start": pygame.K_SPACE,  # Start
    "select": pygame.K_LSHIFT # Select
}

# ============================================================
# ======================== PLATAFORMAS =======================
# ============================================================

# Generar un nivel más interesante
plataformas = []

# Suelo base
plataformas.append(pygame.Rect(0, SCREEN_HEIGHT - 40, NIVEL_ANCHO, 40))

# Definición de plataformas: (x, y, ancho, alto)
# Alturas sugeridas: suelo=560, nivel1=450, nivel2=350, nivel3=250
config_plataformas = [
    # Sección 1: Inicio fácil
    (300, 450, 200, 20),
    (600, 350, 200, 20),
    (900, 450, 200, 20),
    
    # Sección 2: Salto largo
    (1300, 400, 150, 20),
    (1600, 300, 150, 20),
    (1900, 200, 150, 20), # Alto
    
    # Sección 3: Escaleras/Bloques
    (2200, 450, 100, 20),
    (2350, 350, 100, 20),
    (2500, 250, 100, 20),
    
    # Sección 4: Zona extendida (Nuevo)
    (2800, 400, 200, 20),
    (3100, 300, 200, 20),
    (3400, 450, 150, 20),
    (3600, 250, 150, 20),
    (3900, 350, 200, 20),
    (4200, 450, 200, 20),

    # Final
    (4300, 300, 200, 20),
    (4600, 420, 200, 20),
    (4900, 320, 220, 20),
    (5200, 250, 180, 20),
    (5400, 450, 220, 20),
    (5700, 350, 200, 20),
    (6000, 280, 220, 20),
    (6300, 420, 180, 20),
    (6600, 320, 200, 20),
    (6900, 250, 180, 20),
    
    # Plataformas largas bajas
    (1500, 380, 380, 20),
    (2500, 370, 420, 20),
    (3200, 390, 340, 20),
    (4800, 360, 460, 20),
    (6200, 380, 380, 20),
    (6800, 370, 420, 20),
]

for (x, y, w, h) in config_plataformas:
    plataformas.append(pygame.Rect(x, y, w, h))


# ============================================================
# ========================= UTILIDADES =======================
# ============================================================

def draw_text(surface, text, font, color, x, y, center=True):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)

# ============================================================
# ========================= GRÁFICOS =========================
# ============================================================

# Función auxiliar para cargar imagen con fallback
def cargar_imagen(ruta, ancho, alto, color_fallback):
    """Intenta cargar una imagen, si falla crea un rectángulo de color."""
    if os.path.exists(ruta):
        try:
            img = pygame.image.load(ruta).convert_alpha()
            img = pygame.transform.scale(img, (ancho, alto))
            return img
        except Exception as e:
            print(f"Error cargando {ruta}: {e}")
    
    # Fallback: Crear superficie coloreada
    surf = pygame.Surface((ancho, alto))
    surf.fill(color_fallback)
    # Dibujar borde para distinguir
    pygame.draw.rect(surf, NEGRO, (0,0,ancho,alto), 2)
    return surf

def generar_fondo(ancho, alto):
    # Intentar cargar fondo desde archivo
    ruta_fondo = os.path.join("assets", "fondo", "nivel1.png")
    if os.path.exists(ruta_fondo):
        try:
            img = pygame.image.load(ruta_fondo).convert()
            img = pygame.transform.smoothscale(img, (ancho, alto))
            return img
        except:
            pass
            
    # Si no hay imagen, usar el generado proceduralmente
    fondo = pygame.Surface((ancho, alto))
    
    # 1. Cielo
    fondo.fill((100, 150, 255)) 
    
    # 2. Montañas lejanas
    puntos_montanas = []
    x = 0
    while x < ancho:
        h = random.randint(150, 300)
        puntos_montanas.append((x, alto - h))
        x += random.randint(50, 150)
    puntos_montanas.append((ancho, alto))
    puntos_montanas.append((0, alto))
    pygame.draw.polygon(fondo, (100, 100, 100), puntos_montanas)
    
    # 3. Selva/Vegetación fondo
    puntos_selva = []
    x = 0
    while x < ancho:
        h = random.randint(50, 150)
        puntos_selva.append((x, alto - h))
        x += random.randint(20, 50)
    puntos_selva.append((ancho, alto))
    puntos_selva.append((0, alto))
    pygame.draw.polygon(fondo, (0, 100, 0), puntos_selva)
    
    return fondo

FONDO_NIVEL = generar_fondo(SCREEN_WIDTH, SCREEN_HEIGHT)
MENU_BG = cargar_imagen(os.path.join("assets", "fondo", "menu.png"), SCREEN_WIDTH, SCREEN_HEIGHT, NEGRO)

def reproducir_musica(paths, volume):
    if not AUDIO_ENABLED:
        print("Audio no disponible")
        return False
    for p in paths:
        if os.path.exists(p):
            try:
                pygame.mixer.music.load(p)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
                print(f"Reproduciendo música: {p} vol={volume}")
                return True
            except Exception as e:
                print(f"Error reproduciendo {p}: {e}")
    print("No se encontró archivo de música en:", paths)
    return False

def detener_musica():
    try:
        pygame.mixer.music.stop()
    except:
        pass

def listar_pngs(path):
    try:
        files = [f for f in os.listdir(path) if f.lower().endswith((".png",".jpg",".jpeg"))]
        files.sort()
        return [os.path.join(path, f) for f in files]
    except:
        return []

def cargar_frames_anim(dir_path, w, h, fallback_color):
    frames = []
    for ruta in listar_pngs(dir_path):
        frames.append(cargar_imagen(ruta, w, h, fallback_color))
    if not frames:
        frames = [cargar_imagen(os.path.join(dir_path, "frame0.png"), w, h, fallback_color)]
    return frames

PLATAFORMA_FRAMES = cargar_frames_anim(os.path.join("assets","tiles","plataforma"), 32, 32, (0,150,0))
SUELO_FRAMES = cargar_frames_anim(os.path.join("assets","tiles","suelo"), 32, 32, (0,80,200))
TILE_ANIM_SPEED = 8

def ruta_enemigo(tipo):
    nombre = {
        "CORREDOR": "corredor.png",
        "TIRADOR": "tirador.png",
        "TORRETA": "torreta.png",
        "TANQUE": "tanque.png",
        "TANQUE_GIGANTE": "tanque_gigante.png",
        "CAPSULA": "capsula.png",
        "BOSS_FINAL": "boss_final.png",
    }.get(tipo, "enemigo.png")
    return os.path.join("assets", "enemigos", nombre)

def cargar_sprite_enemigo(tipo, w, h):
    color_fallback = {
        "CORREDOR": (255, 100, 100),
        "TIRADOR": ROJO,
        "TORRETA": (150, 0, 0),
        "TANQUE": GRIS,
        "TANQUE_GIGANTE": GRIS,
        "CAPSULA": BLANCO,
        "BOSS_FINAL": (40, 40, 40),
    }.get(tipo, (200, 200, 200))
    return cargar_imagen(ruta_enemigo(tipo), w, h, color_fallback)

def generar_sprites_jugador(color_base, nombre_carpeta):
    """
    Carga sprites desde la carpeta assets/{nombre_carpeta}/...
    Archivos esperados:
      - idle.png
      - run1.png
      - run2.png
      - jump.png (usado para salto)
      - up.png
      - crouch.png
      - up_right.png
      - down_right.png
    """
    sprites = {}
    w, h = 40, 60
    base_dir = os.path.join("assets", nombre_carpeta)
    
    # Mapeo de claves internas a nombres de archivo
    # Claves internas: 'idle_r', 'run1_r', 'run2_r', 'up_right', 'down_right', 'up', 'crouch'
    files = {
        'idle_r': 'idle.png',
        'run1_r': 'run1.png',
        'run2_r': 'run2.png',
        'up_r': 'up.png', # Agregamos _r para consistencia en loop abajo, aunque up es simetrico a veces
        'crouch_r': 'crouch.png',
        'up_right': 'up_right.png',
        'down_right': 'down_right.png'
    }
    
    # Función local para crear fallback procedural (copia del código anterior)
    def crear_fallback(key):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        if key == 'crouch': s = pygame.Surface((w, 40), pygame.SRCALPHA)
        
        # Dibujar algo básico basado en key
        c = color_base
        
        # Cuerpo
        if key == 'crouch':
             pygame.draw.rect(s, c, (10, 10, 20, 20))
        else:
             pygame.draw.rect(s, c, (10, 20, 20, 25))
        
        # Cabeza
        pygame.draw.circle(s, (255, 200, 180), (20, 10 if key != 'crouch' else 5), 8)
        
        # Detalle arma (muy simple)
        if 'up' in key and 'right' not in key:
            pygame.draw.rect(s, GRIS, (18, 0, 4, 30))
        elif 'right' in key and 'up' in key:
            pygame.draw.line(s, GRIS, (20,30), (40,10), 5)
        elif 'right' in key and 'down' in key:
            pygame.draw.line(s, GRIS, (20,30), (40,50), 5)
        else:
            pygame.draw.rect(s, GRIS, (20, 28, 20, 5))
            
        return s

    # Cargar imágenes
    for key, filename in files.items():
        ruta = os.path.join(base_dir, filename)
        
        # Manejo especial para dimensiones crouch
        th = h
        if 'crouch' in key: th = 40
            
        if os.path.exists(ruta):
            try:
                img = pygame.image.load(ruta).convert_alpha()
                img = pygame.transform.scale(img, (w, th))
                sprites[key] = img
            except:
                sprites[key] = crear_fallback(key.replace('_r',''))
        else:
            sprites[key] = crear_fallback(key.replace('_r',''))

    # Generar 'up' sin sufijo si falta (aunque usamos up_r arriba)
    if 'up' not in sprites and 'up_r' in sprites:
        sprites['up'] = sprites['up_r']

    # Generar versiones izquierda (flip)
    # Las claves que terminan en _r se convierten en _l
    # Las que no (up_right, down_right) se convierten en up_left, down_left?
    # El código del jugador espera: up_right + suffix ('_l') -> up_right_l
    
    keys = list(sprites.keys())
    for k in keys:
        img = sprites[k]
        
        new_key = k
        if k.endswith('_r'):
            new_key = k[:-2] + '_l'
        else:
            # up_right -> up_right_l
            new_key = k + '_l'
            
        sprites[new_key] = pygame.transform.flip(img, True, False)

    return sprites

SPRITES_J1 = generar_sprites_jugador(AZUL, "jugador1")
SPRITES_J2 = generar_sprites_jugador(MORADO, "jugador2")

# ============================================================
# ========================== CLASE JUGADOR ==================
# ============================================================

class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, color, controles, vidas_extra=0):
        super().__init__()
        # Determinar set de sprites
        if color == AZUL:
            self.sprites = SPRITES_J1
        else:
            self.sprites = SPRITES_J2
            
        self.image = self.sprites['idle_r']
        self.rect = self.image.get_rect()
        self.rect.center = (x, 100)
        
        self.color = color # Ya no se usa para dibujar, pero quizás para lógica
        self.controles = controles
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -15
        self.vidas = 3 + vidas_extra
        self.on_ground = False
        
        # Animación
        self.facing_right = True
        self.anim_timer = 0
        self.anim_frame = 0 # 0 o 1 para correr
        self.state = "IDLE" # IDLE, RUN, JUMP, CROUCH
        
        # Disparo
        self.arma = "NORMAL" # NORMAL, SPREAD, MACHINE
        self.cooldown_disparo = 0
        self.balas_a_disparar = []
        self.invulnerable_timer = 0
        
        # Apuntado
        self.direccion_vertical = 0 # -1 arriba, 0 neutro, 1 abajo
        self.direccion_horizontal = 1 # 1 derecha, -1 izquierda

    def update(self):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        # 1. Resetear estados transitorios
        self.vel_x = 0
        keys = pygame.key.get_pressed()
        
        up_pressed = keys[self.controles["up"]]
        down_pressed = keys[self.controles["down"]]
        left_pressed = keys[self.controles["left"]]
        right_pressed = keys[self.controles["right"]]
        
        # 2. Movimiento Horizontal
        if left_pressed:
            self.vel_x = -self.speed
            self.facing_right = False
            self.direccion_horizontal = -1
        elif right_pressed:
            self.vel_x = self.speed
            self.facing_right = True
            self.direccion_horizontal = 1
        
        # 3. Determinar dirección vertical para apuntar
        self.direccion_vertical = 0
        if up_pressed:
            self.direccion_vertical = -1
        elif down_pressed:
            self.direccion_vertical = 1

        # 4. Salto
        if keys[self.controles["salto"]] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
        
        # 5. Agacharse (Solo en el suelo)
        is_crouching = False
        if self.on_ground and down_pressed and not (left_pressed or right_pressed):
            is_crouching = True
            # Cambiar hitbox si es necesario (visualmente ya es mas bajo)
            # Pero para colisiones de mundo mantenemos rect similar o ajustamos
            # Para colisiones con balas enemigas, el rect se ajustará al cambiar self.image
        
        # 6. Gravedad
        self.vel_y += PLAYER_GRAVEDAD
        
        # 7. Movimiento y Colisiones Mundo
        self.rect.x += self.vel_x
        self.check_collisions_x()
        self.rect.y += self.vel_y
        self.check_collisions_y()
        
        # 8. Limites pantalla vertical
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.on_ground = True
        
        # 9. Actualizar Animación (Sprite)
        self.update_animation(is_crouching, up_pressed, down_pressed, left_pressed, right_pressed)

        # 10. Disparo
        if self.cooldown_disparo > 0:
            self.cooldown_disparo -= 1
        
        shoot_pressed = keys[self.controles["disparo"]]
        
        # Auto-fire si es MACHINE, o pulsación única para otros
        should_shoot = False
        if self.arma == "MACHINE":
            if shoot_pressed and self.cooldown_disparo == 0:
                should_shoot = True
        else:
            # Para normal/spread necesitamos detectar "just pressed". 
            # Como update corre cada frame, necesitamos un flag o chequear cooldown.
            # Simplificación: usaremos cooldown pequeño para todos, pero mas largo para normal.
            if shoot_pressed and self.cooldown_disparo == 0:
                should_shoot = True
        
        if should_shoot:
            self.crear_balas()
            if self.arma == "MACHINE":
                self.cooldown_disparo = 8 # Rápido
            elif self.arma == "SPREAD":
                self.cooldown_disparo = 30 # Lento
            else:
                self.cooldown_disparo = 15 # Normal

    def update_animation(self, is_crouching, up, down, left, right):
        # Determinar clave del sprite
        sprite_key = 'idle_r' # Default
        
        # Sufijo dirección
        suffix = '_r' if self.facing_right else '_l'
        
        if is_crouching:
            sprite_key = 'crouch' + suffix # crouch_r / crouch_l
        
        elif not self.on_ground:
            # En el aire (Saltando)
            # Contra suele usar una bola girando, pero aquí usaremos frame estático o run
            # Usaremos idle o frame de salto si tuvieramos. Usaremos idle.
            # O mejor: si apunta arriba/abajo en el aire?
            if up:
                if right or left:
                     sprite_key = 'up_right' + suffix
                else:
                     sprite_key = 'up' + suffix
            elif down:
                if right or left:
                    sprite_key = 'down_right' + suffix
                else:
                    # Disparo abajo directo en el aire? Contra no suele dejar abajo directo sin diagonal
                    # A menos que sea Contra III. Asumamos diagonal.
                    sprite_key = 'down_right' + suffix 
            else:
                 sprite_key = 'idle_r' if self.facing_right else 'idle_l' # Salto normal
        
        else:
            # En el suelo (No agachado)
            if up:
                if right or left:
                    # Corriendo y apuntando arriba
                    # Contra: corre cuerpo, arma arriba. Aquí simplificamos a "up_right" estático deslizandose?
                    # O alternamos frames de run?
                    # User pidió "5 frames: up right, down right, static, running".
                    # Si corre y apunta diagonal, usaremos up_right estático deslizandose (común en NES si no hay memoria)
                    # O mejor, alternar 'up_right' con algo mas? No, 'up_right' es solido.
                    sprite_key = 'up_right' + suffix
                else:
                    # Parado apuntando arriba
                    sprite_key = 'up' + suffix
            elif down: # Si no está crouch es porque se mueve?
                # Si se mueve y apunta abajo -> down_right
                if right or left:
                    sprite_key = 'down_right' + suffix
                else:
                    # Debería ser crouch, pero ya chequeamos is_crouching antes.
                    pass
            elif right or left:
                # Corriendo horizontal
                self.anim_timer += 1
                if self.anim_timer > 5: # Velocidad anim
                    self.anim_timer = 0
                    self.anim_frame = 1 - self.anim_frame # Toggle 0/1
                
                if self.anim_frame == 0:
                    sprite_key = 'run1_r' if self.facing_right else 'run1_l'
                else:
                    sprite_key = 'run2_r' if self.facing_right else 'run2_l'
            else:
                # Idle
                sprite_key = 'idle_r' if self.facing_right else 'idle_l'

        # Asignar imagen
        # Guardar BOTTOM para evitar "saltos" de posición al cambiar tamaño (especialmente crouch)
        bottom_pos = self.rect.midbottom
        self.image = self.sprites.get(sprite_key, self.sprites['idle_r'])
        self.rect = self.image.get_rect()
        self.rect.midbottom = bottom_pos
        if self.invulnerable_timer > 0:
            if (self.invulnerable_timer // 4) % 2 == 0:
                self.image.set_alpha(120)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
    
    def get_hurt_rect(self):
        r = self.rect.copy()
        r.inflate_ip(-10, -10)
        return r
        
        # Ajuste fino: si es crouch, ya está alineado al suelo por bottom.
        # No necesitamos lógica extra.

    def check_collisions_x(self):
        # Plataformas (paredes) - Opcional, Contra suele ser passthrough horizontal salvo cajas
        pass

    def check_collisions_y(self):
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.vel_y > 0: # Cayendo
                    # Verificar si estamos cayendo SOBRE la plataforma
                    # Permitir saltar desde abajo (passthrough)
                    if self.rect.bottom < p.bottom: 
                        self.rect.bottom = p.top
                        self.vel_y = 0
                        self.on_ground = True
    
    def crear_balas(self):
        # Determinar dirección exacta basada en teclas (no solo facing)
        # Contra usa 8 direcciones.
        dir_x = 0
        dir_y = 0
        
        # Horizontal
        if self.direccion_horizontal == 1:
            dir_x = 1
        elif self.direccion_horizontal == -1:
            dir_x = -1
        
        # Vertical
        if self.direccion_vertical == -1: # Arriba
            dir_y = -1
            # Si estamos parados y apuntamos arriba, x=0
            # Si corremos y apuntamos arriba, x!=0
            keys = pygame.key.get_pressed()
            if not (keys[self.controles["left"]] or keys[self.controles["right"]]):
                 dir_x = 0 # Disparo vertical puro
        elif self.direccion_vertical == 1: # Abajo
            keys = pygame.key.get_pressed()
            if self.on_ground:
                if keys[self.controles["left"]] or keys[self.controles["right"]]:
                    dir_y = 1
                    dir_x = 1 if keys[self.controles["right"]] else -1
                else:
                    dir_y = 0
            else:
                dir_y = 1
                if keys[self.controles["left"]] or keys[self.controles["right"]]:
                    dir_x = 1 if keys[self.controles["right"]] else -1
                else:
                    dir_x = 0
        
        # Corrección "Up-Right" / "Down-Right"
        # Si dir_x != 0 y dir_y != 0 -> Diagonal
        
        # Caso especial: Agachado (On ground + Down)
        # Disparo es horizontal, pero desde altura baja.
        offset_y = 0
        keys = pygame.key.get_pressed()
        if self.on_ground and keys[self.controles["down"]] and not (keys[self.controles["left"]] or keys[self.controles["right"]]):
             dir_y = 0
             offset_y = 10 # Bajar origen bala
        
        # Caso especial: Solo Arriba (Sin mover) -> X=0, Y=-1
        # Ya manejado arriba.
        
        # Normalizar si es diagonal
        if dir_x == 0 and dir_y == 0:
            dir_x = 1 if self.facing_right else -1 # Default forward
            
        # Origen de la bala
        spawn_x = self.rect.centerx + (dir_x * 10)
        spawn_y = self.rect.centery + (dir_y * 10) + offset_y
        
        # Crear balas según arma
        if self.arma == "SPREAD":
            # 5 balas en abanico (Contra original) o 3 (simplificado)
            # Base angle
            import math
            angle_base = math.atan2(dir_y, dir_x)
            angles = [angle_base, angle_base - 0.25, angle_base + 0.25, angle_base - 0.5, angle_base + 0.5]
            
            for ang in angles:
                dx = math.cos(ang)
                dy = math.sin(ang)
                self.balas_a_disparar.append(Bala(spawn_x, spawn_y, dx, dy, False, "SPREAD"))
                
        elif self.arma == "MACHINE":
            self.balas_a_disparar.append(Bala(spawn_x, spawn_y, dir_x, dir_y, False, "MACHINE"))
        else:
            self.balas_a_disparar.append(Bala(spawn_x, spawn_y, dir_x, dir_y, False, "NORMAL"))

    def morir(self):
        if self.invulnerable_timer > 0:
            return
        self.vidas -= 1
        self.arma = "NORMAL"
        self.invulnerable_timer = 120
        self.rect.y = 0
        self.vel_y = 0

# ============================================================
# ============================ BALAS =========================
# ============================================================

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, dir_x, dir_y, enemiga, tipo="NORMAL"):
        super().__init__()
        # Tamaño y carga desde assets si existen
        def ruta_proyectil(tipo, enemiga):
            nombres = {
                "SPREAD": "spread.png",
                "ENEMIGO_GRANDE": "enemigo_grande.png",
                "ENEMIGO_BOSS": "enemigo_boss.png",
                "BOMBA": "bomba.png",
                "NORMAL_ENEMIGO": "enemigo.png",
                "NORMAL_JUGADOR": "jugador.png",
            }
            key = tipo
            if tipo == "NORMAL":
                key = "NORMAL_ENEMIGO" if enemiga else "NORMAL_JUGADOR"
            nombre = nombres.get(key, "proyectil.png")
            return os.path.join("assets", "proyectiles", nombre)
        
        if tipo == "SPREAD":
            w,h = 10,10
            self.image = cargar_imagen(ruta_proyectil("SPREAD", enemiga), w, h, CIAN)
        elif tipo == "ENEMIGO_GRANDE":
            w,h = 12,12
            self.image = cargar_imagen(ruta_proyectil("ENEMIGO_GRANDE", enemiga), w, h, ROJO)
        elif tipo == "ENEMIGO_BOSS":
            w,h = 16,16
            self.image = cargar_imagen(ruta_proyectil("ENEMIGO_BOSS", enemiga), w, h, (255,50,50))
        elif tipo == "BOMBA":
            w,h = 16,16
            self.image = cargar_imagen(ruta_proyectil("BOMBA", enemiga), w, h, (50,50,50))
        else:
            w,h = 8,8
            fallback = ROJO if enemiga else AMARILLO
            key = "NORMAL_ENEMIGO" if enemiga else "NORMAL_JUGADOR"
            self.image = cargar_imagen(ruta_proyectil(key, enemiga), w, h, fallback)
            
        self.rect = self.image.get_rect(center=(x, y))

        # Velocidad
        speed = VELOCIDAD_BALA
        if enemiga: speed = VELOCIDAD_BALA * 0.6 # Balas enemigas más lentas para esquivar
        
        # Normalización simple si no es Spread (para compatibilidad)
        # Pero si es Spread, confiamos en dir_x/dir_y o normalizamos aqui
        
        if tipo == "BOMBA":
            # Para BOMBA, dir_x y dir_y son velocidades directas calculadas
            self.dx = dir_x
            self.dy = dir_y
            self.vel_y_bomba = dir_y
        else:
            norm = math.hypot(dir_x, dir_y)
            if norm > 0:
                self.dx = (dir_x / norm) * speed
                self.dy = (dir_y / norm) * speed
            else:
                self.dx = dir_x * speed
                self.dy = dir_y * speed
            
        self.enemiga = enemiga
        self.tipo = tipo

    def update(self):
        if self.tipo == "BOMBA":
            self.vel_y_bomba += 0.4 # Gravedad bomba
            self.dy = self.vel_y_bomba
            
        self.rect.x += self.dx
        self.rect.y += self.dy

        if (self.rect.right < 0 or self.rect.left > NIVEL_ANCHO or 
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()
# ============================================================
# ========================== CLASE ENEMIGO ===================
# ============================================================

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, tipo, target_list):
        super().__init__()
        self.tipo = tipo
        self.target_list = target_list
        
        # Atributos por defecto
        self.vel_x = 0
        self.vel_y = 0
        self.timer_disparo = 0
        self.rafaga_count = 0 # Para tanque
        self.estado = "ESPERA" # Para tanque
        
        if tipo == "CORREDOR":
            self.image = cargar_sprite_enemigo("CORREDOR", 30, 50)
            self.vel_x = 5
            self.puede_disparar = False
            y_pos = SCREEN_HEIGHT - 100
            
        elif tipo == "TIRADOR":
            self.image = cargar_sprite_enemigo("TIRADOR", 40, 50)
            self.vel_x = 2
            self.puede_disparar = True
            y_pos = SCREEN_HEIGHT - 100
            self.timer_disparo = random.randint(0, 60)
            
        elif tipo == "TORRETA":
            self.image = cargar_sprite_enemigo("TORRETA", 40, 40)
            self.vel_x = 0
            self.puede_disparar = True
            y_pos = SCREEN_HEIGHT - 90 
            self.timer_disparo = random.randint(0, 60)
            
        elif tipo == "TANQUE":
            self.image = cargar_sprite_enemigo("TANQUE", 60, 60)
            self.vel_x = 0
            self.puede_disparar = True
            y_pos = SCREEN_HEIGHT - 110 # Un poco más arriba del suelo
            # Config Tanque
            self.timer_disparo = 0 # Cuenta hasta 300 (5 seg)
            self.rafaga_timer = 0
            self.balas_rafaga = 0
            self.estado = "ESPERA" # ESPERA -> DISPARANDO
            self.hp = 8
        elif tipo == "TANQUE_GIGANTE":
            self.image = cargar_sprite_enemigo("TANQUE_GIGANTE", 120, 90)
            self.vel_x = 0
            self.puede_disparar = True
            y_pos = SCREEN_HEIGHT - 150
            self.timer_disparo = 0
            self.rafaga_timer = 0
            self.balas_rafaga = 0
            self.estado = "ESPERA"
            self.hp = 30
            
        elif tipo == "CAPSULA":
            self.image = cargar_sprite_enemigo("CAPSULA", 30, 30)
            self.vel_x = 3
            self.puede_disparar = False
            y_pos = 100 # Vuela alto
            self.y_inicial = y_pos
            self.t_vuelo = 0
            
        elif tipo == "BOSS_FINAL":
            self.image = cargar_sprite_enemigo("BOSS_FINAL", 200, 150)
            
            self.vel_x = 0
            self.puede_disparar = True
            y_pos = SCREEN_HEIGHT - 190
            self.timer_disparo = 0
            self.rafaga_timer = 0
            self.balas_rafaga = 0
            self.estado = "ESPERA"
            self.hp = 100 # Mucha vida

        self.rect = self.image.get_rect(topleft=(x, y_pos))
        
        # Ajuste vertical si es plataforma (simple check suelo)
        # Si queremos que aparezcan sobre plataformas, necesitaríamos pasar plataformas al init
        # Por ahora asumo suelo o aire.

    def update(self):
        bala = None
        
        # --- MOVIMIENTO ---
        if self.tipo == "CAPSULA":
            self.rect.x -= self.vel_x
            # Movimiento senoidal
            self.t_vuelo += 0.1
            self.rect.y = self.y_inicial + math.sin(self.t_vuelo) * 50
        elif self.tipo == "TANQUE" or self.tipo == "TANQUE_GIGANTE" or self.tipo == "BOSS_FINAL":
            pass # No se mueve
        else:
            self.rect.x -= self.vel_x
            self.vel_y += GRAVEDAD
            self.rect.y += self.vel_y
            for p in plataformas:
                if self.rect.colliderect(p) and self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
            if (self.tipo == "CORREDOR" or self.tipo == "TIRADOR"):
                self.timer_disparo += 1
                if self.timer_disparo % 120 == 0 and self.vel_y == 0:
                    self.vel_y = -12

        # --- DISPARO ---
        if self.puede_disparar:
            
            if self.tipo == "TANQUE":
                if self.estado == "ESPERA":
                    self.timer_disparo += 1
                    if self.timer_disparo >= 300: # 5 segundos a 60 FPS
                        self.estado = "DISPARANDO"
                        self.timer_disparo = 0
                        self.balas_rafaga = 0
                        self.rafaga_timer = 0
                
                elif self.estado == "DISPARANDO":
                    self.rafaga_timer += 1
                    if self.rafaga_timer >= 10: # Dispara cada 10 frames
                        self.rafaga_timer = 0
                        self.balas_rafaga += 1
                        
                        # Disparar al jugador
                        target = self.get_nearest_player()
                        if target:
                            dx = target.rect.centerx - self.rect.centerx
                            dy = target.rect.centery - self.rect.centery
                            bala = Bala(self.rect.centerx, self.rect.centery, dx, dy, True, tipo="ENEMIGO_GRANDE")
                        
                        if self.balas_rafaga >= 3:
                            self.estado = "ESPERA"
            elif self.tipo == "TANQUE_GIGANTE":
                self.timer_disparo += 1
                if self.timer_disparo >= 200:
                    self.timer_disparo = 0
                    target = self.get_nearest_player()
                    self.balas_emitidas = []
                    if target:
                        base_dx = target.rect.centerx - self.rect.centerx
                        base_dy = target.rect.centery - self.rect.centery
                        base_ang = math.atan2(base_dy, base_dx)
                        angles = [base_ang + a for a in (-0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6)]
                    else:
                        angles = [0]
                    for ang in angles:
                        dx = math.cos(ang)
                        dy = math.sin(ang)
                        b = Bala(self.rect.centerx, self.rect.centery, dx, dy, True, tipo="ENEMIGO_BOSS")
                        self.balas_emitidas.append(b)
            
            elif self.tipo == "BOSS_FINAL":
                self.timer_disparo += 1
                if self.timer_disparo >= 120: # Cada 2 segundos
                    self.timer_disparo = 0
                    
                    target = self.get_nearest_player()
                    if target:
                        # Calcular trayectoria parabólica
                        # Queremos que llegue a target.rect.centerx
                        start_x = self.rect.left
                        start_y = self.rect.centery
                        dest_x = target.rect.centerx
                        
                        # Distancia X
                        dist_x = dest_x - start_x
                        
                        # Asumimos un tiempo de vuelo fijo (ej 60 frames = 1 seg)
                        t = 60
                        # vx = dist_x / t
                        vx = dist_x / t
                        
                        # vy inicial?
                        # y(t) = y0 + vy*t + 0.5*g*t^2
                        # target_y = start_y + vy*t + 0.5*g*t^2
                        # vy = (target_y - start_y - 0.5*g*t^2) / t
                        # Queremos que caiga un poco sobre el jugador o al suelo
                        dest_y = target.rect.bottom
                        g = 0.4 # Misma gravedad que en Bala.update
                        
                        vy = (dest_y - start_y - 0.5 * g * (t**2)) / t
                        
                        # Limitar velocidad vertical para que no sea ridícula
                        if vy > 10: vy = 10
                        if vy < -15: vy = -15
                        
                        # Crear Bomba
                        # Pasamos vx, vy como dir_x, dir_y
                        b = Bala(start_x, start_y, vx, vy, True, tipo="BOMBA")
                        if not hasattr(self, "balas_emitidas"): self.balas_emitidas = []
                        self.balas_emitidas.append(b)

                        # Ráfaga de balas simultánea hacia el jugador
                        base_dx = target.rect.centerx - self.rect.centerx
                        base_dy = target.rect.centery - self.rect.centery
                        base_ang = math.atan2(base_dy, base_dx)
                        angles_volley = [base_ang + a for a in (-0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6)]
                        for ang in angles_volley:
                            dx = math.cos(ang)
                            dy = math.sin(ang)
                            bb = Bala(self.rect.centerx, self.rect.centery, dx, dy, True, tipo="ENEMIGO_BOSS")
                            self.balas_emitidas.append(bb)
                    else:
                        # Si no hay objetivo, disparar bombas y balas hacia la izquierda
                        start_x = self.rect.left
                        start_y = self.rect.centery
                        b = Bala(start_x, start_y, -3, -6, True, tipo="BOMBA")
                        if not hasattr(self, "balas_emitidas"): self.balas_emitidas = []
                        self.balas_emitidas.append(b)
                        for ang in [math.pi + a for a in (-0.4, -0.2, 0, 0.2, 0.4)]:
                            dx = math.cos(ang)
                            dy = math.sin(ang)
                            bb = Bala(self.rect.centerx, self.rect.centery, dx, dy, True, tipo="ENEMIGO_BOSS")
                            self.balas_emitidas.append(bb)

            else: # Tirador o Torreta
                self.timer_disparo += 1
                if self.timer_disparo >= 100:
                    self.timer_disparo = 0
                    
                    if self.tipo == "TORRETA" or self.tipo == "TIRADOR":
                        target = self.get_nearest_player()
                        if target:
                            dx = target.rect.centerx - self.rect.centerx
                            dy = target.rect.centery - self.rect.centery
                            bala = Bala(self.rect.centerx, self.rect.centery, dx, dy, True)
                    else:
                        bala = Bala(self.rect.left, self.rect.centery, -1, 0, True)

        if self.rect.right < 0:
            self.kill()
            
        return bala
        
    def get_nearest_player(self):
        if not self.target_list: return None
        min_dist = float('inf')
        nearest = None
        for p in self.target_list:
            dist = abs(p.rect.centerx - self.rect.centerx)
            if dist < min_dist:
                min_dist = dist
                nearest = p
        return nearest

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo_arma):
        super().__init__()
        self.tipo_arma = tipo_arma
        w,h = 24,24
        ruta = os.path.join("assets", "powerups", f"{'spread' if tipo_arma=='SPREAD' else 'machine'}.png")
        fallback = CIAN if tipo_arma == "SPREAD" else NARANJA
        self.image = cargar_imagen(ruta, w, h, fallback)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = -4 # Saltito al nacer
        
    def update(self):
        self.vel_y += GRAVEDAD
        self.rect.y += self.vel_y
        
        # Colisión suelo simple
        for p in plataformas:
            if self.rect.colliderect(p) and self.vel_y > 0:
                self.rect.bottom = p.top
                self.vel_y = 0
        
        # Eliminar si cae al vacío
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
# ============================================================
# ========================== MENÚ ============================
# ============================================================

def menu_principal():
    """
    Muestra el menú principal.
    - Navegación con flechas arriba/abajo y W / S
    - Presiona ENTER para confirmar
    - Presiona 1 o 2 para seleccionar personaje 1 (forzar)
    - Presiona K o L para seleccionar personaje 2 (forzar)
    Devuelve: (seleccion, jugador_forzado, vidas_extra)
    """
    seleccion = 0
    opciones = ["1 JUGADOR", "2 JUGADORES", "SALIR"]
    jugador_forzado = None
    
    # Konami Code: Arriba, Arriba, Abajo, Abajo, Izq, Der, Izq, Der, B, A
    konami_code = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, 
                   pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT,
                   pygame.K_z, pygame.K_x]
    konami_index = 0
    vidas_extra = 0

    music_started = False
    while True:
        if not music_started:
            reproducir_musica([
                os.path.join("assets", "audio", "menu.mp3"),
                os.path.join("assets", "audio", "menu.ogg"),
                os.path.join("assets", "audio", "menu.wav"),
            ], 0.8)
            music_started = True
        screen.blit(MENU_BG, (0, 0))
        # Título
        draw_text(screen, "CONTRA", font_big, ROJO, SCREEN_WIDTH // 2, 80, center=True)
        
        # Controles info
        draw_text(screen, "CONTROLES:", font_small, GRIS, SCREEN_WIDTH // 2, 160, center=True)
        draw_text(screen, "J1: Flechas + 2(B) + 1(A) + ENTER(Start)", font_small, GRIS, SCREEN_WIDTH // 2, 180, center=True)
        draw_text(screen, "J2: WASD + L(B) + K(A) + ESPACIO(Start)", font_small, GRIS, SCREEN_WIDTH // 2, 200, center=True)

        # Opciones
        for i, texto in enumerate(opciones):
            color = VERDE if i == seleccion else BLANCO
            draw_text(screen, texto, font, color, SCREEN_WIDTH // 2, 280 + i * 50, center=True)

        # Indicador de personaje forzado
        info = "Personaje forzado: "
        if jugador_forzado is None:
            info += "Ninguno (presiona 1/2 o K/L)"
        else:
            info += f"J{jugador_forzado}"
        draw_text(screen, info, font_small, AZUL, SCREEN_WIDTH // 2, 450, center=True)
        
        # Mensaje Konami
        if vidas_extra > 0:
            draw_text(screen, "30 VIDAS ACTIVADAS!", font, AMARILLO, SCREEN_WIDTH // 2, 520, center=True)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                detener_musica()
                return 2, None, 0

            if event.type == pygame.KEYDOWN:
                # Konami Code check
                if event.key == konami_code[konami_index]:
                    konami_index += 1
                    if konami_index == len(konami_code):
                        vidas_extra = 27 # Total 30 (3 base + 27)
                        konami_index = 0
                else:
                    konami_index = 0
                    if event.key == konami_code[0]:
                        konami_index = 1

                # Navegación: flechas o W/S
                if event.key in (pygame.K_UP, pygame.K_w):
                    seleccion = (seleccion - 1) % len(opciones)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    seleccion = (seleccion + 1) % len(opciones)

                # Forzar personaje
                elif event.key in (pygame.K_1, pygame.K_2):
                    jugador_forzado = 1
                elif event.key in (pygame.K_k, pygame.K_l):
                    jugador_forzado = 2

                # Confirmar
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    detener_musica()
                    return seleccion, jugador_forzado, vidas_extra
# ============================================================
# ===================== BUCLE DE JUEGO =======================
# ============================================================

def juego(modo_jugadores, jugador_forzado, vidas_extra=0):
    sprites = pygame.sprite.Group()
    jugadores = []
    balas = pygame.sprite.Group()
    enemigos = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    reproducir_musica([
        os.path.join("assets", "audio", "game.ogg"),
        os.path.join("assets", "audio", "game.mp3"),
        os.path.join("assets", "audio", "game.wav"),
    ], 0.6)
    # ================= CREAR JUGADORES =================
    if modo_jugadores == 0:  # 1 jugador
        if jugador_forzado == 2:
            j1 = Jugador(100, MORADO, CONTROLES_J2, vidas_extra)
        else:
            j1 = Jugador(100, AZUL, CONTROLES_J1, vidas_extra)
        jugadores.append(j1)
        sprites.add(j1)
    else:  # 2 jugadores
        j1 = Jugador(100, AZUL, CONTROLES_J1, vidas_extra)
        j2 = Jugador(160, MORADO, CONTROLES_J2, vidas_extra)
        jugadores.extend([j1, j2])
        sprites.add(j1, j2)

    # ================= VARIABLES =================
    camara_x = 0
    spawn_timer = 0
    contador_enemigos = 0
    boss_spawned = False
    boss_derrotado = False
    tile_anim_timer = 0

    corriendo = True
    while corriendo:
        clock.tick(FPS)
        tile_anim_timer += 1
        idx_plat = (tile_anim_timer // TILE_ANIM_SPEED) % len(PLATAFORMA_FRAMES)
        idx_suelo = (tile_anim_timer // TILE_ANIM_SPEED) % len(SUELO_FRAMES)

        # ================= EVENTOS =================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                detener_musica()
                return False
            
            # El disparo ahora se maneja en update() con get_pressed()

        screen.blit(FONDO_NIVEL, (0, 0))

        # ================= ACTUALIZAR JUGADORES =================
        for j in jugadores[:]:
            j.update()
            
            # Recoger balas generadas
            if j.balas_a_disparar:
                for b in j.balas_a_disparar:
                    sprites.add(b)
                    balas.add(b)
                j.balas_a_disparar = []
            
            # Mantener jugador en pantalla (Cámara)
            if j.rect.left < camara_x:
                j.rect.left = camara_x
            if j.rect.right > camara_x + SCREEN_WIDTH:
                j.rect.right = camara_x + SCREEN_WIDTH

            hurt = j.get_hurt_rect()
            for e in enemigos:
                if getattr(e, "tipo", "") != "CAPSULA" and hurt.colliderect(e.rect):
                    if j.invulnerable_timer == 0:
                        j.morir()
                        if j.vidas <= 0:
                            jugadores.remove(j)
                            sprites.remove(j)

            # Colisión con balas enemigas
            for b in balas:
                if b.enemiga and hurt.colliderect(b.rect):
                    b.kill()
                    j.morir()
                    if j.vidas <= 0:
                        jugadores.remove(j)
                        sprites.remove(j)
            
            # Colisión con PowerUps
            hits_pu = pygame.sprite.spritecollide(j, powerups, True)
            for pu in hits_pu:
                j.arma = pu.tipo_arma

        # ================= ACTUALIZAR ENEMIGOS Y POWERUPS =================
        for e in enemigos:
            bala_enemiga = e.update()
            if bala_enemiga:
                sprites.add(bala_enemiga)
                balas.add(bala_enemiga)
            if hasattr(e, "balas_emitidas") and e.balas_emitidas:
                for bb in e.balas_emitidas:
                    sprites.add(bb)
                    balas.add(bb)
                e.balas_emitidas = []
        
        powerups.update()

        # ================= ACTUALIZAR BALAS =================
        balas.update()
        
        # Colisión Balas Jugador -> Enemigos
        # groupcollide(groupa, groupb, dokilla, dokillb) -> dict
        # No usamos dokill automático para poder chequear tipo de enemigo (capsula)
        hits = pygame.sprite.groupcollide(enemigos, balas, False, False)
        for e, balas_hit in hits.items():
            for b in balas_hit:
                if not b.enemiga:
                    if e.tipo == "TANQUE" or e.tipo == "TANQUE_GIGANTE" or e.tipo == "BOSS_FINAL":
                        dmg = 1
                        if b.tipo == "SPREAD":
                            dmg = 2
                        elif b.tipo == "MACHINE":
                            dmg = 1
                        e.hp -= dmg
                        b.kill()
                        if e.hp <= 0:
                            if e.tipo == "BOSS_FINAL":
                                boss_derrotado = True
                            e.kill()
                    else:
                        b.kill()
                        e.kill()
                        if e.tipo == "CAPSULA":
                            tipo_arma = random.choice(["SPREAD", "MACHINE"])
                            if jugadores:
                                nearest = min(jugadores, key=lambda j: abs(j.rect.centerx - e.rect.centerx))
                                spawn_x = (e.rect.centerx + nearest.rect.centerx) // 2
                                spawn_y = e.rect.centery - 10
                            else:
                                spawn_x = e.rect.centerx
                                spawn_y = e.rect.centery
                            pu = PowerUp(spawn_x, spawn_y, tipo_arma)
                            sprites.add(pu)
                            powerups.add(pu)
                    break

        # ================= SPAWN DE ENEMIGOS =================
        # Si ya spawneó el boss, no spawnear más enemigos normales (o spawnear menos)
        if not boss_spawned:
            spawn_timer += 1
            if spawn_timer >= 120:
                spawn_timer = 0
                if len(enemigos) < MAX_ENEMIGOS_EN_PANTALLA and random.random() < 0.75:
                    contador_enemigos += 1
                    tipos = ["TIRADOR", "TIRADOR", "CORREDOR", "CORREDOR", "TORRETA", "CAPSULA", "TANQUE"]
                    tipo = random.choice(tipos)
                    spawn_x = camara_x + SCREEN_WIDTH + random.randint(50, 200)
                    if tipo == "CAPSULA":
                        spawn_x = camara_x + SCREEN_WIDTH - random.randint(80, 140)
                    if camara_x > NIVEL_ANCHO - SCREEN_WIDTH - 200:
                        tipo = None
                    if tipo:
                        enemigo = Enemigo(spawn_x, tipo, jugadores)
                        enemigos.add(enemigo)
                        sprites.add(enemigo)
                        if tipo in ("CORREDOR", "TIRADOR", "TORRETA"):
                            candidatos = [p for p in plataformas if p.left <= spawn_x <= p.right]
                            if candidatos:
                                psel = max(candidatos, key=lambda p: p.top)
                                if psel.top >= 350:
                                    enemigo.rect.bottom = psel.top
        
        # ================= SPAWN BOSS =================
        if not boss_spawned and camara_x >= NIVEL_ANCHO - SCREEN_WIDTH - 100:
             boss_spawned = True
             # Limpiar enemigos anteriores para que no molesten? Opcional.
             boss = Enemigo(NIVEL_ANCHO - 250, "BOSS_FINAL", jugadores)
             enemigos.add(boss)
             sprites.add(boss)

        # ================= CÁMARA LATERAL =================
        if jugadores:
            camara_x = max(camara_x, max(j.rect.x for j in jugadores) - SCREEN_WIDTH // 2)
            camara_x = min(camara_x, NIVEL_ANCHO - SCREEN_WIDTH)

        # ================= DIBUJAR TODO LO DEMÁS =================
        
        for i, p in enumerate(plataformas):
            # Solo dibujar si está en pantalla
            if p.right > camara_x and p.left < camara_x + SCREEN_WIDTH:
                # Ajustar posición relativa a cámara
                rect_pantalla = p.copy()
                rect_pantalla.x -= camara_x
                tile = SUELO_FRAMES[idx_suelo] if i == 0 else PLATAFORMA_FRAMES[idx_plat]
                tw, th = tile.get_width(), tile.get_height()
                y = rect_pantalla.y
                while y < rect_pantalla.bottom:
                    x = rect_pantalla.x
                    while x < rect_pantalla.right:
                        screen.blit(tile, (x, y))
                        x += tw
                    y += th

        # Dibujar sprites (ajustados a cámara)
        for s in sprites:
            if s.rect.right > camara_x and s.rect.left < camara_x + SCREEN_WIDTH:
                screen.blit(s.image, (s.rect.x - camara_x, s.rect.y))

        # UI / HUD
        # Vidas J1
        if jugadores:
            y = 10
            for i, j in enumerate(jugadores):
                draw_text(
                    screen,
                    f"J{i+1} VIDAS: {j.vidas}",
                    font_small,
                    VERDE,
                    10,
                    y,
                    center=False
                )
                y += 20

        # Mensaje de Victoria
        if boss_derrotado:
            draw_text(screen, "¡MISIÓN CUMPLIDA!", font_big, AMARILLO, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
            draw_text(screen, "PRESIONA ESC PARA SALIR", font, BLANCO, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, center=True)
            
            # Verificar si quiere salir
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                try: pygame.mixer.music.stop()
                except: pass
                return

        pygame.display.flip()

        if not jugadores:
            detener_musica()
            return
# ============================================================
# ===================== GAME OVER ============================
# ============================================================

def pantalla_game_over():
    """
    Muestra Game Over.
    Devuelve True si el jugador quiere continuar, False si quiere salir al menú.
    """
    timer = 0
    
    while True:
        clock.tick(FPS)
        screen.fill(NEGRO)

        draw_text(screen, "GAME OVER", font_title, ROJO,
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        
        # Parpadeo del texto de continuar
        timer += 1
        if timer % 40 < 25: # Parpadeo más lento
            draw_text(screen, "CONTINUAR? PRESIONA ENTER", font, BLANCO,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
        
        draw_text(screen, "SALIR AL MENU: ESC", font_small, GRIS,
                  SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

# ============================================================
# ===================== PROGRAMA PRINCIPAL ==================
# ============================================================

# ============================================================
# ===================== PROGRAMA PRINCIPAL ==================
# ============================================================

def main():
    while True:
        # MENÚ
        seleccion, jugador_forzado, vidas_extra = menu_principal()

        # SALIR
        if seleccion == 2:
            return

        # JUEGO CON CONTINUES
        jugando = True
        while jugando:
            resultado = None
            error_en_juego = False
            try:
                resultado = juego(seleccion, jugador_forzado, vidas_extra)
            except Exception as e:
                print("Error en juego:", e)
                print(traceback.format_exc())
                error_en_juego = True

            # Si el juego terminó por cerrar la ventana, salir completamente
            if resultado is False:
                return

            # Si ocurrió una excepción en el juego, volver al menú sin pantalla de Game Over
            if error_en_juego:
                break

            # GAME OVER - Preguntar si continuar
            if not pantalla_game_over():
                jugando = False


if __name__ == "__main__":
    main()
