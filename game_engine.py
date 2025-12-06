"""
Retro RPG Game Engine
Main game logic using pygame
"""
import pygame
import sys
from db_connection import get_db_connection

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Player settings
PLAYER_SIZE = 20
PLAYER_SPEED = 5


class GameEngine:
    """Main game engine class"""
    
    def __init__(self):
        """Initialize the game engine"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Retro RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "start"  # 'start' or 'playing'
        
        # Player position (will be loaded from database)
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        
        # Database IDs for saving/loading
        self.player_id = None
        self.save_game_id = None
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load images with fallback
        self.player_image = None
        self.background_image = None
        self.load_assets()
    
    def load_assets(self):
        """Load game assets (images) with fallback to shapes if not found"""
        # Try to load player image
        try:
            player_img = pygame.image.load('player.png')
            # Resize to approximately 50x50 pixels
            self.player_image = pygame.transform.scale(player_img, (50, 50))
            print("Successfully loaded player.png")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load player.png: {e}")
            print("Falling back to white square for player")
            self.player_image = None
        
        # Try to load background image
        try:
            bg_img = pygame.image.load('background.png')
            # Scale to fit window size
            self.background_image = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print("Successfully loaded background.png")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load background.png: {e}")
            print("Falling back to black background")
            self.background_image = None
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Save game before quitting
                self.save_game()
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "start":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.game_state = "playing"
                        print("Game started!")
                
                elif self.game_state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "start"
                        # Reset player position
                        self.player_x = SCREEN_WIDTH // 2
                        self.player_y = SCREEN_HEIGHT // 2
    
    def update(self):
        """Update game logic"""
        if self.game_state == "playing":
            # Get keyboard state for continuous movement
            keys = pygame.key.get_pressed()
            
            # Move player with arrow keys
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player_x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player_x += PLAYER_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player_y -= PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player_y += PLAYER_SPEED
            
            # Keep player within screen bounds
            # Use appropriate size based on whether we have an image or not
            if self.player_image:
                player_half_size = 25  # 50x50 image, so half is 25
            else:
                player_half_size = PLAYER_SIZE // 2  # 20x20 square, so half is 10
            
            self.player_x = max(player_half_size, min(SCREEN_WIDTH - player_half_size, self.player_x))
            self.player_y = max(player_half_size, min(SCREEN_HEIGHT - player_half_size, self.player_y))
    
    def draw_start_screen(self):
        """Draw the start screen"""
        self.screen.fill(BLACK)
        
        # Title
        title_text = self.font.render("Retro RPG", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_text, title_rect)
        
        # Instruction
        instruction_text = self.font.render("Press Enter to Start", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Additional hint
        hint_text = self.small_font.render("Press ESC during gameplay to return to start", True, GRAY)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(hint_text, hint_rect)
    
    def draw_game_screen(self):
        """Draw the game screen"""
        # Draw background (image or black fill)
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            # Fallback to black background
            self.screen.fill(BLACK)
        
        # Draw player (image or white square)
        if self.player_image:
            # Get the center position for the image
            player_rect = self.player_image.get_rect()
            player_rect.center = (self.player_x, self.player_y)
            self.screen.blit(self.player_image, player_rect)
        else:
            # Fallback to white square
            player_rect = pygame.Rect(
                self.player_x - PLAYER_SIZE // 2,
                self.player_y - PLAYER_SIZE // 2,
                PLAYER_SIZE,
                PLAYER_SIZE
            )
            pygame.draw.rect(self.screen, WHITE, player_rect)
        
        # Draw instructions
        instruction_text = self.small_font.render("Use Arrow Keys or WASD to move", True, GRAY)
        self.screen.blit(instruction_text, (10, 10))
        
        escape_text = self.small_font.render("Press ESC to return to start", True, GRAY)
        self.screen.blit(escape_text, (10, 35))
    
    def draw(self):
        """Draw everything"""
        if self.game_state == "start":
            self.draw_start_screen()
        elif self.game_state == "playing":
            self.draw_game_screen()
        
        pygame.display.flip()
    
    def load_or_create_player(self):
        """
        Load player data from database or create a new player if it doesn't exist.
        Sets player position from saved game data.
        """
        conn = get_db_connection()
        if not conn:
            print("Warning: Could not connect to database. Using default position.")
            return
        
        try:
            cursor = conn.cursor()
            username = 'Player1'
            
            # Check if player exists
            cursor.execute("SELECT PlayerID FROM Players WHERE Username = ?", (username,))
            player_row = cursor.fetchone()
            
            if player_row:
                # Player exists, get their PlayerID
                self.player_id = player_row[0]
                print(f"Player '{username}' found (ID: {self.player_id})")
                
                # Get the active save game for this player
                cursor.execute("""
                    SELECT SaveGameID, PositionX, PositionY 
                    FROM SaveGames 
                    WHERE PlayerID = ? AND IsActive = 1
                """, (self.player_id,))
                save_row = cursor.fetchone()
                
                if save_row:
                    self.save_game_id = save_row[0]
                    # Load position from database
                    self.player_x = float(save_row[1])
                    self.player_y = float(save_row[2])
                    print(f"Loaded saved position: ({self.player_x}, {self.player_y})")
                else:
                    # Player exists but no save game, create one
                    print("Player exists but no save game found. Creating new save game...")
                    cursor.execute("""
                        INSERT INTO SaveGames (PlayerID, Level, ExperiencePoints, CurrentHP, MaxHP, PositionX, PositionY, PositionZ)
                        OUTPUT INSERTED.SaveGameID
                        VALUES (?, 1, 0, 100, 100, 0.0, 0.0, 0.0)
                    """, (self.player_id,))
                    result = cursor.fetchone()
                    self.save_game_id = result[0] if result else None
                    conn.commit()
                    self.player_x = 0.0
                    self.player_y = 0.0
                    print(f"Created new save game (ID: {self.save_game_id})")
            else:
                # Player doesn't exist, create new player and save game
                print(f"Player '{username}' not found. Creating new player...")
                cursor.execute("""
                    INSERT INTO Players (Username, PasswordHash, Email, IsActive)
                    OUTPUT INSERTED.PlayerID
                    VALUES (?, ?, ?, 1)
                """, (username, 'default_hash', None))
                result = cursor.fetchone()
                self.player_id = result[0] if result else None
                conn.commit()
                print(f"Created new player '{username}' (ID: {self.player_id})")
                
                # Create save game for new player
                if self.player_id:
                    cursor.execute("""
                        INSERT INTO SaveGames (PlayerID, Level, ExperiencePoints, CurrentHP, MaxHP, PositionX, PositionY, PositionZ)
                        OUTPUT INSERTED.SaveGameID
                        VALUES (?, 1, 0, 100, 100, 0.0, 0.0, 0.0)
                    """, (self.player_id,))
                    result = cursor.fetchone()
                    self.save_game_id = result[0] if result else None
                    conn.commit()
                    self.player_x = 0.0
                    self.player_y = 0.0
                    print(f"Created new save game (ID: {self.save_game_id})")
            
        except Exception as e:
            print(f"Error loading/creating player: {e}")
            print("Using default position.")
        finally:
            conn.close()
    
    def save_game(self):
        """
        Save current player position to the database.
        """
        if not self.save_game_id:
            print("Warning: No save game ID available. Cannot save.")
            return
        
        conn = get_db_connection()
        if not conn:
            print("Warning: Could not connect to database. Game state not saved.")
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE SaveGames 
                SET PositionX = ?, PositionY = ?, LastSaved = GETDATE()
                WHERE SaveGameID = ?
            """, (float(self.player_x), float(self.player_y), self.save_game_id))
            conn.commit()
            print(f"Game saved: Position ({self.player_x}, {self.player_y})")
        except Exception as e:
            print(f"Error saving game: {e}")
        finally:
            conn.close()
    
    def run(self):
        """Main game loop"""
        print("Game engine initialized")
        
        # Load or create player before starting game loop
        print("Loading player data from database...")
        self.load_or_create_player()
        
        print("Starting game loop...")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def main():
    """Main entry point"""
    print("=" * 50)
    print("Retro RPG Game")
    print("=" * 50)
    
    game = GameEngine()
    game.run()


if __name__ == "__main__":
    main()

