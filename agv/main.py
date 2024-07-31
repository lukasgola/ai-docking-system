import socket
import time
import pygame
import numpy as np

from Fuzzy import FuzzyLogicController
from Fuzzy_Parallel import FuzzyParallelLogicController
from FuzzyRotate import FuzzyRotateLogicController

UDP_IP_MOVE = "192.168.0.101"
UDP_IP = "192.168.0.102"
UDP_PORT = 4000
MESSAGE = bytes([0xFF, 0x55, 0xFF, 0x55])
MESSAGE_STOP = bytes([0xFF, 0xFF, 0xFF, 0xFF])

STOP_FLAG = True

fuzzy_logic = FuzzyLogicController()
fuzzy_rotate = FuzzyRotateLogicController()
fuzzy_parallel = FuzzyParallelLogicController()

mode = 1
iteration = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)  # 1 second timeout

def keyboard_move(self, keys):
    if keys[pygame.K_r]:
        self.reset_player()
    if keys[pygame.K_m]:
        self.mode = 1
    if keys[pygame.K_p]:
        self.mode = 3
    if keys[pygame.K_o]:
        self.mode = 2

def move(speedL, speedR):
    left_f = 0xFF
    left_b = 0xFF
    right_f = 0xFF
    right_b = 0xFF

    # Convert numpy float64 to integers
    speedL = int(np.round(speedL)) * 2
    speedR = int(np.round(speedR)) * 2

    if speedL >= 0:
        left_f = speedL
    else:
        left_b = abs(speedL)

    if speedR >= 0:
        right_f = speedR
    else:
        right_b = abs(speedR)

    print(f"Speeds: {left_b}, {left_f}, {right_b}, {right_f}")

    MESSAGE = bytes([left_b, left_f, right_b, right_f])
    sock.sendto(MESSAGE, (UDP_IP_MOVE, UDP_PORT))

def send_udp_data():
    global STOP_FLAG

    try:
        # Send UDP message
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

        # Receive UDP response
        response, _ = sock.recvfrom(1024)

        # Decode the bytes response into a string
        response_str = response.decode('utf-8')

        # Split the string into individual values
        values = response_str.split(';')

        distances = [float(x) for x in values[1:] if x]

        # Return the first three distances
        if len(distances) >= 3:
            return distances[0], distances[1], distances[2]
        else:
            return None, None, None

    except socket.timeout:
        print("No response received within the timeout period.")
        return None, None, None

# Call the function every second
while True:
    d1, d2, d3 = send_udp_data()
    if d1 is not None and d2 is not None and d3 is not None:
        print(f"Returned distances: dist1={d1}, dist2={d2}, dist3={d3}")
        
        if iteration == 15:
            prev_d1 = d1
            iteration = 0
        else:
            iteration += 1
        
        # Fuzzy logic control
        if mode == 2:
            print("Rotate")
            speedL, speedR = fuzzy_rotate.compute_action(d1, d2, d3)
        elif mode == 3:
            print("Parallel")
            speedL, speedR = fuzzy_parallel.compute_action(d1 - prev_d1, d2, d3)
        elif mode == 0:
            speedL = 0
            speedR = 0
            mode = 1
        else:
            print("Logic")
            speedL, speedR = fuzzy_logic.compute_action(d1, d2, d3)

        move(speedL, speedR)
