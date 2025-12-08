import pygame
import pyodbc
import random
import sys
import math
from db_connection import get_db_connection

# --- CONFIGURACIÓN ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
BLUE = (30, 144, 255)
PURPLE = (148, 0, 211) 
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
ORANGE = (255, 140, 0)
GRAY = (128, 128, 128)
DARK_OVERLAY = (0, 0, 0, 150)

FPS = 60

# --- EFECTOS ---
class FloatingText:
    def __init__(self, x, y, text, color):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.timer = 40
        self.font = pygame.font.Font(None, 28)
    def update(self):
        self.y -= 1; self.timer -= 1
    def draw(self, screen):
        if self.timer > 0: screen.blit(self.font.render(str(self.text), True, self.color), (self.x, self.y))

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.size = random.randint(3, 6)
        self.life = random.randint(15, 30)
        self.vx, self.vy = random.uniform(-2, 2), random.uniform(-2, 2)
    def update(self):
        self.x += self.vx; self.y += self.vy; self.life -= 1
    def draw(self, screen):
        if self.life > 0: pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

# --- MOTOR DE JUEGO ---
class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Retro RPG - PROYECTO FINAL")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 80)
        self.ui_font = pygame.font.Font(None, 28) 
        
        self.running = True
        self.game_state = "title"

        # --- JUGADOR ---
        self.player_x, self.player_y = 400, 300
        self.player_rect = pygame.Rect(400, 300, 40, 40)
        self.player_stats = {"Username": "Hero", "Level": 1, "HP": 100, "MaxHP": 100, "Mana": 100, "MaxMana": 100, "XP": 0}
        self.potions = 3
        self.player_speed = 5
        self.facing_right = True
        self.last_dir = (1, 0)

        # --- NIVELES ---
        self.current_stage = 1
        self.kills_in_stage = 0
        self.target_kills = 5
        self.max_unlocked_level = 1
        
        self.enemy_action_timer = 0
        self.enemy_projectiles = []

        # Configuración de Niveles
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

        # --- SISTEMAS ---
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

        print("--- CONECTANDO SISTEMAS ---")
        self.load_all_assets()
        self.load_player_from_db()
        self.load_monsters_from_db()

    def load_image(self, name, size):
        try:
            img = pygame.image.load(name).convert_alpha()
            return pygame.transform.scale(img, size)
        except: 
            return None

    def load_all_assets(self):
        # 1. Fondos
        self.images["bg_forest.png"] = self.load_image('bg_forest.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.images["bg_cave.png"] = self.load_image('bg_cave.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.images["bg_dungeon.png"] = self.load_image('bg_dungeon.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 2. Objetos
        self.images["tree.png"] = self.load_image('tree.png', (60, 80))
        self.images["rock.png"] = self.load_image('rock.png', (50, 50))
        self.images["pillar.png"] = self.load_image('pillar.png', (50, 80))

        # 3. Personaje y Efectos
        self.images["player"] = self.load_image('player.png', (50, 50))
        self.images["slash"] = self.load_image('slash.png', (80, 80))
        self.images["fireball"] = self.load_image('fireball.png', (30, 30))

        # 4. Enemigos (Mapeo Manual Seguro)
        self.images["Goblin"] = self.load_image('goblin.png', (50, 50))
        self.images["Shadow"] = self.load_image('shadow.png', (50, 50))
        self.images["Ogre"] = self.load_image('ogre.png', (180, 180))
        self.images["Brain"] = self.load_image('brain.png', (45, 45))

    def load_monsters_from_db(self):
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MonsterName, BaseHP, BaseAttack, BaseSpeed FROM MonsterCatalog")
                for row in cursor.fetchall():
                    self.monster_catalog.append({"Name": row[0], "HP": row[1], "MaxHP": row[1], "Attack": row[2], "Speed": row[3]})
                conn.close()
            except: pass
        if not self.monster_catalog: self.monster_catalog = [{"Name": "Goblin", "HP": 30, "MaxHP": 30, "Attack": 5, "Speed": 2}]

    def load_player_from_db(self):
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT PlayerID FROM Players WHERE Username = 'Player1'")
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO Players (Username, PasswordHash) VALUES ('Player1', '1234')")
                    conn.commit()
                    cursor.execute("SELECT PlayerID FROM Players WHERE Username = 'Player1'")
                    pid = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO SaveGames (PlayerID, CurrentHP, MaxHP, PositionX, PositionY, Level, ExperiencePoints, PositionZ) VALUES (?, 100, 100, 400, 300, 1, 0, 1.0)", pid)
                    conn.commit()
                
                cursor.execute("SELECT p.Username, s.Level, s.CurrentHP, s.MaxHP, s.ExperiencePoints, s.PositionZ FROM SaveGames s JOIN Players p ON s.PlayerID = p.PlayerID WHERE p.Username = 'Player1'")
                data = cursor.fetchone()
                if data:
                    self.player_stats.update({"Username": data[0], "Level": data[1], "HP": data[2], "MaxHP": data[3], "XP": data[4]})
                    self.max_unlocked_level = int(data[5]) if data[5] else 1
                    if self.player_stats["HP"] <= 0: self.player_stats["HP"] = self.player_stats["MaxHP"]
                conn.close()
            except Exception as e: print(f"Error SQL: {e}")

    def save_game_to_db(self):
        self.saving_icon_timer = 60
        print(f"INTENTANDO GUARDAR -> Nivel: {self.player_stats['Level']} | XP: {self.player_stats['XP']}") 
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    UPDATE SaveGames 
                    SET Level = ?, CurrentHP = ?, MaxHP = ?, ExperiencePoints = ?, PositionX = ?, PositionY = ?, PositionZ = ?, LastSaved = GETDATE()
                    FROM SaveGames s JOIN Players p ON s.PlayerID = p.PlayerID
                    WHERE p.Username = 'Player1'
                """
                hp_save = max(0, min(self.player_stats["HP"], self.player_stats["MaxHP"]))
                cursor.execute(query, (self.player_stats["Level"], hp_save, self.player_stats["MaxHP"], self.player_stats["XP"], self.player_x, self.player_y, float(self.max_unlocked_level)))
                conn.commit() 
                conn.close()
                print("--> SQL SUCCESS: Datos guardados correctamente.")
            except Exception as e: print(f"--> SQL ERROR: {e}")

    def start_level(self, stage):
        if stage > 10: 
            self.game_state = "victory"
            self.save_game_to_db()
            return
        
        if stage > self.max_unlocked_level: self.max_unlocked_level = stage
        
        self.current_stage = stage
        config = self.levels_config[stage]
        self.target_kills = config["req"]
        self.kills_in_stage = 0
        self.player_stats["HP"] = self.player_stats["MaxHP"]
        self.save_game_to_db()
        
        self.projectiles.clear(); self.enemy_projectiles.clear()
        self.particles.clear(); self.floating_texts.clear(); self.obstacles.clear()
        
        obs_key = config["obs"]
        for _ in range(12):
            while True:
                ox, oy = random.randint(50, 700), random.randint(50, 500)
                rect = pygame.Rect(ox+10, oy+40, 30, 20)
                if not rect.colliderect(pygame.Rect(350, 250, 150, 150)):
                    self.obstacles.append({"rect": rect, "pos": (ox, oy), "img": obs_key})
                    break
        
        self.game_state = "playing"
        self.spawn_enemy()

    def spawn_enemy(self):
        config = self.levels_config[self.current_stage]
        name = config["enemy"]
        template = next((m for m in self.monster_catalog if m["Name"] == name), self.monster_catalog[0])
        self.enemy_data = template.copy()
        
        mult = 1 + (self.current_stage * 0.1)
        self.enemy_data["MaxHP"] = int(self.enemy_data["MaxHP"] * mult * self.difficulty_mult)
        self.enemy_data["HP"] = self.enemy_data["MaxHP"]
        self.enemy_data["Attack"] = int(self.enemy_data["Attack"] * mult * self.difficulty_mult)

        while True:
            ex, ey = random.randint(50, 700), random.randint(50, 500)
            w, h = (150, 150) if name == "Ogre" else (50, 50)
            self.enemy_rect = pygame.Rect(ex, ey, w, h)
            if math.hypot(ex - self.player_x, ey - self.player_y) > 200: break

    # --- IA ENEMIGA ---
    def update_enemy_ai(self):
        ename = self.enemy_data["Name"]
        speed = self.enemy_data.get("Speed", 2)
        ex, ey = self.enemy_rect.x, self.enemy_rect.y
        dist = math.hypot(self.player_x - ex, self.player_y - ey)

        # BRAIN
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
                if mag != 0:
                    self.enemy_projectiles.append({"rect": pygame.Rect(ex+20, ey+20, 20, 20), "v": (dx/mag*7, dy/mag*7)})

        # SHADOW
        elif ename == "Shadow":
            if self.player_x > ex: ex += speed * 1.2
            else: ex -= speed * 1.2
            if self.player_y > ey: ey += speed * 1.2
            else: ey -= speed * 1.2
            
            self.enemy_action_timer += 1
            if self.enemy_action_timer > 120 and dist < 150:
                self.enemy_action_timer = 0
                ex = self.player_x + random.choice([-60, 60])
                ey = self.player_y + random.choice([-60, 60])
                for _ in range(5): self.particles.append(Particle(ex, ey, BLACK))

        # OTROS
        else: 
            if ename == "Ogre": speed = 1.0
            if self.player_x > ex: ex += speed
            else: ex -= speed
            if self.player_y > ey: ey += speed
            else: ey -= speed

        ex = max(50, min(ex, SCREEN_WIDTH - 100))
        ey = max(50, min(ey, SCREEN_HEIGHT - 100))

        self.enemy_rect.x, self.enemy_rect.y = ex, ey

        if self.player_rect.colliderect(self.enemy_rect):
            self.take_damage(self.enemy_data["Attack"])

        for p in self.enemy_projectiles[:]:
            p["rect"].x += p["v"][0]; p["rect"].y += p["v"][1]
            if not (0 < p["rect"].x < SCREEN_WIDTH and 0 < p["rect"].y < SCREEN_HEIGHT):
                if p in self.enemy_projectiles: self.enemy_projectiles.remove(p)
                continue
            if p["rect"].colliderect(self.player_rect):
                self.take_damage(15)
                if p in self.enemy_projectiles: self.enemy_projectiles.remove(p)

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now - self.last_damage_time > 1000:
            self.player_stats["HP"] -= amount
            self.last_damage_time = now
            self.floating_texts.append(FloatingText(self.player_x, self.player_y, f"-{amount}", RED))
            if self.player_stats["HP"] <= 0: 
                self.game_state = "game_over"
                self.save_game_to_db()

    def use_potion(self):
        if self.potions > 0 and self.player_stats["HP"] < self.player_stats["MaxHP"]:
            self.potions -= 1
            heal = int(self.player_stats["MaxHP"] * 0.5)
            self.player_stats["HP"] = min(self.player_stats["MaxHP"], self.player_stats["HP"] + heal)
            self.floating_texts.append(FloatingText(self.player_x, self.player_y, f"+{heal}", GREEN))

    def shoot(self):
        if self.player_stats["Mana"] >= 10:
            self.player_stats["Mana"] -= 10
            vx, vy = self.last_dir
            self.projectiles.append({"rect": pygame.Rect(self.player_x+20, self.player_y+20, 20, 20), "v": (vx*12, vy*12)})
        else:
            self.floating_texts.append(FloatingText(self.player_x, self.player_y-30, "NO MANA", BLUE))

    def attack_melee(self):
        self.slash_timer = 15
        atk_rect = self.player_rect.inflate(70, 70)
        if atk_rect.colliderect(self.enemy_rect):
            dmg = 20 + (self.player_stats["Level"] * 4)
            self.enemy_data["HP"] -= dmg
            self.floating_texts.append(FloatingText(self.enemy_rect.centerx, self.enemy_rect.y, str(dmg), WHITE))
            dx = self.enemy_rect.centerx - self.player_x
            dy = self.enemy_rect.centery - self.player_y
            self.enemy_rect.x += dx * 0.2
            self.enemy_rect.y += dy * 0.2
            if self.enemy_data["HP"] <= 0: self.handle_kill()

    def handle_kill(self):
        xp = 20 * self.current_stage
        self.player_stats["XP"] += xp
        self.floating_texts.append(FloatingText(self.player_x, self.player_y, f"+{xp} XP", GOLD))
        
        if self.player_stats["XP"] >= self.player_stats["Level"] * 100:
            self.player_stats["Level"] += 1
            self.player_stats["XP"] = 0
            self.player_stats["MaxHP"] += 20
            self.player_stats["HP"] = self.player_stats["MaxHP"]
            self.floating_texts.append(FloatingText(self.player_x, self.player_y-40, "LEVEL UP!", GREEN))
            self.save_game_to_db()

        for _ in range(8): self.particles.append(Particle(self.enemy_rect.centerx, self.enemy_rect.centery, RED))
        
        self.kills_in_stage += 1
        if self.kills_in_stage >= self.target_kills:
            self.start_level(self.current_stage + 1)
        else:
            self.spawn_enemy()

    def update(self):
        if self.player_stats["Mana"] < 100: self.player_stats["Mana"] += 0.2
        if self.player_stats["HP"] < self.player_stats["MaxHP"]: self.player_stats["HP"] += 0.02

        for p in self.projectiles[:]:
            p["rect"].x += p["v"][0]; p["rect"].y += p["v"][1]
            if not (0 < p["rect"].x < SCREEN_WIDTH and 0 < p["rect"].y < SCREEN_HEIGHT):
                if p in self.projectiles: self.projectiles.remove(p)
                continue
            if p["rect"].colliderect(self.enemy_rect):
                self.damage_enemy_ranged(25 + self.player_stats["Level"] * 2)
                if p in self.projectiles: self.projectiles.remove(p)
                break
        
        self.update_enemy_ai()

        for t in self.floating_texts[:]:
            t.update()
            if t.timer <= 0: self.floating_texts.remove(t)
        for part in self.particles[:]:
            part.update()
            if part.life <= 0: self.particles.remove(part)

    def damage_enemy_ranged(self, dmg):
        self.enemy_data["HP"] -= dmg
        self.floating_texts.append(FloatingText(self.enemy_rect.centerx, self.enemy_rect.y, str(dmg), WHITE))
        if self.enemy_data["HP"] <= 0: self.handle_kill()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1; self.facing_right = True
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
        
        if dx!=0 or dy!=0: self.last_dir = (dx, dy)
        
        self.player_x += dx * self.player_speed
        self.player_rect.x = self.player_x
        for obs in self.obstacles:
            if self.player_rect.colliderect(obs["rect"]): self.player_x -= dx*self.player_speed; self.player_rect.x = self.player_x
            
        self.player_y += dy * self.player_speed
        self.player_rect.y = self.player_y
        for obs in self.obstacles:
            if self.player_rect.colliderect(obs["rect"]): self.player_y -= dy*self.player_speed; self.player_rect.y = self.player_y
        
        self.player_x = max(0, min(self.player_x, SCREEN_WIDTH - 40))
        self.player_y = max(0, min(self.player_y, SCREEN_HEIGHT - 40))
        self.player_rect.topleft = (self.player_x, self.player_y)

    def draw_button(self, text, x, y, w, h, active=True, hover=False):
        color = GOLD if hover and active else (GRAY if not active else WHITE)
        bg = (60, 60, 60) if active else (30, 30, 30)
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, bg, rect); pygame.draw.rect(self.screen, color, rect, 3)
        t = self.ui_font.render(text, True, color)
        self.screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))
        return rect

    def draw_ui(self):
        if self.images["bg_forest.png"]: self.screen.blit(self.images["bg_forest.png"], (0,0))
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); s.fill(DARK_OVERLAY); self.screen.blit(s,(0,0))
        m = pygame.mouse.get_pos(); click = pygame.mouse.get_pressed()[0]

        if self.game_state == "title":
            t = self.title_font.render("RETRO RPG", True, GOLD)
            self.screen.blit(t, (SCREEN_WIDTH//2-t.get_width()//2, 80))
            if self.draw_button("JUGAR", 300, 250, 200, 60, True, 300<m[0]<500 and 250<m[1]<310).collidepoint(m) and click:
                self.game_state = "level_select"; pygame.time.delay(200)

        elif self.game_state == "level_select":
            self.screen.blit(self.title_font.render("MAPAS", True, WHITE), (300, 20))
            for i in range(1, 11):
                col = 0 if i <= 5 else 1; row = (i-1) % 5
                x, y = 100 + col * 350, 100 + row * 80
                unlk = i <= self.max_unlocked_level
                nm = f"{i}. {self.levels_config[i]['name']}"
                if self.draw_button(nm if unlk else "BLOQUEADO", x, y, 300, 60, unlk, x<m[0]<x+300 and y<m[1]<y+60).collidepoint(m) and click and unlk:
                    self.start_level(i); pygame.time.delay(200)

        elif self.game_state == "paused":
            t = self.title_font.render("PAUSA", True, WHITE)
            self.screen.blit(t, (SCREEN_WIDTH//2-100, 200))
            s = self.font.render("ESC: Volver | Q: Guardar y Salir", True, YELLOW)
            self.screen.blit(s, (SCREEN_WIDTH//2-180, 300))

    def draw_game(self):
        conf = self.levels_config[self.current_stage]
        if self.images[conf["bg"]]: self.screen.blit(self.images[conf["bg"]], (0,0))
        
        draw_list = []
        for o in self.obstacles: draw_list.append({"y": o["pos"][1]+50, "type": "obs", "obj": o})
        draw_list.append({"y": self.player_y+50, "type": "player"})
        draw_list.append({"y": self.enemy_rect.y+50, "type": "enemy"})
        draw_list.sort(key=lambda x: x["y"])
        
        for item in draw_list:
            if item["type"] == "obs":
                o = item["obj"]
                if self.images[o["img"]]: self.screen.blit(self.images[o["img"]], o["pos"])
            elif item["type"] == "player":
                img = self.images["player"]
                if not self.facing_right: img = pygame.transform.flip(img, True, False)
                self.screen.blit(img, (self.player_x, self.player_y))
                if self.slash_timer > 0:
                    self.slash_timer -= 1
                    if self.images["slash"]: self.screen.blit(self.images["slash"], (self.player_x-15, self.player_y-15))
            elif item["type"] == "enemy":
                # --- AQUI ESTA EL ARREGLO DEL BUG DE KEYERROR ---
                # Usamos .get() para evitar crashes si la imagen no existe
                ename = conf["enemy"]
                img = self.images.get(ename) 
                
                if img: self.screen.blit(img, self.enemy_rect.topleft)
                else: pygame.draw.rect(self.screen, RED, self.enemy_rect) # Fallback rojo
                
                pct = max(0, self.enemy_data["HP"] / self.enemy_data["MaxHP"])
                pygame.draw.rect(self.screen, RED, (self.enemy_rect.x, self.enemy_rect.y-10, 50*pct, 5))

        for p in self.projectiles:
            pygame.draw.circle(self.screen, ORANGE, p["rect"].center, 6)
        for ep in self.enemy_projectiles:
            pygame.draw.circle(self.screen, PURPLE, ep["rect"].center, 8) 
            
        for t in self.floating_texts: t.draw(self.screen)
        for p in self.particles: p.draw(self.screen)

        pygame.draw.rect(self.screen, (0,0,0,180), (0,0,SCREEN_WIDTH, 50))
        self.screen.blit(self.font.render(f"{self.player_stats['Username']} | LVL {self.player_stats['Level']}", True, WHITE), (10, 10))
        
        pygame.draw.rect(self.screen, RED, (220, 10, 200, 15))
        pygame.draw.rect(self.screen, GREEN, (220, 10, 200 * (max(0,self.player_stats["HP"])/self.player_stats["MaxHP"]), 15))
        pygame.draw.rect(self.screen, BLUE, (220, 30, 150 * (self.player_stats["Mana"]/100), 8))
        
        self.screen.blit(self.font.render(f"Pociones: {self.potions} (H)", True, YELLOW), (450, 10))
        goal = f"Faltan: {self.target_kills - self.kills_in_stage}"
        if self.current_stage==10: goal = "BOSS FINAL"
        self.screen.blit(self.font.render(goal, True, GOLD), (600, 10))

        if self.saving_icon_timer > 0:
            self.saving_icon_timer -= 1
            pygame.draw.circle(self.screen, YELLOW, (SCREEN_WIDTH-30, SCREEN_HEIGHT-30), 8)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.save_game_to_db(); self.running = False
                
                if self.game_state == "playing":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE: self.game_state = "paused"
                        if event.key == pygame.K_SPACE: self.attack_melee()
                        if event.key == pygame.K_z: self.shoot()
                        if event.key == pygame.K_h: self.use_potion()
                
                elif self.game_state == "paused":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE: self.game_state = "playing"
                        if event.key == pygame.K_q: self.save_game_to_db(); self.game_state = "title"

                elif self.game_state in ["game_over", "victory"]:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.game_state = "title"

            if self.game_state in ["title", "level_select", "paused"]: self.draw_ui()
            elif self.game_state == "playing": self.handle_input(); self.update(); self.draw_game()
            elif self.game_state == "game_over":
                self.screen.fill(BLACK)
                self.screen.blit(self.title_font.render("GAME OVER", True, RED), (250, 250))
                self.screen.blit(self.font.render("R para Menu", True, WHITE), (330, 350))
            elif self.game_state == "victory":
                self.screen.fill(WHITE)
                self.screen.blit(self.title_font.render("VICTORIA!", True, GOLD), (250, 250))

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    game = GameEngine()
    game.run()