import pygame
import pyodbc
import random
import sys
import math
import os
from db_connection import get_db_connection

# --- CONFIGURACIÓN ---
GAME_WIDTH = 800
GAME_HEIGHT = 600

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
DARK_BLUE = (44, 62, 80) 
GOLD = (241, 196, 15)    
YELLOW = (255, 255, 0)
SILVER = (189, 195, 199) 
PURPLE = (155, 89, 182)
ORANGE = (230, 126, 34)  
GRAY = (127, 140, 141)   
DARK_OVERLAY = (0, 0, 0, 150)

FPS = 60

# --- CLASES VISUALES ---
class FloatingText:
    def __init__(self, x, y, text, color, font):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.timer = 40
        self.font = font
    def update(self):
        self.y -= 1; self.timer -= 1
    def draw(self, surface):
        if self.timer > 0:
            shadow = self.font.render(str(self.text), True, BLACK)
            text = self.font.render(str(self.text), True, self.color)
            surface.blit(shadow, (self.x + 2, self.y + 2))
            surface.blit(text, (self.x, self.y))

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.size = random.randint(4, 8)
        self.life = random.randint(15, 30)
        self.vx, self.vy = random.uniform(-3, 3), random.uniform(-3, 3)
    def update(self):
        self.x += self.vx; self.y += self.vy; self.life -= 1; self.size -= 0.1
    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

