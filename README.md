# PetroEval Dashboard & Well Log Estimator

A comprehensive petrophysical analysis toolkit and interactive **Streamlit** dashboard (**PetroEval Dashboard**) for well log evaluation, multi-method Shale Volume ($V_{shale}$) estimation, and porosity calculation.

---

## 🌟 Key Features

- **Petrophysical Calculation Engine (`petrophysics.py`)**:
  - **Shale Volume ($V_{shale}$)**: Linear Gamma Ray Index, Steiber non-linear model, Larionov (Young vs. Old formations), and Clavier models.
  - **Density Porosity ($\phi_d$ / PHID)**: Matrix-density corrected porosity from Bulk Density ($RHOB$).
  - **Sonic Porosity ($\phi_s$ / PHIS)**: Acoustic transit time ($\Delta t$) porosity via Wyllie time-average equation.
  - **Neutron-Density Combination Porosity ($\phi_{nd}$ / PHIND)**: Root-Mean-Square (RMS) total porosity.
  - **Effective Porosity ($\phi_e$ / PHIE)**: Total porosity corrected for clay-bound water fraction.

- **Interactive Streamlit Dashboard (`app.py` - PetroEval Dashboard)**:
  - **Single-Depth Inspector**: Target depth selection via numeric input or slider with real-time KPI metrics.
  - **Multi-Track Plotly Visualizer**: 4-track interactive well log suite with target depth reference marker line.
  - **$V_{shale}$ Method Comparison**: Side-by-side comparison of 5 shale volume estimation models.
  - **Porosity Breakdown & Crossplots**: Interactive Neutron-Density ($\phi_n$ vs. $\phi_d$) crossplot.
  - **Data Export**: Instant CSV download of all computed petrophysical properties.

- **Jupyter Notebook Suite (`Displaying a Well Plot with MatPlotLib.ipynb`)**:
  - Multi-track Matplotlib visualizer and script workflow for petrophysical analysis.

---

## 📁 Repository Structure

```
.
├── app.py                                   # Streamlit Web Dashboard (PetroEval Dashboard)
├── petrophysics.py                          # Core Petrophysical Calculation Library
├── Displaying a Well Plot with MatPlotLib.ipynb # Jupyter Notebook with pre-rendered results & plots
├── WellData.csv                             # Raw Well Log Dataset (GR, RHOB, NPHI, DT, DEPTH)
├── requirements.txt                         # Project Dependencies
├── LICENSE                                  # MIT License
└── README.md                                # Project Documentation
```

---

## 🚀 Quick Start & Installation

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/5AIhil/Log-Shale-Est.git
cd Log-Shale-Est

# Create virtual environment and activate
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch PetroEval Dashboard

Run the Streamlit application locally:

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser to interact with the dashboard.

---

## 📊 Sample Data & Input Parameters

| Curve | Description | Units |
|---|---|---|
| `DEPTH` | Well Depth | feet (ft) |
| `GR` | Gamma Ray Log | API units |
| `RHOB` | Bulk Density Log | g/cm³ |
| `NPHI` | Neutron Porosity Log | fraction |
| `DT` | Sonic Transit Time Log | μs/ft |

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
