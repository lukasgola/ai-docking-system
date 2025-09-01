import pandas as pd
import matplotlib.pyplot as plt
import argparse

# CLI args
parser = argparse.ArgumentParser(description='Plot AGV data from Excel with optional start/end index.')
parser.add_argument('--file', '-f', default='1_0_1.xlsx', help='Excel file to plot (default: 2_-30_1.xlsx)')
parser.add_argument('--start-index', '-s', type=int, default=0, help='Row index to start plotting from (default: 0)')
parser.add_argument('--end-index', '-e', type=int, default=None, help='Row index to end plotting at (inclusive). If omitted, plots to end.')
args = parser.parse_args()

# Load the Excel file
file_path = args.file
df = pd.read_excel(file_path)

# Slice from start/end index (keep original index so x-axis reflects actual row numbers)
end_slice = None if args.end_index is None else args.end_index + 1  # inclusive end
df = df.iloc[args.start_index:end_slice]

# Extract distance columns
dist1 = df['d1']
dist2 = df['d2']
dist3 = df['d3']
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
plt.ylabel('PVM Value')
plt.title('AGV Route Visualization')
plt.legend()
plt.grid(True)
plt.show()
