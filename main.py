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

# =========================
# CUSTOM CSS - MAROON THEME
# =========================
st.markdown("""
<style>
:root {
    --bg: #f7f3f4;
    --panel: #ffffff;
    --panel-soft: #fcf8f9;
    --line: #ead9dd;
    --text: #3b1f29;
    --muted: #8b6b75;
    --maroon: #7b1e3a;
    --maroon-dark: #5f132c;
    --maroon-soft: #f3e4e9;
    --maroon-soft-2: #ead0d8;
    --green-soft: #dff3e8;
    --green-text: #18794e;
    --amber-soft: #fff0d8;
    --amber-text: #9a6700;
    --red-soft: #fde7eb;
    --red-text: #b42318;
    --shadow: 0 10px 30px rgba(123, 30, 58, 0.08);
}

html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(123,30,58,0.05), transparent 28%),
        radial-gradient(circle at top right, rgba(123,30,58,0.04), transparent 24%),
        linear-gradient(180deg, #fbf8f9 0%, #f5eff1 100%);
    color: var(--text);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1480px;
}

header[data-testid="stHeader"] {
    background: rgba(255,255,255,0);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #4d1024 0%, #6d1732 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #fff7f9 !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: 14px !important;
    border: 1px solid var(--line) !important;
    background: #ffffff !important;
    min-height: 46px;
    box-shadow: none !important;
}

.stTextInput input {
    border-radius: 14px !important;
}

.dashboard-hero {
    background: linear-gradient(135deg, var(--maroon-dark) 0%, var(--maroon) 100%);
    border-radius: 24px;
    padding: 26px 28px;
    color: white;
    box-shadow: 0 18px 40px rgba(95, 19, 44, 0.22);
    margin-bottom: 18px;
}

.hero-top {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: center;
}

.hero-brand {
    display: flex;
    gap: 16px;
    align-items: center;
}

.hero-logo {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    background: rgba(255,255,255,0.14);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 4px;
}

.hero-subtitle {
    font-size: 0.97rem;
    opacity: 0.92;
}

.hero-badge {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.14);
    padding: 12px 14px;
    border-radius: 16px;
    min-width: 220px;
    text-align: right;
    font-size: 0.92rem;
}

.filter-wrap {
    background: rgba(255,255,255,0.9);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 14px;
    box-shadow: var(--shadow);
    margin-bottom: 18px;
}

.kpi-card {
    background: linear-gradient(180deg, #ffffff 0%, #fffafb 100%);
    border: 1px solid var(--line);
    border-left: 5px solid var(--maroon);
    border-radius: 20px;
    padding: 18px 18px 16px 18px;
    box-shadow: var(--shadow);
    min-height: 120px;
}

.kpi-label {
    font-size: 0.92rem;
    color: var(--muted);
    font-weight: 700;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1.1;
}

.kpi-note {
    margin-top: 10px;
    color: var(--muted);
    font-size: 0.86rem;
}

.panel {
    background: linear-gradient(180deg, #ffffff 0%, #fffafb 100%);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 18px;
    box-shadow: var(--shadow);
    height: 100%;
}

.panel-title {
    font-size: 1.55rem;
    font-weight: 800;
    color: var(--text);
    margin-bottom: 14px;
}

.panel-subtitle {
    font-size: 0.92rem;
    color: var(--muted);
    margin-top: -4px;
    margin-bottom: 14px;
}

.note-box {
    background: linear-gradient(180deg, #fff8fa 0%, #fff2f5 100%);
    border: 1px solid var(--maroon-soft-2);
    border-radius: 18px;
    padding: 16px 18px;
    color: var(--text);
    margin-top: 8px;
    margin-bottom: 16px;
}

.note-box b {
    color: var(--maroon);
}

.status-chip {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 800;
    border: 1px solid transparent;
}

.chip-lunas {
    background: var(--green-soft);
    color: var(--green-text);
    border-color: #b7e4c7;
}

.chip-belum {
    background: var(--amber-soft);
    color: var(--amber-text);
    border-color: #f1d39b;
}

.chip-jatuh {
    background: var(--red-soft);
    color: var(--red-text);
    border-color: #f1c0cb;
}

.small-stat {
    background: var(--panel-soft);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.small-stat-label {
    color: var(--muted);
    font-size: 0.9rem;
    margin-bottom: 4px;
}

.small-stat-value {
    color: var(--maroon);
    font-size: 1.6rem;
    font-weight: 800;
}

.table-caption {
    color: var(--muted);
    margin-bottom: 10px;
    font-size: 0.92rem;
}

.stDataFrame, .stTable {
    border-radius: 18px !important;
    overflow: hidden !important;
    border: 1px solid var(--line) !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 18px !important;
    overflow: hidden !important;
    border: 1px solid var(--line);
    background: white;
}

.section-gap {
    height: 8px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# GOOGLE SHEETS CONFIG
# =========================
SHEET_ID = "1wi4id0XqYlTuw_KO89-cOLSPTFAQ6ODv_tH09LK_2Ao"
GID = "0"

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
GVIZ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"

# =========================
# HELPERS
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
    s = series.astype(str).str.strip()
    s = s.replace(["nan", "NaN", "None", "<NA>"], "", regex=False)
    s = s.str.replace(".0", "", regex=False)
    return s

def normalize_status(status):
    status = str(status).strip().lower()
    if status in ["lunas", "sudah lunas"]:
        return "Lunas"
    return "Belum Lunas"

def make_status_chip(value):
    if value == "Lunas":
        return '<span class="status-chip chip-lunas">Lunas</span>'
    if value == "Jatuh Tempo":
        return '<span class="status-chip chip-jatuh">Jatuh Tempo</span>'
    return '<span class="status-chip chip-belum">Belum Lunas</span>'

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

    raise Exception("\\n".join(errors))

# =========================
# LOAD DATA
# =========================
try:
    data = load_data()
except Exception as e:
    st.error("Gagal mengambil data dari Google Sheets.")
    st.code(str(e))
    st.stop()

data.columns = [str(col).strip() for col in data.columns]

column_aliases = {
    "No HP Penerima": "No Hp Penerima",
    "No Hp": "No Hp Penerima",
    "No HP": "No Hp Penerima",
    "Nomor HP Penerima": "No Hp Penerima",
    "jumlah Bantuan (Rp)": "Jumlah Bantuan (Rp)",
    "Tanggal dibantu": "Tanggal Dibantu",
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

data["Nama Bantuan"] = data["Nama Bantuan"].astype(str).str.strip()
data["PIC"] = data["PIC"].astype(str).str.strip()
data["No Hp Penerima"] = clean_phone(data["No Hp Penerima"])
data["Status"] = data["Status"].astype(str).str.strip()

data["Jumlah Bantuan (Rp)"] = clean_currency(data["Jumlah Bantuan (Rp)"])
data["Tanggal Dibantu"] = pd.to_datetime(data["Tanggal Dibantu"], errors="coerce", dayfirst=True)
data["Tenggat"] = pd.to_datetime(data["Tenggat"], errors="coerce", dayfirst=True)

data["Tahun"] = data["Tanggal Dibantu"].dt.year
today = pd.Timestamp.today().normalize()

# =========================
# LOGIKA STATUS
# =========================
data["Status Pembayaran"] = data["Status"].apply(normalize_status)

data["Kondisi Tenggat"] = data.apply(
    lambda row: "Jatuh Tempo"
    if row["Status Pembayaran"] == "Belum Lunas" and pd.notna(row["Tenggat"]) and row["Tenggat"] < today
    else "Belum Jatuh Tempo",
    axis=1
)

data["Terlambat Hari"] = data["Tenggat"].apply(
    lambda x: (today - x).days if pd.notna(x) and x < today else 0
)

def get_label_tampilan(row):
    if row["Status Pembayaran"] == "Lunas":
        return "Lunas"
    if row["Kondisi Tenggat"] == "Jatuh Tempo":
        return "Jatuh Tempo"
    return "Belum Lunas"

data["Label Tampilan"] = data.apply(get_label_tampilan, axis=1)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## Dashboard Bantuan")
    st.caption("Tema maroon • tampilan lebih rapih")
    st.markdown("---")
    st.markdown("Gunakan filter di area utama untuk menyaring data.")

# =========================
# HEADER
# =========================
st.markdown("""
<div class="dashboard-hero">
    <div class="hero-top">
        <div class="hero-brand">
            <div class="hero-logo">📊</div>
            <div>
                <div class="hero-title">Dashboard Penerima Bantuan</div>
                <div class="hero-subtitle">
                    Monitoring status bantuan, jatuh tempo, dan prioritas penerima bantuan yang perlu segera ditindaklanjuti.
                </div>
            </div>
        </div>
        <div class="hero-badge">
            <div><b>Mode Tampilan</b></div>
            <div>Maroon Clean Dashboard</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# FILTER BAR
# =========================
st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
f1, f2 = st.columns([1, 1])

with f1:
    selected_tahun = st.selectbox("Pilih Tahun", ["Semua", 2023, 2024, 2025, 2026])

with f2:
    selected_status = st.selectbox(
        "Pilih Kondisi",
        ["Semua", "Lunas", "Belum Lunas", "Jatuh Tempo"]
    )
st.markdown('</div>', unsafe_allow_html=True)

filtered = data.copy()

if selected_tahun != "Semua":
    filtered = filtered[filtered["Tahun"] == selected_tahun]

if selected_status == "Lunas":
    filtered = filtered[filtered["Status Pembayaran"] == "Lunas"]
elif selected_status == "Belum Lunas":
    filtered = filtered[
        (filtered["Status Pembayaran"] == "Belum Lunas") &
        (filtered["Kondisi Tenggat"] == "Belum Jatuh Tempo")
    ]
elif selected_status == "Jatuh Tempo":
    filtered = filtered[filtered["Kondisi Tenggat"] == "Jatuh Tempo"]

# =========================
# METRICS
# =========================
total_penerima = len(filtered)
total_lunas = len(filtered[filtered["Status Pembayaran"] == "Lunas"])
total_belum_lunas = len(filtered[filtered["Status Pembayaran"] == "Belum Lunas"])
total_jatuh_tempo = len(filtered[filtered["Kondisi Tenggat"] == "Jatuh Tempo"])

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Penerima Bantuan</div>
        <div class="kpi-value">{total_penerima}</div>
        <div class="kpi-note">Jumlah data setelah filter diterapkan</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Lunas</div>
        <div class="kpi-value">{total_lunas}</div>
        <div class="kpi-note">Penerima bantuan dengan status lunas</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Belum Lunas</div>
        <div class="kpi-value">{total_belum_lunas}</div>
        <div class="kpi-note">Masih menunggu penyelesaian</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Jatuh Tempo</div>
        <div class="kpi-value">{total_jatuh_tempo}</div>
        <div class="kpi-note">Perlu segera dihubungi</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

# =========================
# CHART AREA
# =========================
left_chart, right_chart = st.columns([1.5, 1])

chart_df = filtered["Status Pembayaran"].value_counts().reset_index()
chart_df.columns = ["Status", "Jumlah"]

with left_chart:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Persentase Status Bantuan</div>
        <div class="panel-subtitle">Perbandingan status utama penerima bantuan</div>
    """, unsafe_allow_html=True)

    if not chart_df.empty:
        fig = px.pie(
            chart_df,
            names="Status",
            values="Jumlah",
            hole=0.62,
            color="Status",
            color_discrete_map={
                "Lunas": "#7b1e3a",
                "Belum Lunas": "#d4a5b2",
            }
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="white", width=3))
        )
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text=""
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Tidak ada data untuk ditampilkan.")

    st.markdown("</div>", unsafe_allow_html=True)

with right_chart:
    jatuh_tempo_pct = round((total_jatuh_tempo / total_penerima) * 100, 1) if total_penerima else 0
    lunas_pct = round((total_lunas / total_penerima) * 100, 1) if total_penerima else 0
    belum_lunas_pct = round((total_belum_lunas / total_penerima) * 100, 1) if total_penerima else 0

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">Ringkasan Cepat</div>
        <div class="small-stat">
            <div class="small-stat-label">Persentase Lunas</div>
            <div class="small-stat-value">{lunas_pct}%</div>
        </div>
        <div class="small-stat">
            <div class="small-stat-label">Persentase Belum Lunas</div>
            <div class="small-stat-value">{belum_lunas_pct}%</div>
        </div>
        <div class="small-stat">
            <div class="small-stat-label">Persentase Jatuh Tempo</div>
            <div class="small-stat-value">{jatuh_tempo_pct}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# INFO BOX
# =========================
st.markdown(f"""
<div class="note-box">
    <b>Catatan:</b>
    Status utama dibagi menjadi <b>Lunas</b> dan <b>Belum Lunas</b>.
    Sementara <b>Jatuh Tempo</b> adalah penerima bantuan yang <b>Belum Lunas</b>
    dan sudah melewati tenggat.
</div>
""", unsafe_allow_html=True)

# =========================
# PRIORITAS
# =========================
prioritas = filtered[
    (filtered["Status Pembayaran"] == "Belum Lunas") &
    (filtered["Kondisi Tenggat"] == "Jatuh Tempo")
].copy()

prioritas = prioritas.sort_values(
    by=["Terlambat Hari", "Tenggat"],
    ascending=[False, True]
)

st.markdown("""
<div class="panel-title" style="margin-top:8px;">Penerima Bantuan Jatuh Tempo - Segera Hubungi</div>
""", unsafe_allow_html=True)
st.markdown(f'<div class="table-caption">{len(prioritas)} penerima bantuan perlu segera dihubungi</div>', unsafe_allow_html=True)

if prioritas.empty:
    st.success("Tidak ada penerima bantuan yang jatuh tempo.")
else:
    prioritas_view = prioritas[[
        "Nama Bantuan",
        "Jumlah Bantuan (Rp)",
        "Tanggal Dibantu",
        "Tenggat",
        "PIC",
        "No Hp Penerima",
        "Terlambat Hari"
    ]].copy()

    prioritas_view["Jumlah Bantuan (Rp)"] = prioritas_view["Jumlah Bantuan (Rp)"].apply(format_rupiah)
    prioritas_view["Tanggal Dibantu"] = prioritas_view["Tanggal Dibantu"].apply(format_tanggal_indo)
    prioritas_view["Tenggat"] = prioritas_view["Tenggat"].apply(format_tanggal_indo)
    prioritas_view["No Hp Penerima"] = prioritas_view["No Hp Penerima"].replace("", "-")
    prioritas_view["Terlambat Hari"] = prioritas_view["Terlambat Hari"].apply(lambda x: f"{int(x)} hari")

    st.dataframe(prioritas_view, use_container_width=True, hide_index=True)

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

# =========================
# SEMUA DATA
# =========================
st.markdown("""
<div class="panel-title">Data Semua Penerima Bantuan</div>
""", unsafe_allow_html=True)

search = st.text_input("Cari nama bantuan, PIC, nomor HP penerima, atau status...")

table_df = filtered.copy()

if search:
    keyword = search.lower()
    table_df = table_df[
        table_df["Nama Bantuan"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["PIC"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["No Hp Penerima"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["Label Tampilan"].astype(str).str.lower().str.contains(keyword, na=False)
    ]

st.markdown(f'<div class="table-caption">Menampilkan {len(table_df)} dari {len(filtered)} penerima bantuan</div>', unsafe_allow_html=True)

display_df = table_df[[
    "Nama Bantuan",
    "Jumlah Bantuan (Rp)",
    "Tanggal Dibantu",
    "Tenggat",
    "PIC",
    "No Hp Penerima",
    "Tahun",
    "Label Tampilan"
]].copy()

display_df["Jumlah Bantuan (Rp)"] = display_df["Jumlah Bantuan (Rp)"].apply(format_rupiah)
display_df["Tanggal Dibantu"] = display_df["Tanggal Dibantu"].apply(format_tanggal_indo)
display_df["Tenggat"] = display_df["Tenggat"].apply(format_tanggal_indo)
display_df["No Hp Penerima"] = display_df["No Hp Penerima"].replace("", "-")
display_df["Status"] = display_df["Label Tampilan"].apply(make_status_chip)
display_df = display_df.drop(columns=["Label Tampilan"])

st.markdown(
    display_df.to_html(escape=False, index=False),
    unsafe_allow_html=True
)

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

# =========================
# BELUM LUNAS
# =========================
st.markdown("""
<div class="panel-title">Daftar Penerima Bantuan Belum Lunas</div>
""", unsafe_allow_html=True)

belum_lunas_df = filtered[
    filtered["Status Pembayaran"] == "Belum Lunas"
][[
    "Nama Bantuan",
    "Jumlah Bantuan (Rp)",
    "PIC",
    "No Hp Penerima",
    "Tenggat",
    "Label Tampilan"
]].copy()

belum_lunas_df["Jumlah Bantuan (Rp)"] = belum_lunas_df["Jumlah Bantuan (Rp)"].apply(format_rupiah)
belum_lunas_df["Tenggat"] = belum_lunas_df["Tenggat"].apply(format_tanggal_indo)
belum_lunas_df["No Hp Penerima"] = belum_lunas_df["No Hp Penerima"].replace("", "-")
belum_lunas_df["Status"] = belum_lunas_df["Label Tampilan"].apply(make_status_chip)
belum_lunas_df = belum_lunas_df.drop(columns=["Label Tampilan"])

st.markdown(
    belum_lunas_df.to_html(escape=False, index=False),
    unsafe_allow_html=True
)
