# %% ZBIERANIE DANYCH - STEROWANIE RECZNE

import socket
import time



from pynput.mouse import Controller
from screeninfo import get_monitors

# Utworzenie obiektu Controller do kontroli myszy
mouse = Controller()

# host i port modułu sterowania silnikami
mot_host = "192.168.1.100"
mot_port = 4000


# host i port modułu sterowania czujnikami
sen_host = "192.168.1.200"
sen_port = 4000

# Tworzenie gniazda UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Ustawienie czasu oczekiwania na odpowiedź (timeout) na 1 sekundę
client.settimeout(1)

# Zmienna do zapisu danych
rekord = []

for i in range(200):
    
    
    #
    # wypracowanie sygnału sterującego
    #
    
    # Odczytanie aktualnej pozycji myszy
    current_position = mouse.position
    
    # Odczytanie rozdzielczości ekranu
    monitor = get_monitors()[0]  # Zakładamy, że używamy głównego monitora
    screen_width = monitor.width
    screen_height = monitor.height
    
    # Obliczenie pozycji myszy w procentach ekranu
    x_percent = (current_position[0] / screen_width)
    y_percent = (current_position[1] / screen_height)
    
    # speed = int((1-y_percent) * 255)
    speed = 128
     
    speed_L = (255 - int(x_percent * speed))
    speed_R = (255 - int((1-x_percent) * speed))
    
    # 
    # rejestracja wartości PWM na silniki
    # 
    
    #
    # sterowanie silnikami - rozkaz z PWM dla silnika 1 i 2
    #
    message = bytes([0xFF, speed_L, 0xFF, speed_R])
    
    client.sendto(message, (mot_host, mot_port))
    
    #
    # sterowanie silnikami - odpowiedź ze znacznikiem czasu i prądami  
    #
    
    try:
        data, addr = client.recvfrom(1024)  # Odbieranie danych (maksymalnie 1024 bajty)
        print(f"Otrzymano odpowiedź od {addr}: {data}")
    except socket.timeout:
        print("Brak odpowiedzi, przekroczono czas oczekiwania")
        
    #
    # sterowanie czujnikami - inicjacja
    #
    message = bytes([0x00, 0x00, 0x00, 0x00])
    client.sendto(message, (sen_host, sen_port))
    
    #
    # sterowanie czujnikami - odpowiedź z odległościami 
    #
    
    try:
        data, addr = client.recvfrom(1024)  # Odbieranie danych (maksymalnie 1024 bajty)
        print(f"Otrzymano odpowiedź od {addr}: {data}")
        
        data = str(data)
        
        # zapis danych
        d0 = data.split(";")[0]
        d1 = data.split(";")[1]
        d2 = data.split(";")[2]
        d3 = data.split(";")[3]
        d3_d2 = int(d3) - int(d2)
        
        rekord.append([d1, d2, d3, d3_d2, speed_L, speed_R])
        
        
    except socket.timeout:
        print("Brak odpowiedzi, przekroczono czas oczekiwania")  
                     

    time.sleep(0.1)
    
client.close()


# zapisanie zebranych danych

import pandas as pd

df = pd.DataFrame(rekord, columns=['d1','d2','d3', 'd3_d2', 'speed_L', 'speed_R'])

# df.to_excel('record.xlsx')


# %% TRENING MODELU


import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_excel('record.xlsx')


# 
# Model model_L
# 

X = df[['d1','d2','d3', 'd3_d2']].to_numpy()
y = df[['speed_L']].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,  random_state=42)


from sklearn.tree import DecisionTreeRegressor

model_L = DecisionTreeRegressor()

model_L.fit(X_train,y_train)


y_predict = model_L.predict(X_test)

import matplotlib.pyplot as plt

plt.plot(y_test, y_predict,'.')
plt.title("model_L")
plt.show()

# 
# Model model_R
# 

X = df[['d1','d2','d3', 'd3_d2']].to_numpy()
y = df[['speed_R']].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,  random_state=42)


from sklearn.tree import DecisionTreeRegressor

model_R = DecisionTreeRegressor()

model_R.fit(X_train,y_train)


y_predict = model_R.predict(X_test)

import matplotlib.pyplot as plt

plt.plot(y_test, y_predict,'.')
plt.title("model_R")
plt.show()


# %% JAZDA AUTONOMICZNA

import socket
import time

# host i port modułu sterowania silnikami
mot_host = "192.168.1.100"
mot_port = 4000


# host i port modułu sterowania czujnikami
sen_host = "192.168.1.200"
sen_port = 4000

# Tworzenie gniazda UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Ustawienie czasu oczekiwania na odpowiedź (timeout) na 1 sekundę
client.settimeout(1)


# inicjacja pakietu danych UDP
message = bytes([0xFF, 0xFF, 0xFF, 0xFF])


for i in range(300):
    
    
    #
    # sterowanie czujnikami - inicjacja
    #
    message = bytes([0x00, 0x00, 0x00, 0x00])
    client.sendto(message, (sen_host, sen_port))
    
    #
    # sterowanie czujnikami - odpowiedź z odległościami 
    #
    
    try:
        data, addr = client.recvfrom(1024)  # Odbieranie danych (maksymalnie 1024 bajty)
        print(f"Otrzymano odpowiedź od {addr}: {data}")
        
        data = str(data)
        
        # zapis danych
        d0 = data.split(";")[0]
        d1 = data.split(";")[1]
        d2 = data.split(";")[2]
        d3 = data.split(";")[3]
        d3_d2 = int(d3) - int(d2)
        
        
    except socket.timeout:
        print("Brak odpowiedzi, przekroczono czas oczekiwania")  
    
    
    #
    # wypracowanie sygnału sterującego
    #
     
    speed_L = int(model_L.predict([[d1, d2, d3, d3_d2]]))
    speed_R = int(model_R.predict([[d1, d2, d3, d3_d2]]))
    
    # 
    # rejestracja wartości PWM na silniki
    # 
    
    #
    # sterowanie silnikami - rozkaz z PWM dla silnika 1 i 2
    #
    message = bytes([0xFF, speed_L, 0xFF, speed_R])
    
    client.sendto(message, (mot_host, mot_port))
    
    #
    # sterowanie silnikami - odpowiedź ze znacznikiem czasu i prądami  
    #
    
    try:
        data, addr = client.recvfrom(1024)  # Odbieranie danych (maksymalnie 1024 bajty)
        print(f"Otrzymano odpowiedź od {addr}: {data}")
    except socket.timeout:
        print("Brak odpowiedzi, przekroczono czas oczekiwania")
        

    time.sleep(0.1)
    
client.close()












