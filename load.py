import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="LoadCheck Dashboard", layout="wide")

# Database Connection Function
def get_data():
    try:
        conn = mysql.connector.connect(
            host="82.180.143.66",
            user="u263681140_students",
            password="testStudents@123",
            database="u263681140_students"
        )
        query = "SELECT * FROM LoadCheck ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Convert VARCHAR columns to numeric for graphing
        cols_to_fix = ['Vtg1', 'Vtg2', 'Vtg3', 'current1', 'current2', 'current3']
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# UI Layout
st.title("⚡ Electrical Load Monitor")
st.subheader("Real-time data from LoadCheck table")

if st.button('🔄 Refresh Data'):
    st.rerun()

df = get_data()

if df is not None:
    # --- METRICS SECTION ---
    col1, col2, col3 = st.columns(3)
    latest = df.iloc[0]
    col1.metric("Latest Voltage (V1)", f"{latest['Vtg1']}V")
    col2.metric("Latest Current (C1)", f"{latest['current1']}A")
    col3.metric("Total Records", len(df))

    # --- GRAPH SECTION ---
    st.divider()
    tab1, tab2 = st.tabs(["📈 Voltage Trends", "📉 Current Trends"])
    
    with tab1:
        fig_vtg = px.line(df, x='id', y=['Vtg1', 'Vtg2', 'Vtg3'], 
                         title="Voltage levels over time",
                         labels={"value": "Voltage (V)", "id": "Record ID"},
                         template="plotly_dark")
        st.plotly_chart(fig_vtg, use_container_width=True)

    with tab2:
        fig_curr = px.line(df, x='id', y=['current1', 'current2', 'current3'], 
                          title="Current levels over time",
                          labels={"value": "Current (A)", "id": "Record ID"},
                          line_shape='spline',
                          template="plotly_dark")
        st.plotly_chart(fig_curr, use_container_width=True)

    # --- TABLE SECTION ---
    st.divider()
    st.write("### 📋 Raw Data Table")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("No data available to display.")
