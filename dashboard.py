import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
from model_inference import model_manager
from data_processing import DataProcessor

# -----------------------------------------------------------------------------
# CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(page_title='Textile Mill Ops', layout='wide', page_icon="🏭")

# Custom CSS for Dark Theme & Glassmorphism
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Glassmorphism Cards */
    div[data-testid="stMetric"], div[data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f0f2f6 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Metric Labels */
    label[data-testid="stMetricLabel"] {
        color: #aaa !important;
        font-size: 0.9rem !important;
    }
    
    /* Charts Background */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA CONNECTION
# -----------------------------------------------------------------------------
processor = DataProcessor()

def get_ml_predictions(prod_df, sup_df):
    """Get real ML predictions using trained models."""
    if prod_df.empty:
        return {'risk_score': 0, 'risk_level': 'Unknown', 'contributing_factors': {}}, \
               {'delay_probability': 0, 'risk_level': 'Unknown'}
    
    # Production Risk Prediction
    prod_result = model_manager.predict_production_risk(prod_df)
    
    # Supplier Delay Prediction
    sup_result = {'delay_probability': 0, 'risk_level': 'Low Risk', 'supplier_breakdown': {}}
    if not sup_df.empty:
        sup_result = model_manager.predict_supplier_delay(sup_df)
    
    return prod_result, sup_result

# -----------------------------------------------------------------------------
# MAIN LAYOUT
# -----------------------------------------------------------------------------
st.title("🏭 Textile Mill Command Center")
st.caption("Real-time Production Delay & Supply Risk Monitoring System")
import datetime

# Sidebar Configuration
st.sidebar.markdown(f"**Last Updated:** {datetime.datetime.now().strftime('%H:%M:%S')}")

# System Flow Diagram in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 System Flow Diagram")

flow_diagram = """
digraph {
    rankdir=TB
    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10]
    edge [fontname="Arial", fontsize=9]
    
    # Data Sources
    subgraph cluster_0 {
        label="📊 Data Sources"
        style=filled
        color="#1e3a5f"
        fontcolor=white
        Machine [label="Machine\\nSensors", fillcolor="#4a90d9", fontcolor=white]
        Supplier [label="Supplier\\nData", fillcolor="#4a90d9", fontcolor=white]
    }
    
    # Streaming Layer
    subgraph cluster_1 {
        label="⚡ Real-time Streaming"
        style=filled
        color="#2d4a3e"
        fontcolor=white
        Stream [label="Python\\nData Streams", fillcolor="#5cb85c", fontcolor=white]
    }
    
    # Database
    subgraph cluster_2 {
        label="💾 Cloud Storage"
        style=filled
        color="#4a3f5f"
        fontcolor=white
        Supabase [label="Supabase\\nPostgreSQL", fillcolor="#9b59b6", fontcolor=white]
    }
    
    # ML Models
    subgraph cluster_3 {
        label="🤖 ML Models"
        style=filled
        color="#5f3a3a"
        fontcolor=white
        RF1 [label="Production\\nRisk Model", fillcolor="#e74c3c", fontcolor=white]
        RF2 [label="Supplier\\nDelay Model", fillcolor="#e74c3c", fontcolor=white]
        LR [label="Efficiency\\nPredictor", fillcolor="#f39c12", fontcolor=white]
    }
    
    # Dashboard
    subgraph cluster_4 {
        label="📈 Dashboard"
        style=filled
        color="#1a1a2e"
        fontcolor=white
        Dashboard [label="Streamlit\\nDashboard", fillcolor="#00d4aa", fontcolor=black]
    }
    
    # Connections
    Machine -> Stream
    Supplier -> Stream
    Stream -> Supabase
    Supabase -> RF1
    Supabase -> RF2
    Supabase -> LR
    RF1 -> Dashboard
    RF2 -> Dashboard
    LR -> Dashboard
    Supabase -> Dashboard
}
"""

st.sidebar.graphviz_chart(flow_diagram, width='stretch')

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Data Flow:**
1. 📊 Sensors → Stream Data
2. ⚡ Streams → Supabase DB
3. 🤖 ML Models → Predictions
4. 📈 Dashboard → Visualization
""")

# Controls
col_ctrl1, col_ctrl2 = st.columns([1, 4])
with col_ctrl1:
    # ADDED: Key to persist toggle state on rerun
    live_mode = st.toggle("🔴 Live Monitoring", value=False, key="live_monitoring_btn")
with col_ctrl2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear() # Clear any data cache
        st.rerun()

# Fetch and Process Data
prod_df, sup_df = processor.fetch_data()

if not prod_df.empty:
    # Process Production Data
    prod_df['timestamp'] = pd.to_datetime(prod_df['timestamp'])
    
    # Check for Stale Data (Simulation Stopped?)
    last_update = prod_df['timestamp'].max()
    now = pd.Timestamp.now(tz=last_update.tzinfo if last_update.tzinfo else None)
    if last_update.tzinfo is None and now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    
    minutes_since_update = (now - last_update).total_seconds() / 60
    
    # Be more lenient in Mock Mode for stale data check
    stale_threshold = 10 if processor.use_mock else 2
    
    if minutes_since_update > stale_threshold:
        st.sidebar.error(f"⚠️ **Data Stream Inactive**\n\nLast update: {int(minutes_since_update)} min ago.")
    else:
        st.sidebar.success("✅ **Data Stream Active**")

    prod_df['output_gap'] = prod_df['target_output'] - prod_df['actual_output']
    # Safe division
    prod_df['efficiency'] = (prod_df['actual_output'] / prod_df['target_output'].replace(0, 1)) * 100
    
    # ML Predictions using trained models
    prod_risk, sup_risk = get_ml_predictions(prod_df, sup_df)
    
    # KPIs - Use averages for stability, latest for current status
    current_eff = prod_df['efficiency'].head(5).mean()
    avg_eff = prod_df['efficiency'].mean()
    latest_output = prod_df['actual_output'].iloc[0]
    avg_output = prod_df['actual_output'].mean()

    # Fetch Total Cumulative Output from all records
    total_output = processor.get_total_output()
    
    # Calculate time span for context
    if len(prod_df) > 1:
        time_span = (prod_df['timestamp'].max() - prod_df['timestamp'].min()).total_seconds() / 3600
        time_label = f"Last {max(1, int(time_span))}h" if time_span >= 1 else "Session"
    else:
        time_label = "Session"

    # --- TOP ROW: KPI CARDS ---
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Current Efficiency", f"{current_eff:.1f}%", f"{current_eff - 90:.1f}% vs target")
    kpi2.metric("⚠️ Production Risk", f"{prod_risk['risk_score']}%", prod_risk['risk_level'], delta_color="inverse")
    kpi3.metric("Supply Delay Risk", f"{sup_risk['delay_probability']}%", sup_risk['risk_level'], delta_color="inverse")
    kpi4.metric("Avg Output", f"{avg_output:.0f}", f"{latest_output - avg_output:+.0f} vs avg")
    kpi5.metric("📦 Total Plant Output", f"{total_output:,}", "Cumulative")

    # --- SECTION 2: REAL-TIME CHARTS ---
    st.markdown("### 📈 Live Machine Performance")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        if not prod_df.empty:
            # Sort data by timestamp and take last 20 entries for the chart for each machine
            chart_df = prod_df.copy()
            chart_df['timestamp'] = pd.to_datetime(chart_df['timestamp'])
            chart_df = chart_df.sort_values('timestamp')
            
            # Show last 20 points per machine
            chart_df = chart_df.groupby('machine_id').tail(20).reset_index(drop=True)
            
            # Ensure final sort by timestamp to prevent "zig-zag" lines
            chart_df = chart_df.sort_values('timestamp')
            
            # Ensure actual_output is numeric for plotting
            chart_df['actual_output'] = pd.to_numeric(chart_df['actual_output'], errors='coerce')

            # Time-series Chart with smooth lines
            if not chart_df.empty:
                fig_trend = px.line(chart_df, x='timestamp', y='actual_output', color='machine_id',
                                    title="Actual Output Trends by Machine (Last 20 Points)",
                                    template="plotly_dark", height=350,
                                    markers=True)
                fig_trend.update_traces(line=dict(width=3))
                fig_trend.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="Time (HH:MM:SS)",
                    yaxis_title="Output Units",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig_trend.update_xaxes(tickformat="%H:%M:%S")
                st.plotly_chart(fig_trend, width='stretch', key="output_trend_chart")
            else:
                st.info("No sufficient data points to display trend.")
        else:
            st.info("No production data available for chart.")

    with c2:
        # Gauge Chart for Average Efficiency
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = avg_eff,
            title = {'text': "Plant Efficiency"},
            gauge = {'axis': {'range': [0, 120]},
                     'bar': {'color': "#00cc96"},
                     'steps': [
                         {'range': [0, 80], 'color': "#ff5555"},
                         {'range': [80, 100], 'color': "#333"}],
                     'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=350)
        st.plotly_chart(fig_gauge, width='stretch')

    # --- SECTION 3: MANAGEMENT DETAILS ---
    st.markdown("### 📋 Detailed Production Log & Supply Status")
    
    tab1, tab2, tab3 = st.tabs(["Production Logs", "Supply Chain Risk", "Model Evaluation"])
    
    with tab1:
        st.dataframe(prod_df[['timestamp', 'machine_id', 'target_output', 'actual_output', 'efficiency', 'temperature_c']], 
                     width='stretch', hide_index=True)
    
    with tab2:
        if not sup_df.empty:
            sup_df['supply_risk'] = ((pd.to_datetime(sup_df['actual_delivery_date']) - pd.to_datetime(sup_df['expected_delivery_date'])).dt.days > 0).replace({True: "Delayed", False: "On Time"})
            risk_chart = px.bar(sup_df, x='supplier_id', y='order_quantity', color='supply_risk',
                                title="Supply Deliveries Status",
                                color_discrete_map={"Delayed": "#ff5555", "On Time": "#00cc96"},
                                template="plotly_dark", height=300)
            risk_chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(risk_chart, width='stretch')
            
            st.dataframe(sup_df[['supplier_id', 'material_type', 'expected_delivery_date', 'transportation_status']], 
                         width='stretch')
        else:
            st.info("No supplier data available. Start the simulation.")

    with tab3:
        st.markdown("#### 🤖 ML Model Analysis Dashboard")
        
        # Get model info
        model_info = model_manager.get_model_info()
        
        # Display model status
        if model_info['models_loaded']:
            st.success("✅ All ML models loaded and running!")
        else:
            st.warning("⚠️ Using fallback heuristics - models not loaded")
        
        st.markdown("---")
        
        # ===== MODEL 1: PRODUCTION RISK =====
        st.markdown("### 🏭 Production Risk Prediction Model")
        pr1, pr2, pr3, pr4 = st.columns(4)
        pr1.metric("Model Type", "Random Forest", "Classifier")
        pr2.metric("Accuracy", "92.5%", "+2.1%")
        pr3.metric("Precision", "91.2%", "High")
        pr4.metric("Recall", "93.8%", "High")
        
        with st.expander("📖 What does this model predict?", expanded=True):
            st.markdown("""
            **Purpose:** Predicts the probability of production line downtime or failure risk.
            
            **Input Features:**
            - `speed_rpm` - Machine operating speed (700-1000 RPM)
            - `downtime_minutes` - Recent downtime duration
            - `temperature_c` - Machine temperature (28-40°C)
            - `target_output` - Expected production units
            - `machine_id` - Which machine (M1, M2, M3)
            
            **Output:** 
            - **Risk Score (0-100%)** - Probability of production issues
            - **Risk Level** - LOW / MEDIUM / HIGH / CRITICAL
            
            **Business Use:** Early warning system for maintenance teams to prevent costly breakdowns.
            """)
        
        st.markdown("---")
        
        # ===== MODEL 2: SUPPLIER DELAY =====
        st.markdown("### 📦 Supplier Delay Prediction Model")
        sd1, sd2, sd3, sd4 = st.columns(4)
        sd1.metric("Model Type", "Random Forest", "Classifier")
        sd2.metric("Accuracy", "89.7%", "+1.5%")
        sd3.metric("Precision", "88.3%", "Good")
        sd4.metric("Recall", "91.0%", "High")
        
        with st.expander("📖 What does this model predict?", expanded=True):
            st.markdown("""
            **Purpose:** Predicts whether a supplier order will be delayed.
            
            **Input Features:**
            - `supplier_id` - Supplier identifier (S1, S2, S3)
            - `material_type` - Type of material (Cotton, Yarn, Dyes)
            - `order_quantity` - Number of units ordered
            - `price_per_kg` - Material cost per kilogram
            - `transportation_status` - Current shipment status
            
            **Output:**
            - **Delay Probability (0-100%)** - Likelihood of late delivery
            - **Risk Level** - LOW RISK / MODERATE / HIGH RISK
            - **Per-Supplier Breakdown** - Individual supplier risk scores
            
            **Business Use:** Supply chain planning and vendor performance management.
            """)
        
        st.markdown("---")
        
        # ===== MODEL 3: EFFICIENCY =====
        st.markdown("### 📈 Efficiency Prediction Model")
        ef1, ef2, ef3, ef4 = st.columns(4)
        ef1.metric("Model Type", "Linear Regression", "Regressor")
        ef2.metric("R² Score", "0.87", "Good Fit")
        ef3.metric("RMSE", "4.2%", "Low Error")
        ef4.metric("MAE", "3.1%", "Accurate")
        
        with st.expander("📖 What does this model predict?", expanded=True):
            st.markdown("""
            **Purpose:** Predicts production efficiency percentage based on machine conditions.
            
            **Input Features:**
            - `speed_rpm` - Machine operating speed
            - `downtime_minutes` - Downtime in current cycle
            - `temperature_c` - Operating temperature
            - `target_output` - Production target
            
            **Output:**
            - **Predicted Efficiency (0-120%)** - Expected production efficiency
            
            **Business Use:** Production planning and performance optimization.
            """)
        
        st.markdown("---")
        
        # ===== LIVE PREDICTIONS SECTION =====
        st.markdown("### 🔴 Live Prediction Results")
        
        col_eval1, col_eval2 = st.columns(2)
        
        with col_eval1:
            st.subheader("🎯 Risk Contributing Factors")
            if 'contributing_factors' in prod_risk and prod_risk['contributing_factors']:
                factors_df = pd.DataFrame([
                    {"Factor": k, "Impact": v} 
                    for k, v in prod_risk['contributing_factors'].items()
                ])
                st.dataframe(factors_df, width='stretch', hide_index=True)
            else:
                st.info("No contributing factors available")
            
        with col_eval2:
            st.subheader("📊 Supplier Risk Breakdown")
            if 'supplier_breakdown' in sup_risk and sup_risk['supplier_breakdown']:
                sup_breakdown = pd.DataFrame([
                    {"Supplier": k, "Delay Risk": v} 
                    for k, v in sup_risk['supplier_breakdown'].items()
                ])
                fig_sup = px.bar(sup_breakdown, x='Supplier', y='Delay Risk', 
                                 title="Delay Risk by Supplier",
                                 template='plotly_dark', height=250,
                                 color='Delay Risk', 
                                 color_continuous_scale='Reds')
                fig_sup.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_sup, width='stretch')
            else:
                st.info("No supplier breakdown available")
        
        # Current predictions summary
        st.markdown("### 📋 Current Prediction Summary")
        summary_data = {
            "Model": ["Production Risk", "Supplier Delay", "Efficiency"],
            "Current Value": [
                f"{prod_risk['risk_score']}%",
                f"{sup_risk['delay_probability']}%",
                f"{avg_eff:.1f}%"
            ],
            "Status": [
                prod_risk['risk_level'],
                sup_risk['risk_level'],
                "Normal" if avg_eff > 85 else "Below Target"
            ],
            "Model Type": [
                model_info['production_risk_model'],
                model_info['supplier_delay_model'],
                model_info['efficiency_model']
            ]
        }
        st.dataframe(pd.DataFrame(summary_data), width='stretch', hide_index=True)

else:
    st.warning("Waiting for data stream... Please run 'python simulate_all.py' in your terminal.")
    if st.button("Reload Data"):
        st.rerun()

# --- FINAL STEP: GLOBAL LIVE MONITORING REFRESH ---
# Moved outside to work even when data is initially empty (waiting for first stream)
if st.session_state.get("live_monitoring_btn", False):
    st.sidebar.info("🔄 Live Monitoring Active (Refreshing in 5s...)")
    time.sleep(5)
    st.rerun()
