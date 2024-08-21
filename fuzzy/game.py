import pygame
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Player with Differential Steering")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Player settings
player_pos = [WIDTH // 2, HEIGHT // 2]
player_size = 50
player_angle = 0  # Initial angle
speedL = 2  # Speed of the left wheel
speedR = 2  # Speed of the right wheel

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player_pos = player_pos
        self.player_size = player_size
        self.player_angle = player_angle
        self.speedL = speedL
        self.speedR = speedR
        self.angle = 0
        self.red = RED

    def rotate_point(self, point, angle, origin):
        """Rotate a point around an origin (pivot)"""
        ox, oy = origin
        px, py = point
        angle = math.radians(angle)
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return [qx, qy]

    def draw_player(self):
        # Differential steering logic
        action_speed = (self.speedL + self.speedR)
        action_angle = (self.speedL - self.speedR)

        self.angle += 0.01  # Example increment to simulate time passing or other dynamics
        self.player_angle += action_angle
        self.player_speed = action_speed

        # Update player position based on the calculated speed and angle
        self.player_pos[0] += self.player_speed * math.sin(math.radians(self.player_angle))
        self.player_pos[1] -= self.player_speed * math.cos(math.radians(self.player_angle))

        # Define rectangle corners relative to player position
        self.top_left = [self.player_pos[0] - self.player_size, self.player_pos[1] - self.player_size // 2]
        self.top_right = [self.player_pos[0] + self.player_size, self.player_pos[1] - self.player_size // 2]
        self.bottom_left = [self.player_pos[0] - self.player_size, self.player_pos[1] + self.player_size // 2]
        self.bottom_right = [self.player_pos[0] + self.player_size, self.player_pos[1] + self.player_size // 2]

        origin = self.player_pos
        self.top_left = self.rotate_point(self.top_left, self.player_angle, origin)
        self.top_right = self.rotate_point(self.top_right, self.player_angle, origin)
        self.bottom_left = self.rotate_point(self.bottom_left, self.player_angle, origin)
        self.bottom_right = self.rotate_point(self.bottom_right, self.player_angle, origin)

        # Draw player
        self.player_rect = pygame.draw.polygon(self.screen, self.red, [self.top_left, self.top_right, self.bottom_right, self.bottom_left])

# Main game loop
game = Game(screen)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    screen.fill(BLACK)

    # Draw player
    game.draw_player()

    # Refresh display
    pygame.display.flip()

    # Frame rate
    pygame.time.delay(30)

pygame.quit()
