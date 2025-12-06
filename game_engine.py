"""
Retro RPG Game Engine
Main game logic using pygame
"""
import pygame
import sys

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
        
        # Player position
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
            self.player_x = max(PLAYER_SIZE // 2, min(SCREEN_WIDTH - PLAYER_SIZE // 2, self.player_x))
            self.player_y = max(PLAYER_SIZE // 2, min(SCREEN_HEIGHT - PLAYER_SIZE // 2, self.player_y))
    
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
        # Clear screen with black background
        self.screen.fill(BLACK)
        
        # Draw player (white square)
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
    
    def run(self):
        """Main game loop"""
        print("Game engine initialized")
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

