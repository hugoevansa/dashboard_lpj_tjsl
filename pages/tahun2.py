import streamlit as st
import pandas as pd
from datetime import datetime

st.title("📅 Dashboard Tahun 2")

data = pd.DataFrame({
    "Nama": ["Citra", "Dewi"],
    "Nominal": [3000000, 1000000],
    "Jatuh_Tempo": ["2026-03-28", "2026-04-10"],
    "Status": ["Belum", "Lunas"]
})

data["Jatuh_Tempo"] = pd.to_datetime(data["Jatuh_Tempo"])
today = pd.to_datetime(datetime.today().date())

# OVERDUE
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
