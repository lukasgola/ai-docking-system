import socket
import time
import numpy as np

from Fuzzy import FuzzyLogicController
from Fuzzy_Parallel import FuzzyParallelLogicController
from FuzzyRotate import FuzzyRotateLogicController

class MotorSensorController:
    def __init__(self, mot_host, mot_port, sen_host, sen_port):
        self.mot_host = mot_host
        self.mot_port = mot_port
        self.sen_host = sen_host
        self.sen_port = sen_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.speed_L = 0
        self.speed_R = 0
        self.iteration = 0
        self.mode = 1
        self.prev_d1 = 0

        # Inicjalizacja kontrolerów fuzzy
        self.fuzzy_logic = FuzzyLogicController()
        self.fuzzy_rotate = FuzzyRotateLogicController()
        self.fuzzy_parallel = FuzzyParallelLogicController()

    def send_motor_command(self):

        left_f = 0xFF
        left_b = 0xFF
        right_f = 0xFF
        right_b = 0xFF

        if self.speed_L >= 0:
            left_f = 255 - (self.speed_L + 80)
        else:
            left_b = 255 - (abs(self.speed_L) + 80)

        if self.speed_R >= 0:
            right_f = 255 - (self.speed_R + 80)
        else:
            right_b = 255 - (abs(self.speed_R) + 80)

        # print(f"{left_b}, {left_f}, {right_b}, {right_f}")

        if left_b > 170:
            left_b = 255
        if left_f > 170:
            left_f = 255
        if right_b > 170:
            right_b = 255
        if right_f > 170:
            right_f = 255


        message = bytes([int(left_b), int(left_f), int(right_b), int(right_f)])
        # message = bytes([0xFF, 0x60, 0xFF, 0x60])
        self.client.sendto(message, (self.mot_host, self.mot_port))

    def receive_motor_response(self):
        try:
            data, addr = self.client.recvfrom(1024)
            # print(f"Otrzymano odpowiedź od {addr}: {data}")
        except socket.timeout:
            print("Brak odpowiedzi, przekroczono czas oczekiwania")

    def send_sensor_command(self):
        message = bytes([0x00, 0x00, 0x00, 0x00])
        self.client.sendto(message, (self.sen_host, self.sen_port))

    def receive_sensor_response(self):
        try:
            data, addr = self.client.recvfrom(1024)
            data_str = data.decode('utf-8')
            values = data_str.split(";")
            d1 = int(values[1])
            d2 = int(values[2])
            d3 = int(values[3])
            print(f"{d1}, {d2}, {d3}")
            return d1, d2, d3
        except socket.timeout:
            print("Brak odpowiedzi, przekroczono czas oczekiwania")
            return None, None, None

    def update_speeds(self, d1, d2, d3):
        if d1 is not None and d2 is not None and d3 is not None:
            # Replace this with actual fuzzy logic control

            if self.iteration == 3:
                #print( str(self.iteration) + " : " + str(self.prev_d1) + " : " + str(self.d1))
                self.prev_d1 = d1
                self.iteration = 0
            else:
                self.iteration += 1

            if self.mode == 1:
                speedL, speedR = self.fuzzy_logic.compute_action(d1, d2, d3)
                if d2 > 150 and d2 < 200 and d3 > 150 and d3 < 250:
                    self.mode = 2
            elif self.mode == 2:
                speedL, speedR = self.fuzzy_rotate.compute_action(d1, d2, d3)
                if d2 > 250 and d3 > 250 and d1 < 350:
                    self.mode = 3
            elif self.mode == 3:
                speedL, speedR = self.fuzzy_parallel.compute_action(d1 - self.prev_d1, d2, d3)
            
            
            self.speed_L = speedL
            self.speed_R = speedR

    def run(self, iterations):
        for i in range(iterations):
            # print(f"Updated speeds: speedL={self.speed_L}, speedR={self.speed_R}")
            self.send_motor_command()
            self.receive_motor_response()
            self.send_sensor_command()
            d1, d2, d3 = self.receive_sensor_response()
            self.update_speeds(d1, d2, d3)
            time.sleep(0.01)
        self.client.close()

if __name__ == "__main__":
    mot_host = "192.168.0.101"
    mot_port = 4000
    sen_host = "192.168.0.102"
    sen_port = 4000

    controller = MotorSensorController(mot_host, mot_port, sen_host, sen_port)
    controller.run(2000)
