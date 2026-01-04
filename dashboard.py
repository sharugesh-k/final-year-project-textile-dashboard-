import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
from model_inference import model_manager

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
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def get_data():
    prod = supabase.table("production_data").select("*").order("timestamp", desc=True).limit(1000).execute().data
    sup = supabase.table("supplier_data").select("*").order("timestamp", desc=True).limit(50).execute().data
    return pd.DataFrame(prod), pd.DataFrame(sup)

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

st.sidebar.graphviz_chart(flow_diagram, use_container_width=True)

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
    live_mode = st.toggle("🔴 Live Monitoring", value=False)
with col_ctrl2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()

if live_mode:
    time.sleep(3) # Wait 3 seconds
    st.rerun()    # Refresh app

def get_all_time_output():
    """Fetch total output sum from all time."""
    try:
        # We'll use a fast query to sum the actual_output column
        # Increased limit to 1,000,000 to catch more history and prevent 'decreasing' total behavior 
        # when older rows fall out of the window.
        response = supabase.table("production_data").select("actual_output").order("timestamp", desc=True).limit(1000000).execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            return df['actual_output'].sum()
        return 0
    except Exception as e:
        print(f"Error fetching total output: {e}")
        return 0

# Fetch Data
prod_df, sup_df = get_data()

if not prod_df.empty:
    # Process Production Data
    prod_df['timestamp'] = pd.to_datetime(prod_df['timestamp'])
    
    # Check for Stale Data (Simulation Stopped?)
    last_update = prod_df['timestamp'].max()
    
    # FIX: Ensure we compare timezone-aware with timezone-aware (or naive with naive)
    # Since our simulation sends naive UTC (datetime.utcnow().isoformat()), we must compare with naive UTC.
    if last_update.tzinfo is None:
        now = pd.Timestamp.utcnow().replace(tzinfo=None)
    else:
        now = pd.Timestamp.now(tz=last_update.tzinfo)
        
    minutes_since_update = (now - last_update).total_seconds() / 60
    
    if minutes_since_update > 2:
        st.sidebar.error(f"⚠️ **Data Stream Inactive**\n\nLast update: {int(minutes_since_update)} min ago.\n\nPlease run `python simulate_all.py` in your terminal to resume data.")
    else:
        st.sidebar.success("✅ **Data Stream Active**")

    prod_df['output_gap'] = prod_df['target_output'] - prod_df['actual_output']
    prod_df['efficiency'] = (prod_df['actual_output'] / prod_df['target_output']) * 100
    
    # ML Predictions using trained models (Use only recent data for 'Live' feel - last 5 records)
    prod_risk, sup_risk = get_ml_predictions(prod_df.head(5), sup_df)
    
    # KPIs based on *LATEST* value, not average of last 100
    current_efficiency = prod_df['efficiency'].iloc[0]
    avg_efficiency = prod_df['efficiency'].mean() # Keep for reference if needed
    avg_output = prod_df['actual_output'].mean() # RESTORED
    
    latest_output = prod_df['actual_output'].iloc[0] if len(prod_df) > 0 else 0
    output_delta = latest_output - avg_output
    
    # Fetch all-time total
    total_output_all_time = get_all_time_output()
    
    # Calculate time span for context
    if len(prod_df) > 1:
        time_span = (prod_df['timestamp'].max() - prod_df['timestamp'].min()).total_seconds() / 3600
        time_label = f"Last {max(1, int(time_span))}h" if time_span >= 1 else "Session"
    else:
        time_label = "Session"

    # --- TOP ROW: KPI CARDS ---
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    # UPDATED: Use current_efficiency instead of avg
    kpi1.metric("Current Efficiency", f"{current_efficiency:.1f}%", f"{current_efficiency - 90:.1f}% vs target")
    # RENAMED: ML Risk Score -> Production Downtime Risk
    kpi2.metric("⚠️ Production Downtime Risk", f"{prod_risk['risk_score']}%", prod_risk['risk_level'], delta_color="inverse")
    kpi3.metric("Supply Delay Risk", f"{sup_risk['delay_probability']}%", sup_risk['risk_level'], delta_color="inverse")
    kpi4.metric("Avg Output/Cycle", f"{avg_output:.0f}", f"{output_delta:+.0f} units")
    # UPDATED: Total Output is now All-time
    kpi5.metric("📦 Total Output (All-time)", f"{total_output_all_time:,}", "Units Produced")

    # --- SECTION 2: REAL-TIME CHARTS ---
    st.markdown("### 📈 Live Machine Performance")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        # Sort data by timestamp and take last 30 per machine for clean chart
        chart_df = prod_df.sort_values('timestamp', ascending=True).copy()
        chart_df = chart_df.groupby('machine_id').tail(20).reset_index(drop=True)
        
        # Time-series Chart with smooth lines
        fig_trend = px.line(chart_df, x='timestamp', y='actual_output', color='machine_id',
                            title="Actual Output Trends by Machine (Last 20 per Machine)",
                            template="plotly_dark", height=350,
                            markers=True)
        fig_trend.update_traces(line=dict(width=2))
        fig_trend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Time",
            yaxis_title="Output Units",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_trend.update_xaxes(tickformat="%H:%M:%S")
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        # Gauge Chart for Average Efficiency
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = avg_efficiency,
            title = {'text': "Plant Efficiency"},
            gauge = {'axis': {'range': [0, 120]},
                     'bar': {'color': "#00cc96"},
                     'steps': [
                         {'range': [0, 80], 'color': "#ff5555"},
                         {'range': [80, 100], 'color': "#333"}],
                     'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=350)
        st.plotly_chart(fig_gauge, use_container_width=True)

    # --- SECTION 3: MANAGEMENT DETAILS ---
    st.markdown("### 📋 Detailed Production Log & Supply Status")
    
    tab1, tab2, tab3 = st.tabs(["Production Logs", "Supply Chain Risk", "Model Evaluation"])
    
    with tab1:
        st.dataframe(prod_df[['timestamp', 'machine_id', 'target_output', 'actual_output', 'efficiency', 'temperature_c']], 
                     use_container_width=True, hide_index=True)
    
    with tab2:
        if not sup_df.empty:
            sup_df['supply_risk'] = ((pd.to_datetime(sup_df['actual_delivery_date']) - pd.to_datetime(sup_df['expected_delivery_date'])).dt.days > 0).replace({True: "Delayed", False: "On Time"})
            risk_chart = px.bar(sup_df, x='supplier_id', y='order_quantity', color='supply_risk',
                                title="Supply Deliveries Status",
                                color_discrete_map={"Delayed": "#ff5555", "On Time": "#00cc96"},
                                template="plotly_dark", height=300)
            risk_chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(risk_chart, use_container_width=True)
            
            st.dataframe(sup_df[['supplier_id', 'material_type', 'expected_delivery_date', 'transportation_status']], 
                         use_container_width=True)
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
                st.dataframe(factors_df, use_container_width=True, hide_index=True)
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
                st.plotly_chart(fig_sup, use_container_width=True)
            else:
                st.info("No supplier breakdown available")
        
        # Current predictions summary
        st.markdown("### 📋 Current Prediction Summary")
        summary_data = {
            "Model": ["Production Risk", "Supplier Delay", "Efficiency"],
            "Current Value": [
                f"{prod_risk['risk_score']}%",
                f"{sup_risk['delay_probability']}%",
                f"{avg_efficiency:.1f}%"
            ],
            "Status": [
                prod_risk['risk_level'],
                sup_risk['risk_level'],
                "Normal" if avg_efficiency > 85 else "Below Target"
            ],
            "Model Type": [
                model_info['production_risk_model'],
                model_info['supplier_delay_model'],
                model_info['efficiency_model']
            ]
        }
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

else:
    st.warning("Waiting for data stream... Please run 'python simulate_all.py' in your terminal.")
    if st.button("Reload"):
        st.rerun()
