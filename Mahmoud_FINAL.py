import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import bruges as bg

# =============================================================================
# 1) Data Loading and Basic Setup
# =============================================================================
# Data is loaded from an Excel file containing the coordinate grids and physical properties.
# The file contains four sheets: X, Y, VPH_export (velocity in m/s), and RHOB_export (density in kg/m^3).
sheets = pd.read_excel(
    'data2D.xlsx',
    sheet_name=['X', 'Y', 'VPH_export', 'RHOB_export'],
    header=None
)

# Extract the data arrays from the Excel sheets.
X = sheets['X'].values
Y = sheets['Y'].values
VP = sheets['VPH_export'].values    # Velocity (m/s)
RHOB = sheets['RHOB_export'].values # Density (kg/m^3)

# Determine the dimensions of the input grid.
ny, nx = VP.shape
x_axis = X[0, :]  # Horizontal axis (e.g., distance)
y_axis = Y[:, 0]  # Vertical axis (e.g., depth or elevation)

# Display the shapes and ranges of the loaded data.
print("Data shapes:")
print("  X   =", X.shape)
print("  Y   =", Y.shape)
print("  VP  =", VP.shape)
print("  RHOB=", RHOB.shape)
print("x_range:", x_axis.min(), "->", x_axis.max())
print("y_range:", y_axis.min(), "->", y_axis.max())

# If necessary, ensure the y_axis is in ascending order.
# Uncomment the following block if the top of the data is not at the beginning.
# if y_axis[0] > y_axis[-1]:
#     y_axis = y_axis[::-1]
#     VP = VP[::-1, :]
#     RHOB = RHOB[::-1, :]

# =============================================================================
# 2) Acoustic Impedance (AI) and Reflection Coefficients (RC)
# =============================================================================
# Convert velocity from m/s to km/s and density from kg/m^3 to g/m^3.
VP_km = VP * 1e-3       
RHOB_g = RHOB * 1e3     

# Compute Acoustic Impedance: AI = velocity (km/s) * density (g/m^3)
AI = VP_km * RHOB_g

# Calculate reflection coefficients using a finite-difference approximation:
# RC[i] = (AI[i+1] - AI[i]) / (AI[i+1] + AI[i])
RC = np.zeros_like(AI)
RC[1:, :] = (AI[1:, :] - AI[:-1, :]) / (AI[1:, :] + AI[:-1, :])

# =============================================================================
# 3) Two-Way Travel Time (TWT) Calculation
# =============================================================================
# TWT is computed as a cumulative sum of the time increments between depth samples.
# The time increment between two depth samples is calculated as:
#   dt_ms = (2 * (delta z) / velocity) * 1000, to convert seconds to milliseconds.
TWT = np.zeros_like(VP, dtype=np.float32)
global_tmax = 0.0

for ix in range(nx):
    twt_col = np.zeros(ny, dtype=np.float32)
    for i in range(1, ny):
        dz = abs(y_axis[i] - y_axis[i-1])  # Depth increment (meters)
        vel = VP[i, ix]                   # Velocity at current depth (m/s)
        dt_ms = 2.0 * dz / vel * 1000.0     # Time increment in milliseconds
        twt_col[i] = twt_col[i-1] + dt_ms   # Cumulative two-way travel time
    TWT[:, ix] = twt_col
    if twt_col[-1] > global_tmax:
        global_tmax = twt_col[-1]

print(f"Global max TWT across all traces = {global_tmax:.2f} ms")

# =============================================================================
# 4) Uniform Time Axis & Reflection Coefficient Mapping (Teacher's Method)
# =============================================================================
# The wavelet duration is defined as the maximum TWT plus the sampling interval (dt).
# dt is set as the time sampling interval in milliseconds.
dt = 0.02  # ms (sampling interval; adjust as needed)
wavelet_duration_ms = global_tmax + dt

# A uniform time axis is created using np.arange from 0 to (global_tmax + dt) with step dt.
time_axis = np.arange(0, wavelet_duration_ms + dt, dt)
nt = len(time_axis)
print(f"Using dt = {dt} ms, wavelet duration = {wavelet_duration_ms:.2f} ms")
print(f"Time axis length = {nt}")

# Prepare a 2D array (RC_time) to store the reflection coefficients on the uniform time grid.
RC_time = np.zeros((nt, nx), dtype=np.float32)

# The reflection coefficients and TWT for each trace are stored in separate lists.
rc_lists = []
twt_lists = []
for ix in range(nx):
    rc_lists.append(RC[:, ix])     # Reflection coefficients for trace ix
    twt_lists.append(TWT[:, ix])   # TWT for trace ix

