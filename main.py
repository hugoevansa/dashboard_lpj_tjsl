import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

st.set_page_config(
    page_title="Dashboard Penerima Bantuan",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Penerima Bantuan")

# =========================
# GOOGLE SHEETS CONFIG
# =========================
SHEET_ID = "1wi4id0XqYlTuw_KO89-cOLSPTFAQ6ODv_tH09LK_2Ao"
GID = "0"

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
GVIZ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"


# =========================
# HELPER
# =========================
def format_rupiah(x):
    if pd.isna(x):
        return "-"
    return f"Rp {int(float(x)):,}".replace(",", ".")


def format_tanggal_indo(x):
    if pd.isna(x):
        return "-"
    bulan = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember",
    }
    return f"{x.day} {bulan[x.month]} {x.year}"


def clean_currency(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("Rp", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.strip(),
        errors="coerce"
    )


def clean_phone(series):
    """
    Paksa nomor HP jadi string agar tidak berubah jadi None / scientific notation.
    """
    s = series.astype(str).str.strip()

    # ubah nilai kosong / nan jadi kosong
    s = s.replace(["nan", "None", "NaN", "<NA>"], "", regex=False)

    # kalau ada .0 dari hasil numeric, hapus
    s = s.str.replace(".0", "", regex=False)

    return s


def normalize_base_status(status):
    status = str(status).strip().lower()
    if status in ["lunas", "sudah lunas"]:
        return "Lunas"
    return "Belum Lunas"


@st.cache_data(ttl=300)
def load_data():
    errors = []

    try:
        r = requests.get(CSV_URL, timeout=20)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text), dtype=str)
        if not df.empty:
            return df
    except Exception as e:
        errors.append(f"CSV export gagal: {e}")

    try:
        r = requests.get(GVIZ_URL, timeout=20)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text), dtype=str)
        if not df.empty:
            return df
    except Exception as e:
        errors.append(f"GVIZ gagal: {e}")

    raise Exception("\n".join(errors))


# =========================
# LOAD DATA
# =========================
try:
    data = load_data()
except Exception as e:
    st.error("Gagal mengambil data dari Google Sheets.")
    st.code(str(e))
    st.stop()

# Rapikan nama kolom
data.columns = [str(col).strip() for col in data.columns]

# Alias nama kolom kalau ada sedikit beda penulisan
column_aliases = {
    "No HP Penerima": "No Hp Penerima",
    "No Hp": "No Hp Penerima",
    "No HP": "No Hp Penerima",
    "Nomor HP Penerima": "No Hp Penerima",
    "Tanggal dibantu": "Tanggal Dibantu",
    "jumlah Bantuan (Rp)": "Jumlah Bantuan (Rp)",
}

data = data.rename(columns={k: v for k, v in column_aliases.items() if k in data.columns})

required_cols = [
    "Nama Bantuan",
    "Jumlah Bantuan (Rp)",
    "Tanggal Dibantu",
    "Tenggat",
    "PIC",
    "No Hp Penerima",
    "Status",
]

for col in required_cols:
    if col not in data.columns:
        data[col] = ""

# Bersihkan data
data["Nama Bantuan"] = data["Nama Bantuan"].astype(str).str.strip()
data["PIC"] = data["PIC"].astype(str).str.strip()
data["Status"] = data["Status"].astype(str).str.strip()
data["No Hp Penerima"] = clean_phone(data["No Hp Penerima"])

data["Jumlah Bantuan (Rp)"] = clean_currency(data["Jumlah Bantuan (Rp)"])
data["Tanggal Dibantu"] = pd.to_datetime(data["Tanggal Dibantu"], errors="coerce", dayfirst=True)
data["Tenggat"] = pd.to_datetime(data["Tenggat"], errors="coerce", dayfirst=True)

# Tahun dari tanggal dibantu
data["Tahun"] = data["Tanggal Dibantu"].dt.year

today = pd.Timestamp.today().normalize()

# Status dasar: Lunas / Belum Lunas
data["Status Dasar"] = data["Status"].apply(normalize_base_status)

# Jatuh tempo = Belum Lunas yang tenggatnya sudah lewat
def get_status_final(row):
    if row["Status Dasar"] == "Lunas":
        return "Lunas"
    if pd.notna(row["Tenggat"]) and row["Tenggat"] < today:
        return "Jatuh Tempo"
    return "Belum Lunas"

data["Status Final"] = data.apply(get_status_final, axis=1)

# Kelompok utama untuk ringkasan: Lunas vs Belum Lunas
# Jatuh Tempo tetap dihitung sebagai Belum Lunas
def get_kelompok_status(status_final):
    if status_final == "Lunas":
        return "Lunas"
    return "Belum Lunas"

data["Kelompok Status"] = data["Status Final"].apply(get_kelompok_status)

# Keterlambatan
data["Terlambat Hari"] = data["Tenggat"].apply(
    lambda x: (today - x).days if pd.notna(x) and x < today else 0
)

# =========================
# FILTER
# =========================
st.markdown("## 🔎 Filter Data")

f1, f2 = st.columns(2)

with f1:
    tahun_options = ["Semua", 2023, 2024, 2025, 2026]
    selected_tahun = st.selectbox("Pilih Tahun", tahun_options)

