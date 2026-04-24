import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ==========================================
# 1. APP CONFIGURATION & CYBER THEME
# ==========================================
st.set_page_config(page_title="HydraCalc Nexus", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# Injecting Dark Mode / Neon Cyber CSS
st.markdown("""
<style>
    /* Dark cyber background */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    
    /* Neon accents for inputs */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        border: 1px solid #1e3a8a !important;
        color: #00f3ff !important;
        border-radius: 4px !important;
    }
    
    /* Glowing Monospace Metrics */
    .metric-value {
        font-family: 'Courier New', Courier, monospace;
        font-size: 2.2rem;
        font-weight: 800;
        color: #00f3ff;
        text-shadow: 0px 0px 10px rgba(0, 243, 255, 0.5);
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #9ca3af;
        font-weight: 600;
    }
    
    /* Hide default watermarks */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .cyber-header {
        border-bottom: 2px solid #00f3ff;
        padding-bottom: 10px;
        margin-bottom: 30px;
        box-shadow: 0px 10px 15px -10px rgba(0,243,255,0.2);
    }
    .cyber-header h1 {
        color: #ffffff;
        font-weight: 900;
        letter-spacing: 1px;
        margin: 0;
    }
    .cyber-header span {
        color: #00f3ff;
    }
    .cyber-header p {
        color: #9ca3af;
        margin: 0;
        font-weight: 400;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="cyber-header">
    <h1>⚡ HydraCalc <span>NEXUS</span></h1>
    <p>ADVANCED FLUID DYNAMICS & SYSTEM MODELING</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. FLUID & MATERIAL DATABASE
# ==========================================
FLUID_DB = {
    "Water (20°C)": {"rho": 998.2, "mu": 0.001002},
    "Water (80°C)": {"rho": 971.8, "mu": 0.000355},
    "Light Oil": {"rho": 880.0, "mu": 0.0350},
}

MATERIAL_ROUGHNESS = {
    "Smooth PVC / Glass": 0.0015,
    "Commercial Steel": 0.045,
    "Cast Iron": 0.26,
}

FITTINGS_DB = {
    "90° Standard Elbow": 0.75,
    "Gate Valve (Open)": 0.15,
    "Swing Check Valve": 2.0
}

# ==========================================
# 3. GLOBAL INPUTS (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ SYSTEM PARAMETERS")
    fluid_choice = st.selectbox("Operating Fluid", options=list(FLUID_DB.keys()))
    rho = FLUID_DB[fluid_choice]["rho"]
    mu = FLUID_DB[fluid_choice]["mu"]
    
    flow_rate_m3h = st.number_input("Design Flow Rate (m³/hr)", min_value=0.1, value=50.0, step=5.0)
    Q = flow_rate_m3h / 3600.0
    pump_eff = st.slider("Pump Efficiency (%)", 40, 90, 75) / 100.0

# ==========================================
# 4. NETWORK BUILDER (MAIN UI)
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 📐 GEOMETRY")
    pipe_dia_mm = st.number_input("Internal Diameter (mm)", min_value=10.0, value=150.0, step=10.0)
    pipe_len_m = st.number_input("Total Length (m)", min_value=1.0, value=100.0, step=1.0)
    mat_choice = st.selectbox("Pipe Material", options=list(MATERIAL_ROUGHNESS.keys()))
    elevation_change = st.number_input("Elevation Change (m)", value=5.0)
    
    D = pipe_dia_mm / 1000.0
    L = pipe_len_m
    epsilon = MATERIAL_ROUGHNESS[mat_choice] / 1000.0

with col2:
    st.markdown("#### 🔧 FITTINGS")
    fittings_counts = {}
    for fitting, k_val in FITTINGS_DB.items():
        fittings_counts[fitting] = st.number_input(f"{fitting} (K={k_val})", min_value=0, value=0, step=1)

# ==========================================
# 5. CORE MATHEMATICS ENGINE
# ==========================================
g = 9.81
Area = np.pi * (D / 2)**2
V = Q / Area
Re = (rho * V * D) / mu

if Re < 2300:
    flow_regime = "LAMINAR"
    f = 64.0 / Re if Re > 0 else 0
else:
    flow_regime = "TURBULENT"
    term1 = (epsilon / D) / 3.7
    term2 = 6.9 / Re
    f = (-1.8 * np.log10(term1**1.11 + term2))**-2

h_major = f * (L / D) * (V**2 / (2 * g))
sum_K = sum([count * FITTINGS_DB[fitting] for fitting, count in fittings_counts.items()])
h_minor = sum_K * (V**2 / (2 * g))
h_total = h_major + h_minor + elevation_change
P_kw = (rho * g * Q * h_total) / (pump_eff * 1000.0)

# ==========================================
# 6. CYBER DASHBOARD OUTPUT
# ==========================================
st.markdown("---")
mc1, mc2, mc3, mc4 = st.columns(4)
mc1.markdown(f"<div class='metric-label'>Reynolds Number</div><div class='metric-value'>{Re:,.0f}</div><div style='color: #ff0055;'>{flow_regime}</div>", unsafe_allow_html=True)
mc2.markdown(f"<div class='metric-label'>Fluid Velocity</div><div class='metric-value'>{V:.2f} m/s</div>", unsafe_allow_html=True)
mc3.markdown(f"<div class='metric-label'>Total System Head</div><div class='metric-value'>{h_total:.2f} m</div>", unsafe_allow_html=True)
mc4.markdown(f"<div class='metric-label'>Req. Pump Power</div><div class='metric-value'>{P_kw:.2f} kW</div>", unsafe_allow_html=True)

# ==========================================
# 7. NEW VISUAL: 2D PRESSURE GRADIENT MAP
# ==========================================
st.markdown("---")
st.markdown("#### 🌊 DIGITAL TWIN: PRESSURE GRADIENT")

# Generate grid for the pipe visual
x_grid = np.linspace(0, L, 50)
y_grid = np.linspace(-D/2, D/2, 20)
X, Y = np.meshgrid(x_grid, y_grid)

# Simulate pressure dropping linearly across the pipe length
# We use max pressure at inlet (h_total * rho * g) and 0 at outlet for visualization
P_inlet = h_total * rho * g / 1000 # kPa
Z_pressure = P_inlet * (1 - (X / L)) 

fig_pipe = go.Figure()

# Add the pressure heatmap inside the pipe
# Use a smoothed Heatmap instead of blocky Contours
fig_pipe.add_trace(go.Heatmap(
    z=Z_pressure, x=x_grid, y=y_grid,
    colorscale="Electric", 
    zsmooth="best", # This applies the buttery-smooth gradient blend
    colorbar=dict(
        title=dict(text="Pressure (kPa)", font=dict(color="#00f3ff")), 
        tickfont=dict(color="#e2e8f0"), # Lighter text for the numbers
        thickness=15
    ),
    name="Pressure Gradient"
))
# Draw the top and bottom pipe walls with neon lines
fig_pipe.add_trace(go.Scatter(x=[0, L], y=[D/2, D/2], mode='lines', line=dict(color='#ff0055', width=4), name='Pipe Wall'))
fig_pipe.add_trace(go.Scatter(x=[0, L], y=[-D/2, -D/2], mode='lines', line=dict(color='#ff0055', width=4), showlegend=False))

fig_pipe.update_layout(
    xaxis_title="Pipe Length (m)",
    yaxis_title="Diameter (m)",
    plot_bgcolor='#0b0f19',
    paper_bgcolor='#0b0f19',
    font=dict(color="#00f3ff"),
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(showgrid=True, gridcolor='#1e3a8a', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='#1e3a8a', zeroline=False, range=[-D, D]),
)
st.plotly_chart(fig_pipe, use_container_width=True)

# ==========================================
# 8. SYSTEM CURVE PLOTTING
# ==========================================
st.markdown("#### 📈 SYSTEM RESISTANCE CURVE")
q_array = np.linspace(0.001, Q * 1.5, 50)
v_array = q_array / Area
re_array = (rho * v_array * D) / mu
f_array = np.where(re_array < 2300, 64.0 / re_array, (-1.8 * np.log10(((epsilon/D)/3.7)**1.11 + 6.9/re_array))**-2)
h_sys_array = (f_array * (L / D) * (v_array**2 / (2 * g))) + (sum_K * (v_array**2 / (2 * g))) + elevation_change

fig_curve = go.Figure()
fig_curve.add_trace(go.Scatter(x=q_array * 3600, y=h_sys_array, mode='lines', name='System Curve', line=dict(color='#00f3ff', width=3)))
fig_curve.add_trace(go.Scatter(x=[flow_rate_m3h], y=[h_total], mode='markers+text', name='Design Point', text=['Target Op Point'], textposition='top left', marker=dict(color='#ff0055', size=12, symbol='diamond')))

fig_curve.update_layout(
    xaxis_title="Flow Rate Q (m³/hr)", yaxis_title="System Head H (m)",
    plot_bgcolor='#0b0f19', paper_bgcolor='#0b0f19', font=dict(color="#00f3ff"),
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(showgrid=True, gridcolor='#1e3a8a'), yaxis=dict(showgrid=True, gridcolor='#1e3a8a'),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)
st.plotly_chart(fig_curve, use_container_width=True)
