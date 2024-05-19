# %% Zbieranie danych
import pygame
import sys
import math
import pandas as pd

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
player_speed = 5
player_angle = -45

# L-shaped wall dimensions and position
wall_thickness = 20
horizontal_wall = pygame.Rect(10, 10, screen_width, wall_thickness)
vertical_wall = pygame.Rect(10, 10, wall_thickness, screen_height)

# Parking spot settings
parking_size = 100
parking_pos = [80, 80]  # Top-left corner of the parking spot
parking_rect = pygame.Rect(parking_pos[0], parking_pos[1], parking_size, parking_size)

# Game loop
running = True
clock = pygame.time.Clock()
finish = False

# Zmienna do zapisu danych
rekord = []

def rotate_point(point, angle, origin):
    angle_rad = math.radians(angle)
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
    qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
    return [qx, qy]

def check_collision(player_rect, walls):
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

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    original_pos = player_pos[:]
    original_angle = player_angle
    
    # Get keys pressed
    keys = pygame.key.get_pressed()
    
    player_pos[0] += player_speed * math.sin(math.radians(player_angle))
    player_pos[1] -= player_speed * math.cos(math.radians(player_angle))

    if keys[pygame.K_w]:
        player_pos[0] += player_speed * math.sin(math.radians(player_angle))
        player_pos[1] -= player_speed * math.cos(math.radians(player_angle))
    if keys[pygame.K_s]:
        player_pos[0] -= player_speed * math.sin(math.radians(player_angle))
        player_pos[1] += player_speed * math.cos(math.radians(player_angle))
    if keys[pygame.K_a]:
        player_angle -= 1
    if keys[pygame.K_d]:
        player_angle += 2
    if keys[pygame.K_RETURN]:
        # zapisanie zebranych danych
        df = pd.DataFrame(rekord, columns=['d1', 'd2', 'd3', 'player_angle', 'pos_x', 'pos_y'])
        df.to_excel('record.xlsx')

    # Define the player rectangle corners
    half_size = player_size // 2
    top_left = [player_pos[0] - half_size, player_pos[1] - 2*half_size]
    top_right = [player_pos[0] + half_size, player_pos[1] - 2*half_size]
    bottom_left = [player_pos[0] - half_size, player_pos[1] + half_size]
    bottom_right = [player_pos[0] + half_size, player_pos[1] + half_size]

    # Rotate the corners around the center
    origin = player_pos
    top_left = rotate_point(top_left, player_angle, origin)
    top_right = rotate_point(top_right, player_angle, origin)
    bottom_left = rotate_point(bottom_left, player_angle, origin)
    bottom_right = rotate_point(bottom_right, player_angle, origin)

    # Check if player is in parking spot
    points = [top_left, top_right, bottom_left, bottom_right]
    if is_in_parking_spot(points, parking_rect):
        finish = True

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
    if check_collision(player_rect, [horizontal_wall, vertical_wall]):
        player_pos = original_pos
        player_angle = original_angle


    
    rekord.append([distance_left, distance_right, distance_bottom_left, player_angle, int(player_pos[0]), int(player_pos[1])])

    # Display "FINISH" if in parking spot
    if finish:
        player_pos = [screen_width - 50, screen_height - 50]
        player_angle = -45
        finish = False
        #text = font.render('FINISH', True, white)
        #screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
        

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)


pygame.quit()
sys.exit()


# %% TRENING MODELU


import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_excel('record.xlsx')


# 
# Model model_X
# 

X = df[['d1','d2','d3']].to_numpy()
y = df[['pos_x']].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,  random_state=42)


from sklearn.tree import DecisionTreeRegressor

model_X = DecisionTreeRegressor()

model_X.fit(X_train,y_train)


y_predict = model_X.predict(X_test)

import matplotlib.pyplot as plt

plt.plot(y_test, y_predict,'.')
plt.title("model_X")
plt.show()

# 
# Model model_Y
# 

X = df[['d1','d2','d3']].to_numpy()
y = df[['pos_y']].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,  random_state=42)


from sklearn.tree import DecisionTreeRegressor

model_Y = DecisionTreeRegressor()

model_Y.fit(X_train,y_train)


y_predict = model_Y.predict(X_test)

