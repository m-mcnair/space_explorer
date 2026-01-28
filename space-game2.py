"""
Space Explorer Game - Dodge asteroids, collect power-ups, and survive!
A different take on space games - focus on navigation and collection.
"""

import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
PURPLE = (200, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Player settings
PLAYER_SIZE = 30
PLAYER_SPEED = 5
PLAYER_COLOR = CYAN

# Asteroid settings
ASTEROID_MIN_SIZE = 20
ASTEROID_MAX_SIZE = 60
ASTEROID_SPEED_MIN = 2
ASTEROID_SPEED_MAX = 6
ASTEROID_SPAWN_RATE = 0.02

# Power-up settings
POWERUP_SIZE = 20
POWERUP_SPAWN_RATE = 0.005
POWERUP_DURATION = 300  # frames (5 seconds at 60 FPS)

# Star settings
STAR_COUNT = 100

# Lives settings
STARTING_LIVES = 3
INVINCIBILITY_DURATION = 180  # frames (3 seconds at 60 FPS)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.angle = 0
        self.shield_active = False
        self.shield_timer = 0
        self.slow_motion_active = False
        self.slow_motion_timer = 0
        self.invincible = False
        self.invincibility_timer = 0
        
    def update(self, keys):
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            
        # Keep player on screen
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
        
        # Update power-up timers
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
                
        if self.slow_motion_active:
            self.slow_motion_timer -= 1
            if self.slow_motion_timer <= 0:
                self.slow_motion_active = False
                
        # Update invincibility timer
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False
        
        # Rotate player
        self.angle += 3
        
    def draw(self, screen):
        # Draw shield if active
        if self.shield_active:
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), 
                             self.size + 10, 3)
        
        # Draw triangular ship
        points = []
        for i in range(3):
            angle_rad = math.radians(self.angle + i * 120)
            px = self.x + self.size * math.cos(angle_rad)
            py = self.y + self.size * math.sin(angle_rad)
            points.append((px, py))
        
        # Flash when invincible (every 10 frames)
        if self.invincible and (self.invincibility_timer // 10) % 2 == 0:
            # Don't draw when flashing (makes it invisible)
            pass
        else:
            pygame.draw.polygon(screen, PLAYER_COLOR, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

class Asteroid:
    def __init__(self):
        self.size = random.randint(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)
        self.x = random.choice([
            random.randint(-50, 0),  # Left
            random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 50),  # Right
            random.randint(-50, SCREEN_WIDTH + 50),  # Top/Bottom
        ])
        self.y = random.choice([
            random.randint(-50, SCREEN_HEIGHT + 50),  # Top/Bottom
            random.randint(-50, 0),  # Top
            random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 50),  # Bottom
        ])
        
        # Move towards center
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        dx = center_x - self.x
        dy = center_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        self.vx = (dx / distance) * random.uniform(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)
        self.vy = (dy / distance) * random.uniform(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)
        
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.color = random.choice([RED, ORANGE, YELLOW])
        
    def update(self, slow_motion_factor=1.0):
        self.x += self.vx * slow_motion_factor
        self.y += self.vy * slow_motion_factor
        self.rotation += self.rotation_speed
        
    def draw(self, screen):
        # Draw asteroid as irregular polygon
        points = []
        for i in range(8):
            angle = math.radians(self.rotation + i * 45)
            offset = self.size * (0.7 + random.uniform(-0.2, 0.2))
            px = self.x + offset * math.cos(angle)
            py = self.y + offset * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)
    
    def is_off_screen(self):
        margin = 100
        return (self.x < -margin or self.x > SCREEN_WIDTH + margin or
                self.y < -margin or self.y > SCREEN_HEIGHT + margin)

