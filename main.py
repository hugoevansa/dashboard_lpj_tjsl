import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Dashboard Utama", layout="wide")

st.title("📊 Dashboard Debt Collector (All Tahun)")

# ======================
# DATA CONTOH (GABUNGAN)
# ======================
data = pd.DataFrame({
    "Nama": ["Andi", "Budi", "Citra", "Dewi"],
    "Nominal": [2000000, 1500000, 3000000, 1000000],
    "Status": ["Belum", "Lunas", "Belum", "Lunas"],
    "Tahun": ["Tahun 1", "Tahun 1", "Tahun 2", "Tahun 2"]
})

# ======================
# METRIC
# ======================
total = len(data)
lunas = len(data[data["Status"] == "Lunas"])
belum = len(data[data["Status"] == "Belum"])

col1, col2, col3 = st.columns(3)
col1.metric("Total Nasabah", total)
col2.metric("Lunas", lunas)
col3.metric("Belum", belum)

# ======================
# CHART
# ======================
fig = px.pie(data, names="Status", title="Persentase Lunas vs Belum")
st.plotly_chart(fig, use_container_width=True)

# ======================
# INFO
# ======================
st.info("👉 Gunakan sidebar untuk lihat detail per tahun")
