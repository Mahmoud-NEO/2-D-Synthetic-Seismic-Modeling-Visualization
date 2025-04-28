
# 2-D Synthetic Seismic Forward-Modelling  
*A start-to-finish Python workflow that converts velocity–density grids into synthetic seismic sections in both time and depth domains.*

---

## 🎯 Project Purpose
Forward modelling is the fastest way to **stress-test geologic scenarios** and check whether your velocity-density model produces the reflector geometry and amplitudes you expect—*before* spending money on field operations.  
This repository implements the **zero-offset 1-D convolutional model** entirely in open-source Python so that anyone can:

1. Load a VP–RHOB grid exported from Petrel, Petromod, GoCad, etc.  
2. Generate seismic in time and depth.  
3. QC every link of the chain with one script.

---

## 🗂 Repository Layout
```
.
├── Mahmoud_FINAL.py               # Main script – run it and get the plots
├── data2D.xlsx                    # Demo X, Y, velocity & density sheets
├── Mahmoud-Mohamed_Presentation.pdf
├── docs
│   └── img
│       └── final_2x2_grid.png
└── README.md                      # You are here
```

---

## 🔬 Method Explained Step-by-Step  

Below is a line-by-line interpretation of **Mahmoud_FINAL.py**  
(Section numbers match the comments in the code).

| # | Code Block | What Happens | Why It Matters |
|---|------------|--------------|----------------|
| **1** | **Data Loading**<br>`pd.read_excel(... sheet_name=[...])` | Four sheets—`X`, `Y`, `VPH_export`, `RHOB_export`—are loaded into NumPy arrays. | Keeps grid geometry (X, Y) aligned with property grids (VP, RHOB). |
| **2** | **Unit Conversion**<br>`VP_km = VP*1e-3`, `RHOB_g = RHOB*1e3` | Velocity → km s⁻¹ ; Density → g cm⁻³. | Keeps Acoustic Impedance (AI) in practical ranges (≈ 10³–10⁴) and avoids floating-point overflow. |
| **2** | **Acoustic Impedance**<br>`AI = VP_km * RHOB_g` | AI grid is computed cell-by-cell. | AI is the first-order control on reflection strength. |
| **2** | **Reflection Coefficient (RC)**<br>`RC[1:] = (AI[i+1]-AI[i])/(AI[i+1]+AI[i])` | 1-D normal-incidence Zoeppritz simplification applied down each column. | Produces a reflectivity series that a zero-offset source would “see.” |
| **3** | **Two-Way Time (TWT)** | For each depth sample, time increment is `2 Δz / VP` (seconds → ms). Cumulative sum builds TWT curve per trace. | Converts depth grid to time so you can later convolve with a wavelet. |
| **4** | **Uniform Time Axis** | A global axis from 0 to `max(TWT) + dt` with step `dt = 0.02 ms`. | Convolution needs equal sample spacing; different traces must share the same time axis. |
| **4** | **Mapping RC to Time** | Each `(RC, TWT)` pair is placed in the nearest time-sample slot using `np.argmin`. | Aligns all traces onto the common axis without resampling velocity. |
| **5** | **Wavelet Generation**<br>`bg.filters.ricker(duration, dt, f=4000)` | Creates a zero-phase Ricker with 4 kHz peak frequency. | A compact, bandwidth-limited pulse ideal for synthetic demos. |
| **5** | **Convolution**<br>`np.convolve(RC_time[:,ix], wavelet, 'same')` | RC series acts as reflectivity; wavelet is the source; convolution yields synthetic seismic in time. | Implements the classic *“seismic = wavelet ⊗ reflectivity”* model. |
| **6** | **Time-to-Depth Interpolation** | `interp1d(time_axis, seis_time, ...)` samples the time trace at each depth’s TWT value. | Produces a seismic depth slice so you can check reflector placement against geology. |
| **7** | **QC Plots** | 2 × 2 grid: AI, RC(time), seismic(time), seismic(depth). | One look confirms whether conversions and convolution behaved as intended. |

---

## ⚙️ Why These Design Choices?

| Design Choice | Rationale |
|---------------|-----------|
| **Excel input** | Most interpreters export to XLSX without license fees; `pandas` reads it in one line. |
| **Ricker @ 4 kHz** | High-frequency pulse shows fine layering in classroom-scale models; easy to swap. |
| **0.02 ms `dt`** | Nyquist for 4 kHz is 0.125 ms; oversampling avoids dispersion in convolution. |
| **Global max TWT** | Guarantees the wavelet length covers the deepest sample on any trace. |
| **`interp1d`** | Linear depth interpolation is faster and adequate given small cell height. |
| **Matplotlib** | Universal, scriptable; results identical on any OS. |

---

## 🚀 Quick-Start Guide

```bash
# 1️⃣  Clone the repo
git clone https://github.com/<your-user>/seismic-2D.git
cd seismic-2D

# 2️⃣  Install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # numpy pandas matplotlib scipy bruges openpyxl

# 3️⃣  Run the entire workflow
python Mahmoud_FINAL.py
```

You’ll see terminal prints of data shapes, maximum TWT, and the plot window shown below:

![Final 2x2 grid](docs/img/final_2x2_grid.png)

---

## 🧪 Validating Your Own Models

1. Replace `data2D.xlsx` with your **X, Y, VPH_export, RHOB_export** sheets.  
2. Adjust `dt` or the wavelet frequency in the script header if your model scale differs.  
3. Compare the depth seismic panel with known stratigraphy or horizons to confirm alignment.

---

## 🛠️ Extending the Code

| Idea | How to Implement |
|------|------------------|
| **Angle-dependent RC (AVA)** | Replace the simple RC formula with `bruges.reflection.zoeppritz_rpp`. |
| **Different wavelets** | Swap `bg.filters.ricker` for `bg.filters.ormsby` or a custom array. |
| **Random noise** | Add `np.random.normal(0, σ, seis_time.shape)` before depth interpolation. |
| **Streamlit GUI** | Wrap key parameters (`dt`, `f`, sheet names) in sliders and run real-time. |

Pull requests and forks are welcome—please open an issue first if you plan a major change.

---

## 📝 Presentation Slide-Deck
`Mahmoud-Mohamed_Presentation.pdf` (8 slides) mirrors the script sections with graphics and equations—handy for rapid knowledge transfer in a classroom or team meeting.

---

## 🤝 Acknowledgements
- **IFP School** for academic guidance.  
- The **Bruges** open-source project for clean seismic utility functions.

---

## 📜 Licence
```
MIT © 2025 Mahmoud Mohamed
```
