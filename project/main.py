import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


import streamlit as st

st.set_page_config(layout="wide")

# SIDEBAR
with st.sidebar:
    st.markdown("## 👤 John Doe")
    st.markdown("---")

    st.markdown("### GENERAL")
    if st.button("🏠 Home"):
        st.session_state.page = "home"

    st.markdown("### DASHBOARD")
    if st.button("📊 Dashboard 1"):
        st.session_state.page = "d1"
    if st.button("📊 Dashboard 2"):
        st.session_state.page = "d2"
    if st.button("📊 Dashboard 3"):
        st.session_state.page = "d3"

    st.markdown("### DATA")
    if st.button("📁 Data"):
        st.session_state.page = "data"

# DEFAULT PAGE
if "page" not in st.session_state:
    st.session_state.page = "home"

# MAIN CONTENT
if st.session_state.page == "home":
    st.title("🏠 Home")
elif st.session_state.page == "d1":
    st.title("📊 Dashboard 1")
elif st.session_state.page == "d2":
    st.title("📊 Dashboard 2")
elif st.session_state.page == "d3":
    st.title("📊 Dashboard 3")
elif st.session_state.page == "data":
    st.title("📁 Data")
    
# CONFIG
st.set_page_config(page_title="Dashboard Debt Collector", layout="wide")

st.title("📊 Dashboard Debt Collector")

# ======================
# DATA CONTOH
# ======================
data = pd.DataFrame({
    "Nama": ["Andi", "Budi", "Citra", "Dewi", "Eka", "Fajar"],
    "Nominal": [2000000, 1500000, 3000000, 1000000, 2500000, 1800000],
    "Jatuh_Tempo": [
        "2026-04-10",
        "2026-04-15",
        "2026-04-01",
        "2026-04-20",
        "2026-03-28",
        "2026-04-05"
    ],
    "Status": ["Belum", "Belum", "Lunas", "Belum", "Belum", "Lunas"],
    "No_HP": ["0812xxx", "0813xxx", "0814xxx", "0815xxx", "0816xxx", "0817xxx"]
})

data["Jatuh_Tempo"] = pd.to_datetime(data["Jatuh_Tempo"])
today = pd.to_datetime(datetime.today().date())

# ======================
# LOGIKA TAMBAHAN
# ======================
data["Keterangan"] = data.apply(
    lambda x: "Overdue" if x["Jatuh_Tempo"] < today and x["Status"] == "Belum"
    else "Aman", axis=1
)

# ======================
# SUMMARY
# ======================
total = len(data)
lunas = len(data[data["Status"] == "Lunas"])
belum = len(data[data["Status"] == "Belum"])
overdue = len(data[data["Keterangan"] == "Overdue"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Nasabah", total)
col2.metric("Sudah Lunas", lunas)
col3.metric("Belum Lunas", belum)
col4.metric("Overdue ⚠️", overdue)

# ======================
# CHART
# ======================
colA, colB = st.columns(2)

with colA:
    fig_pie = px.pie(
        data,
        names="Status",
        title="Persentase Lunas vs Belum"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with colB:
    fig_bar = px.histogram(
        data,
        x="Jatuh_Tempo",
        color="Status",
        title="Distribusi Jatuh Tempo"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ======================
# FILTER
# ======================
st.markdown("## 🔍 Filter Data")

status_filter = st.selectbox(
    "Pilih Status",
    ["Semua", "Lunas", "Belum"]
)

if status_filter != "Semua":
    data_filtered = data[data["Status"] == status_filter]
else:
    data_filtered = data

# ======================
# PRIORITAS TAGIHAN
# ======================
st.markdown("## 🚨 Prioritas Penagihan (Overdue)")

overdue_data = data[
    (data["Keterangan"] == "Overdue")
].sort_values(by="Jatuh_Tempo")

st.dataframe(overdue_data, use_container_width=True)

# ======================
# TABEL SEMUA NASABAH
# ======================
st.markdown("## 📋 Semua Nasabah")

for i, row in data_filtered.iterrows():
    col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])

    col1.write(row["Nama"])
    col2.write(f"Rp {row['Nominal']:,}")
    col3.write(row["Jatuh_Tempo"].date())
    col4.write(row["Status"])

    if col5.button("Chat", key=i):
        st.success(f"Siap hubungi {row['Nama']} ke {row['No_HP']}")
