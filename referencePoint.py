import pandas as pd
import matplotlib.pyplot as plt

# Wczytaj dane z pliku Excel
file_path = 'LastMeasurement.xlsx'  # Zmień nazwę pliku, jeśli jest inna
df = pd.read_excel(file_path)

# Sprawdź, jakie kolumny są w pliku
print(df.columns)

# Pobierz dane z kolumn Xref i Yref
x_coords = df['Xref']
y_coords = df['Yref']

x_ref = [325]
y_ref = [300]

# Tworzenie wykresu
plt.figure(figsize=(10, 6))
plt.scatter(x_coords, y_coords, c='blue', marker='o')
plt.scatter(x_ref, y_ref, c='red', marker='o')
plt.title('Reference Point Coords')
plt.xlabel('Xref')
plt.ylabel('Yref')
plt.grid(True)
plt.show()
