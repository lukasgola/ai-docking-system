import pygame
import sys
import math
import random
import numpy as np
from enum import Enum

class AGV:
    def __init__(self):
        pygame.init()
        
        # Screen dimensions
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('AVG Simulator')
        self.clock = pygame.time.Clock()
        self.reset()
        
        # Font settings
        self.font = pygame.font.SysFont(None, 55)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # Colors
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        
        # Player settings
        self.player_size = 50
        self.player_pos = [self.screen_width - 80, self.screen_height - 80]
        self.player_speed = 2  # Speed is initially set to 0
        self.player_angle = 0
        self.turn_force = 1
        
        # L-shaped wall dimensions and position
        self.wall_thickness = 20
        self.horizontal_wall = pygame.Rect(10, 10, self.screen_width, self.wall_thickness)
        self.vertical_wall = pygame.Rect(10, 10, self.wall_thickness, self.screen_height)
        self.horizontal_wall2 = pygame.Rect(10, self.screen_height - 30, self.screen_width, self.wall_thickness)
        self.vertical_wall2 = pygame.Rect(self.screen_width - 30, 10, self.wall_thickness, self.screen_height)

        
        # Parking spot settings
        self.parking_size = 50
        self.parking_pos = [300, 300]  # Top-left corner of the parking spot
        self.parking_rect = pygame.Rect(self.parking_pos[0], self.parking_pos[1], self.parking_size , self.parking_size)

        # Score
        self.score = 0

        # Sensors
        self.d1 = 0
        self.d2 = 0
        self.d3 = 0
        
        # Agent values
        self.reward = 0
        self.running = True
        self.clock = pygame.time.Clock()

    def rotate_point(self, point, angle, origin):
        angle_rad = math.radians(angle)
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
        qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
        return [qx, qy]

    def is_collision(self, player_rect, walls):
        for wall in walls:
            if player_rect.colliderect(wall):
                return True
        return False
    
    def check_collision(self, point):
        for wall in [self.horizontal_wall, self.vertical_wall, self.horizontal_wall2, self.vertical_wall2]:
            if wall.collidepoint(point):
                return True
        return False

    

    def is_in_parking_spot(self, points, parking_rect):
        for point in points:
            if parking_rect.collidepoint(point):
                return True
        return False
    
    def new_parking_spot(self):
        self.parking_pos = [random.randint(50, self.screen_width - 500), random.randint(50, self.screen_height - 500)]
        self.parking_rect = pygame.Rect(self.parking_pos[0], self.parking_pos[1], self.parking_size , self.parking_size)

    def distance_to_wall(self, point, angle, walls):
        px, py = point
        angle_rad = math.radians(angle)
        dx = math.sin(angle_rad)
        dy = -math.cos(angle_rad)
        distance = 0

        while True:
            test_point = (px + distance * dx, py + distance * dy)
            if test_point[0] < 0 or test_point[0] > self.screen_width or test_point[1] < 0 or test_point[1] > self.screen_height:
                break
            for wall in walls:
                if wall.collidepoint(test_point):
                    return distance
            distance += 1

        return distance

    def reset(self):
        self.player_pos = [self.screen_width - 100, self.screen_height - 100]
        self.player_angle = 0


    def move(self, action):
        if np.array_equal(action, [1, 0 ,0]):
            self.player_angle = self.player_angle  # no change
        elif np.array_equal(action, [0, 1, 0]):  # turn right
            self.player_angle += self.turn_force
        elif np.array_equal(action, [0, 0, 1]):  # turn left
            self.player_angle -= self.turn_force

        # Ensure player_angle is always between 0 and 360
        self.player_angle %= 360

        # Move the player
        self.player_pos[0] += self.player_speed * math.sin(math.radians(self.player_angle))
        self.player_pos[1] -= self.player_speed * math.cos(math.radians(self.player_angle))

    def play_step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        self.move(action)

        # Define the player rectangle corners
        half_size = self.player_size // 2
        top_left = [self.player_pos[0] - half_size, self.player_pos[1] - 2 * half_size]
        top_right = [self.player_pos[0] + half_size, self.player_pos[1] - 2 * half_size]
        bottom_left = [self.player_pos[0] - half_size, self.player_pos[1] + half_size]
        bottom_right = [self.player_pos[0] + half_size, self.player_pos[1] + half_size]

        # Rotate the corners around the center
        origin = self.player_pos
        top_left = self.rotate_point(top_left, self.player_angle, origin)
        top_right = self.rotate_point(top_right, self.player_angle, origin)
        bottom_left = self.rotate_point(bottom_left, self.player_angle, origin)
        bottom_right = self.rotate_point(bottom_right, self.player_angle, origin)

        # Clear screen
        self.screen.fill(self.black)

        # Draw the L-shaped wall
        pygame.draw.rect(self.screen, self.white, self.horizontal_wall)
        pygame.draw.rect(self.screen, self.white, self.vertical_wall)
        pygame.draw.rect(self.screen, self.white, self.horizontal_wall2)
        pygame.draw.rect(self.screen, self.white, self.vertical_wall2)
        

        # Draw the parking spot
        pygame.draw.rect(self.screen, self.green, self.parking_rect)

        # Draw the player (rotated rectangle)
        player_rect = pygame.draw.polygon(self.screen, self.red, [top_left, top_right, bottom_right, bottom_left])

        # Calculate and display distance to the nearest wall from top_left
        self.d2 = self.distance_to_wall(top_left, self.player_angle, [self.horizontal_wall, self.vertical_wall])
        end_point_left = (top_left[0] + self.d2 * math.sin(math.radians(self.player_angle)), top_left[1] - self.d2 * math.cos(math.radians(self.player_angle)))
        pygame.draw.line(self.screen, self.blue, top_left, end_point_left, 2)
        distance_text_left = self.small_font.render(f'{self.d2:.2f}', True, self.blue)
        self.screen.blit(distance_text_left, end_point_left)

        # Calculate and display distance to the nearest wall from top_right
        self.d3 = self.distance_to_wall(top_right, self.player_angle, [self.horizontal_wall, self.vertical_wall])
        end_point_right = (top_right[0] + self.d3 * math.sin(math.radians(self.player_angle)), top_right[1] - self.d3 * math.cos(math.radians(self.player_angle)))
        pygame.draw.line(self.screen, self.blue, top_right, end_point_right, 2)
        distance_text_right = self.small_font.render(f'{self.d3:.2f}', True, self.blue)
        self.screen.blit(distance_text_right, end_point_right)

        # Calculate and display distance to the nearest wall from bottom_left parallel to the bottom side
        bottom_angle = self.player_angle + 270  # Angle parallel to the bottom side
        self.d1 = self.distance_to_wall(bottom_left, bottom_angle, [self.horizontal_wall, self.vertical_wall])
        end_point_bottom_left = (bottom_left[0] + self.d1 * math.sin(math.radians(bottom_angle)), bottom_left[1] - self.d1 * math.cos(math.radians(bottom_angle)))
        pygame.draw.line(self.screen, self.blue, bottom_left, end_point_bottom_left, 2)
        distance_text_bottom_left = self.small_font.render(f'{self.d1:.2f}', True, self.blue)
        self.screen.blit(distance_text_bottom_left, end_point_bottom_left)

        # Display sensor distances in the top right corner
        distances_text = [
            f'Top Left: {self.d2:.2f}',
            f'Top Right: {self.d3:.2f}',
            f'Bottom Left: {self.d1:.2f}'
        ]
        for i, text in enumerate(distances_text):
            distance_text = self.small_font.render(text, True, self.white)
            self.screen.blit(distance_text, (self.screen_width - distance_text.get_width() - 10, 50 + i * 20))

        # Display score
        text = self.small_font.render("Score: " + str(self.score), True, self.white)
        self.screen.blit(text, [self.screen_width - 100, 200])

        reward = 0
        game_over = False
        # Check for collisions
        if self.is_collision(player_rect, [self.horizontal_wall, self.vertical_wall, self.horizontal_wall2, self.vertical_wall2]):
            reward = -10
            self.score = 0
            game_over = True
            self.reset()
            return reward, game_over, self.score

        # Display "FINISH" if in parking spot
        # Check if player is in parking spot
        points = [top_left, top_right, bottom_left, bottom_right]
        if self.is_in_parking_spot(points, self.parking_rect):
            reward = 10
            self.score += 1
            self.new_parking_spot()
            game_over = True
            #self.reset()
            text = self.font.render('FINISH', True, self.white)
            self.screen.blit(text, (self.screen_width // 2 - text.get_width() // 2, self.screen_height // 2 - text.get_height() // 2))

        # Update display
        pygame.display.flip()

        return reward, game_over, self.score
