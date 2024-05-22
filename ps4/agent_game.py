import pygame
import sys
import math
import random
import numpy as np
import torch

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('AVG Simulator')

# Font settings
font = pygame.font.SysFont(None, 55)
small_font = pygame.font.SysFont(None, 20)

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Player settings
player_size = 50
player_pos = [screen_width - 50, screen_height - 50]
player_speed = 5  # Speed is initially set to 0
player_angle = 0
turn_force = 3

# L-shaped wall dimensions and position
wall_thickness = 20
horizontal_wall = pygame.Rect(10, 10, screen_width, wall_thickness)
vertical_wall = pygame.Rect(10, 10, wall_thickness, screen_height)

# Parking spot settings
parking_size = 100
parking_pos = [80, 80]  # Top-left corner of the parking spot
parking_rect = pygame.Rect(parking_pos[0], parking_pos[1], parking_size - 30, parking_size)

# Agent values
reward = 0


def rotate_point(point, angle, origin):
    angle_rad = math.radians(angle)
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
    qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
    return [qx, qy]

def is_collision(player_rect, walls):
    for wall in walls:
        if player_rect.colliderect(wall):
            return True
    return False

def is_in_parking_spot(points, parking_rect):
    for point in points:
        if not parking_rect.collidepoint(point):
            return False
    return True

def distance_to_wall(point, angle, walls):
    px, py = point
    angle_rad = math.radians(angle)
    dx = math.sin(angle_rad)
    dy = -math.cos(angle_rad)
    distance = 0

    while True:
        test_point = (px + distance * dx, py + distance * dy)
        if test_point[0] < 0 or test_point[0] > screen_width or test_point[1] < 0 or test_point[1] > screen_height:
            break
        for wall in walls:
            if wall.collidepoint(test_point):
                return distance
        distance += 1

    return distance

def reset_game():
    global player_pos, player_angle
    player_pos = [screen_width - random.randint(50, 300), screen_height - random.randint(50, 200)]
    player_angle = random.randint(0, 360)
    

def move(action):
    global player_pos, player_speed, player_angle

    if np.array_equal(action, [1, 0 ,0]):
        player_angle = player_angle  # no change
    elif np.array_equal(action, [0, 1, 0]): # turn right
        player_angle += turn_force
    elif np.array_equal(action, [0, 0, 1]): # turn left
        player_angle -= turn_force


    # Move the player
    player_pos[0] += player_speed * math.sin(math.radians(player_angle))
    player_pos[1] -= player_speed * math.cos(math.radians(player_angle))


#reset
#reward
#play(action) -> direction
#game_iteration



# Game loop
running = True
clock = pygame.time.Clock()
finish = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            

    move([0,0,1])
    

    # Define the player rectangle corners
    half_size = player_size // 2
    top_left = [player_pos[0] - half_size, player_pos[1] - 2 * half_size]
    top_right = [player_pos[0] + half_size, player_pos[1] - 2 * half_size]
    bottom_left = [player_pos[0] - half_size, player_pos[1] + half_size]
    bottom_right = [player_pos[0] + half_size, player_pos[1] + half_size]

    # Rotate the corners around the center
    origin = player_pos
    top_left = rotate_point(top_left, player_angle, origin)
    top_right = rotate_point(top_right, player_angle, origin)
    bottom_left = rotate_point(bottom_left, player_angle, origin)
    bottom_right = rotate_point(bottom_right, player_angle, origin)

    # Clear screen
    screen.fill(black)

    # Draw the L-shaped wall
    pygame.draw.rect(screen, white, horizontal_wall)
    pygame.draw.rect(screen, white, vertical_wall)

    # Draw the parking spot
    pygame.draw.rect(screen, green, parking_rect)

    # Draw the player (rotated rectangle)
    player_rect = pygame.draw.polygon(screen, red, [top_left, top_right, bottom_right, bottom_left])

    # Calculate and display distance to the nearest wall from top_left
    distance_left = distance_to_wall(top_left, player_angle, [horizontal_wall, vertical_wall])
    end_point_left = (top_left[0] + distance_left * math.sin(math.radians(player_angle)), top_left[1] - distance_left * math.cos(math.radians(player_angle)))
    pygame.draw.line(screen, blue, top_left, end_point_left, 2)
    distance_text_left = small_font.render(f'{distance_left:.2f}', True, blue)
    screen.blit(distance_text_left, end_point_left)

    # Calculate and display distance to the nearest wall from top_right
    distance_right = distance_to_wall(top_right, player_angle, [horizontal_wall, vertical_wall])
    end_point_right = (top_right[0] + distance_right * math.sin(math.radians(player_angle)), top_right[1] - distance_right * math.cos(math.radians(player_angle)))
    pygame.draw.line(screen, blue, top_right, end_point_right, 2)
    distance_text_right = small_font.render(f'{distance_right:.2f}', True, blue)
    screen.blit(distance_text_right, end_point_right)

    # Calculate and display distance to the nearest wall from bottom_left parallel to the bottom side
    bottom_angle = player_angle + 270  # Angle parallel to the bottom side
    distance_bottom_left = distance_to_wall(bottom_left, bottom_angle, [horizontal_wall, vertical_wall])
    end_point_bottom_left = (bottom_left[0] + distance_bottom_left * math.sin(math.radians(bottom_angle)), bottom_left[1] - distance_bottom_left * math.cos(math.radians(bottom_angle)))
    pygame.draw.line(screen, blue, bottom_left, end_point_bottom_left, 2)
    distance_text_bottom_left = small_font.render(f'{distance_bottom_left:.2f}', True, blue)
    screen.blit(distance_text_bottom_left, end_point_bottom_left)


    # Display sensor distances in the top right corner
    distances_text = [
        f'Top Left: {distance_left:.2f}',
        f'Top Right: {distance_right:.2f}',
        f'Bottom Left: {distance_bottom_left:.2f}'
    ]
    for i, text in enumerate(distances_text):
        distance_text = small_font.render(text, True, white)
        screen.blit(distance_text, (screen_width - distance_text.get_width() - 10, 50 + i * 20))


    # Check for collisions
    if is_collision(player_rect, [horizontal_wall, vertical_wall]):
        reward = -10
        reset_game()

    # Display "FINISH" if in parking spot
    # Check if player is in parking spot
    points = [top_left, top_right, bottom_left, bottom_right]
    if is_in_parking_spot(points, parking_rect):
        reward = 10
        text = font.render('FINISH', True, white)
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)

pygame.quit()
sys.exit()
