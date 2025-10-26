# Pygame Actividad 11 - Fondos y Animaciones (Área 1)
# Autor: Erick Alfredo Ponce Rubio
# Objetivo: Implementar fondos con parallax y animación de sprite (idle/run) con control básico.
import pygame, sys, math, random

pygame.init()
WIDTH, HEIGHT = 960, 540
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Actividad 11 - Fondos y Animaciones")
CLOCK = pygame.time.Clock()
FPS = 60

# -------------------------- UTILIDADES --------------------
def make_text(txt, size=20, color=(230,230,240)):
    return pygame.font.SysFont(None, size).render(txt, True, color)

def clamp(v, a, b):
    return max(a, min(v, b))

# ------------------------- CAPAS DE FONDO ------------------
class StarLayer:
    """Capa de estrellas que se desplaza (parallax)."""
    def __init__(self, w, h, density=0.0008, speed=0.4):
        self.w, self.h = w, h
        self.speed = speed
        self.offset = 0.0
        self.surf = pygame.Surface((w*2, h), pygame.SRCALPHA) # *2 PARA SCROLL CONTINUO
        self.surf.fill((0,0,0,0))
        count = int(w*h*density)
        for _ in range(count):
            x = random.randint(0, w*2-1)
            y = random.randint(0, h-1)
            c = random.randint(180,255)
            self.surf.set_at((x,y), (c,c,c,255))
    
    def update(self, dt_ms):
        # dt_ms en milisegundos
        self.offset = (self.offset + self.speed*dt_ms) % self.w
        
    def draw(self, screen):
        x = int(self.offset)
        screen.blit(self.surf, (-x, 0))
        screen.blit(self.surf, (-x + self.w, 0))
        
class HillsLayer:
    """Capa de colinas dibujadas con polígono, parallax."""
    def __init__(self, w, h, color=(40,80,60), base=420, amp=28, freq=0.012, speed=1.0):
        self.w, self.h = w, h
        self.color = color
        self.base = base
        self.amp = amp
        self.freq = freq
        self.speed = speed
        self.offset = 0.0
        # Pre-render con *2 para scroll continuo
        self.surf = pygame.Surface((w*2, h), pygame.SRCALPHA)
        self._render()
        
    def _render(self):
        self.surf.fill((0,0,0,0))
        for x in range(self.w*2):
            y = int(self.base + math.sin((x)*self.freq)*self.amp)
            pygame.draw.line(self.surf, self.color, (x, y), (x, self.h))
        # Suaviza el borde superior
        overlay = pygame.Surface((self.w*2, self.h), pygame.SRCALPHA)
        overlay.fill((*self.color, 30))
        self.surf.blit(overlay, (0,0))
        
    def update(self, dt_ms):
        self.offset = (self.offset + self.speed*dt_ms) % self.w
        
    def draw(self, screen):
        x = int(self.offset)
        screen.blit(self.surf, (-x, 0))
        screen.blit(self.surf, (-x + self.w, 0))
        
