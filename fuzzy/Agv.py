import pygame
import sys
import math
import random
from Fuzzy import FuzzyLogicController
from Fuzzy_Parallel import FuzzyParallelLogicController
from FuzzyRotate import FuzzyRotateLogicController

MAX_SPEED = 5

class AGV:
    def __init__(self):
        pygame.init()

        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('AGV Simulator')

        self.iteration = 0
        self.mode = 1

        self.font = pygame.font.SysFont(None, 55)
        self.small_font = pygame.font.SysFont(None, 20)

        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)

        self.wall_thickness = 20
        self.horizontal_wall = pygame.Rect(10, 10, self.screen_width, self.wall_thickness)
        self.vertical_wall = pygame.Rect(10, 10, self.wall_thickness, self.screen_height)

        # Sensors
        self.d1 = 0
        self.d2 = 0
        self.d3 = 0

        self.prev_d1 = 0

        self.joystick = None
        self.initialize_joystick()

        self.analog_keys = {0: 0, 1: 0, 2: 0, 3: 0, 4: -1, 5: -1}

        self.running = True
        self.clock = pygame.time.Clock()
        self.finish = False
        self.screen_text = ''

        self.fuzzy_logic = FuzzyLogicController()
        self.fuzzy_parallel = FuzzyParallelLogicController()
        self.fuzzy_rotate = FuzzyRotateLogicController()

        self.reset_game()

    def reset_spot(self):
        # Parking spot settings
        self.parking_size = 120
        self.parking_pos = [70, 70]  # Top-left corner of the parking spot
        self.parking_rect = pygame.Rect(self.parking_pos[0], self.parking_pos[1], self.parking_size , self.parking_size)

    def reset_player(self):
        # Player settings
        r = random.randint(1, 4)
        self.player_size = 40
        # self.player_pos = [120, self.screen_height - 200]
        self.player_pos = [ 150 + 50 * r , self.screen_height - 50]
        self.spawn_points = [(150 + 50 * i, self.screen_height - 50) for i in range(1, 5)]
        self.player_speed = 0
        self.player_angle = -90
        self.player_angle = random.randint(-15, 15)  # Random angle between -15 and 15
        self.mode = 0

        # self.top_left = [self.player_pos[0] - self.player_size // 2, self.player_pos[1] - self.player_size // 2]
        # self.top_right = [self.player_pos[0] + self.player_size // 2, self.player_pos[1] - self.player_size // 2]
        # self.bottom_left = [self.player_pos[0] - self.player_size // 2, self.player_pos[1] + self.player_size // 2]
        # self.bottom_right = [self.player_pos[0] + self.player_size // 2, self.player_pos[1] + self.player_size // 2]
        # self.player_rect = pygame.draw.polygon(self.screen, self.red, [self.top_left, self.top_right, self.bottom_right, self.bottom_left])


    def reset_game(self):
        self.reset_player()
        self.reset_spot()
        self.score = 0

    def initialize_joystick(self):
        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Joystick name: {self.joystick.get_name()}")
            print(f"Number of axes: {self.joystick.get_numaxes()}")
            print(f"Number of buttons: {self.joystick.get_numbuttons()}")
        except pygame.error:
            print("No joystick found, using keyboard controls")

    def rotate_point(self, point, angle, origin):
        angle_rad = math.radians(angle)
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
        qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
        return [qx, qy]

    def check_collision(self, player_rect, walls):
        for wall in walls:
            if player_rect.colliderect(wall):
                return True
        return False

    def is_in_parking_spot(self, player_rect, parking_rect):
        return parking_rect.contains(player_rect)

    def distance_to_wall(self, point, angle, walls):
        px, py = point
        angle_rad = math.radians(angle)
        dx = math.sin(angle_rad)
        dy = -math.cos(angle_rad)
        distance = 0

        while True:
            test_point = (px + distance * dx, py + distance * dy)

            if test_point[0] < 0 or test_point[0] >= self.screen_width or test_point[1] < 0 or test_point[1] >= self.screen_height:
                return 800

            for wall in walls:
                if wall.collidepoint(test_point):
                    return distance
            distance += 1

    def draw_sensors(self, top_left, top_right, bottom_left):
        # Calculate and display distance to the nearest wall from top_left
        distance_left = self.distance_to_wall(top_left, self.player_angle, [self.horizontal_wall, self.vertical_wall])
        self.d2 = distance_left
        end_point_left = (top_left[0] + distance_left * math.sin(math.radians(self.player_angle)), top_left[1] - distance_left * math.cos(math.radians(self.player_angle)))
        pygame.draw.line(self.screen, self.blue, top_left, end_point_left, 2)
        distance_text_left = self.small_font.render(f'{distance_left:.2f}', True, self.blue)
        self.screen.blit(distance_text_left, end_point_left)

        # Calculate and display distance to the nearest wall from top_right
        distance_right = self.distance_to_wall(top_right, self.player_angle, [self.horizontal_wall, self.vertical_wall])
        self.d3 = distance_right
        end_point_right = (top_right[0] + distance_right * math.sin(math.radians(self.player_angle)), top_right[1] - distance_right * math.cos(math.radians(self.player_angle)))
        pygame.draw.line(self.screen, self.blue, top_right, end_point_right, 2)
        distance_text_right = self.small_font.render(f'{distance_right:.2f}', True, self.blue)
        self.screen.blit(distance_text_right, end_point_right)

        # Calculate and display distance to the nearest wall from bottom_left
        bottom_angle = self.player_angle + 270
        distance_bottom_left = self.distance_to_wall(bottom_left, bottom_angle, [self.horizontal_wall, self.vertical_wall])
        self.d1 = distance_bottom_left
        end_point_bottom_left = (bottom_left[0] + distance_bottom_left * math.sin(math.radians(bottom_angle)), bottom_left[1] - distance_bottom_left * math.cos(math.radians(bottom_angle)))
        pygame.draw.line(self.screen, self.blue, bottom_left, end_point_bottom_left, 2)
        distance_text_bottom_left = self.small_font.render(f'{distance_bottom_left:.2f}', True, self.blue)
        self.screen.blit(distance_text_bottom_left, end_point_bottom_left)

        distances_text = [
            f'Top Left: {distance_left:.2f}',
            f'Top Right: {distance_right:.2f}',
            f'Bottom Left: {distance_bottom_left:.2f}'
        ]
        for i, text in enumerate(distances_text):
            distance_text = self.small_font.render(text, True, self.white)
            self.screen.blit(distance_text, (self.screen_width - distance_text.get_width() - 10, 50 + i * 20))

    def draw_scene(self):
        # Draw scene
        self.screen.fill(self.black)
        pygame.draw.rect(self.screen, self.white, self.horizontal_wall)
        pygame.draw.rect(self.screen, self.white, self.vertical_wall)
        pygame.draw.rect(self.screen, self.green, self.parking_rect)

        for spawn_point in self.spawn_points:
            pygame.draw.rect(self.screen, (255, 255, 255), (spawn_point[0], spawn_point[1], 5, 5))

        
    def draw_player(self):
        self.top_left = [self.player_pos[0] - self.player_size, self.player_pos[1] - 2 * self.player_size // 2]
        self.top_right = [self.player_pos[0] + self.player_size, self.player_pos[1] - 2 * self.player_size // 2]
        self.bottom_left = [self.player_pos[0] - self.player_size, self.player_pos[1] + self.player_size // 2]
        self.bottom_right = [self.player_pos[0] + self.player_size, self.player_pos[1] + self.player_size // 2]

        origin = self.player_pos
        self.top_left = self.rotate_point(self.top_left, self.player_angle, origin)
        self.top_right = self.rotate_point(self.top_right, self.player_angle, origin)
        self.bottom_left = self.rotate_point(self.bottom_left, self.player_angle, origin)
        self.bottom_right = self.rotate_point(self.bottom_right, self.player_angle, origin)

        # Draw player
        self.player_rect = pygame.draw.polygon(self.screen, self.red, [self.top_left, self.top_right, self.bottom_right, self.bottom_left])



    def analog_move(self):
        if self.analog_keys[0] < -0.3:
            self.player_angle -= abs(self.analog_keys[0]) * 2

        if self.analog_keys[0] > 0.3:
            self.player_angle += abs(self.analog_keys[0]) * 2

        if self.analog_keys[5] > -1:
            self.player_speed = (self.analog_keys[5] + 1) * 2
        elif self.analog_keys[4] > -1:
            self.player_speed = -(self.analog_keys[4] + 1) * 2
        else:
            self.player_speed = 1

    def keyboard_move(self, keys):
        if keys[pygame.K_w]:
            self.player_speed = MAX_SPEED
        elif keys[pygame.K_s]:
            self.player_speed = -3
        else:
            self.player_speed = 0
        if keys[pygame.K_a]:
            self.player_angle -= 5
        if keys[pygame.K_d]:
            self.player_angle += 5
        if keys[pygame.K_r]:
            self.reset_player()
        if keys[pygame.K_m]:
            self.mode = 1
        if keys[pygame.K_p]:
            self.mode = 3
        if keys[pygame.K_o]:
            self.mode = 2

    def fuzzy_move(self, player_angle, player_speed):
        self.player_angle += player_angle
        self.player_speed = player_speed


    def translate(self, speedL, speedR):
        speedL = speedL / 2
        speedR = speedR / 2
        angle = (speedL - speedR) / 10
        speed = (speedL + speedR) / 10

        #print(str(speedL*2) + "  :  " + str(speedR*2))

        return angle, speed

    def play_step(self):
        self.draw_scene()

        print(str(self.d1) + " : " + str(self.d2) + " : " + str(self.d3))

        original_pos = self.player_pos[:]
        original_angle = self.player_angle

        if self.iteration == 15:
            #print( str(self.iteration) + " : " + str(self.prev_d1) + " : " + str(self.d1))
            self.prev_d1 = self.d1
            self.iteration = 0
        else:
            self.iteration += 1

    

        # Fuzzy logic control
        if self.mode == 2:
            print("Rotate")
            speedL, speedR = self.fuzzy_rotate.compute_action(self.d1, self.d2, self.d3)
        elif self.mode == 3:
            print("Parallel")
            speedL, speedR = self.fuzzy_parallel.compute_action(self.d1 - self.prev_d1, self.d2, self.d3)
        elif self.mode == 0:
            speedL = 0
            speedR = 0
            self.mode = 1
        else:
            print("Logic")
            speedL, speedR = self.fuzzy_logic.compute_action(self.d1, self.d2, self.d3)

        angle_action, speed_action = self.translate(speedL, speedR)

        self.fuzzy_move(angle_action, speed_action)

        self.player_pos[0] += self.player_speed * math.sin(math.radians(self.player_angle))
        self.player_pos[1] -= self.player_speed * math.cos(math.radians(self.player_angle))


        self.draw_player()

        self.draw_sensors(self.top_left, self.top_right, self.bottom_left)

        if self.check_collision(self.player_rect, [self.horizontal_wall, self.vertical_wall]):
            self.player_pos = original_pos
            self.player_angle = original_angle
            self.screen_text = self.font.render('COLISION', True, self.white)\
            
            self.reset_player()

        elif self.is_in_parking_spot(self.player_rect, self.parking_rect):
                self.screen_text = self.font.render('FINISH', True, self.white)
                self.finish = True
                self.screen.blit(self.screen_text, (self.screen_width // 2 - self.screen_text.get_width() // 2, self.screen_height // 2 - self.screen_text.get_height() // 2))
                # Wait for 1000 milliseconds
                pygame.display.flip()  # Update the display
                # if self.d1 <= 60 and self.d2 <= 60 and self.d3 <= 60:
                #     pygame.time.delay(1000)  # Wait for 1000 ms
                #     self.reset_player()
        else:
            self.screen_text = self.font.render('', True, self.white)

        self.screen.blit(self.screen_text, (self.screen_width // 2 - self.screen_text.get_width() // 2, self.screen_height // 2 - self.screen_text.get_height() // 2))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.joystick:
                    if event.type == pygame.JOYAXISMOTION:
                        self.analog_keys[event.axis] = event.value

            keys = pygame.key.get_pressed()

            if self.joystick:
                self.analog_move()
            else:
                self.keyboard_move(keys)

            self.play_step()

            self.clock.tick(30)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    agv = AGV()
    agv.run()
