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
        # Querying based on the confirmed schema
        query = "SELECT id, DateT, Vtg1, Vtg2, Vtg3, current1, current2, current3 FROM LoadCheck ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        
        # 1. Convert DateT to datetime objects
        df['DateT'] = pd.to_datetime(df['DateT'])
        
        # 2. Convert VARCHAR columns to numeric for calculation/graphing
        cols_to_fix = ['Vtg1', 'Vtg2', 'Vtg3', 'current1', 'current2', 'current3']
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 3. Calculate Wattage (P = V * I)
        df['Watt1'] = df['Vtg1'] * df['current1']
        df['Watt2'] = df['Vtg2'] * df['current2']
        df['Watt3'] = df['Vtg3'] * df['current3']
        df['Total_Wattage'] = df['Watt1'] + df['Watt2'] + df['Watt3']
            
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
    # Latest record for metrics
    latest = df.iloc[0]

    # --- METRICS SECTION ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Voltage (V1)", f"{latest['Vtg1']:.1f} V")
    col2.metric("Latest Current (C1)", f"{latest['current1']:.2f} A")
    col3.metric("Total Load (W)", f"{latest['Total_Wattage']:.1f} W")
    # Displaying time from DateT column
    col4.metric("Last Sync", latest['DateT'].strftime('%H:%M:%S'))

    # --- GRAPH SECTION ---
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📈 Voltage Trends", "📉 Current Trends", "🔥 Power Consumption"])
    
    with tab1:
        fig_vtg = px.line(df, x='DateT', y=['Vtg1', 'Vtg2', 'Vtg3'], 
                         title="Voltage Levels (V) over Time",
                         labels={"value": "Voltage (V)", "DateT": "Time"},
                         template="plotly_dark")
        st.plotly_chart(fig_vtg, use_container_width=True)

    with tab2:
        fig_curr = px.line(df, x='DateT', y=['current1', 'current2', 'current3'], 
                          title="Current Levels (A) over Time",
                          labels={"value": "Current (A)", "DateT": "Time"},
                          template="plotly_dark")
        st.plotly_chart(fig_curr, use_container_width=True)

    with tab3:
        # Wattage breakdown area chart
        fig_watt = px.area(df, x='DateT', y=['Watt1', 'Watt2', 'Watt3'],
                          title="Power Consumption per Phase (Watts)",
                          labels={"value": "Watts", "DateT": "Time"},
                          template="plotly_dark")
        st.plotly_chart(fig_watt, use_container_width=True)
        
        # Total Wattage trend
        fig_total_watt = px.line(df, x='DateT', y='Total_Wattage',
                                title="Total System Load",
                                labels={"Total_Wattage": "Total Watts", "DateT": "Time"},
                                color_discrete_sequence=['#FF4B4B'],
                                template="plotly_dark")
        st.plotly_chart(fig_total_watt, use_container_width=True)

    # --- TABLE SECTION ---
    st.divider()
    st.write("### 📋 Data Log")
    
    # Selecting and ordering specific columns for the display table
    display_cols = ['id', 'DateT', 'Vtg1', 'current1', 'Watt1', 'Vtg2', 'current2', 'Watt2', 'Vtg3', 'current3', 'Watt3', 'Total_Wattage']
    
    st.dataframe(
        df[display_cols], 
        use_container_width=True,
        column_config={
            "DateT": st.column_config.DatetimeColumn("Timestamp", format="D MMM, h:mm:ss a"),
            "Total_Wattage": st.column_config.NumberColumn("Total Watts", format="%.2f W")
        },
        hide_index=True
    )

else:
    st.warning("Unable to fetch data. Check your database connection.")
