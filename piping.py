import streamlit as st
import numpy as np
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ==========================================
# 1. APP CONFIGURATION & ENTERPRISE LIGHT THEME
# ==========================================
st.set_page_config(page_title="HydraCalc Enterprise", page_icon="💧", layout="wide")

st.markdown("""
<style>
    /* Enterprise Light SaaS Background */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Clean inputs with focus states */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    
    /* Text colors inside inputs */
    input[type="number"], input[type="text"], div[data-baseweb="select"] span {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }
    
    /* Minimalist Header */
    .saas-header {
        padding-bottom: 1rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .saas-header h1 {
        color: #0f172a;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        font-size: 2.5rem;
    }
    .saas-header p {
        color: #64748b;
        margin-top: 0.2rem;
        font-weight: 500;
    }
    
    /* Metric Cards */
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2563eb; /* Primary Blue */
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Hide default watermarks */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="saas-header">
    <h1>💧 HydraCalc Enterprise</h1>
    <p>1D Piping Network Engine & Pump Selection</p>
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
MATERIAL_ROUGHNESS = {"Smooth PVC / Glass": 0.0015, "Commercial Steel": 0.045, "Cast Iron": 0.26}
FITTINGS_DB = {"90° Standard Elbow": 0.75, "Gate Valve (Open)": 0.15, "Swing Check Valve": 2.0}

# ==========================================
# 3. TOP RIBBON: GLOBAL PARAMETERS (No Sidebar)
# ==========================================
st.markdown("#### 1. System Parameters")
ribbon_1, ribbon_2, ribbon_3, ribbon_4 = st.columns(4)

with ribbon_1: fluid_choice = st.selectbox("Operating Fluid", options=list(FLUID_DB.keys()))
with ribbon_2: flow_rate_m3h = st.number_input("Design Flow Rate (m³/hr)", min_value=0.1, value=50.0, step=5.0)
with ribbon_3: pump_eff = st.number_input("Pump Efficiency (%)", min_value=10, max_value=100, value=75) / 100.0
with ribbon_4: elec_cost = st.number_input("Electricity Cost ($/kWh)", value=0.12, step=0.01)

rho = FLUID_DB[fluid_choice]["rho"]
mu = FLUID_DB[fluid_choice]["mu"]
Q = flow_rate_m3h / 3600.0

st.markdown("<br>", unsafe_allow_html=True) # Spacer

# ==========================================
# 4. MIDDLE SECTION: GEOMETRY & FITTINGS CARDS
# ==========================================
col_geo, col_fit = st.columns(2)

with col_geo:
    st.markdown("#### 2. Pipe Geometry")
    with st.container(border=True):
        g1, g2 = st.columns(2)
        pipe_dia_mm = g1.number_input("Internal Diameter (mm)", min_value=10.0, value=150.0, step=10.0)
        pipe_len_m = g2.number_input("Total Length (m)", min_value=1.0, value=100.0, step=1.0)
        mat_choice = g1.selectbox("Pipe Material", options=list(MATERIAL_ROUGHNESS.keys()))
        elevation_change = g2.number_input("Elevation Lift (m)", value=5.0)

with col_fit:
    st.markdown("#### 3. Fitting Inventory")
    with st.container(border=True):
        fittings_counts = {}
        f1, f2 = st.columns(2)
        keys = list(FITTINGS_DB.keys())
        for i, fitting in enumerate(keys):
            target_col = f1 if i % 2 == 0 else f2
            fittings_counts[fitting] = target_col.number_input(f"{fitting} (K={FITTINGS_DB[fitting]})", min_value=0, value=0, step=1)

D = pipe_dia_mm / 1000.0
L = pipe_len_m
epsilon = MATERIAL_ROUGHNESS[mat_choice] / 1000.0

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
    f = (-1.8 * np.log10(((epsilon / D) / 3.7)**1.11 + 6.9 / Re))**-2

h_major = f * (L / D) * (V**2 / (2 * g))
sum_K = sum([count * FITTINGS_DB[fitting] for fitting, count in fittings_counts.items()])
h_minor = sum_K * (V**2 / (2 * g))
h_total = h_major + h_minor + elevation_change
P_kw = (rho * g * Q * h_total) / (pump_eff * 1000.0)

# ==========================================
# 6. RESULTS DASHBOARD (Clean SaaS Look)
# ==========================================
st.markdown("---")
st.markdown("#### 📊 Performance Analytics")

with st.container(border=True):
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.markdown(f"<div class='metric-label'>Reynolds Number</div><div class='metric-value'>{Re:,.0f}</div><div style='color: #64748b; font-size: 0.85rem;'>{flow_regime}</div>", unsafe_allow_html=True)
    mc2.markdown(f"<div class='metric-label'>Fluid Velocity</div><div class='metric-value'>{V:.2f} <span style='font-size:1rem; color:#64748b;'>m/s</span></div>", unsafe_allow_html=True)
    mc3.markdown(f"<div class='metric-label'>Total System Head</div><div class='metric-value'>{h_total:.2f} <span style='font-size:1rem; color:#64748b;'>m</span></div>", unsafe_allow_html=True)
    mc4.markdown(f"<div class='metric-label'>Req. Pump Power</div><div class='metric-value'>{P_kw:.2f} <span style='font-size:1rem; color:#64748b;'>kW</span></div>", unsafe_allow_html=True)

# ==========================================
# 7. LIVE FLOW VISUALIZER (Light Theme)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)

pipe_height_px = max(60, min(250, int(D * 1000))) 
anim_duration_base = max(0.2, 2.0 / (V + 0.1)) 
particle_qty = int(max(30, min(200, Q * 6000)))

particle_animation = f"""
<style>
    .pipe-container {{
        width: 100%;
        height: {pipe_height_px}px;
        background: linear-gradient(to bottom, #f1f5f9, #ffffff, #f1f5f9);
        border-top: 4px solid #cbd5e1;
        border-bottom: 4px solid #cbd5e1;
        position: relative;
        overflow: hidden;
        border-radius: 2px;
        transition: height 0.4s ease-out;
    }}
    .particle {{
        position: absolute;
        background-color: #3b82f6; /* Water Blue */
        border-radius: 50%;
        opacity: 0.6;
        animation: flow linear infinite;
    }}
    @keyframes flow {{
        0% {{ left: -20px; opacity: 0; }}
        10% {{ opacity: 0.8; }}
        90% {{ opacity: 0.8; }}
        100% {{ left: 100%; opacity: 0; }}
    }}
</style>
<div class="pipe-container" id="pipe"></div>
<script>
    const pipe = document.getElementById('pipe');
    for(let i = 0; i < {particle_qty}; i++) {{
        let p = document.createElement('div');
        p.className = 'particle';
        let size = Math.random() * 8 + 4;
        p.style.width = size + 'px'; p.style.height = size + 'px';
        p.style.top = Math.random() * 90 + 5 + '%'; p.style.left = Math.random() * 100 + '%';
        p.style.animationDuration = (Math.random() * 0.5 * {anim_duration_base}) + {anim_duration_base} + 's';
        p.style.animationDelay = Math.random() * 2 + 's';
        pipe.appendChild(p);
    }}
</script>
"""
components.html(particle_animation, height=pipe_height_px + 20)

# ==========================================
# 8. VISUALIZATIONS (Light Theme Plotly)
# ==========================================
col_heat, col_curve = st.columns(2)

with col_heat:
    st.markdown("##### Pressure Gradient Map")
    x_grid, y_grid = np.linspace(0, L, 50), np.linspace(-D/2, D/2, 20)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z_pressure = (h_total * rho * g / 1000) * (1 - (X / L)) 
    
    fig_pipe = go.Figure()
    fig_pipe.add_trace(go.Heatmap(
        z=Z_pressure, x=x_grid, y=y_grid, colorscale="Blues", zsmooth="best", 
        colorbar=dict(title="kPa", thickness=10)
    ))
    fig_pipe.add_trace(go.Scatter(x=[0, L], y=[D/2, D/2], mode='lines', line=dict(color='#94a3b8', width=3), showlegend=False))
    fig_pipe.add_trace(go.Scatter(x=[0, L], y=[-D/2, -D/2], mode='lines', line=dict(color='#94a3b8', width=3), showlegend=False))
    
    fig_pipe.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=False, zeroline=False, range=[-D, D])
    )
    st.plotly_chart(fig_pipe, use_container_width=True)

with col_curve:
    st.markdown("##### Pump System Curve")
    q_array = np.linspace(0.001, Q * 1.5, 50)
    v_array = q_array / Area
    re_array = (rho * v_array * D) / mu
    f_array = np.where(re_array < 2300, 64.0 / re_array, (-1.8 * np.log10(((epsilon/D)/3.7)**1.11 + 6.9/re_array))**-2)
    h_sys_array = (f_array * (L / D) * (v_array**2 / (2 * g))) + (sum_K * (v_array**2 / (2 * g))) + elevation_change

    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(x=q_array * 3600, y=h_sys_array, mode='lines', name='System Curve', line=dict(color='#2563eb', width=3)))
    fig_curve.add_trace(go.Scatter(x=[flow_rate_m3h], y=[h_total], mode='markers', name='Design Point', marker=dict(color='#ef4444', size=10)))
    
    fig_curve.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        plot_bgcolor='#ffffff', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Flow Rate (m³/hr)"), 
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Head (m)"),
        showlegend=False
    )
    st.plotly_chart(fig_curve, use_container_width=True)
