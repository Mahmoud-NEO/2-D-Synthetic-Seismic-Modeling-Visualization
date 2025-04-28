# 2-D-Synthetic-Seismic-Modeling-Visualization
A complete Python workflow for generating time- and depth-domain seismic sections from velocity-density grids

📑 Project Overview
This project turns a pair of 2-D velocity (VP) and density (RHOB) grids into synthetic seismic sections.
It was built as a coursework project at IFP School to demonstrate how each link in the seismic forward-modeling chain works, from raw property grids to final wiggles in both time and depth.

<p align="center"> <img src="docs/img/final_2x2_grid.png" width="700"> </p>
Key Objectives
Compute acoustic impedance & reflection coefficients directly from cell-based velocity and density.

Convert depth to two-way time (TWT) and map every RC value onto a uniform time grid.

Generate synthetic seismic by convolving the RC series with a Ricker wavelet.

Back-interpolate the seismic from time to depth to visualise reflectors in geological space.

Publish clean, reproducible code together with a concise presentation explaining each step.

🗂️ Repository Structure
bash
Copy
Edit
.
├── Mahmoud_FINAL.py          # Main script – end-to-end workflow
├── data2D.xlsx               # X, Y, VP, RHOB grids (sample data)
├── Mahmoud-Mohamed_Presentation.pdf
├── docs
│   └── img
│       └── final_2x2_grid.png
└── README.md                 # (this file)
🔬 Methodology

Step	Description	Core Functions
1	Data loading – read X, Y, velocity and density from Excel into NumPy arrays.	pandas.read_excel
2	Acoustic Impedance (AI) – convert units and compute AI = VP × RHOB.	NumPy vector ops
3	Reflection Coefficients (RC) – finite-difference formula on AI grid.	array slicing
4	Two-Way Time (TWT) – cumulative sum of Δz / VP per trace.	custom loop
5	Uniform time grid – map each RC to nearest sample on a global time axis.	np.argmin
6	Wavelet convolution – Ricker wavelet (4 kHz) ➜ convolve with RC series.	bruges.filters.ricker, np.convolve
7	Time-to-depth conversion – interpolate seismic back onto depth grid.	scipy.interpolate.interp1d
8	Plotting – 2 × 2 grid: AI, RC(time), seismic(time), seismic(depth).	matplotlib
🚀 Quick-Start
Clone repo & install deps

bash
Copy
Edit
git clone <repo_url>
cd seismic-2D
pip install numpy pandas matplotlib scipy bruges openpyxl
Run the workflow

bash
Copy
Edit
python Mahmoud_FINAL.py
The script prints data shapes, plots the 2 × 2 figure and saves it to docs/img.

Swap in your own data
Replace data2D.xlsx with a file containing X, Y, velocity and density sheets named exactly:
X, Y, VPH_export, RHOB_export.

✨ Features
Self-contained: no proprietary software; pure Python & open-source libraries.

Adaptive sampling: global TWT pick ensures the wavelet length always covers the section.

Depth & time views: instant sanity check of reflector positions after conversion.

Easily extendable: plug in different wavelets, frequencies or 3-D volumes.

📈 Results
Global max TWT reported for QC.

Uniform time axis printed for reproducibility.

Final figure summarises the entire forward model at a glance.

📄 Presentation
The accompanying PDF (Mahmoud-Mohamed_Presentation.pdf) walks through:

Data loading logic

TWT derivation

RC mapping onto time grid

Wavelet convolution process

Depth conversion & final plots

Use it as a teaching aid or quick refresher on the code.

🤝 Acknowledgements
IFP School faculty for guidance.

Bruges library for simple seismic wavelet generation.

🛈 Licence
This repository is released under the MIT License – free to use, modify, and distribute with attribution.

Happy modeling!







