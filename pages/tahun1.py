import streamlit as st
import pandas as pd
from datetime import datetime

st.title("📅 Dashboard Tahun 1")

data = pd.DataFrame({
    "Nama": ["Andi", "Budi"],
    "Nominal": [2000000, 1500000],
    "Jatuh_Tempo": ["2026-04-01", "2026-04-20"],
    "Status": ["Belum", "Lunas"]
})

data["Jatuh_Tempo"] = pd.to_datetime(data["Jatuh_Tempo"])
today = pd.to_datetime(datetime.today().date())

# DETEKSI OVERDUE
data["Keterangan"] = data.apply(
    lambda x: "Overdue" if x["Jatuh_Tempo"] < today and x["Status"] == "Belum"
    else "Aman", axis=1
)

# METRIC
st.metric("Total Nasabah", len(data))

# OVERDUE
st.markdown("## 🚨 Overdue")
st.dataframe(data[data["Keterangan"] == "Overdue"])

# SEMUA DATA
st.markdown("## 📋 Semua Data")
st.dataframe(data)