# --- MOTOR PRINCIPAL ---
class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.RESIZABLE)
        self.canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Retro RPG - FINAL VERSION")
        self.clock = pygame.time.Clock()
        
        # Fuentes
        try:
            self.font_s = pygame.font.Font("PressStart2P.ttf", 12)
            self.font_m = pygame.font.Font("PressStart2P.ttf", 20)
            self.font_l = pygame.font.Font("PressStart2P.ttf", 40)
            self.font_xl = pygame.font.Font("PressStart2P.ttf", 60)
        except:
            self.font_s = pygame.font.Font(None, 24)
            self.font_m = pygame.font.Font(None, 36)
            self.font_l = pygame.font.Font(None, 74)
            self.font_xl = pygame.font.Font(None, 100)
        
        self.running = True
        self.game_state = "title"

        # Jugador
        self.player_x, self.player_y = 400, 300
        self.player_rect = pygame.Rect(400, 300, 40, 40)
        self.player_stats = {"Username": "Hero", "Level": 1, "HP": 100, "MaxHP": 100, "Mana": 100, "MaxMana": 100, "XP": 0}
        self.potions = 3
        self.player_speed = 5
        self.facing_right = True
        self.last_dir = (1, 0)

        # Progreso
        self.current_stage = 1
        self.kills_in_stage = 0
        self.target_kills = 5
        self.max_unlocked_level = 1
        
        self.levels_config = {
            1: {"name": "Bosque Inicio", "bg": "bg_forest.png", "obs": "tree.png", "enemy": "Goblin", "req": 3},
            2: {"name": "Espesura", "bg": "bg_forest.png", "obs": "tree.png", "enemy": "Goblin", "req": 4},
            3: {"name": "Bosque Oscuro", "bg": "bg_forest.png", "obs": "tree.png", "enemy": "Brain", "req": 4},
            4: {"name": "Cueva Entrada", "bg": "bg_cave.png", "obs": "rock.png", "enemy": "Brain", "req": 5},
            5: {"name": "Profundidades", "bg": "bg_cave.png", "obs": "rock.png", "enemy": "Shadow", "req": 5},
            6: {"name": "Nido Sombras", "bg": "bg_cave.png", "obs": "rock.png", "enemy": "Shadow", "req": 6},
            7: {"name": "Mazmorra", "bg": "bg_dungeon.png", "obs": "pillar.png", "enemy": "Brain", "req": 7},
            8: {"name": "Pasillo Lava", "bg": "bg_dungeon.png", "obs": "pillar.png", "enemy": "Shadow", "req": 8},
            9: {"name": "Sala Real", "bg": "bg_dungeon.png", "obs": "pillar.png", "enemy": "Shadow", "req": 10},
            10: {"name": "BOSS FINAL", "bg": "bg_dungeon.png", "obs": "pillar.png", "enemy": "Ogre", "req": 1}
        }

        self.difficulty_mult = 1.0 
        self.saving_icon_timer = 0
        self.last_damage_time = 0
        self.slash_timer = 0
        
        self.projectiles = []
        self.floating_texts = []
        self.particles = []
        self.obstacles = []
        self.monster_catalog = []
        self.images = {}
        self.sounds = {}
        self.enemy_projectiles = []
        self.enemy_action_timer = 0

        print("--- CARGANDO ---")
        self.load_all_assets()
        self.load_player_from_db()
        self.load_monsters_from_db()

    def load_image(self, name, size):
        try:
            img = pygame.image.load(name).convert_alpha()
            return pygame.transform.scale(img, size)
        except: return None

    def load_sound(self, name):
        if os.path.exists(name):
            try: return pygame.mixer.Sound(name)
            except: return None
        return None

    def load_all_assets(self):
        assets = {
            "bg_forest.png": (800,600), "bg_cave.png": (800,600), "bg_dungeon.png": (800,600),
            "tree.png": (60,80), "rock.png": (50,50), "pillar.png": (50,80),
            "player.png": (50,50), "slash.png": (80,80), "fireball.png": (30,30),
            "goblin.png": (50,50), "shadow.png": (50,50), "ogre.png": (180,180), "brain.png": (45,45)
        }
        for name, size in assets.items(): self.images[name] = self.load_image(name, size)
        
        # Audio Seguro
        if os.path.exists("music.mp3"):
            try:
                pygame.mixer.music.load("music.mp3")
                pygame.mixer.music.set_volume(1.0) # Volumen MAXIMO
                pygame.mixer.music.play(-1)
                print("Música OK")
            except: print("Error musica")
        
        self.sounds["hit"] = self.load_sound("hit.wav")
        self.sounds["magic"] = self.load_sound("magic.wav")
        self.sounds["drink"] = self.load_sound("drink.wav")

    def load_monsters_from_db(self):
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute("SELECT MonsterName, BaseHP, BaseAttack, BaseSpeed FROM MonsterCatalog")
                for r in c.fetchall(): self.monster_catalog.append({"Name": r[0], "HP": r[1], "MaxHP": r[1], "Attack": r[2], "Speed": r[3]})
                conn.close()
            except: pass
        if not self.monster_catalog: self.monster_catalog = [{"Name": "Goblin", "HP": 30, "MaxHP": 30, "Attack": 5, "Speed": 2}]

    def load_player_from_db(self):
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute("SELECT PlayerID FROM Players WHERE Username = 'Player1'")
                if not c.fetchone():
                    c.execute("INSERT INTO Players (Username, PasswordHash) VALUES ('Player1', '1234')"); conn.commit()
                    c.execute("SELECT PlayerID FROM Players WHERE Username = 'Player1'"); pid = c.fetchone()[0]
                    c.execute("INSERT INTO SaveGames (PlayerID, CurrentHP, MaxHP, PositionX, PositionY, Level, ExperiencePoints, PositionZ) VALUES (?, 100, 100, 400, 300, 1, 0, 1.0)", pid); conn.commit()
                
                c.execute("SELECT Level, CurrentHP, MaxHP, ExperiencePoints, PositionZ FROM SaveGames s JOIN Players p ON s.PlayerID = p.PlayerID WHERE p.Username = 'Player1'")
                data = c.fetchone()
                if data:
                    self.player_stats.update({"Level": data[0], "HP": data[1], "MaxHP": data[2], "XP": data[3]})
                    self.max_unlocked_level = int(data[4]) if data[4] else 1
                    if self.player_stats["HP"] <= 0: self.player_stats["HP"] = self.player_stats["MaxHP"]
                conn.close()
            except Exception as e: print(f"Error SQL: {e}")

    def save_game_to_db(self):
        self.saving_icon_timer = 60
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                hp_save = max(0, min(self.player_stats["HP"], self.player_stats["MaxHP"]))
                c.execute("""UPDATE SaveGames SET Level=?, CurrentHP=?, MaxHP=?, ExperiencePoints=?, PositionX=?, PositionY=?, PositionZ=?, LastSaved=GETDATE()
                             FROM SaveGames s JOIN Players p ON s.PlayerID=p.PlayerID WHERE p.Username='Player1'""",
                          (self.player_stats["Level"], hp_save, self.player_stats["MaxHP"], self.player_stats["XP"], self.player_x, self.player_y, float(self.max_unlocked_level)))
                conn.commit(); conn.close()
            except: pass

    def reset_progress(self):
        print("--- REINICIANDO PARTIDA ---")
        conn = get_db_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute("""UPDATE SaveGames SET Level=1, CurrentHP=100, MaxHP=100, ExperiencePoints=0, PositionX=400, PositionY=300, PositionZ=1.0, LastSaved=GETDATE()
                             FROM SaveGames s JOIN Players p ON s.PlayerID=p.PlayerID WHERE p.Username='Player1'""")
                conn.commit(); conn.close()
                self.player_stats = {"Username": "Hero", "Level": 1, "HP": 100, "MaxHP": 100, "Mana": 100, "MaxMana": 100, "XP": 0}
                self.max_unlocked_level = 1
                self.current_stage = 1
                self.potions = 3
                print("Reiniciado.")
            except: pass

    def start_level(self, stage):
        if stage > 10: self.game_state = "victory"; self.save_game_to_db(); return
        if stage > self.max_unlocked_level: self.max_unlocked_level = stage
        
        self.current_stage = stage
        config = self.levels_config[stage]
        self.target_kills = config["req"]
        self.kills_in_stage = 0
        self.player_stats["HP"] = self.player_stats["MaxHP"]
        self.save_game_to_db()
        
        self.projectiles = []; self.enemy_projectiles = []; self.particles = []; self.floating_texts = []; self.obstacles = []
        
        obs_key = config["obs"]
        for _ in range(12):
            while True:
                ox, oy = random.randint(50, GAME_WIDTH-100), random.randint(100, GAME_HEIGHT-100)
                rect = pygame.Rect(ox+10, oy+40, 30, 20)
                if not rect.colliderect(pygame.Rect(350, 250, 150, 150)):
                    self.obstacles.append({"rect": rect, "pos": (ox, oy), "img": obs_key}); break
        
        self.game_state = "playing"
        self.spawn_enemy()

    def spawn_enemy(self):
        conf = self.levels_config[self.current_stage]
        name = conf["enemy"]
        tmpl = next((m for m in self.monster_catalog if m["Name"] == name), self.monster_catalog[0])
        self.enemy_data = tmpl.copy()
        
        mult = 1 + (self.current_stage * 0.1)
        self.enemy_data["MaxHP"] = int(self.enemy_data["MaxHP"] * mult * self.difficulty_mult)
        self.enemy_data["HP"] = self.enemy_data["MaxHP"]
        self.enemy_data["Attack"] = int(self.enemy_data["Attack"] * mult * self.difficulty_mult)

        while True:
            ex, ey = random.randint(50, GAME_WIDTH-100), random.randint(100, GAME_HEIGHT-100)
            w, h = (150, 150) if name == "Ogre" else (50, 50)
            self.enemy_rect = pygame.Rect(ex, ey, w, h)
            if math.hypot(ex-self.player_x, ey-self.player_y) > 200: break

    def update(self):
        if self.player_stats["Mana"] < 100: self.player_stats["Mana"] += 0.2
        if self.player_stats["HP"] < self.player_stats["MaxHP"]: self.player_stats["HP"] += 0.02

        for p in self.projectiles[:]:
            p["rect"].x += p["v"][0]; p["rect"].y += p["v"][1]
            if not (0 < p["rect"].x < GAME_WIDTH and 0 < p["rect"].y < GAME_HEIGHT):
                if p in self.projectiles: self.projectiles.remove(p)
                continue
            if p["rect"].colliderect(self.enemy_rect):
                self.damage_enemy_ranged(25 + self.player_stats["Level"] * 2)
                if p in self.projectiles: self.projectiles.remove(p)
                break

        ename = self.enemy_data["Name"]
        speed = self.enemy_data.get("Speed", 2)
        ex, ey = self.enemy_rect.x, self.enemy_rect.y
        dist = math.hypot(self.player_x - ex, self.player_y - ey)

        if ename == "Brain": 
            if dist < 200: 
                if self.player_x > ex: ex -= speed
                else: ex += speed
                if self.player_y > ey: ey -= speed
                else: ey += speed
            else:
                if self.player_x > ex: ex += speed
                else: ex -= speed
            self.enemy_action_timer += 1
            if self.enemy_action_timer > 90:
                self.enemy_action_timer = 0
                dx, dy = self.player_x - ex, self.player_y - ey
                mag = math.sqrt(dx**2 + dy**2)
                if mag != 0: self.enemy_projectiles.append({"rect": pygame.Rect(ex+20, ey+20, 20, 20), "v": (dx/mag*7, dy/mag*7)})

        elif ename == "Shadow":
            if self.player_x > ex: ex += speed*1.2
            else: ex -= speed*1.2
            if self.player_y > ey: ey += speed*1.2
            else: ey -= speed*1.2
            self.enemy_action_timer += 1
            if self.enemy_action_timer > 120 and dist < 150:
                self.enemy_action_timer = 0
                ex = max(50, min(self.player_x + random.choice([-80, 80]), GAME_WIDTH-50))
                ey = max(100, min(self.player_y + random.choice([-80, 80]), GAME_HEIGHT-50))
                for _ in range(5): self.particles.append(Particle(ex, ey, BLACK))
        else: 
            if ename=="Ogre": speed=1.0
            if self.player_x > ex: ex += speed
            else: ex -= speed
            if self.player_y > ey: ey += speed
            else: ey -= speed

        ex = max(0, min(ex, GAME_WIDTH - self.enemy_rect.width))
        ey = max(100, min(ey, GAME_HEIGHT - self.enemy_rect.height))
        self.enemy_rect.x, self.enemy_rect.y = ex, ey

        if self.player_rect.colliderect(self.enemy_rect): self.take_damage(self.enemy_data["Attack"])

        for p in self.enemy_projectiles[:]:
            p["rect"].x += p["v"][0]; p["rect"].y += p["v"][1]
            if not (0 < p["rect"].x < GAME_WIDTH and 0 < p["rect"].y < GAME_HEIGHT):
                if p in self.enemy_projectiles: self.enemy_projectiles.remove(p)
                continue
            if p["rect"].colliderect(self.player_rect):
                self.take_damage(15); 
                if p in self.enemy_projectiles: self.enemy_projectiles.remove(p)

        for t in self.floating_texts[:]:
            t.update(); 
            if t.timer <= 0: self.floating_texts.remove(t)
        for part in self.particles[:]:
            part.update(); 
            if part.life <= 0: self.particles.remove(part)

    def take_damage(self, dmg):
        now = pygame.time.get_ticks()
        if now - self.last_damage_time > 1000:
            self.player_stats["HP"] -= dmg
            self.last_damage_time = now
            self.floating_texts.append(FloatingText(self.player_x, self.player_y, f"-{dmg}", RED, self.font_m))
            if self.player_stats["HP"] <= 0: self.game_state = "game_over"; self.save_game_to_db()

    def damage_enemy(self, dmg):
        self.enemy_data["HP"] -= dmg
        self.floating_texts.append(FloatingText(self.enemy_rect.centerx, self.enemy_rect.y, str(dmg), WHITE, self.font_m))
        if "hit" in self.sounds and self.sounds["hit"]: self.sounds["hit"].play()
        
        if self.enemy_data["HP"] <= 0:
            xp = 20 * self.current_stage; self.player_stats["XP"] += xp
            self.floating_texts.append(FloatingText(self.player_x, self.player_y, f"+{xp} XP", GOLD, self.font_m))
            if self.player_stats["XP"] >= self.player_stats["Level"]*100:
                self.player_stats["Level"] += 1; self.player_stats["XP"] = 0
                self.player_stats["MaxHP"] += 20; self.player_stats["HP"] = self.player_stats["MaxHP"]
                self.floating_texts.append(FloatingText(self.player_x, self.player_y-40, "LEVEL UP!", GREEN, self.font_l))
                self.save_game_to_db()
            for _ in range(8): self.particles.append(Particle(self.enemy_rect.centerx, self.enemy_rect.centery, RED))
            self.kills_in_stage += 1
            if self.kills_in_stage >= self.target_kills: self.start_level(self.current_stage + 1)
            else: self.spawn_enemy()

    # --- DISPARO & MELEE (RESTITUIDOS) ---
    def shoot(self):
        if self.player_stats["Mana"] >= 10:
            self.player_stats["Mana"] -= 10
            vx, vy = self.last_dir
            self.projectiles.append({"rect": pygame.Rect(self.player_x+20, self.player_y+20, 20, 20), "v": (vx*12, vy*12)})
            if "magic" in self.sounds and self.sounds["magic"]: self.sounds["magic"].play()
        else:
            self.floating_texts.append(FloatingText(self.player_x, self.player_y-30, "NO MANA", BLUE, self.font_s))

    def damage_enemy_ranged(self, dmg):
        self.enemy_data["HP"] -= dmg
        self.floating_texts.append(FloatingText(self.enemy_rect.centerx, self.enemy_rect.y, str(dmg), WHITE, self.font_m))
        if self.enemy_data["HP"] <= 0: self.handle_kill()

    def handle_kill(self):
        # Misma logica que damage_enemy
        xp = 20 * self.current_stage; self.player_stats["XP"] += xp
        self.floating_texts.append(FloatingText(self.player_x, self.player_y, f"+{xp} XP", GOLD, self.font_m))
        if self.player_stats["XP"] >= self.player_stats["Level"]*100:
            self.player_stats["Level"] += 1; self.player_stats["XP"] = 0
            self.player_stats["MaxHP"] += 20; self.player_stats["HP"] = self.player_stats["MaxHP"]
            self.floating_texts.append(FloatingText(self.player_x, self.player_y-40, "LEVEL UP!", GREEN, self.font_l))
            self.save_game_to_db()
        for _ in range(8): self.particles.append(Particle(self.enemy_rect.centerx, self.enemy_rect.centery, RED))
        self.kills_in_stage += 1
        if self.kills_in_stage >= self.target_kills: self.start_level(self.current_stage + 1)
        else: self.spawn_enemy()

    def attack_melee(self):
        self.slash_timer = 15
        atk_rect = self.player_rect.inflate(70, 70)
        if atk_rect.colliderect(self.enemy_rect):
            dmg = 20 + (self.player_stats["Level"] * 4)
            self.damage_enemy(dmg)

    def use_potion(self):
        if self.potions > 0 and self.player_stats["HP"] < self.player_stats["MaxHP"]:
            self.potions -= 1
            heal = int(self.player_stats["MaxHP"] * 0.5)
            self.player_stats["HP"] = min(self.player_stats["MaxHP"], self.player_stats["HP"] + heal)
            self.floating_texts.append(FloatingText(self.player_x, self.player_y, f"+{heal}", GREEN, self.font_m))
            if "drink" in self.sounds and self.sounds["drink"]: self.sounds["drink"].play()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1; self.facing_right = True
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
        if dx!=0 or dy!=0: self.last_dir = (dx, dy)
        
        self.player_x = max(0, min(self.player_x + dx*self.player_speed, GAME_WIDTH-40))
        self.player_y = max(100, min(self.player_y + dy*self.player_speed, GAME_HEIGHT-40))
        self.player_rect.topleft = (self.player_x, self.player_y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.save_game_to_db(); self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.game_state = "paused"
                if event.key == pygame.K_SPACE: self.attack_melee()
                if event.key == pygame.K_z: self.shoot()
                if event.key == pygame.K_h: self.use_potion()

    # --- DIBUJO ---
    def get_game_pos(self, mouse_pos):
        win_w, win_h = self.screen.get_size()
        scale_x = win_w / GAME_WIDTH
        scale_y = win_h / GAME_HEIGHT
        scale = min(scale_x, scale_y)
        new_w = int(GAME_WIDTH * scale); new_h = int(GAME_HEIGHT * scale)
        offset_x = (win_w - new_w) // 2; offset_y = (win_h - new_h) // 2
        mx = (mouse_pos[0] - offset_x) / scale
        my = (mouse_pos[1] - offset_y) / scale
        return (mx, my)

    def draw_panel(self, x, y, w, h):
        pygame.draw.rect(self.canvas, DARK_BLUE, (x, y, w, h))
        pygame.draw.rect(self.canvas, SILVER, (x, y, w, h), 3)

    def draw_bar_pro(self, x, y, current, max_val, color, label):
        bar_w, bar_h = 200, 20
        pygame.draw.rect(self.canvas, BLACK, (x, y, bar_w, bar_h))
        pct = max(0, min(current / max_val, 1))
        pygame.draw.rect(self.canvas, color, (x, y, bar_w * pct, bar_h))
        pygame.draw.rect(self.canvas, WHITE, (x, y, bar_w, bar_h), 2)
        lbl = self.font_s.render(f"{label}: {int(current)}/{max_val}", True, WHITE)
        self.canvas.blit(lbl, (x + 5, y + 2))

    def draw_ui(self):
        if self.images["bg_forest.png"]: self.canvas.blit(self.images["bg_forest.png"], (0,0))
        s = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA); s.fill(DARK_OVERLAY); self.canvas.blit(s,(0,0))
        
        real_mouse = pygame.mouse.get_pos()
        m = self.get_game_pos(real_mouse)
        click = pygame.mouse.get_pressed()[0]

        if self.game_state == "title":
            t = self.font_l.render("RETRO RPG", True, GOLD)
            shadow = self.font_l.render("RETRO RPG", True, BLACK)
            self.canvas.blit(shadow, (GAME_WIDTH//2-t.get_width()//2+4, 104))
            self.canvas.blit(t, (GAME_WIDTH//2-t.get_width()//2, 100))
            
            bx, by, bw, bh = 300, 280, 200, 60
            self.draw_panel(bx, by, bw, bh)
            btn_txt = self.font_m.render("JUGAR", True, WHITE)
            if pygame.Rect(bx, by, bw, bh).collidepoint(m): 
                pygame.draw.rect(self.canvas, WHITE, (bx, by, bw, bh), 3)
                if click: self.game_state = "level_select"; pygame.time.delay(200)
            self.canvas.blit(btn_txt, (bx + (bw-btn_txt.get_width())//2, by + 20))

        elif self.game_state == "level_select":
            t = self.font_l.render("MAPAS", True, WHITE)
            self.canvas.blit(t, (GAME_WIDTH//2 - t.get_width()//2, 30))
            for i in range(1, 11):
                col = 0 if i <= 5 else 1; row = (i-1) % 5
                x, y = 100 + col * 350, 100 + row * 80
                unlk = i <= self.max_unlocked_level
                nm = self.levels_config.get(i, {}).get("name", f"Nivel {i}")
                
                self.draw_panel(x, y, 300, 60)
                color_txt = GREEN if unlk else RED
                txt = self.font_s.render(nm if unlk else "BLOQUEADO", True, color_txt)
                self.canvas.blit(txt, (x + 20, y + 25))
                if unlk and pygame.Rect(x,y,300,60).collidepoint(m) and click:
                    self.start_level(i); pygame.time.delay(200)

            # Botón RESET
            rx, ry, rw, rh = 300, 520, 200, 60
            self.draw_panel(rx, ry, rw, rh)
            pygame.draw.rect(self.canvas, RED, (rx, ry, rw, rh), 1)
            rtxt = self.font_m.render("RESET", True, RED)
            if pygame.Rect(rx, ry, rw, rh).collidepoint(m):
                pygame.draw.rect(self.canvas, RED, (rx, ry, rw, rh), 3)
                if click: self.reset_progress(); pygame.time.delay(500)
            self.canvas.blit(rtxt, (rx + (rw-rtxt.get_width())//2, ry + 20))


        elif self.game_state == "paused":
            self.draw_panel(200, 200, 400, 200)
            t = self.font_l.render("PAUSA", True, WHITE)
            self.canvas.blit(t, (GAME_WIDTH//2 - t.get_width()//2, 220))
            msg = self.font_s.render("ESC: Volver | Q: Menu", True, YELLOW)
            self.canvas.blit(msg, (GAME_WIDTH//2 - msg.get_width()//2, 300))

    def draw_game(self):
        conf = self.levels_config[self.current_stage]
        if self.images[conf["bg"]]: self.canvas.blit(self.images[conf["bg"]], (0,0))
        
        draw_list = []
        for o in self.obstacles: draw_list.append({"y": o["pos"][1]+50, "type": "obs", "obj": o})
        draw_list.append({"y": self.player_y+50, "type": "player"})
        draw_list.append({"y": self.enemy_rect.y+50, "type": "enemy"})
        draw_list.sort(key=lambda x: x["y"])
        
        for item in draw_list:
            if item["type"] == "obs":
                o = item["obj"]
                if self.images[o["img"]]: self.canvas.blit(self.images[o["img"]], o["pos"])
            elif item["type"] == "player":
                img = self.images["player.png"] 
                if not self.facing_right: img = pygame.transform.flip(img, True, False)
                self.canvas.blit(img, (self.player_x, self.player_y))
                if self.slash_timer > 0:
                    sl = self.images["slash.png"] 
                    if sl: self.canvas.blit(sl, (self.player_x-15, self.player_y-15))
            elif item["type"] == "enemy":
                img_name = conf["enemy"]
                filename = ""
                if img_name == "Goblin": filename = "goblin.png"
                elif img_name == "Shadow": filename = "shadow.png"
                elif img_name == "Brain": filename = "brain.png"
                elif img_name == "Ogre": filename = "ogre.png"
                
                img = self.images.get(filename) 
                if img: self.canvas.blit(img, self.enemy_rect.topleft)
                else: pygame.draw.rect(self.canvas, RED, self.enemy_rect)
                pct = max(0, self.enemy_data["HP"] / self.enemy_data["MaxHP"])
                pygame.draw.rect(self.canvas, RED, (self.enemy_rect.x, self.enemy_rect.y-10, 50*pct, 5))

        for p in self.projectiles:
            if self.images["fireball.png"]: self.canvas.blit(self.images["fireball.png"], p["rect"]) 
            else: pygame.draw.circle(self.canvas, ORANGE, p["rect"].center, 6)
        for ep in self.enemy_projectiles:
            pygame.draw.circle(self.canvas, PURPLE, ep["rect"].center, 8) 
            
        for t in self.floating_texts: t.draw(self.canvas)
        for p in self.particles: p.draw(self.canvas)

        self.draw_panel(0, 0, GAME_WIDTH, 80)
        info = f"{self.player_stats['Username']} | LVL {self.player_stats['Level']}"
        self.canvas.blit(self.font_m.render(info, True, GOLD), (20, 15))
        self.draw_bar_pro(20, 45, self.player_stats["HP"], self.player_stats["MaxHP"], RED, "HP")
        self.draw_bar_pro(240, 45, self.player_stats["Mana"], 100, BLUE, "MP")
        self.canvas.blit(self.font_s.render(f"Pociones: {self.potions} [H]", True, GREEN), (460, 20))
        goal = f"Meta: {self.target_kills - self.kills_in_stage}"
        if self.current_stage==10: goal = "BOSS FINAL"
        self.canvas.blit(self.font_m.render(goal, True, RED), (460, 50))

        if self.saving_icon_timer > 0:
            self.saving_icon_timer -= 1
            pygame.draw.circle(self.canvas, YELLOW, (GAME_WIDTH-30, GAME_HEIGHT-30), 8)

    def draw_victory_screen(self):
        s = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA); s.fill(DARK_OVERLAY)
        self.canvas.blit(s, (0,0))
        
        t = self.font_xl.render("¡VICTORIA!", True, GOLD)
        t_rect = t.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//3))
        self.canvas.blit(t, t_rect)
        
        sub = self.font_m.render("Has salvado el reino.", True, WHITE)
        sub_rect = sub.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//2))
        self.canvas.blit(sub, sub_rect)

        bx, by, bw, bh = GAME_WIDTH//2 - 100, GAME_HEIGHT//2 + 100, 200, 60
        self.draw_panel(bx, by, bw, bh)
        
        real_mouse = pygame.mouse.get_pos()
        m = self.get_game_pos(real_mouse)
        click = pygame.mouse.get_pressed()[0]
        
        if pygame.Rect(bx, by, bw, bh).collidepoint(m):
            pygame.draw.rect(self.canvas, WHITE, (bx, by, bw, bh), 3)
            if click: self.game_state = "title"; pygame.time.delay(200)
            
        btn_txt = self.font_m.render("MENU", True, WHITE)
        self.canvas.blit(btn_txt, (bx + (bw-btn_txt.get_width())//2, by + 20))

    def draw_window(self):
        win_w, win_h = self.screen.get_size()
        scale_x = win_w / GAME_WIDTH
        scale_y = win_h / GAME_HEIGHT
        scale = min(scale_x, scale_y)
        new_w = int(GAME_WIDTH * scale); new_h = int(GAME_HEIGHT * scale)
        offset_x = (win_w - new_w) // 2; offset_y = (win_h - new_h) // 2
        scaled_surf = pygame.transform.scale(self.canvas, (new_w, new_h))
        self.screen.fill(BLACK) 
        self.screen.blit(scaled_surf, (offset_x, offset_y))
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.save_game_to_db(); self.running = False
                if event.type == pygame.KEYDOWN:
                    if self.game_state == "playing":
                        if event.key == pygame.K_ESCAPE: self.game_state = "paused"
                        if event.key == pygame.K_SPACE: self.attack_melee()
                        if event.key == pygame.K_z: self.shoot()
                        if event.key == pygame.K_h: self.use_potion()
                    elif self.game_state == "paused":
                        if event.key == pygame.K_ESCAPE: self.game_state = "playing"
                        if event.key == pygame.K_q: self.save_game_to_db(); self.game_state = "title"

            if self.game_state == "playing": self.handle_input(); self.update(); self.draw_game()
            elif self.game_state == "title": self.draw_ui()
            elif self.game_state == "level_select": self.draw_ui()
            elif self.game_state == "paused": self.draw_ui()
            elif self.game_state == "game_over":
                self.canvas.fill(BLACK)
                t = self.font_l.render("GAME OVER", True, RED)
                self.canvas.blit(t, (GAME_WIDTH//2-t.get_width()//2, 250))
                self.draw_victory_screen() 
            elif self.game_state == "victory":
                self.draw_game()
                self.draw_victory_screen()

            self.draw_window()
            self.clock.tick(FPS)
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    game = GameEngine()
    game.run()