class PowerUp:
    def __init__(self):
        self.x = random.randint(POWERUP_SIZE, SCREEN_WIDTH - POWERUP_SIZE)
        self.y = random.randint(POWERUP_SIZE, SCREEN_HEIGHT - POWERUP_SIZE)
        self.size = POWERUP_SIZE
        self.type = random.choice(['shield', 'slow_motion', 'points'])
        self.rotation = 0
        self.rotation_speed = 3
        
        # Color based on type
        if self.type == 'shield':
            self.color = BLUE
        elif self.type == 'slow_motion':
            self.color = PURPLE
        else:
            self.color = GREEN
            
    def update(self):
        self.rotation += self.rotation_speed
        
    def draw(self, screen):
        # Draw power-up as rotating star
        points = []
        for i in range(5):
            angle = math.radians(self.rotation + i * 72)
            px = self.x + self.size * math.cos(angle)
            py = self.y + self.size * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 
                         self.size // 2, 2)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)
        
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Explorer - Dodge & Collect!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.asteroids = []
        self.powerups = []
        self.stars = [Star() for _ in range(STAR_COUNT)]
        self.score = 0
        self.game_over = False
        self.survival_time = 0
        self.lives = STARTING_LIVES
        
    def handle_collisions(self):
        player_rect = self.player.get_rect()
        
        # Check asteroid collisions
        for asteroid in self.asteroids[:]:
            if player_rect.colliderect(asteroid.get_rect()):
                if self.player.shield_active:
                    # Shield protects, remove asteroid and add points
                    self.asteroids.remove(asteroid)
                    self.score += 50
                elif not self.player.invincible:
                    # Lose a life
                    self.lives -= 1
                    self.asteroids.remove(asteroid)
                    
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        # Activate invincibility period
                        self.player.invincible = True
                        self.player.invincibility_timer = INVINCIBILITY_DURATION
                        # Reset player to center for safety
                        self.player.x = SCREEN_WIDTH // 2
                        self.player.y = SCREEN_HEIGHT // 2
                    
        # Check power-up collisions
        for powerup in self.powerups[:]:
            if player_rect.colliderect(powerup.get_rect()):
                if powerup.type == 'shield':
                    self.player.shield_active = True
                    self.player.shield_timer = POWERUP_DURATION
                elif powerup.type == 'slow_motion':
                    self.player.slow_motion_active = True
                    self.player.slow_motion_timer = POWERUP_DURATION
                elif powerup.type == 'points':
                    self.score += 200
                    
                self.powerups.remove(powerup)
                
    def spawn_objects(self):
        # Spawn asteroids
        if random.random() < ASTEROID_SPAWN_RATE:
            self.asteroids.append(Asteroid())
            
        # Spawn power-ups (less frequent)
        if random.random() < POWERUP_SPAWN_RATE and len(self.powerups) < 3:
            self.powerups.append(PowerUp())
            
    def update(self):
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Get slow motion factor
        slow_factor = 0.5 if self.player.slow_motion_active else 1.0
        
        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update(slow_factor)
            if asteroid.is_off_screen():
                self.asteroids.remove(asteroid)
                self.score += 10  # Points for surviving
                
        # Update power-ups
        for powerup in self.powerups:
            powerup.update()
            
        # Spawn new objects
        self.spawn_objects()
        
        # Check collisions
        self.handle_collisions()
        
        # Update survival time
        self.survival_time += 1
        
    def draw(self):
        # Draw stars background
        self.screen.fill(BLACK)
        for star in self.stars:
            star.draw(self.screen)
            
        if not self.game_over:
            # Draw power-ups
            for powerup in self.powerups:
                powerup.draw(self.screen)
                
            # Draw asteroids
            for asteroid in self.asteroids:
                asteroid.draw(self.screen)
                
            # Draw player
            self.player.draw(self.screen)
            
            # Draw UI
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            time_text = self.small_font.render(
                f"Time: {self.survival_time // 60:.1f}s", True, WHITE)
            self.screen.blit(time_text, (10, 50))
            
            # Draw lives
            lives_text = self.font.render(f"Lives: {self.lives}", True, RED)
            self.screen.blit(lives_text, (10, 80))
            
            # Draw invincibility indicator
            if self.player.invincible:
                inv_text = self.small_font.render(
                    f"Invincible: {self.player.invincibility_timer // 60:.1f}s", 
                    True, YELLOW)
                self.screen.blit(inv_text, (10, 120))
            
            # Draw power-up indicators
            y_offset = 80
            if self.player.shield_active:
                shield_text = self.small_font.render(
                    f"Shield: {self.player.shield_timer // 60:.1f}s", True, BLUE)
                self.screen.blit(shield_text, (10, y_offset))
                y_offset += 25
                
            if self.player.slow_motion_active:
                slow_text = self.small_font.render(
                    f"Slow Motion: {self.player.slow_motion_timer // 60:.1f}s", 
                    True, PURPLE)
                self.screen.blit(slow_text, (10, y_offset))
        else:
            # Game over screen
            game_over_text = self.font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            time_text = self.small_font.render(
                f"Survival Time: {self.survival_time // 60:.1f}s", True, WHITE)
            lives_text = self.small_font.render(
                f"Lives Remaining: {self.lives}", True, WHITE)
            restart_text = self.small_font.render(
                "Press R to Restart or Q to Quit", True, YELLOW)
            
            # Center text
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(game_over_text, text_rect)
            
            text_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(score_text, text_rect)
            
            text_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(time_text, text_rect)
            
            text_rect = lives_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(lives_text, text_rect)
            
            text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(restart_text, text_rect)
            
        pygame.display.flip()
        
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                        
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