with f2:
    status_options = ["Semua", "Lunas", "Belum Lunas", "Jatuh Tempo"]
    selected_status = st.selectbox("Pilih Status", status_options)

filtered = data.copy()

if selected_tahun != "Semua":
    filtered = filtered[filtered["Tahun"] == selected_tahun]

if selected_status != "Semua":
    filtered = filtered[filtered["Status Final"] == selected_status]

# =========================
# METRICS
# =========================
total_penerima = len(filtered)
total_lunas = len(filtered[filtered["Kelompok Status"] == "Lunas"])
total_belum_lunas = len(filtered[filtered["Kelompok Status"] == "Belum Lunas"])
total_jatuh_tempo = len(filtered[filtered["Status Final"] == "Jatuh Tempo"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Penerima Bantuan", total_penerima)
c2.metric("Lunas", total_lunas)
c3.metric("Belum Lunas", total_belum_lunas)
c4.metric("Jatuh Tempo", total_jatuh_tempo)

# =========================
# CHART
# =========================
st.markdown("## 📈 Persentase Status Bantuan")

chart_df = filtered["Kelompok Status"].value_counts().reset_index()
chart_df.columns = ["Status", "Jumlah"]

if not chart_df.empty:
    fig = px.pie(chart_df, names="Status", values="Jumlah", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Tidak ada data untuk ditampilkan.")

# =========================
# SEGERA HUBUNGI
# =========================
st.markdown("## 🚨 Penerima Bantuan Jatuh Tempo - Segera Hubungi")

# hanya yang sudah jatuh tempo
prioritas = filtered[filtered["Status Final"] == "Jatuh Tempo"].copy()

prioritas = prioritas.sort_values(
    by=["Terlambat Hari", "Tenggat"],
    ascending=[False, True]
)

st.caption(f"{len(prioritas)} penerima bantuan perlu segera dihubungi")

if prioritas.empty:
    st.success("Tidak ada penerima bantuan yang jatuh tempo hari ini.")
else:
    prioritas_view = prioritas[[
        "Nama Bantuan",
        "Jumlah Bantuan (Rp)",
        "Tanggal Dibantu",
        "Tenggat",
        "PIC",
        "No Hp Penerima",
        "Status Final",
        "Terlambat Hari"
    ]].copy()

    prioritas_view["Jumlah Bantuan (Rp)"] = prioritas_view["Jumlah Bantuan (Rp)"].apply(format_rupiah)
    prioritas_view["Tanggal Dibantu"] = prioritas_view["Tanggal Dibantu"].apply(format_tanggal_indo)
    prioritas_view["Tenggat"] = prioritas_view["Tenggat"].apply(format_tanggal_indo)
    prioritas_view["No Hp Penerima"] = prioritas_view["No Hp Penerima"].replace("", "-")
    prioritas_view["Terlambat Hari"] = prioritas_view["Terlambat Hari"].apply(lambda x: f"{int(x)} hari")

    st.dataframe(prioritas_view, use_container_width=True, hide_index=True)

# =========================
# DATA SEMUA PENERIMA BANTUAN
# =========================
st.markdown("## 📋 Data Semua Penerima Bantuan")

search = st.text_input("Cari nama bantuan, PIC, nomor HP penerima, atau status...")

table_df = filtered.copy()

if search:
    keyword = search.lower()
    table_df = table_df[
        table_df["Nama Bantuan"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["PIC"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["No Hp Penerima"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["Status Final"].astype(str).str.lower().str.contains(keyword, na=False)
    ]

st.caption(f"Menampilkan {len(table_df)} dari {len(filtered)} penerima bantuan")

display_df = table_df[[
    "Nama Bantuan",
    "Jumlah Bantuan (Rp)",
    "Tanggal Dibantu",
    "Tenggat",
    "PIC",
    "No Hp Penerima",
    "Tahun",
    "Status Final"
]].copy()

display_df["Jumlah Bantuan (Rp)"] = display_df["Jumlah Bantuan (Rp)"].apply(format_rupiah)
display_df["Tanggal Dibantu"] = display_df["Tanggal Dibantu"].apply(format_tanggal_indo)
display_df["Tenggat"] = display_df["Tenggat"].apply(format_tanggal_indo)
display_df["No Hp Penerima"] = display_df["No Hp Penerima"].replace("", "-")

st.dataframe(display_df, use_container_width=True, hide_index=True)

# =========================
# DAFTAR BELUM LUNAS
# =========================
st.markdown("## 📞 Daftar Penerima Bantuan Belum Lunas")

belum_lunas_df = filtered[
    filtered["Kelompok Status"] == "Belum Lunas"
][[
    "Nama Bantuan",
    "Jumlah Bantuan (Rp)",
    "PIC",
    "No Hp Penerima",
    "Tenggat",
    "Status Final"
]].copy()

belum_lunas_df["Jumlah Bantuan (Rp)"] = belum_lunas_df["Jumlah Bantuan (Rp)"].apply(format_rupiah)
belum_lunas_df["Tenggat"] = belum_lunas_df["Tenggat"].apply(format_tanggal_indo)
belum_lunas_df["No Hp Penerima"] = belum_lunas_df["No Hp Penerima"].replace("", "-")

st.dataframe(belum_lunas_df, use_container_width=True, hide_index=True)
