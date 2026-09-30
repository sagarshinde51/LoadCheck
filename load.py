import streamlit as st
import pandas as pd
import mysql.connector
import streamlit.components.v1 as components

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Concrete Calculator", layout="wide")

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
<style>
.main-title {
    font-size: 40px;
    font-weight: bold;
    color: #1F618D;
    text-align: center;
}
.card {
    background-color: #F4F6F7;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🛣️ Concrete Recommendation System</p>', unsafe_allow_html=True)

# -------------------------------
# Database Connection Function (mysql-connector)
# -------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="82.180.143.66",
        user="u263681140_students",
        password="testStudents@123",
        database="u263681140_students"
    )

def fetch_pothole_data():
    conn = None
    try:
        conn = get_db_connection()
        # Query database directly using mysql.connector
        query = "SELECT id, Lat, `Long`, DigLenhth, DigWidth, DigDepth FROM Pothole ORDER BY id DESC"[cite: 1]
        df = pd.read_sql(query, conn)
        
        # Convert numeric columns
        df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')[cite: 1]
        df['Long'] = pd.to_numeric(df['Long'], errors='coerce')[cite: 1]
        df['DigLenhth'] = pd.to_numeric(df['DigLenhth'], errors='coerce')[cite: 1]
        df['DigWidth'] = pd.to_numeric(df['DigWidth'], errors='coerce')[cite: 1]
        df['DigDepth'] = pd.to_numeric(df['DigDepth'], errors='coerce')[cite: 1]
        
        return df
    except mysql.connector.Error as err:
        st.error(f"MySQL Error: {err}")
        return pd.DataFrame()
    finally:
        if conn and conn.is_connected():
            conn.close()

# -------------------------------
# Load Data
# -------------------------------
df_potholes = fetch_pothole_data()

# -------------------------------
# Tabs
# -------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Live Database View", "🧮 Selected Pothole Analysis", "🗺️ All Potholes Map"])

# ===============================
# TAB 1 - LIVE DATABASE VIEW
# ===============================
with tab1:
    col_hdr1, col_hdr2 = st.columns([6, 1])
    with col_hdr1:
        st.subheader("Live Pothole Data from Database")
    with col_hdr2:
        if st.button("🔄 Refresh"):
            st.rerun()

    if not df_potholes.empty:
        st.dataframe(df_potholes, use_container_width=True)
    else:
        st.warning("No records found in the Pothole table.")

# ===============================
# TAB 2 - SELECTED POTHOLE ANALYSIS
# ===============================
with tab2:
    st.subheader("Pothole Inspection & Concrete Requirement")

    if not df_potholes.empty:
        pothole_ids = df_potholes['id'].tolist()[cite: 1]
        selected_id = st.selectbox("Select Pothole ID to Inspect:", pothole_ids)

        record = df_potholes[df_potholes['id'] == selected_id].iloc[0][cite: 1]

        length = record['DigLenhth'][cite: 1]
        width = record['DigWidth'][cite: 1]
        depth = record['DigDepth'][cite: 1]
        lat = record['Lat'][cite: 1]
        lon = record['Long'][cite: 1]

        # Volume & Concrete calculation
        volume = length * width * depth
        concrete_kg = volume * 2400

        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Length:** {length} m")
            st.write(f"**Width:** {width} m")
            st.write(f"**Depth:** {depth} m")
        with col2:
            st.write(f"**Latitude:** {lat}")
            st.write(f"**Longitude:** {lon}")
            st.write(f"**Calculated Volume:** {volume:.4f} m³")
            st.write(f"**Concrete Required:** {concrete_kg:.2f} kg")
        st.markdown('</div>', unsafe_allow_html=True)

        if pd.notnull(lat) and pd.notnull(lon):
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
        else:
            st.warning("Coordinates not available for this record.")
    else:
        st.warning("No data available to display.")

# ===============================
# TAB 3 - ALL POTHOLES MAP
# ===============================
with tab3:
    st.subheader("Pothole Distribution Map")
    if not df_potholes.empty:
        valid_coords = df_potholes.dropna(subset=['Lat', 'Long']).rename(columns={'Lat': 'lat', 'Long': 'lon'})[cite: 1]
        if not valid_coords.empty:
            st.map(valid_coords[['lat', 'lon']])
        else:
            st.warning("No valid GPS coordinates found.")
    else:
        st.warning("No data available.")

# -------------------------------
# JS Enhancement
# -------------------------------
components.html("""
<script>
console.log("Interactive Dashboard Loaded");
</script>
""", height=0)
