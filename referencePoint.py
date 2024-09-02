import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Wczytaj dane z pliku Excel
file_path = 'LastMeasurement.xlsx'  # Zmień nazwę pliku, jeśli jest inna
df = pd.read_excel(file_path)

# Sprawdź, jakie kolumny są w pliku
print(df.columns)

# Pobierz dane z kolumn Xref i Yref
x_coords = df['Xref']
y_coords = df['Yref']

x_ref = [350]
y_ref = [350]

# Punkt docelowy
target_x = 350
target_y = 350

# Oblicz błędy bezwzględne względem punktu docelowego
errors_x = np.abs(x_coords - target_x)
errors_y = np.abs(y_coords - target_y)

# Oblicz błędy względne
relative_errors_x = errors_x / target_x
relative_errors_y = errors_y / target_y

# Oblicz średnie błędy
mean_error_x = np.mean(errors_x)
mean_error_y = np.mean(errors_y)

# Oblicz odchylenie standardowe błędów
std_dev_error_x = np.std(errors_x, ddof=1)
std_dev_error_y = np.std(errors_y, ddof=1)

# Wyświetl wyniki
# print(f"Średni błąd względny dla X: {relative_errors_x:.2f}")
# print(f"Średni błąd względny dla Y: {relative_errors_y:.2f}")
print(f"Średni błąd bezwzględny dla X: {mean_error_x:.2f}")
print(f"Średni błąd bezwzględny dla Y: {mean_error_y:.2f}")
print(f"Odchylenie standardowe błędów dla X: {std_dev_error_x:.2f}")
print(f"Odchylenie standardowe błędów dla Y: {std_dev_error_y:.2f}")

# Tworzenie wykresu
plt.figure(figsize=(10, 6))

# Ustaw zakresy osi
plt.xlim(0, 1000)
plt.ylim(0, 1000)

plt.scatter(x_coords, y_coords, c='blue', marker='o')
plt.scatter(x_ref, y_ref, c='red', marker='o')
plt.title('Dead Reckoning Algorithm Reference Point Coords')
plt.xlabel('Xref')
plt.ylabel('Yref')
plt.grid(True)
plt.show()
