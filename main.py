import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from urllib.parse import quote
import requests

st.set_page_config(
    page_title="Dashboard Penerima Bantuan",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Penerima Bantuan")

# =========================
# GOOGLE SHEET CONFIG
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
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    return f"{x.day} {bulan[x.month]} {x.year}"


def clean_numeric(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("Rp", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.strip(),
        errors="coerce"
    )


def normalize_columns(df):
    df.columns = [str(col).strip() for col in df.columns]

    aliases = {
        "Nama": "Nama Penerima Bantuan",
        "Penerima Bantuan": "Nama Penerima Bantuan",
        "Nama_Penerima_Bantuan": "Nama Penerima Bantuan",
        "Nama Nasabah": "Nama Penerima Bantuan",
        "No HP": "Kontak",
        "No_HP": "Kontak",
        "Phone": "Kontak",
        "Nominal": "Pinjaman",
        "Total Pinjaman": "Pinjaman",
        "Total": "Pinjaman",
        "Sisa Pinjaman": "Sisa",
        "Outstanding": "Sisa",
        "Tahun Bantuan": "Tahun",
        "Tanggal Jatuh Tempo": "Jatuh Tempo",
        "Jatuh_Tempo": "Jatuh Tempo",
        "Status Final": "Status"
    }

    df = df.rename(columns={k: v for k, v in aliases.items() if k in df.columns})

    required_cols = [
        "ID", "Nama Penerima Bantuan", "Email", "Tahun",
        "Pinjaman", "Dibayar", "Sisa",
        "Jatuh Tempo", "Status", "Kontak"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    return df


def normalize_status(row):
    status = str(row.get("Status", "")).strip().lower()
    sisa = row.get("Sisa", 0)
    jatuh_tempo = row.get("Jatuh Tempo", pd.NaT)
    today = pd.Timestamp.today().normalize()

    if pd.notna(sisa) and sisa <= 0:
        return "Lunas"

    if status in ["lunas", "sudah lunas"]:
        return "Lunas"

    if pd.notna(jatuh_tempo) and jatuh_tempo < today:
        return "Jatuh Tempo"

    return "Belum Lunas"


@st.cache_data(ttl=300)
def load_data():
    errors = []

    # Cara 1: export CSV langsung
    try:
        r = requests.get(CSV_URL, timeout=20)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        if not df.empty:
            return df
    except Exception as e:
        errors.append(f"CSV export gagal: {e}")

    # Cara 2: gviz fallback
    try:
        r = requests.get(GVIZ_URL, timeout=20)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
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
    st.code(
        "Pastikan Google Sheets sudah di-set 'Anyone with the link can view' "
        "atau 'Publish to web'.\n\nDetail error:\n" + str(e)
    )
    st.stop()

data = normalize_columns(data)

# Konversi tipe data
data["Tahun"] = clean_numeric(data["Tahun"])
data["Pinjaman"] = clean_numeric(data["Pinjaman"])
data["Dibayar"] = clean_numeric(data["Dibayar"])
data["Sisa"] = clean_numeric(data["Sisa"])
data["Jatuh Tempo"] = pd.to_datetime(data["Jatuh Tempo"], errors="coerce", dayfirst=True)

if data.empty:
    st.warning("Data Google Sheets kosong.")
    st.stop()

# Status final
data["Status Final"] = data.apply(normalize_status, axis=1)

today = pd.Timestamp.today().normalize()
data["Terlambat Hari"] = data["Jatuh Tempo"].apply(
    lambda x: (today - x).days if pd.notna(x) and x < today else 0
)

# =========================
# FILTER
# =========================
st.markdown("## 🔎 Filter Data")

f1, f2 = st.columns(2)

with f1:
    selected_tahun = st.selectbox("Pilih Tahun", ["Semua", 2023, 2024, 2025, 2026])

with f2:
    selected_status = st.selectbox(
        "Pilih Status",
        ["Semua", "Lunas", "Belum Lunas", "Jatuh Tempo"]
    )

filtered = data.copy()

if selected_tahun != "Semua":
    filtered = filtered[filtered["Tahun"] == selected_tahun]

if selected_status != "Semua":
    filtered = filtered[filtered["Status Final"] == selected_status]

# =========================
# METRICS
# =========================
total_penerima = len(filtered)
total_lunas = len(filtered[filtered["Status Final"] == "Lunas"])
total_belum = len(filtered[filtered["Status Final"] == "Belum Lunas"])
total_jatuh_tempo = len(filtered[filtered["Status Final"] == "Jatuh Tempo"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Penerima Bantuan", total_penerima)
c2.metric("Lunas", total_lunas)
c3.metric("Belum Lunas", total_belum)
c4.metric("Jatuh Tempo", total_jatuh_tempo)

# =========================
# CHART
# =========================
st.markdown("## 📈 Persentase Status Pembayaran")

chart_df = filtered["Status Final"].value_counts().reset_index()
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

prioritas = filtered[
    filtered["Status Final"].isin(["Belum Lunas", "Jatuh Tempo"])
].copy()

prioritas["Urutan"] = prioritas["Status Final"].map({
    "Jatuh Tempo": 0,
    "Belum Lunas": 1
})

prioritas = prioritas.sort_values(
    by=["Urutan", "Terlambat Hari", "Jatuh Tempo"],
    ascending=[True, False, True]
)

st.caption(f"{len(prioritas)} penerima bantuan memerlukan tindak lanjut")

if prioritas.empty:
    st.success("Tidak ada penerima bantuan yang perlu segera dihubungi.")
else:
    show_prioritas = prioritas[[
        "ID", "Nama Penerima Bantuan", "Sisa", "Pinjaman",
        "Jatuh Tempo", "Terlambat Hari", "Status Final", "Kontak"
    ]].copy()

    show_prioritas["Sisa"] = show_prioritas["Sisa"].apply(format_rupiah)
    show_prioritas["Pinjaman"] = show_prioritas["Pinjaman"].apply(format_rupiah)
    show_prioritas["Jatuh Tempo"] = show_prioritas["Jatuh Tempo"].apply(format_tanggal_indo)
    show_prioritas["Terlambat Hari"] = show_prioritas["Terlambat Hari"].apply(
        lambda x: f"{int(x)} hari" if x > 0 else "-"
    )

    st.dataframe(show_prioritas, use_container_width=True, hide_index=True)

# =========================
# TABEL SEMUA PENERIMA BANTUAN
# =========================
st.markdown("## 📋 Data Semua Penerima Bantuan")

search = st.text_input("Cari nama, ID, email, atau kontak...")

table_df = filtered.copy()

if search:
    keyword = search.lower()
    table_df = table_df[
        table_df["ID"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["Nama Penerima Bantuan"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["Email"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["Kontak"].astype(str).str.lower().str.contains(keyword, na=False)
    ]

st.caption(f"Menampilkan {len(table_df)} dari {len(filtered)} penerima bantuan")

display_df = table_df[[
    "ID", "Nama Penerima Bantuan", "Email", "Tahun",
    "Pinjaman", "Dibayar", "Sisa",
    "Jatuh Tempo", "Status Final", "Kontak"
]].copy()

display_df["Pinjaman"] = display_df["Pinjaman"].apply(format_rupiah)
display_df["Dibayar"] = display_df["Dibayar"].apply(format_rupiah)
display_df["Sisa"] = display_df["Sisa"].apply(format_rupiah)
display_df["Jatuh Tempo"] = display_df["Jatuh Tempo"].apply(format_tanggal_indo)

st.dataframe(display_df, use_container_width=True, hide_index=True)

# =========================
# DAFTAR BELUM LUNAS
# =========================
st.markdown("## 📞 Daftar Penerima Bantuan Belum Lunas")

belum_lunas_df = filtered[
    filtered["Status Final"].isin(["Belum Lunas", "Jatuh Tempo"])
][[
    "ID", "Nama Penerima Bantuan", "Tahun",
    "Sisa", "Jatuh Tempo", "Status Final", "Kontak"
]].copy()

belum_lunas_df["Sisa"] = belum_lunas_df["Sisa"].apply(format_rupiah)
belum_lunas_df["Jatuh Tempo"] = belum_lunas_df["Jatuh Tempo"].apply(format_tanggal_indo)

st.dataframe(belum_lunas_df, use_container_width=True, hide_index=True)