# Map each RC value to the closest time sample on the uniform time axis using np.argmin.
for ix in range(nx):
    rc_col = rc_lists[ix]
    twt_col = twt_lists[ix]
    for i in range(ny):
        t_ms = twt_col[i]
        if t_ms <= wavelet_duration_ms:
            idx = np.argmin(np.abs(time_axis - t_ms))
            RC_time[idx, ix] = rc_col[i]

# =============================================================================
# 5) Seismic in Time: Wavelet Generation & Convolution
# =============================================================================
# A Ricker wavelet is generated with duration equal to the wavelet_duration (converted to seconds)
# and sampling interval dt (converted to seconds). A frequency of 4000 Hz is used.
wavelet_t, _ = bg.filters.ricker(
    duration=wavelet_duration_ms / 1000.0,  # Convert ms to seconds
    dt=dt / 1000.0,                        # Convert ms to seconds
    f=4000.0                               # Wavelet central frequency in Hz
)
ws_t = wavelet_t.flatten()

# Each trace in RC_time is convolved with the Ricker wavelet to simulate the seismic response.
seis_time = np.zeros_like(RC_time)
for ix in range(nx):
    seis_time[:, ix] = np.convolve(RC_time[:, ix], ws_t, mode='same')

# =============================================================================
# 6) Conversion from Time-Domain Seismic to Depth-Domain Seismic
# =============================================================================
# The time-domain seismic is converted to depth by interpolating at the TWT for each depth sample.
seis_depth = np.zeros((ny, nx), dtype=np.float32)
for ix in range(nx):
    # An interpolation function is created for the current trace.
    f_seis_t = interp1d(
        time_axis,
        seis_time[:, ix],
        kind='linear',
        bounds_error=False,
        fill_value=0.0
    )
    # The seismic amplitude is interpolated at each TWT value corresponding to the depth samples.
    for i in range(ny):
        t_ms = TWT[i, ix]
        seis_depth[i, ix] = f_seis_t(t_ms)

# =============================================================================
# 7) Plotting the Results: 2x2 Grid Display
# =============================================================================
# The final results are displayed in a 2x2 grid:
#   (0,0) P-wave Impedance (AI) in depth domain,
#   (0,1) Reflection Coefficients mapped on the uniform time axis (RC_time),
#   (1,0) Synthetic Seismic in Time Domain (seis_time),
#   (1,1) Synthetic Seismic in Depth Domain (seis_depth).
fig, axs = plt.subplots(2, 2, figsize=(14, 5))

# Plot Acoustic Impedance (AI)
im0 = axs[0, 0].imshow(
    AI,
    aspect='equal',
    cmap='jet',
    extent=[x_axis.min(), x_axis.max(), y_axis.max(), y_axis.min()]
)
cbar0 = fig.colorbar(im0, ax=axs[0, 0])
cbar0.set_label('AI (km/s·g/m³)')
axs[0, 0].set_title('P-wave Impedance')
axs[0, 0].set_xlabel('X Distance')
axs[0, 0].set_ylabel('Depth (m)')

# Plot Reflection Coefficients in Time Domain (RC_time)
im1 = axs[0, 1].imshow(
    RC_time,
    aspect='auto',
    cmap='seismic',
    extent=[x_axis.min(), x_axis.max(), time_axis.max(), time_axis.min()]
)
cbar1 = fig.colorbar(im1, ax=axs[0, 1])
cbar1.set_label('RC')
axs[0, 1].set_title('RC Data on Full Time Grid')
axs[0, 1].set_xlabel('X Distance')
axs[0, 1].set_ylabel('Two-Way Time (ms)')

# Plot Seismic in Time Domain (seis_time)
im2 = axs[1, 0].imshow(
    seis_time,
    aspect='auto',
    cmap='seismic',
    interpolation='bicubic',
    extent=[x_axis.min(), x_axis.max(), time_axis.max(), time_axis.min()]
)
cbar2 = fig.colorbar(im2, ax=axs[1, 0])
cbar2.set_label('Amplitude')
axs[1, 0].set_title('Seismic in Time Domain')
axs[1, 0].set_xlabel('X Distance')
axs[1, 0].set_ylabel('Two-Way Time (ms)')

# Plot Seismic in Depth Domain (seis_depth)
im3 = axs[1, 1].imshow(
    seis_depth,
    aspect='equal',
    cmap='seismic',
    interpolation='bicubic',
    extent=[x_axis.min(), x_axis.max(), y_axis.max(), y_axis.min()]
)
cbar3 = fig.colorbar(im3, ax=axs[1, 1])
cbar3.set_label('Amplitude')
axs[1, 1].set_title('Seismic in Depth Domain')
axs[1, 1].set_xlabel('X Distance')
axs[1, 1].set_ylabel('Depth (m)')

plt.tight_layout()
plt.show()

print("\nDone! Final shapes:")
print("  RC_time:", RC_time.shape)
print("  seis_time:", seis_time.shape)
print("  seis_depth:", seis_depth.shape)
