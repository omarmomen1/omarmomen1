import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ==========================================
# 1. APP CONFIGURATION & INDUSTRIAL THEME
# ==========================================
st.set_page_config(page_title="HydraCalc Industrial", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

# Injecting a strictly industrial, light-mode, tab-less CSS design
st.markdown("""
<style>
    /* Clean, flat white background for a CAD-software feel */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    /* Sharp borders for inputs, removing the 'bubbly' Streamlit look */
    div[data-baseweb="input"] > div {
        border-radius: 0px !important;
        border: 1px solid #ced4da !important;
    }
    /* Monospace font for metrics to simulate engineering terminals */
    .metric-value {
        font-family: 'Courier New', Courier, monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #0d6efd;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6c757d;
        font-weight: 600;
    }
    /* Hide default watermarks */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .industrial-header {
        border-bottom: 3px solid #0d6efd;
        padding-bottom: 10px;
        margin-bottom: 30px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .industrial-header h1 {
        color: #212529;
        font-weight: 900;
        letter-spacing: -1px;
        margin: 0;
    }
    .industrial-header p {
        color: #495057;
        margin: 0;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="industrial-header">
    <h1>🏭 HydraCalc 1D | Piping Network Engine</h1>
    <p>Empirical Fluid Mechanics & Pump Selection System</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. FLUID & MATERIAL DATABASE
# ==========================================
FLUID_DB = {
    "Water (20°C)": {"rho": 998.2, "mu": 0.001002},
    "Water (80°C)": {"rho": 971.8, "mu": 0.000355},
    "Light Oil": {"rho": 880.0, "mu": 0.0350},
    "Heavy Crude": {"rho": 920.0, "mu": 0.4000}
}

MATERIAL_ROUGHNESS = {
    "Smooth PVC / Glass": 0.0015,
    "Commercial Steel": 0.045,
    "Galvanized Iron": 0.15,
    "Cast Iron": 0.26,
    "Concrete (Rough)": 1.5
}

# Minor loss coefficients (K-factors)
FITTINGS_DB = {
    "90° Standard Elbow": 0.75,
    "45° Standard Elbow": 0.35,
    "Gate Valve (Fully Open)": 0.15,
    "Globe Valve (Fully Open)": 10.0,
    "Swing Check Valve": 2.0
}

# ==========================================
# 3. GLOBAL INPUTS (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("### 💧 FLUID PROPERTIES")
    fluid_choice = st.selectbox("Operating Fluid", options=list(FLUID_DB.keys()))
    rho = FLUID_DB[fluid_choice]["rho"]
    mu = FLUID_DB[fluid_choice]["mu"]
    
    st.markdown("---")
    st.markdown("### ⚙️ SYSTEM DEMAND")
    flow_rate_m3h = st.number_input("Design Flow Rate (m³/hr)", min_value=0.1, value=50.0, step=5.0)
    # Convert to standard SI units (m^3/s) for calculations
    Q = flow_rate_m3h / 3600.0
    
    pump_eff = st.slider("Assumed Pump Efficiency (%)", 40, 90, 75) / 100.0

# ==========================================
# 4. NETWORK BUILDER (MAIN UI)
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 📐 PIPE GEOMETRY")
    with st.container(border=True):
        pipe_dia_mm = st.number_input("Internal Diameter (mm)", min_value=10.0, value=150.0, step=10.0)
        pipe_len_m = st.number_input("Total Straight Length (m)", min_value=1.0, value=100.0, step=1.0)
        mat_choice = st.selectbox("Pipe Material", options=list(MATERIAL_ROUGHNESS.keys()))
        elevation_change = st.number_input("Elevation Change (m)", value=5.0, help="Positive if pumping UP.")
        
        # Internal variables
        D = pipe_dia_mm / 1000.0
        L = pipe_len_m
        epsilon = MATERIAL_ROUGHNESS[mat_choice] / 1000.0

with col2:
    st.markdown("#### 🔧 MINOR LOSSES (FITTINGS)")
    with st.container(border=True):
        st.markdown("Specify the quantity of each fitting in the network.")
        fittings_counts = {}
        for fitting, k_val in FITTINGS_DB.items():
            fittings_counts[fitting] = st.number_input(f"{fitting} (K={k_val})", min_value=0, value=0, step=1)

# ==========================================
# 5. CORE MATHEMATICS ENGINE
# ==========================================
g = 9.81
Area = np.pi * (D / 2)**2
V = Q / Area

# Reynolds Number
Re = (rho * V * D) / mu

# Friction Factor (Haaland Equation for implicit Colebrook-White approximation)
if Re < 2300:
    flow_regime = "LAMINAR"
    f = 64.0 / Re if Re > 0 else 0
else:
    flow_regime = "TURBULENT"
    # Haaland Equation
    term1 = (epsilon / D) / 3.7
    term2 = 6.9 / Re
    f = (-1.8 * np.log10(term1**1.11 + term2))**-2

# Major Losses (Darcy-Weisbach)
h_major = f * (L / D) * (V**2 / (2 * g))

# Minor Losses
sum_K = sum([count * FITTINGS_DB[fitting] for fitting, count in fittings_counts.items()])
h_minor = sum_K * (V**2 / (2 * g))

# Total System Head (Friction + Fittings + Elevation)
h_total = h_major + h_minor + elevation_change

# Required Pump Power (Watts -> kW)
P_kw = (rho * g * Q * h_total) / (pump_eff * 1000.0)

# ==========================================
# 6. INDUSTRIAL DASHBOARD OUTPUT
# ==========================================
st.markdown("---")
st.markdown("#### 📊 SYSTEM CALCULATION RESULTS")

mc1, mc2, mc3, mc4 = st.columns(4)
mc1.markdown(f"<div class='metric-label'>Reynolds Number</div><div class='metric-value'>{Re:,.0f}</div><div style='color: #6c757d;'>{flow_regime}</div>", unsafe_allow_html=True)
mc2.markdown(f"<div class='metric-label'>Fluid Velocity</div><div class='metric-value'>{V:.2f} m/s</div>", unsafe_allow_html=True)
mc3.markdown(f"<div class='metric-label'>Total System Head</div><div class='metric-value'>{h_total:.2f} m</div>", unsafe_allow_html=True)
mc4.markdown(f"<div class='metric-label'>Req. Pump Power</div><div class='metric-value'>{P_kw:.2f} kW</div>", unsafe_allow_html=True)

# ==========================================
# 7. ADVANCED FEATURE: SYSTEM CURVE PLOTTING
# ==========================================
st.markdown("---")
st.markdown("#### 📈 PUMP SYSTEM CURVE")
st.markdown("Generates the specific System Resistance Curve ($H_{sys}$ vs $Q$) required for pump catalog selection.")

# Generate an array of flow rates from 0 up to 1.5x the design flow
q_array = np.linspace(0.001, Q * 1.5, 50)
v_array = q_array / Area
re_array = (rho * v_array * D) / mu

# Calculate friction factor array (ignoring transition zone complexities for the plot)
f_array = np.where(re_array < 2300, 64.0 / re_array, (-1.8 * np.log10(((epsilon/D)/3.7)**1.11 + 6.9/re_array))**-2)

# Calculate Head array
h_major_array = f_array * (L / D) * (v_array**2 / (2 * g))
h_minor_array = sum_K * (v_array**2 / (2 * g))
h_sys_array = h_major_array + h_minor_array + elevation_change

# Plotly Canvas
fig = go.Figure()

# Plot the continuous system curve
fig.add_trace(go.Scatter(
    x=q_array * 3600, # Convert back to m3/hr for the graph
    y=h_sys_array,
    mode='lines',
    name='System Resistance Curve',
    line=dict(color='#0d6efd', width=3)
))

# Plot the specific Design Point
fig.add_trace(go.Scatter(
    x=[flow_rate_m3h],
    y=[h_total],
    mode='markers+text',
    name='Design Point',
    text=['Design Operating Point'],
    textposition='top left',
    marker=dict(color='#dc3545', size=12, symbol='diamond')
))

fig.update_layout(
    xaxis_title="Flow Rate Q (m³/hr)",
    yaxis_title="System Head H (m)",
    plot_bgcolor='white',
    paper_bgcolor='#f8f9fa',
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e9ecef', zeroline=False),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e9ecef', zeroline=False),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig, use_container_width=True)