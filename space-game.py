import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 5
        self.health = 100
        self.max_health = 100

    def draw(self, screen):
        # Draw player ship (triangle)
        points = [
            (self.x, self.y - self.height // 2),
            (self.x - self.width // 2, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height // 2)
        ]
        pygame.draw.polygon(screen, CYAN, points)
        # Draw engine glow
        pygame.draw.circle(
            screen, YELLOW, (self.x, self.y + self.height // 2 + 5), 5)

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(self.width // 2, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(SCREEN_WIDTH - self.width // 2, self.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(self.height // 2, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(SCREEN_HEIGHT - self.height // 2, self.y + self.speed)

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = 10
        self.active = True

    def update(self):
        self.y -= self.speed
        if self.y < 0:
            self.active = False

    def draw(self, screen):
        pygame.draw.circle(
            screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x),
                           int(self.y)), self.radius - 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = random.uniform(2, 4)
        self.health = 1

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        # Draw enemy ship
        points = [
            (self.x, self.y + self.height // 2),
            (self.x - self.width // 2, self.y - self.height // 2),
            (self.x + self.width // 2, self.y - self.height // 2)
        ]
        pygame.draw.polygon(screen, RED, points)
        pygame.draw.circle(screen, PURPLE, (self.x, self.y), 8)

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT


class Asteroid:
    def __init__(self):
        self.size = random.randint(20, 50)
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = -self.size
        self.speed = random.uniform(1, 3)
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)

    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed

    def draw(self, screen):
        # Draw asteroid as a polygon
        points = []
        for i in range(8):
            angle = math.radians(self.rotation + i * 45)
            px = self.x + math.cos(angle) * self.size
            py = self.y + math.sin(angle) * self.size
            points.append((px, py))
        pygame.draw.polygon(screen, (100, 100, 100), points)
        pygame.draw.polygon(screen, (150, 150, 150), points, 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT


class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.brightness = random.randint(100, 255)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.level = 1

        # Game objects
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.bullets = []
        self.enemies = []
        self.asteroids = []
        self.stars = [Star() for _ in range(100)]

        # Timing
        self.last_enemy_spawn = 0
        self.last_asteroid_spawn = 0
        self.enemy_spawn_rate = 2000  # milliseconds
        self.asteroid_spawn_rate = 3000

        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def spawn_enemy(self):
        self.enemies.append(Enemy(random.randint(30, SCREEN_WIDTH - 30), -30))

    def spawn_asteroid(self):
        self.asteroids.append(Asteroid())

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)

        # Shooting
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            if not hasattr(self, 'last_shot') or current_time - self.last_shot > 200:
                self.bullets.append(Bullet(self.player.x, self.player.y - 20))
                self.last_shot = current_time

    def update(self):
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()

        # Spawn enemies
        if current_time - self.last_enemy_spawn > self.enemy_spawn_rate:
            self.spawn_enemy()
            self.last_enemy_spawn = current_time

        # Spawn asteroids
        if current_time - self.last_asteroid_spawn > self.asteroid_spawn_rate:
            self.spawn_asteroid()
            self.last_asteroid_spawn = current_time

        # Update stars
        for star in self.stars:
            star.update()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.is_off_screen():
                self.enemies.remove(enemy)

        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update()
            if asteroid.is_off_screen():
                self.asteroids.remove(asteroid)

        # Bullet-Enemy collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break

        # Bullet-Asteroid collisions
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if bullet.get_rect().colliderect(asteroid.get_rect()):
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.score += 5
                    break

        # Player-Enemy collisions
        for enemy in self.enemies[:]:
            if self.player.get_rect().colliderect(enemy.get_rect()):
                self.player.health -= 20
                self.enemies.remove(enemy)
                if self.player.health <= 0:
                    self.game_over = True

        # Player-Asteroid collisions
        for asteroid in self.asteroids[:]:
            if self.player.get_rect().colliderect(asteroid.get_rect()):
                self.player.health -= 15
                self.asteroids.remove(asteroid)
                if self.player.health <= 0:
                    self.game_over = True

        # Increase difficulty
        self.level = self.score // 100 + 1
        self.enemy_spawn_rate = max(500, 2000 - self.level * 100)
        self.asteroid_spawn_rate = max(1000, 3000 - self.level * 150)

    def draw(self):
        self.screen.fill(BLACK)

        # Draw stars
        for star in self.stars:
            star.draw(self.screen)

        if not self.game_over:
            # Draw game objects
            self.player.draw(self.screen)

            for bullet in self.bullets:
                bullet.draw(self.screen)

            for enemy in self.enemies:
                enemy.draw(self.screen)

            for asteroid in self.asteroids:
                asteroid.draw(self.screen)

            # Draw UI
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))

            level_text = self.font.render(f"Level: {self.level}", True, WHITE)
            self.screen.blit(level_text, (10, 50))

            # Health bar
            health_width = 200
            health_height = 20
            health_x = SCREEN_WIDTH - health_width - 10
            health_y = 10

            # Background
            pygame.draw.rect(self.screen, RED,
                             (health_x, health_y, health_width, health_height))
            # Health
            health_percent = self.player.health / self.player.max_health
            pygame.draw.rect(self.screen, GREEN,
                             (health_x, health_y, health_width * health_percent, health_height))
            # Border
            pygame.draw.rect(self.screen, WHITE,
                             (health_x, health_y, health_width, health_height), 2)

            health_text = self.small_font.render(
                f"Health: {int(self.player.health)}", True, WHITE)
            self.screen.blit(health_text, (health_x, health_y + 25))

            # Instructions
            if self.score == 0:
                inst1 = self.small_font.render(
                    "WASD or Arrow Keys: Move", True, WHITE)
                inst2 = self.small_font.render("SPACE: Shoot", True, WHITE)
                self.screen.blit(
                    inst1, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 60))
                self.screen.blit(
                    inst2, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 35))
        else:
            # Game over screen
            game_over_text = self.font.render("GAME OVER", True, RED)
            score_text = self.font.render(
                f"Final Score: {self.score}", True, WHITE)
            level_text = self.font.render(
                f"Level Reached: {self.level}", True, WHITE)
            restart_text = self.small_font.render(
                "Press R to Restart or ESC to Quit", True, WHITE)

            self.screen.blit(game_over_text,
                             (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 80))
            self.screen.blit(score_text,
                             (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(level_text,
                             (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text,
                             (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()

    def restart(self):
        self.game_over = False
        self.score = 0
        self.level = 1
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.bullets = []
        self.enemies = []
        self.asteroids = []
        self.last_enemy_spawn = 0
        self.last_asteroid_spawn = 0
        self.enemy_spawn_rate = 2000
        self.asteroid_spawn_rate = 3000

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.restart()

            if not self.game_over:
                self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