class CloudsLayer:
    """Capa de 'nubes' translúcidas que se repiten."""
    def __init__(self, w, h, speed=1.8, count=10):
        self.w, self.h = w, h
        self.speed = speed
        self.offset = 0.0
        self.surf = pygame.Surface((w*2, h), pygame.SRCALPHA)
        for _ in range(count):
            cx = random.randint(0, w*2-1)
            cy = random.randint(40, h//2)
            r = random.randint(20, 60)
            cloud = pygame.Surface((r*4, r*2), pygame.SRCALPHA)
            for i in range(6):
                pygame.draw.circle(cloud, (255,255,255,60), (random.randint(r,3*r), random.randint(r//2, r)), random.randint(r//2, r))
            self.surf.blit(cloud, (cx, cy))
            
    def update(self, dt_ms):
        self.offset = (self.offset + self.speed*dt_ms) % self.w
        
    def draw(self, screen):
        x = int(self.offset)
        screen.blit(self.surf, (-x, 0))
        screen.blit(self.surf, (-x + self.w, 0))
        
# --------------------- SPRITE ANIMADO --------------------------
def make_idle_frames(size=(48,48)):
    """Genera frames 'idle' simples (boteo) sin assetes externos."""
    w,h = size
    frames = []
    for i in range(6):
        surf = pygame.Surface((w,h), pygame.SRCALPHA)
        # cuerpo
        pygame.draw.rect(surf, (240, 220, 90), (8, 12, w-16, h-20), border_radius=10)
        #cara/bote
        dy = int(math.sin(i/6*math.tau)*2)
        pygame.draw.circle(surf, (30,30,30), (w//2-6, 18+dy), 4)
        pygame.draw.circle(surf, (30,30,30), (w//2-6, 18+dy), 4)
        pygame.draw.rect(surf, (30,30,30), (w//2-8, 26+dy, 16, 3), border_radius=2)
        frames.append(surf)
    return frames

def make_run_frames(size=(48, 48)):
    """Genera frames 'run' básicos (brazos/piernas)."""
    w,h = size
    frames = []
    for i in range(8):
        surf = pygame.Surface((w,h), pygame.SRCALPHA)
        # cuerpo
        pygame.draw.rect(surf,(240, 120, 90), (8, 8, w-16, h-16), border_radius=10)
        phase = i/8*math.tau
        arm = int(math.sin(phase)*6)
        leg = int(math.cos(phase)*6)
        # brazos
        pygame.draw.rect(surf, (60,60,60), (4, 18*arm, 10, 6), border_radius=3)
        pygame.draw.rect(surf, (60,60,60), (w-14, 18-arm, 10, 6), border_radius=3)
        # piernas
        pygame.draw.rect(surf, (40,40,40), (12, h-14+leg, 10, 6), border_radius=2)
        pygame.draw.rect(surf, (40,40,40), (w-22, h-14-leg, 10, 6), border_radius=2)
        # ojos
        pygame.draw.circle(surf, (30,30,30), (w//2-6, 18), 4)
        pygame.draw.circle(surf, (30,30,30), (w//2+6, 18), 4)
        frames.append(surf)
    return frames

class AnimSprite(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.frames_idle = make_idle_frames()
        self.frames_run = make_run_frames()
        self.frames = self.frames_idle
        self.frame_index = 0
        self.frame_time = 0.0
        self.frame_duration = 0.08 # s por frame
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)
        # movimiento
        self.vel = pygame.Vector2(0,0)
        self.accel = 0.7
        self.friction = 0.86
        self.max_speed = 6.5
        self.facing_left = False
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys [pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x -= self.accel
            self.facing_left = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x += self.accel
            self.facing_left = False
    
    def apply_physics(self):
        # límites y fricción
        self.vel.x = clamp(self.vel.x, -self.max_speed, self.max_speed)
        self.vel *= self.friction
        self.rect.x += int(self.vel.x)
        if self.rect.left < 0:
            self.rect.left = 0; self.vel.x = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH; self.vel.x = 0
            
    def choose_animation(self):
        moving = abs(self.vel.x) > 0.2
        target = self.frames_run if moving else self.frames_idle
        if target is not self.frames:
            self.frames = target
            self.frame_index = 0
            self.frame_time = 0.0
            # animación corre más rápido que idle
            self.frame_duration = 0.06 if target is self.frames_run else 0.10
            
    def animate(self, dt):
        self.frame_time += dt
        if self.frame_time >= self.frame_duration:
            self.frame_time = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            frame = self.frames[self.frame_index]
            self.image = pygame.transform.flip(frame, True, False) if self.facing_left else frame
            
    def update(self, dt):
        self.handle_input()
        self.apply_physics()
        self.choose_animation()
        self.animate(dt)
        
# ---------------------- ESCENA -----------------------
def draw_gradient_bg(screen, top=(10,12,22), bottom=(25,28,48)):
    """Fondo de degradado vertical rápido."""
    for y in range(HEIGHT):
        t = y/HEIGHT
        r = int(top[0]*(1-t) + bottom[0]*t)
        g = int(top[1]*(1-t) + bottom[1]*t)
        b = int(top[2]*(1-t) + bottom[2]*t)
        pygame.draw.line(screen, (r,g,b), (0,y), (WIDTH,y))
        
def main():
    # Capas de fondo
    stars_far = StarLayer(WIDTH, HEIGHT, density=0.0010, speed=0.25)
    clouds  = CloudsLayer(WIDTH, HEIGHT, speed=1.2, count=10)
    hills = HillsLayer(WIDTH, HEIGHT, color=(35, 90, 70), base=400, amp=36, freq=0.010, speed=2.0)
    
    player = AnimSprite((WIDTH//2, 360))
    group = pygame.sprite.Group(player)
    
    running = True
    while running:
        dt_ms = CLOCK.tick(FPS)
        dt = dt_ms/1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        # Update
        stars_far.update(dt_ms)
        clouds.update(dt_ms)
        hills.update(dt_ms)
        group.update(dt)
        
        # Draw
        draw_gradient_bg(WINDOW)
        stars_far.draw(WINDOW)  # más lejos (más lento)
        clouds.draw(WINDOW)     # medio
        hills.draw(WINDOW)      # cercano (más rápido)
        group.draw(WINDOW)
        
        # HUD
        hud = [
            "Actividad 11 - Fondos y Animaciones",
            f"FPS: {int(CLOCK.get_fps())} | Frame: {player.frame_index} | Anim: {'RUN' if player.frames is player.frames_run else 'IDLE'}",
            "Izq/Der o A/D para mover | ESC para salir",
            "Consejo: observa el parallax (estrellas, nubes, colinas)."
        ]
        for i, line in enumerate(hud):
            WINDOW.blit(make_text(line, 20), (10, 10 + i*20))
        
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()
    
# ----------------------------- Retos/Extensiones --------------------------
# 1) Sprite sheet real: carga una hoja (PNG) y corta frames con subsurface.
# 2) Estado 'salto' (JUMP): agrega una animación y física vertical simple (gravedad).
# 3) Parallax 4+ capas: agrega una capa de ciudad/montañas extra al frente.
# 4) Cámera: desplazsa el mundo según la posición del jugador y repite fondo infinito.
# 5) Control de tiempo: usa acumulador para animación independiente del FPS.
# 6) Transiciones de día/noche: modifica el gradiente y alfa de nubes con un ciclo.
# 7) Efectos: agrega partículas al correr (polvo) que desaparezcan con el tiempo.   