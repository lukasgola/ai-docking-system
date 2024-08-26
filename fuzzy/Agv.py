import pygame
import sys
import math
import random
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from Fuzzy import FuzzyLogicController
from Fuzzy_Parallel import FuzzyParallelLogicController
from FuzzyRotate import FuzzyRotateLogicController
from Fuzzy_Dock import FuzzyDockLogicController

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

        self.rekord = []

        # Sensors
        self.d1 = 0
        self.d2 = 0
        self.d3 = 0

        self.prev_d1 = 0

        self.speedL = 0
        self.speedR = 0

        self.circle_center = [0,0]
        self.radius_l = 0
        self.radius_r = 0
        self.angle = 0
        self.angle_r = 0

        self.left_wheel = 0
        self.right_wheel = 0

        self.start_pos = [0,0]
        self.start_angle = 0

        self.distance_history = []
        self.distance_average = 0

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
        self.fuzzy_dock = FuzzyDockLogicController();


        self.reset_game()

    def reset_spot(self):
        # Parking spot settings
        self.parking_size = 120
        self.parking_pos = [350, 350]  # Top-left corner of the parking spot
        self.parking_rect = pygame.Rect(self.parking_pos[0], self.parking_pos[1], self.parking_size , self.parking_size)

    def reset_player(self):
        # Player settings
        r = random.randint(1, 4)
        self.player_size = 20
        # self.player_pos = [120, self.screen_height - 200]
        # self.player_pos = [ 150 + 50 * r , self.screen_height - 50]
        # self.player_pos_r = [ 150 + 50 * r , self.screen_height - 50]
        # self.start_pos = [ 150 + 50 * r , self.screen_height - 50]
        self.player_pos = [1800, 2450]
        self.player_pos_r = [1800, 2450]
        self.start_pos = [1800, 2450]
        self.spawn_points = [(150 + 50 * i, self.screen_height - 50) for i in range(1, 5)]
        self.player_speed = 0
        # self.player_angle = 0
        # self.player_angle = random.choice([-30, 0, 30])
        # self.player_angle_r = self.player_angle
        self.player_angle = 0
        self.player_angle_r = 0
        self.angle = self.player_angle
        self.mode = 0
        self.distance_history = []
        self.distance_average = 0
        self.speedL = 0
        self.speedR = 0

        self.top_left = [self.player_pos[0] - self.player_size, self.player_pos[1] - self.player_size]
        self.top_right = [self.player_pos[0] + self.player_size, self.player_pos[1] - self.player_size]
        self.bottom_left = [self.player_pos[0] - self.player_size, self.player_pos[1] + self.player_size]
        self.bottom_right = [self.player_pos[0] + self.player_size, self.player_pos[1] + self.player_size]

        self.top_left_r = [self.player_pos_r[0] - self.player_size, self.player_pos_r[1] - self.player_size]
        self.top_right_r = [self.player_pos_r[0] + self.player_size, self.player_pos_r[1] - self.player_size]
        self.bottom_left_r = [self.player_pos_r[0] - self.player_size, self.player_pos_r[1] + self.player_size]
        self.bottom_right_r = [self.player_pos_r[0] + self.player_size, self.player_pos_r[1] + self.player_size]

        self.player_rect = self.draw_player(self.player_pos, self.player_angle, self.top_left, self.top_right, self.bottom_left, self.bottom_right )
        self.player_rect_r = self.draw_player(self.player_pos_r, self.player_angle_r, self.top_left_r, self.top_right_r, self.bottom_left_r, self.bottom_right_r )

        self.left_wheel = self.top_left
        self.right_wheel = self.top_right
        self.start_angle = self.player_angle
        # self.radius = 0
        # self.circle_center = [0,0]

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

        
    def draw_player(self, player_pos, player_angle, top_left, top_right, bottom_left, bottom_right):
        # Obliczanie punktów na podstawie podanej pozycji i rozmiaru
        top_left = [player_pos[0] - self.player_size, player_pos[1] - 2 * self.player_size // 2]
        top_right = [player_pos[0] + self.player_size, player_pos[1] - 2 * self.player_size // 2]
        bottom_left = [player_pos[0] - self.player_size, player_pos[1] + self.player_size // 2]
        bottom_right = [player_pos[0] + self.player_size, player_pos[1] + self.player_size // 2]

        origin_r = player_pos

        # Rotacja punktów
        top_left = self.rotate_point(top_left, player_angle, origin_r)
        top_right = self.rotate_point(top_right, player_angle, origin_r)
        bottom_left = self.rotate_point(bottom_left, player_angle, origin_r)
        bottom_right = self.rotate_point(bottom_right, player_angle, origin_r)

        # Rysowanie prostokąta
        player_rect = pygame.draw.polygon(self.screen, self.red, [top_left, top_right, bottom_right, bottom_left])
        
        return player_rect





    def find_arc_parameters(self, start_pos, end_pos, start_angle):
        def objective(params):
            h, k, R = params
            return R  # Chcemy minimalizować promień

        def constraints(params):
            h, k, R = params
            x0, y0 = start_pos
            xf, yf = end_pos

            # Punkt startowy musi należeć do okręgu
            c1 = (x0 - h)**2 + (y0 - k)**2 - R**2
            
            # Punkt końcowy musi należeć do okręgu
            c2 = (xf - h)**2 + (yf - k)**2 - R**2
            
            # Warunek styczności w punkcie startowym
            normal_x = x0 - h
            normal_y = y0 - k
            tangent_x = -np.sin(start_angle)
            tangent_y = np.cos(start_angle)

            # Sprawdzamy czy wektor normalny i wektor kierunku są prostopadłe
            c3 = normal_x * tangent_x + normal_y * tangent_y

            return [c1, c2, c3]

        # Początkowe zgadnięcie dla (h, k, R)
        initial_guess = [0, 0, 10]

        # Ograniczenie, aby promień był dodatni
        bounds = [(None, None), (None, None), (1e-3, 10000)]

        # Optymalizacja
        result = minimize(objective, initial_guess, constraints={'type': 'eq', 'fun': constraints}, bounds=bounds)

        h, k, R = result.x

        # Upewnij się, że promień jest dodatni
        if R <= 0:
            R = 0.1  # Ustaw minimalny dodatni promień, jeśli promień jest niepoprawny

        return h, k, R

    
    def calculate_arc_length(self, start_pos, end_pos, center_pos, R):
        # Punkt startowy i końcowy
        x0, y0 = start_pos
        xf, yf = end_pos
        h, k = center_pos

        # Wektory do punktów startowego i końcowego
        vector_start = np.array([x0 - h, y0 - k])
        vector_end = np.array([xf - h, yf - k])

        # Obliczanie kąta między wektorami
        dot_product = np.dot(vector_start, vector_end)
        norm_start = np.linalg.norm(vector_start)
        norm_end = np.linalg.norm(vector_end)

        # Użycie wzoru kosinusa do obliczenia kąta
        cos_theta = dot_product / (norm_start * norm_end)

        # Upewnij się, że cos_theta jest w zakresie [-1, 1]
        cos_theta = np.clip(cos_theta, -1.0, 1.0)

        theta = np.arccos(cos_theta)  # Kąt środkowy w radianach

        # Obliczanie długości łuku
        arc_length = R * theta
        return arc_length

    
    def draw_arc(self, start_pos, end_pos, start_angle_deg):
        # Konwersja kąta startowego do radianów
        start_angle = math.radians(start_angle_deg)
        
        # Obliczanie promienia i środka okręgu
        h, k, R = self.find_arc_parameters(start_pos, end_pos, start_angle)

        # Obliczenie kąta początkowego w radianach (od kierunku pojazdu)
        start_angle_rad = start_angle  # zakładamy, że start_angle jest podany w radianach

        # Obliczenie kąta końcowego w radianach na podstawie punktu końcowego
        end_angle_rad = np.arctan2(end_pos[1] - k, end_pos[0] - h)

        # Sprawdzanie, czy kąt końcowy jest mniejszy od kąta początkowego
        if end_angle_rad <= start_angle_rad:
            end_angle_rad += 2 * np.pi  # Dostosowanie kąta końcowego do pełnego obrotu
        
        # Obliczanie długości łuku
        arc_length = self.calculate_arc_length(start_pos, end_pos, (h, k), R)


        # Rysowanie okręgu i łuku w Pygame
        rect = pygame.Rect(h - R, k - R, 2 * R, 2 * R)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(h), int(k)), int(R), 2)

        return [arc_length, h, k, R]


    def draw_wheel_arc(self, start_pos, end_pos, center, radius):
        # Obliczanie kąta początkowego i końcowego w radianach
        start_angle_rad = np.arctan2(start_pos[1] - center[1], start_pos[0] - center[0])
        end_angle_rad = np.arctan2(end_pos[1] - center[1], end_pos[0] - center[0])

        # Sprawdzanie, czy kąt końcowy jest mniejszy od kąta początkowego
        if end_angle_rad <= start_angle_rad:
            end_angle_rad += 2 * np.pi  # Dostosowanie kąta końcowego do pełnego obrotu
        
        # Obliczanie długości łuku
        arc_length = radius * (end_angle_rad - start_angle_rad)

        # Rysowanie okręgu i łuku w Pygame
        rect = pygame.Rect(center[0] - radius, center[1] - radius, 2 * radius, 2 * radius)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(center[0]), int(center[1])), int(radius), 2)
        
        # Rysowanie łuku - Pygame nie ma funkcji do rysowania łuków, ale możemy to zrobić w sposób bardziej zaawansowany.
        pygame.draw.arc(self.screen, (255, 255, 255), rect, start_angle_rad, end_angle_rad, 2)
        
        return [arc_length, radius]
    

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
            df = pd.DataFrame(self.rekord, columns=['speed_L', 'speed_R'])
            df.to_excel('speeds.xlsx')
            self.reset_player()
        if keys[pygame.K_m]:
            self.mode = 1
        if keys[pygame.K_p]:
            self.mode = 3
        if keys[pygame.K_o]:
            self.mode = 2
        if keys[pygame.K_d]:
            self.mode = 4
    
    def caclucate_average(self, lista):
        # Sprawdzamy, czy lista nie jest pusta
        if not lista:
            raise ValueError("Lista nie może być pusta")
        
        # Obliczamy sumę elementów i dzielimy przez liczbę elementów
        suma = sum(lista)
        liczba_elementow = len(lista)
        srednia = suma / liczba_elementow
        
        return srednia
    
    def calculate_average_last_five(self, lista):
        # Sprawdzamy, czy lista nie jest pusta
        if not lista:
            raise ValueError("Lista nie może być pusta")

        # Wybieramy ostatnie 5 elementów
        ostatnie_elementy = lista[-5:]

        # Obliczamy sumę wybranych elementów i dzielimy przez ich liczbę
        suma = sum(ostatnie_elementy)
        liczba_elementow = len(ostatnie_elementy)
        srednia = suma / liczba_elementow

        return srednia



    def odleglosc(self, p1, p2):
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    def kat_centralny(self, p1, p2, r):
        d = self.odleglosc(p1, p2)
        return 2 * math.asin(d / (2 * r))

    def dlugosc_luku(self, p1, p2, r):
        theta = self.kat_centralny(p1, p2, r)
        return r * theta

    def kat_przeciecia(self, srodek, punkt):
        x0, y0 = srodek
        x, y = punkt
        theta = math.atan2(y - y0, x - x0)
        return math.degrees(theta)
    
    def kat_z_punktu(self, srodek, punkt):
        x0, y0 = srodek
        x, y = punkt
        return math.atan2(y - y0, x - x0)

    def wspolrzedne_punktow(self, srodek, r1, r2, r3, punkt_na_centralnym_okregu):

        # Oblicz kąt theta z punktu na centralnym okręgu
        theta = self.kat_z_punktu(srodek, punkt_na_centralnym_okregu)
        
        x0, y0 = srodek
        
        # Współrzędne punktów dla każdego z promieni
        P1 = (x0 + r1 * math.cos(theta), y0 + r1 * math.sin(theta))
        P2 = (x0 + r2 * math.cos(theta), y0 + r2 * math.sin(theta))
        P3 = (x0 + r3 * math.cos(theta), y0 + r3 * math.sin(theta))
        
        return P1, P2, P3

    def normalizuj_predkosci(self, v_1, v_2, norm_min=115):
        v_min = min(v_1, v_2)
        v_max = max(v_1, v_2)
        
        # Znormalizowana prędkość dla mniejszej wartości
        v_min_norm = norm_min
        
        # Znormalizowana prędkość dla większej wartości, proporcjonalnie
        v_max_norm = norm_min * (v_max / v_min)
        
        # Przypisanie znormalizowanych wartości do odpowiednich zmiennych
        if v_1 == v_min:
            return v_min_norm, v_max_norm
        else:
            return v_max_norm, v_min_norm
        

    def play_step(self):
        self.draw_scene()

        original_pos = self.player_pos[:]
        original_angle = self.player_angle

        if self.mode == 3:
            if len(self.distance_history) >= 20:
                self.distance_history.pop()
                self.distance_history.append(self.d1)
            else:
                self.distance_history.append(self.d1)
            
            if len(self.distance_history) < 5:
                self.distance_average = self.caclucate_average(self.distance_history)
                # print(str(self.distance_average) + " : " +  str(self.d1))
            else:
                self.distance_average = self.calculate_average_last_five(self.distance_history)
            



        if self.iteration == 15:
            #print( str(self.iteration) + " : " + str(self.prev_d1) + " : " + str(self.d1))
            self.prev_d1 = self.d1
            self.iteration = 0
        else:
            self.iteration += 1

    

        # # Fuzzy logic control
        # if self.mode == 2:
        #     # print("Rotate")
        #     speedL, speedR = self.fuzzy_rotate.compute_action(self.d1, self.d2, self.d3)
        # elif self.mode == 3:
        #     # print("Parallel")
        #     speedL, speedR = self.fuzzy_parallel.compute_action(self.d1 - self.distance_average, self.d2, self.d3)
        # elif self.mode == 0:
        #     speedL = 0
        #     speedR = 0
        #     self.mode = 1
        # elif self.mode == 1:
        #     # print("Logic")
        #     speedL, speedR = self.fuzzy_logic.compute_action(self.d1, self.d2, self.d3)
        # else:
        #     speedL, speedR = self.fuzzy_dock.compute_action(self.d2 - self.d3, self.d2, self.d3)


        # print(str(self.speedL) + " : " + str(self.speedR))

        # self.draw_sensors(self.top_left, self.top_right, self.bottom_left)
        # if(self.left_wheel == 0 and self.right_wheel == 0):
        #     self.left_wheel = self.top_left
        #     self.right_wheel = self.top_right
        #     self.start_angle = self.player_angle
        
        [center_length, x, y, Rc] = self.draw_arc((self.start_pos[0], self.start_pos[1]), self.parking_pos, self.start_angle)

        [left_length, Rl] = self.draw_wheel_arc((self.left_wheel[0], self.left_wheel[1]), self.parking_pos, (x,y), Rc - 150)
        [right_length, Rr] = self.draw_wheel_arc((self.right_wheel[0], self.right_wheel[1]), self.parking_pos, (x, y), Rc + 150)


        print("Pozycja startowa: " + str(self.start_pos[0]) + ' : ' + str(self.start_pos[1]))

        s_P1, s_P2, s_P3 = self.wspolrzedne_punktow((x,y), Rl, Rc, Rr, self.start_pos)
        print(f"Punkt startowy na okręgu o promieniu {Rl}: {s_P1}")
        print(f"Punkt startowy na okręgu o promieniu {Rc}: {s_P2}")
        print(f"Punkt startowy na okręgu o promieniu {Rr}: {s_P3}")

        k_P1, k_P2, k_P3 = self.wspolrzedne_punktow((x,y), Rl, Rc, Rr, self.parking_pos)
        print(f"Punkt koncowy na okręgu o promieniu {Rl}: {k_P1}")
        print(f"Punkt koncowy na okręgu o promieniu {Rc}: {k_P2}")
        print(f"Punkt koncowy na okręgu o promieniu {Rr}: {k_P3}")
        

        if(self.speedL == 0 and self.speedR == 0):

            # Obliczanie prędkości kół na podstawie promieni
            print("new circle")

            speed_L = Rl / 500
            speed_R = Rr / 500
            
            self.speedL = speed_L
            self.speedR = speed_R

            self.circle_center = [x,y]
            self.radius_l = Rl
            self.radius_r = Rr



        # action_speed = (self.speedL + self.speedR)
        # action_angle = (self.speedL - self.speedR)

        angle_speed = -0.1
        self.angle += angle_speed
        self.player_angle = math.degrees(self.angle)
        self.player_angle_r = math.degrees(self.angle)

        self.speedL = angle_speed * self.radius_l
        self.speedR = angle_speed * self.radius_r


        print(str(self.speedL) + " : " + str(self.speedR))
        norm_right_speed, norm_left_speed = self.normalizuj_predkosci(self.speedL, self.speedR)

        print(str(norm_right_speed) + " : " + str(norm_left_speed))
        print(str(self.dlugosc_luku(s_P1, k_P1, Rl)) + " : " + str(self.dlugosc_luku(s_P2, k_P2, Rc)) + " : " + str(self.dlugosc_luku(s_P3, k_P3, Rr)))
        print(str(self.kat_przeciecia((x,y), self.parking_pos)))
        # self.player_angle += action_angle
        # self.player_speed = action_speed

        # Aktualizacja pozycji prostokąta na podstawie kąta i promienia
        self.player_pos[0] = self.circle_center[0] + self.radius_l * math.cos(self.angle)
        self.player_pos[1] = self.circle_center[1] + self.radius_l * math.sin(self.angle)

        self.player_pos_r[0] = self.circle_center[0] + self.radius_r * math.cos(self.angle)
        self.player_pos_r[1] = self.circle_center[1] + self.radius_r * math.sin(self.angle)

        # self.player_pos[0] += self.player_speed * math.sin(math.radians(self.player_angle))
        # self.player_pos[1] -= self.player_speed * math.cos(math.radians(self.player_angle))


        self.player_rect = self.draw_player(self.player_pos, self.player_angle, self.top_left, self.top_right, self.bottom_left, self.bottom_right )
        self.player_rect_r = self.draw_player(self.player_pos_r, self.player_angle_r, self.top_left_r, self.top_right_r, self.bottom_left_r, self.bottom_right_r )

        if self.check_collision(self.player_rect, [self.horizontal_wall, self.vertical_wall]):
            self.player_pos = original_pos
            self.player_angle = original_angle
            self.screen_text = self.font.render('COLISION', True, self.white)
            
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
