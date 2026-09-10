import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import petrophysics as petro

# ---------------------------------------------------------
# Page Configuration & CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="PetroEval Dashboard",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS: Hides sidebar completely, removes gradients, uses solid dark background
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        font-family: 'DM Sans', sans-serif;
        background-color: #0b132b !important;
        color: #f8fafc !important;
    }
    
    /* Hide sidebar completely */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Hide top header toolbar */
    header[data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
    }
    
    .block-container {
        padding: 1.5rem 2rem 3rem !important;
        max-width: 1400px !important;
    }
    
    /* Header Container - Solid color background, no gradients */
    .app-header {
        background-color: #1c2541;
        border: 1px solid #3a506b;
        border-radius: 10px;
        padding: 1.25rem 1.8rem;
        margin-bottom: 1.25rem;
        color: #f8fafc;
    }
    .app-header h1 {
        font-size: 1.9rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
        color: #6fffe9;
    }
    .app-header p {
        font-size: 0.92rem;
        color: #94a3b8;
        margin: 0;
    }
    
    /* Top Depth Control Card - Solid background */
    .control-card {
        background-color: #1c2541;
        border: 1px solid #3a506b;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.25rem;
    }
    
    /* KPI Metric Cards - Solid dark slate color, no gradients */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 1rem;
        margin-bottom: 1.25rem;
    }
    .kpi-card {
        background-color: #1c2541;
        border: 1px solid #3a506b;
        border-radius: 10px;
        padding: 0.95rem 1.1rem;
        transition: border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #6fffe9;
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0.25rem 0;
    }
    .kpi-subtitle {
        font-size: 0.72rem;
        color: #6fffe9;
    }
    
    /* Solid color Badges */
    .badge {
        display: inline-block;
        padding: 0.18rem 0.55rem;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-blue { background-color: #1e3a8a; color: #60a5fa; border: 1px solid #2563eb; }
    .badge-amber { background-color: #78350f; color: #fbbf24; border: 1px solid #d97706; }
    .badge-green { background-color: #064e3b; color: #4ade80; border: 1px solid #16a34a; }
    .badge-purple { background-color: #581c87; color: #c084fc; border: 1px solid #9333ea; }
    
    /* Streamlit expander styling */
    .stExpander {
        background-color: #1c2541 !important;
        border: 1px solid #3a506b !important;
        border-radius: 10px !important;
        margin-bottom: 1.25rem !important;
    }
    
    /* Data table styling */
    .stDataFrame {
        border: 1px solid #3a506b;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Loader
# ---------------------------------------------------------
@st.cache_data
def load_well_data():
    df = pd.read_csv("WellData.csv", header=0)
    df = df.rename(columns=str.strip)
    df = df.replace(-999, np.nan)
    return df

df_raw = load_well_data()
depth_min = float(df_raw['DEPTH'].min())
depth_max = float(df_raw['DEPTH'].max())

# Auto-calculate default percentiles for GR baselines
default_gr_sand = float(np.round(np.percentile(df_raw['GR'].dropna(), 5), 2))
default_gr_shale = float(np.round(np.percentile(df_raw['GR'].dropna(), 95), 2))

# ---------------------------------------------------------
# App Header Banner (Solid dark theme, no gradients)
# ---------------------------------------------------------
st.markdown("""
<div class="app-header">
    <h1>🪵 PetroEval Dashboard</h1>
    <p>Interactive formation evaluation, multi-method Shale Volume (V<sub>shale</sub>) calculations, and depth-by-depth petrophysical log visualizer.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Top Control Section: Target Depth Selector & Parameters
# ---------------------------------------------------------
top_col1, top_col2 = st.columns([1, 2])

with top_col1:
    selected_depth = st.number_input(
        "🎯 Enter Target Depth (ft):",
        min_value=depth_min,
        max_value=depth_max,
        value=float(np.round((depth_min + depth_max) / 2.0, 1)),
        step=0.5
    )

with top_col2:
    selected_depth_slider = st.slider(
        "Navigate Depth Profile:",
        min_value=depth_min,
        max_value=depth_max,
        value=selected_depth,
        step=0.5
    )
    if selected_depth_slider != selected_depth:
        selected_depth = selected_depth_slider

# Expandable Parameters & Baselines Control Panel
with st.expander("⚙️ Calculation Parameters & Baselines", expanded=False):
    param_col1, param_col2, param_col3 = st.columns(3)
    
    with param_col1:
        st.markdown("##### 🧪 Gamma Ray Baselines")
        gr_sand = st.number_input("GR Sand Baseline (API):", value=default_gr_sand, step=1.0)
        gr_shale = st.number_input("GR Shale Baseline (API):", value=default_gr_shale, step=1.0)
        
    with param_col2:
        st.markdown("##### 🧱 Matrix & Fluid Properties")
        rho_ma = st.number_input("Matrix Density ρ_ma (g/cc):", value=2.65, step=0.01)
        rho_f = st.number_input("Fluid Density ρ_f (g/cc):", value=1.00, step=0.01)
        phi_shale = st.number_input("Shale Porosity φ_shale (frac):", value=0.10, step=0.01)

    with param_col3:
        st.markdown("##### ⏱️ Sonic Transit & Vsh Model")
        dt_ma = st.number_input("Matrix Transit Time Δt_ma (μs/ft):", value=55.5, step=0.5)
        dt_f = st.number_input("Fluid Transit Time Δt_f (μs/ft):", value=189.0, step=1.0)
        primary_vsh_method = st.selectbox(
            "Primary Vshale Model:",
            options=['linear', 'steiber', 'larionov_young', 'larionov_old', 'clavier'],
            index=0
        )

# ---------------------------------------------------------
# Petrophysical Calculations
# ---------------------------------------------------------
df_calc = df_raw.copy()

# Compute all Vshale methods
df_calc['VSH_linear'] = petro.calculate_vshale(df_calc['GR'], gr_sand, gr_shale, method='linear')
df_calc['VSH_steiber'] = petro.calculate_vshale(df_calc['GR'], gr_sand, gr_shale, method='steiber')
df_calc['VSH_larionov_young'] = petro.calculate_vshale(df_calc['GR'], gr_sand, gr_shale, method='larionov_young')
df_calc['VSH_larionov_old'] = petro.calculate_vshale(df_calc['GR'], gr_sand, gr_shale, method='larionov_old')
df_calc['VSH_clavier'] = petro.calculate_vshale(df_calc['GR'], gr_sand, gr_shale, method='clavier')

# Porosity calculations
if 'RHOB' in df_calc.columns:
    df_calc['PHID'] = petro.calculate_density_porosity(df_calc['RHOB'], rho_ma=rho_ma, rho_f=rho_f)
if 'DT' in df_calc.columns:
    df_calc['PHIS'] = petro.calculate_sonic_porosity(df_calc['DT'], dt_ma=dt_ma, dt_f=dt_f, method='wyllie')
if 'NPHI' in df_calc.columns and 'PHID' in df_calc.columns:
    df_calc['PHIND'] = petro.calculate_neutron_density_porosity(df_calc['NPHI'], df_calc['PHID'], method='rms')
if 'PHIND' in df_calc.columns:
    df_calc['PHIE'] = petro.calculate_effective_porosity(df_calc['PHIND'], df_calc['VSH_linear'], phi_shale=phi_shale)

# Get index & row for target depth
idx_target = (df_calc['DEPTH'] - selected_depth).abs().idxmin()
row = df_calc.loc[idx_target]
actual_depth = row['DEPTH']

# ---------------------------------------------------------
# Single Depth Petrophysical Inspection KPI Cards
# ---------------------------------------------------------
st.markdown(f"### 📍 Petrophysical Inspection at **{actual_depth:.2f} ft**")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Target Depth</div>
        <div class="kpi-value">{actual_depth:.1f} <span style="font-size:0.85rem">ft</span></div>
        <div class="kpi-subtitle"><span class="badge badge-blue">Selected</span></div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    vsh_val = row[f'VSH_{primary_vsh_method}'] * 100
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Vshale ({primary_vsh_method.split('_')[0].title()})</div>
        <div class="kpi-value">{vsh_val:.1f}%</div>
        <div class="kpi-subtitle"><span class="badge badge-amber">Shale Content</span></div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    phid_val = row['PHID'] * 100 if pd.notnull(row.get('PHID')) else 0.0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Density Porosity (PHID)</div>
        <div class="kpi-value">{phid_val:.1f}%</div>
        <div class="kpi-subtitle"><span class="badge badge-green">RHOB: {row['RHOB']:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    phis_val = row['PHIS'] * 100 if pd.notnull(row.get('PHIS')) else 0.0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Sonic Porosity (PHIS)</div>
        <div class="kpi-value">{phis_val:.1f}%</div>
        <div class="kpi-subtitle"><span class="badge badge-purple">DT: {row['DT']:.1f}</span></div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col5:
    phind_val = row['PHIND'] * 100 if pd.notnull(row.get('PHIND')) else 0.0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Porosity (PHIND)</div>
        <div class="kpi-value">{phind_val:.1f}%</div>
        <div class="kpi-subtitle"><span class="badge badge-blue">RMS Combination</span></div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col6:
    phie_val = row['PHIE'] * 100 if pd.notnull(row.get('PHIE')) else 0.0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Effective Porosity (PHIE)</div>
        <div class="kpi-value">{phie_val:.1f}%</div>
        <div class="kpi-subtitle"><span class="badge badge-green">Clay Corrected</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Multi-Tab Main Interface
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Multi-Track Log Visualizer",
    "⛰️ Vshale Calculations & Model Comparison",
    "📊 Porosity Breakdown",
    "📋 Data Explorer & Export"
])

# ---------------------------------------------------------
# TAB 1: Multi-Track Interactive Log Visualizer
# ---------------------------------------------------------
with tab1:
    st.markdown("#### Multi-Track Well Log Suite with Depth Reference Line")
    
    fig = make_subplots(
        rows=1, cols=4,
        shared_yaxes=True,
        horizontal_spacing=0.04,
        subplot_titles=[
            "Track 1: Gamma Ray (GR)",
            "Track 2: Shale Volume (Vshale)",
            "Track 3: Porosity Logs (NPHI, RHOB, DT)",
            "Track 4: Total & Effective Porosity"
        ]
    )
    
    # Track 1: Gamma Ray
    fig.add_trace(go.Scatter(x=df_calc['GR'], y=df_calc['DEPTH'], mode='lines', name='GR (API)', line=dict(color='#4ade80', width=1.5)), row=1, col=1)
    fig.add_vline(x=gr_sand, line_dash="dash", line_color="#10b981", annotation_text=f"Sand ({gr_sand})", row=1, col=1)
    fig.add_vline(x=gr_shale, line_dash="dash", line_color="#b45309", annotation_text=f"Shale ({gr_shale})", row=1, col=1)
    
    # Track 2: Vshale Models
    fig.add_trace(go.Scatter(x=df_calc['VSH_linear']*100, y=df_calc['DEPTH'], mode='lines', name='Vsh (Linear)', line=dict(color='#f87171', width=1.5)), row=1, col=2)
    fig.add_trace(go.Scatter(x=df_calc['VSH_steiber']*100, y=df_calc['DEPTH'], mode='lines', name='Vsh (Steiber)', line=dict(color='#60a5fa', width=1.5, dash='dash')), row=1, col=2)
    fig.add_trace(go.Scatter(x=df_calc['VSH_larionov_young']*100, y=df_calc['DEPTH'], mode='lines', name='Vsh (Larionov Young)', line=dict(color='#c084fc', width=1, dash='dot')), row=1, col=2)
    
    # Track 3: Porosity Logs
    fig.add_trace(go.Scatter(x=df_calc['PHID']*100, y=df_calc['DEPTH'], mode='lines', name='PHID (Density %)', line=dict(color='#f87171', width=1.2)), row=1, col=3)
    fig.add_trace(go.Scatter(x=df_calc['PHIS']*100, y=df_calc['DEPTH'], mode='lines', name='PHIS (Sonic %)', line=dict(color='#e879f9', width=1.2, dash='dash')), row=1, col=3)
    fig.add_trace(go.Scatter(x=df_calc['NPHI']*100, y=df_calc['DEPTH'], mode='lines', name='NPHI (Neutron %)', line=dict(color='#60a5fa', width=1.2, dash='dot')), row=1, col=3)
    
    # Track 4: Combo & Effective Porosity
    fig.add_trace(go.Scatter(x=df_calc['PHIND']*100, y=df_calc['DEPTH'], mode='lines', name='PHIND (Total %)', line=dict(color='#f8fafc', width=1.5)), row=1, col=4)
    fig.add_trace(go.Scatter(x=df_calc['PHIE']*100, y=df_calc['DEPTH'], mode='lines', name='PHIE (Effective %)', line=dict(color='#34d399', width=2)), row=1, col=4)
    
    # Highlight selected depth with horizontal reference line across all tracks
    for c in range(1, 5):
        fig.add_hline(y=actual_depth, line_color="#fbbf24", line_width=2, line_dash="solid", row=1, col=c)
        fig.update_yaxes(autorange="reversed", row=1, col=c, title_text="Depth (ft)" if c == 1 else "")
    
    # Track X ranges
    fig.update_xaxes(title_text="GR (API)", range=[0, 200], row=1, col=1)
    fig.update_xaxes(title_text="Vshale (%)", range=[0, 100], row=1, col=2)
    fig.update_xaxes(title_text="Porosity (%)", range=[50, 0], row=1, col=3)
    fig.update_xaxes(title_text="Porosity (%)", range=[50, 0], row=1, col=4)
    
    fig.update_layout(
        height=850,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#1c2541',
        font=dict(color='#94a3b8', family='DM Sans'),
        showlegend=True,
        legend=dict(orientation="h", y=-0.05, x=0.1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: Vshale Calculations Comparison
# ---------------------------------------------------------
with tab2:
    st.markdown("#### Comparison of Shale Volume (Vshale) Estimation Methods")
    
    vcol1, vcol2 = st.columns([1, 1])
    
    with vcol1:
        st.markdown(f"##### Vshale Values at Target Depth **{actual_depth:.2f} ft**")
        
        vsh_table = pd.DataFrame({
            "Calculation Method": [
                "Linear Gamma Ray Index",
                "Steiber Model (Non-linear)",
                "Larionov (Young / Soft Rocks)",
                "Larionov (Old / Mesozoic-Paleozoic)",
                "Clavier Model"
            ],
            "Vshale Fraction": [
                row['VSH_linear'],
                row['VSH_steiber'],
                row['VSH_larionov_young'],
                row['VSH_larionov_old'],
                row['VSH_clavier']
            ],
            "Vshale Percentage (%)": [
                row['VSH_linear'] * 100,
                row['VSH_steiber'] * 100,
                row['VSH_larionov_young'] * 100,
                row['VSH_larionov_old'] * 100,
                row['VSH_clavier'] * 100
            ]
        })
        
        st.dataframe(
            vsh_table.style.format({
                "Vshale Fraction": "{:.4f}",
                "Vshale Percentage (%)": "{:.2f}%"
            }),
            use_container_width=True
        )
        
        st.markdown("""
        **Method Comparison Notes:**
        - **Linear Index**: Direct linear relationship ($V_{sh} = I_{GR}$).
        - **Steiber Model**: Corrects linear overestimation for Tertiary rocks.
        - **Larionov Models**: Optimized for young (soft) vs. old (consolidated) formations.
        - **Clavier Model**: Standard non-linear model for shaly sand formations.
        """)
        
    with vcol2:
        st.markdown("##### Vshale Depth Profiles")
        fig_vsh = go.Figure()
        fig_vsh.add_trace(go.Scatter(x=df_calc['VSH_linear']*100, y=df_calc['DEPTH'], mode='lines', name='Linear', line=dict(color='#f87171')))
        fig_vsh.add_trace(go.Scatter(x=df_calc['VSH_steiber']*100, y=df_calc['DEPTH'], mode='lines', name='Steiber', line=dict(color='#60a5fa')))
        fig_vsh.add_trace(go.Scatter(x=df_calc['VSH_larionov_young']*100, y=df_calc['DEPTH'], mode='lines', name='Larionov (Young)', line=dict(color='#c084fc')))
        fig_vsh.add_trace(go.Scatter(x=df_calc['VSH_larionov_old']*100, y=df_calc['DEPTH'], mode='lines', name='Larionov (Old)', line=dict(color='#fbbf24')))
        fig_vsh.add_trace(go.Scatter(x=df_calc['VSH_clavier']*100, y=df_calc['DEPTH'], mode='lines', name='Clavier', line=dict(color='#34d399')))
        fig_vsh.add_hline(y=actual_depth, line_color="#fbbf24", line_width=2, annotation_text=f"{actual_depth:.1f} ft")
        
        fig_vsh.update_yaxes(autorange="reversed", title_text="Depth (ft)")
        fig_vsh.update_xaxes(title_text="Vshale (%)", range=[0, 100])
        fig_vsh.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#1c2541',
            font=dict(color='#94a3b8', family='DM Sans'),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_vsh, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: Porosity Breakdown & Crossplots
# ---------------------------------------------------------
with tab3:
    st.markdown("#### Porosity Analysis & Neutron-Density Crossplot")
    
    pcol1, pcol2 = st.columns([1, 1])
    
    with pcol1:
        st.markdown(f"##### Porosity Log Readings at **{actual_depth:.2f} ft**")
        poro_summary = pd.DataFrame({
            "Porosity Parameter": [
                "Density Porosity (PHID)",
                "Sonic Porosity (PHIS)",
                "Neutron Porosity (NPHI)",
                "Total Combo Porosity (PHIND)",
                "Effective Porosity (PHIE)"
            ],
            "Value (Fraction)": [
                row.get('PHID', np.nan),
                row.get('PHIS', np.nan),
                row.get('NPHI', np.nan),
                row.get('PHIND', np.nan),
                row.get('PHIE', np.nan)
            ],
            "Percentage (%)": [
                row.get('PHID', 0)*100,
                row.get('PHIS', 0)*100,
                row.get('NPHI', 0)*100,
                row.get('PHIND', 0)*100,
                row.get('PHIE', 0)*100
            ]
        })
        st.dataframe(
            poro_summary.style.format({
                "Value (Fraction)": "{:.4f}",
                "Percentage (%)": "{:.2f}%"
            }),
            use_container_width=True
        )
        
    with pcol2:
        st.markdown("##### Neutron-Density Porosity Crossplot")
        fig_xp = go.Figure()
        fig_xp.add_trace(go.Scatter(
            x=df_calc['NPHI'],
            y=df_calc['PHID'],
            mode='markers',
            marker=dict(
                size=5,
                color=df_calc['VSH_linear']*100,
                colorscale='YlOrBr',
                colorbar=dict(title="Vshale (%)"),
                showscale=True
            ),
            name="Well Log Points"
        ))
        
        # Highlight selected depth point
        fig_xp.add_trace(go.Scatter(
            x=[row['NPHI']],
            y=[row['PHID']],
            mode='markers',
            marker=dict(size=14, color='#f87171', symbol='star'),
            name=f"Depth {actual_depth:.1f} ft"
        ))
        
        # 1:1 Reference Line
        fig_xp.add_trace(go.Scatter(
            x=[0, 0.45], y=[0, 0.45],
            mode='lines',
            line=dict(color='#64748b', dash='dash'),
            name='1:1 Sandstone Line'
        ))
        
        fig_xp.update_xaxes(title_text="Neutron Porosity NPHI (frac)", range=[-0.05, 0.45])
        fig_xp.update_yaxes(title_text="Density Porosity PHID (frac)", range=[-0.05, 0.45])
        fig_xp.update_layout(
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#1c2541',
            font=dict(color='#94a3b8', family='DM Sans'),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_xp, use_container_width=True)

# ---------------------------------------------------------
# TAB 4: Data Explorer & CSV Export
# ---------------------------------------------------------
with tab4:
    st.markdown("#### Petrophysical Data Explorer")
    
    st.markdown("##### Filter around Target Depth")
    depth_window = st.slider("Depth Window Around Target Depth (ft):", min_value=10, max_value=200, value=50, step=10)
    
    filtered_df = df_calc[
        (df_calc['DEPTH'] >= actual_depth - depth_window) &
        (df_calc['DEPTH'] <= actual_depth + depth_window)
    ]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    csv_data = df_calc.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Calculated Dataset (CSV)",
        data=csv_data,
        file_name="petrophysical_eval_results.csv",
        mime="text/csv"
    )