import matplotlib.pyplot as plt

plt.plot(y_test, y_predict,'.')
plt.title("model_Y")
plt.show()

# 
# Model model_A
# 

X = df[['d1','d2','d3']].to_numpy()
y = df[['player_angle']].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,  random_state=42)


from sklearn.tree import DecisionTreeRegressor

model_A = DecisionTreeRegressor()

model_A.fit(X_train,y_train)


y_predict = model_A.predict(X_test)

import matplotlib.pyplot as plt

plt.plot(y_test, y_predict,'.')
plt.title("model_angle")
plt.show()


# %% Jazda autonomiczna

import pygame
import sys
import math
import pandas as pd

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
player_speed = 5
player_angle = 0

# L-shaped wall dimensions and position
wall_thickness = 20
horizontal_wall = pygame.Rect(10, 10, screen_width, wall_thickness)
vertical_wall = pygame.Rect(10, 10, wall_thickness, screen_height)

# Parking spot settings
parking_size = 100
parking_pos = [80, 80]  # Top-left corner of the parking spot
parking_rect = pygame.Rect(parking_pos[0], parking_pos[1], parking_size, parking_size)

# Game loop
running = True
clock = pygame.time.Clock()
finish = False

# Zmienna do zapisu danych
rekord = []

def rotate_point(point, angle, origin):
    angle_rad = math.radians(angle)
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
    qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
    return [qx, qy]

def check_collision(player_rect, walls):
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

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    original_pos = player_pos[:]
    original_angle = player_angle
    
    # Define the player rectangle corners
    half_size = player_size // 2
    top_left = [player_pos[0] - half_size, player_pos[1] - 2*half_size]
    top_right = [player_pos[0] + half_size, player_pos[1] - 2*half_size]
    bottom_left = [player_pos[0] - half_size, player_pos[1] + half_size]
    bottom_right = [player_pos[0] + half_size, player_pos[1] + half_size]
    
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
    
    player_angle = int(model_A.predict([[distance_left, distance_right, distance_bottom_left]]))
    player_pos[0] += player_speed * math.sin(math.radians(player_angle))
    player_pos[1] -= player_speed * math.cos(math.radians(player_angle))
    
    
    #print(int(model_X.predict([[distance_left, distance_right, distance_bottom_left]])))
    #print(int(model_Y.predict([[distance_left, distance_right, distance_bottom_left]])))
    print(int(model_Y.predict([[distance_left, distance_right, distance_bottom_left]])))
    
    
    #player_pos[0] = int(model_X.predict([[distance_left, distance_right, distance_bottom_left]]))
    #player_pos[1] = int(model_Y.predict([[distance_left, distance_right, distance_bottom_left]]))

    

    # Rotate the corners around the center
    origin = player_pos
    top_left = rotate_point(top_left, player_angle, origin)
    top_right = rotate_point(top_right, player_angle, origin)
    bottom_left = rotate_point(bottom_left, player_angle, origin)
    bottom_right = rotate_point(bottom_right, player_angle, origin)

    # Check if player is in parking spot
    points = [top_left, top_right, bottom_left, bottom_right]
    if is_in_parking_spot(points, parking_rect):
        finish = True

    # Clear screen
    screen.fill(black)

    # Draw the L-shaped wall
    pygame.draw.rect(screen, white, horizontal_wall)
    pygame.draw.rect(screen, white, vertical_wall)

    # Draw the parking spot
    pygame.draw.rect(screen, green, parking_rect)

    # Draw the player (rotated rectangle)
    player_rect = pygame.draw.polygon(screen, red, [top_left, top_right, bottom_right, bottom_left])
    
    

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
    if check_collision(player_rect, [horizontal_wall, vertical_wall]):
        player_pos = original_pos
        player_angle = original_angle


    
    rekord.append([distance_left, distance_right, distance_bottom_left, player_angle, player_pos[0], player_pos[1]])

    # Display "FINISH" if in parking spot
    if finish:
        #player_pos = [screen_width - 50, screen_height - 50]
        #player_angle = -45
        #finish = False
        player_speed = 0
        text = font.render('FINISH', True, white)
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
        

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)


pygame.quit()
sys.exit()

