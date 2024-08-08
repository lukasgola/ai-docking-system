import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
file_path = 'speeds.xlsx'
df = pd.read_excel(file_path)

# Extract distance columns
# dist1 = df['d1']
# dist2 = df['d2']
# dist3 = df['d3']
speed_L = df['speed_L']
speed_R = df['speed_R']

# For simplicity, let's assume these distances are in a sequence and can be plotted directly.
# If these distances represent x, y coordinates, we need to adjust the approach.

# Plot the points and the route
plt.figure(figsize=(10, 6))
# plt.plot(dist1, label='Dist1')
# plt.plot(dist2, label='Dist2')
# plt.plot(dist3, label='Dist3')
plt.plot(speed_L, label='Speed_L')
plt.plot(speed_R, label='Speed_R')
plt.xlabel('Index')
plt.ylabel('Distance [mm]')
plt.title('Car Route Visualization')
plt.legend()
plt.grid(True)
plt.show()
