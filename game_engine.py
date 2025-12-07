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
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
ORANGE = (255, 140, 0)
GRAY = (100, 100, 100)
DARK_OVERLAY = (0, 0, 0, 200)

FPS = 60

# --- CLASES AUXILIARES (EFECTOS) ---
class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.timer = 40 
        self.font = pygame.font.Font(None, 28)
        
    def update(self):
        self.y -= 1 
        self.timer -= 1
        
    def draw(self, screen):
        if self.timer > 0:
            surf = self.font.render(self.text, True, self.color)
            screen.blit(surf, (self.x, self.y))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 8)
        self.life = random.randint(20, 40)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size -= 0.1
        
    def draw(self, screen):
        if self.life > 0 and self.size > 0:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

# --- MOTOR PRINCIPAL ---
class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Retro RPG - ULTIMATE EDITION")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 80)
        
        self.running = True
        self.game_state = "title"

        # --- NIVELES ---
        self.levels_config = {
            1: {"name": "Bosque Incial", "bg": "bg_forest.png", "obs": "tree.png", "enemy": "Goblin", "kills": 3},
            2: {"name": "Espesura Verde", "bg": "bg_forest.png", "obs": "tree.png", "enemy": "Goblin", "kills": 4},
            3: {"name": "Claro del Bosque", "bg": "bg_forest.png", "obs": "tree.png", "enemy": "Brain", "kills": 5},
            4: {"name": "Entrada a la Cueva", "bg": "bg_cave.png", "obs": "rock.png", "enemy": "Brain", "kills": 5},
            5: {"name": "Profundidades", "bg": "bg_cave.png", "obs": "rock.png", "enemy": "Shadow", "kills": 6},
            6: {"name": "Nido de Sombras", "bg": "bg_cave.png", "obs": "rock.png", "enemy": "Shadow", "kills": 7},
            7: {"name": "Mazmorra de Lava", "bg": "bg_dungeon.png", "obs": "pillar.png", "enemy": "Shadow", "kills": 6},
            8: {"name": "Pasillo Infernal", "bg": "bg_dungeon.png", "obs": "pillar.png", "enemy": "Brain", "kills": 8},
            9: {"name": "Sala del Trono", "bg": "bg_dungeon.png", "obs": "pillar.png", "enemy": "Shadow", "kills": 10},
            10: {"name": "BOSS FINAL", "bg": "bg_dungeon.png", "obs": "pillar.png", "enemy": "Ogre", "kills": 1}
        }

        # --- JUGADOR ---
        self.player_x = 400
        self.player_y = 300
        self.player_rect = pygame.Rect(self.player_x, self.player_y, 40, 40)
        self.player_stats = {"Username": "Hero", "Level": 1, "HP": 100, "MaxHP": 100, "Mana": 100, "MaxMana": 100}
        self.potions = 3
        self.player_speed = 5
        self.facing_right = True
        self.last_move_dir = (1, 0)

        # --- SISTEMAS ---
        self.difficulty = "Normal"
        self.difficulty_mult = 1.0
        self.max_unlocked_level = 1 
        self.current_stage = 1
        self.kills_in_stage = 0
        self.target_kills = 5
        
        # --- EFECTOS ---
        self.slash_timer = 0
        self.hit_flash_timer = 0 
        self.last_damage_time = 0
        self.projectiles = [] 
        self.floating_texts = []
        self.particles = []
        self.last_shot_time = 0
        
        # --- CARGA ---
        self.monster_catalog = [] 
        self.obstacles = [] 
        self.images = {} 

        print("--- INICIANDO SISTEMAS ---")
        self.load_all_assets()
        self.load_player_from_db()     
        self.load_all_monsters_data()  

    def load_image(self, filename, size):
        try:
            img = pygame.image.load(filename).convert_alpha()
            return pygame.transform.scale(img, size)
        except: return None

    def load_all_assets(self):
        self.images["bg_forest.png"] = self.load_image('bg_forest.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.images["bg_cave.png"] = self.load_image('bg_cave.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.images["bg_dungeon.png"] = self.load_image('bg_dungeon.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.images["tree.png"] = self.load_image('tree.png', (60, 80))
        self.images["rock.png"] = self.load_image('rock.png', (50, 50))
        self.images["pillar.png"] = self.load_image('pillar.png', (50, 80))

        self.images["player"] = self.load_image('player.png', (50, 50))
        self.images["slash"] = self.load_image('slash.png', (80, 80))
        self.images["fireball"] = self.load_image('fireball.png', (30, 30))

        self.images["Goblin"] = self.load_image('goblin.png', (50, 50))
        self.images["Shadow"] = self.load_image('shadow.png', (50, 50))
        self.images["Ogre"] = self.load_image('ogre.png', (180, 180))
        self.images["Brain"] = self.load_image('brain.png', (45, 45))

    def load_all_monsters_data(self):
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MonsterName, BaseHP, BaseAttack, BaseSpeed FROM MonsterCatalog")
                for row in cursor.fetchall():
                    self.monster_catalog.append({"Name": row[0], "HP": row[1], "MaxHP": row[1], "Attack": row[2], "Speed": row[3]})
                conn.close()
            except: pass
        if not self.monster_catalog: 
            self.monster_catalog = [{"Name": "Goblin", "HP": 30, "MaxHP": 30, "Attack": 5, "Speed": 2}]

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
                    cursor.execute("INSERT INTO SaveGames (PlayerID, CurrentHP, MaxHP, PositionX, PositionY, Level) VALUES (?, 100, 100, 400, 300, 1)", pid)
                    conn.commit()
                
                cursor.execute("SELECT p.Username, s.Level, s.CurrentHP, s.MaxHP FROM SaveGames s JOIN Players p ON s.PlayerID = p.PlayerID WHERE p.Username = 'Player1'")
                data = cursor.fetchone()
                if data: self.player_stats.update({"Username": data[0], "Level": data[1], "HP": data[2], "MaxHP": data[3]})
                conn.close()
            except: pass

    def start_level(self, stage):
        if stage > 10: self.game_state = "victory"; return
        if stage > self.max_unlocked_level: self.max_unlocked_level = stage

        self.current_stage = stage
        config = self.levels_config[stage]
        self.target_kills = config["kills"]
        self.kills_in_stage = 0
        self.player_stats["HP"] = self.player_stats["MaxHP"] 
        self.projectiles = []
        self.floating_texts = []
        self.particles = []
        
        self.obstacles = []
        obs_key = config["obs"]
        for _ in range(12):
            while True:
                ox, oy = random.randint(50, 700), random.randint(50, 500)
                rect = pygame.Rect(ox + 10, oy + 40, 30, 20)
                if not rect.colliderect(pygame.Rect(350, 250, 150, 150)):
                    self.obstacles.append({"rect": rect, "pos": (ox, oy), "img_key": obs_key})
                    break
        
        self.game_state = "playing"
        self.spawn_enemy()

    def spawn_enemy(self):
        config = self.levels_config[self.current_stage]
        enemy_name = config["enemy"]
        template = next((m for m in self.monster_catalog if m["Name"] == enemy_name), self.monster_catalog[0])
        self.enemy_data = template.copy()
        
        mult = 1 + (self.current_stage * 0.1)
        self.enemy_data["MaxHP"] = int(self.enemy_data["MaxHP"] * mult * self.difficulty_mult)
        self.enemy_data["HP"] = self.enemy_data["MaxHP"]
        self.enemy_data["Attack"] = int(self.enemy_data["Attack"] * mult * self.difficulty_mult)

        while True:
            ex, ey = random.randint(50, 700), random.randint(50, 500)
            w, h = 50, 50
            if enemy_name == "Ogre": w, h = 150, 150
            self.enemy_rect = pygame.Rect(ex, ey, w, h)
            if math.hypot(ex - self.player_x, ey - self.player_y) > 200: break

    def use_potion(self):
        if self.potions > 0 and self.player_stats["HP"] < self.player_stats["MaxHP"]:
            self.potions -= 1
            heal = 50
            self.player_stats["HP"] = min(self.player_stats["MaxHP"], self.player_stats["HP"] + heal)
            self.floating_texts.append(FloatingText(self.player_x, self.player_y, f"+{heal}", GREEN))

    def shoot_fireball(self):
        if self.player_stats["Mana"] >= 10: 
            self.player_stats["Mana"] -= 10
            vx, vy = self.last_move_dir
            speed = 10
            bullet_rect = pygame.Rect(self.player_x + 20, self.player_y + 20, 20, 20)
            self.projectiles.append({"rect": bullet_rect, "vx": vx * speed, "vy": vy * speed})
        else:
            self.floating_texts.append(FloatingText(self.player_x, self.player_y - 40, "¡No Mana!", BLUE))

    def create_blood(self, x, y):
        for _ in range(10):
            self.particles.append(Particle(x, y, RED))

    def damage_enemy(self, amount):
        self.enemy_data["HP"] -= amount
        self.floating_texts.append(FloatingText(self.enemy_rect.centerx, self.enemy_rect.y, f"-{amount}", WHITE))
        
        self.enemy_rect.x += random.randint(-10, 10)
        
        if self.enemy_data["HP"] <= 0:
            self.create_blood(self.enemy_rect.centerx, self.enemy_rect.centery)
            self.kills_in_stage += 1
            if self.kills_in_stage >= self.target_kills:
                self.start_level(self.current_stage + 1)
            else:
                self.spawn_enemy()

    def combat_melee(self):
        self.slash_timer = 10 
        attk_rect = self.player_rect.inflate(60, 60)
        if attk_rect.colliderect(self.enemy_rect):
            dmg = 15 + (self.player_stats["Level"] * 3)
            self.damage_enemy(dmg)

    def update(self):
        if self.game_state == "playing":
            if self.player_stats["Mana"] < self.player_stats["MaxMana"]:
                self.player_stats["Mana"] += 0.2

            # --- CORRECCIÓN AQUÍ: PROYECTILES ---
            # Iteramos sobre una copia para poder borrar sin romper el loop
            for p in self.projectiles[:]:
                p["rect"].x += p["vx"]
                p["rect"].y += p["vy"]
                
                # Checar si salió de pantalla
                if not (0 < p["rect"].x < SCREEN_WIDTH and 0 < p["rect"].y < SCREEN_HEIGHT):
                    if p in self.projectiles: # SEGURIDAD
                        self.projectiles.remove(p)
                    continue
                
                # Checar colisión
                if p["rect"].colliderect(self.enemy_rect):
                    self.damage_enemy(25 + self.player_stats["Level"])
                    if p in self.projectiles: # SEGURIDAD: Solo borrar si aun existe
                        self.projectiles.remove(p)
                    break

            for t in self.floating_texts[:]:
                t.update()
                if t.timer <= 0: self.floating_texts.remove(t)
            
            for part in self.particles[:]:
                part.update()
                if part.life <= 0: self.particles.remove(part)

            speed = min(self.enemy_data.get("Speed", 2), 3.5 if self.difficulty=="Hard" else 2.5)
            if self.enemy_data["Name"] == "Ogre": speed = 1.5
            
            if self.player_x > self.enemy_rect.x: self.enemy_rect.x += speed
            if self.player_x < self.enemy_rect.x: self.enemy_rect.x -= speed
            if self.player_y > self.enemy_rect.y: self.enemy_rect.y += speed
            if self.player_y < self.enemy_rect.y: self.enemy_rect.y -= speed
            
            if self.player_rect.colliderect(self.enemy_rect):
                now = pygame.time.get_ticks()
                if now - self.last_damage_time > 1000:
                    dmg = self.enemy_data["Attack"]
                    self.player_stats["HP"] -= dmg
                    self.last_damage_time = now
                    self.hit_flash_timer = 10
                    self.floating_texts.append(FloatingText(self.player_x, self.player_y, f"-{dmg}", RED))
                    if self.player_stats["HP"] <= 0: self.game_state = "game_over"

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1; self.facing_right = True
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1

        if dx != 0 or dy != 0:
            self.last_move_dir = (dx, dy)

        self.player_x += dx * self.player_speed
        self.player_rect.x = self.player_x
        for obs in self.obstacles:
            if self.player_rect.colliderect(obs["rect"]): self.player_x -= dx * self.player_speed; self.player_rect.x = self.player_x

        self.player_y += dy * self.player_speed
        self.player_rect.y = self.player_y
        for obs in self.obstacles:
            if self.player_rect.colliderect(obs["rect"]): self.player_y -= dy * self.player_speed; self.player_rect.y = self.player_y
        
        self.player_rect.topleft = (self.player_x, self.player_y)

    def draw_button(self, text, x, y, w, h, active=True, hover=False):
        color = GOLD if hover and active else (GRAY if not active else WHITE)
        bg = (60, 60, 60) if active else (30, 30, 30)
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, bg, rect)
        pygame.draw.rect(self.screen, color, rect, 3)
        t = self.font.render(text, True, color)
        self.screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))
        return rect

    def draw_ui_screens(self):
        m_pos = pygame.mouse.get_pos(); click = pygame.mouse.get_pressed()[0]
        if self.images["bg_forest.png"]: self.screen.blit(self.images["bg_forest.png"], (0,0))
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); s.fill(DARK_OVERLAY); self.screen.blit(s, (0,0))

        if self.game_state == "title":
            t = self.title_font.render("RETRO RPG", True, GOLD)
            self.screen.blit(t, (SCREEN_WIDTH//2-t.get_width()//2, 80))
            if self.draw_button("JUGAR", 300, 250, 200, 60, True, 300<m_pos[0]<500 and 250<m_pos[1]<310).collidepoint(m_pos) and click:
                self.game_state = "difficulty_select"; pygame.time.delay(200)
            
            box = pygame.Rect(150, 350, 500, 200)
            pygame.draw.rect(self.screen, (0,0,0,200), box); pygame.draw.rect(self.screen, WHITE, box, 2)
            lines = ["Mover: WASD / Flechas", "Atacar: ESPACIO", "Disparar: Z (Gasta Mana)", "Pocion: H", "Pausa: ESC"]
            for i, l in enumerate(lines):
                self.screen.blit(self.font.render(l, True, WHITE), (170, 370 + i*35))

        elif self.game_state == "difficulty_select":
            self.screen.blit(self.title_font.render("DIFICULTAD", True, WHITE), (220, 80))
            opts = [("FACIL", 0.8), ("NORMAL", 1.0), ("DIFICIL", 2.0)]
            for i, (nm, mul) in enumerate(opts):
                y = 200 + i*90
                if self.draw_button(nm, 250, y, 300, 60, True, 250<m_pos[0]<550 and y<m_pos[1]<y+60).collidepoint(m_pos) and click:
                    self.difficulty = nm; self.difficulty_mult = mul; self.game_state = "level_select"; pygame.time.delay(200)

        elif self.game_state == "level_select":
            self.screen.blit(self.title_font.render("NIVELES", True, WHITE), (250, 20))
            for i in range(1, 11):
                col = 0 if i <= 5 else 1; row = (i-1) % 5
                x, y = 100 + col * 350, 100 + row * 80
                unlk = i <= self.max_unlocked_level
                nm = f"{i}. {self.levels_config[i]['name']}"
                if self.draw_button(nm if unlk else "BLOQUEADO", x, y, 300, 60, unlk, x<m_pos[0]<x+300 and y<m_pos[1]<y+60).collidepoint(m_pos) and click and unlk:
                    self.start_level(i); pygame.time.delay(200)

    def draw_game(self):
        conf = self.levels_config[self.current_stage]
        bg = self.images.get(conf["bg"])
        if bg: self.screen.blit(bg, (0, 0))
        
        if self.hit_flash_timer > 0:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); s.fill((255, 0, 0, 100))
            self.screen.blit(s, (0,0)); self.hit_flash_timer -= 1

        for p in self.particles: p.draw(self.screen)
        
        draw_order = []
        for obs in self.obstacles: draw_order.append({"type": "obs", "y": obs["pos"][1] + 50, "obj": obs})
        draw_order.append({"type": "player", "y": self.player_y + 50, "obj": None})
        draw_order.append({"type": "enemy", "y": self.enemy_rect.y + 50, "obj": None})
        draw_order.sort(key=lambda x: x["y"])

        for item in draw_order:
            if item["type"] == "obs":
                o = item["obj"]
                img = self.images.get(o["img_key"])
                if img: self.screen.blit(img, o["pos"])
                else: pygame.draw.rect(self.screen, (100,50,0), o["rect"])
            elif item["type"] == "player":
                img = self.images["player"]
                if not self.facing_right and img: img = pygame.transform.flip(img, True, False)
                if img: self.screen.blit(img, (self.player_x, self.player_y))
                else: pygame.draw.rect(self.screen, WHITE, self.player_rect)
                if self.slash_timer > 0:
                    slash = self.images["slash"]
                    if slash: self.screen.blit(slash, (self.player_x-15, self.player_y-15))
            elif item["type"] == "enemy":
                img = self.images.get(self.levels_config[self.current_stage]["enemy"])
                if img: self.screen.blit(img, self.enemy_rect.topleft)
                else: pygame.draw.rect(self.screen, RED, self.enemy_rect)
                pct = max(0, self.enemy_data["HP"] / self.enemy_data["MaxHP"])
                pygame.draw.rect(self.screen, RED, (self.enemy_rect.x, self.enemy_rect.y-10, 50*pct, 5))

        for p in self.projectiles:
            if self.images["fireball"]: self.screen.blit(self.images["fireball"], p["rect"])
            else: pygame.draw.circle(self.screen, ORANGE, p["rect"].center, 8)

        for t in self.floating_texts: t.draw(self.screen)

        pygame.draw.rect(self.screen, (0,0,0,180), (0,0, SCREEN_WIDTH, 50))
        pygame.draw.rect(self.screen, RED, (10, 10, 200, 15))
        pygame.draw.rect(self.screen, GREEN, (10, 10, 200 * (max(0, self.player_stats["HP"])/self.player_stats["MaxHP"]), 15))
        self.screen.blit(self.font.render("HP", True, WHITE), (15, 8))
        pygame.draw.rect(self.screen, BLUE, (10, 30, 150 * (self.player_stats["Mana"]/100), 10))
        
        info = f"Pociones: {self.potions} (H)"
        self.screen.blit(self.font.render(info, True, YELLOW), (230, 10))
        
        goal = f"LVL {self.current_stage}: Matar {self.target_kills - self.kills_in_stage}"
        if self.current_stage == 10: goal = "BOSS FINAL"
        self.screen.blit(self.font.render(goal, True, GOLD), (SCREEN_WIDTH - 250, 10))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if self.game_state == "playing":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE: self.game_state = "level_select"
                        if event.key == pygame.K_SPACE: self.combat_melee()
                        if event.key == pygame.K_z: self.shoot_fireball()
                        if event.key == pygame.K_h: self.use_potion()
                elif self.game_state == "game_over" or self.game_state == "victory":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.game_state = "level_select"

            if self.game_state in ["title", "difficulty_select", "level_select"]: self.draw_ui_screens()
            elif self.game_state == "playing": self.handle_input(); self.update(); self.draw_game()
            elif self.game_state == "game_over":
                self.screen.fill(BLACK)
                self.screen.blit(self.title_font.render("GAME OVER", True, RED), (250, 250))
                self.screen.blit(self.font.render("R para volver", True, WHITE), (330, 350))
            elif self.game_state == "victory":
                self.screen.fill(WHITE)
                self.screen.blit(self.title_font.render("VICTORIA!", True, GOLD), (250, 250))

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    game = GameEngine()
    game.run()