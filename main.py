import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from io import StringIO

st.set_page_config(
    page_title="Dashboard Penerima Bantuan",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS - MAROON CLEAN LAYOUT
# =========================
st.markdown("""
<style>
:root {
    --bg: #f7f3f5;
    --panel: #ffffff;
    --panel-2: #fcf8f9;
    --line: #ead8de;
    --text: #34111c;
    --muted: #8d6a76;
    --maroon: #7a1f3d;
    --maroon-2: #5e132d;
    --maroon-3: #a24a68;
    --maroon-soft: #f6e8ed;
    --maroon-soft-2: #ecd4dc;
    --success-bg: #e6f4ea;
    --success-text: #1f7a4d;
    --warning-bg: #fff2df;
    --warning-text: #a56a00;
    --danger-bg: #fde8ec;
    --danger-text: #b42318;
    --shadow: 0 10px 28px rgba(122, 31, 61, 0.08);
}

html, body, [class*="css"]  {
    font-family: "Inter", "Segoe UI", sans-serif;
    color: var(--text);
}

.stApp {
    background:
        radial-gradient(circle at 0% 0%, rgba(122,31,61,0.05), transparent 18%),
        radial-gradient(circle at 100% 0%, rgba(122,31,61,0.04), transparent 18%),
        linear-gradient(180deg, #fbf8f9 0%, #f4eef1 100%);
}

.block-container {
    max-width: 1500px;
    padding-top: 0.9rem;
    padding-bottom: 2rem;
}

header[data-testid="stHeader"] {
    background: rgba(255,255,255,0);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--maroon-2) 0%, var(--maroon) 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}

section[data-testid="stSidebar"] * {
    color: #fff7fa !important;
}

div[data-testid="stToolbar"] {
    visibility: visible;
}

[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > div:empty {
    display: none;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: 14px !important;
    border: 1px solid var(--line) !important;
    background: #ffffff !important;
    min-height: 44px;
    box-shadow: none !important;
}

.stTextInput input {
    border-radius: 14px !important;
}

.top-strip {
    display: grid;
    grid-template-columns: 1.6fr 0.8fr 0.8fr;
    gap: 14px;
    align-items: center;
    margin-bottom: 14px;
}

.brand-box {
    background: linear-gradient(135deg, #fffefe 0%, #fff7fa 100%);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 16px 18px;
    box-shadow: var(--shadow);
    min-height: 78px;
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand-icon {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    background: linear-gradient(135deg, var(--maroon-2), var(--maroon));
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: 800;
    box-shadow: 0 10px 20px rgba(122,31,61,0.18);
}

.brand-title {
    font-size: 1.95rem;
    font-weight: 900;
    color: var(--maroon-2);
    line-height: 1.05;
    margin-bottom: 2px;
}

.brand-subtitle {
    font-size: 0.92rem;
    color: var(--muted);
}

.filter-card {
    background: linear-gradient(180deg, #fffefe 0%, #fff8fa 100%);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 10px 12px 6px 12px;
    box-shadow: var(--shadow);
    min-height: 78px;
}

.kpi-card {
    background: linear-gradient(180deg, #ffffff 0%, #fffafb 100%);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 16px 18px;
    box-shadow: var(--shadow);
    min-height: 108px;
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 6px;
    height: 100%;
    background: linear-gradient(180deg, var(--maroon) 0%, var(--maroon-3) 100%);
}

.kpi-label {
    font-size: 0.9rem;
    color: var(--muted);
    font-weight: 700;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 900;
    color: var(--text);
    line-height: 1.1;
}

.kpi-note {
    margin-top: 8px;
    color: var(--muted);
    font-size: 0.82rem;
}

.panel {
    background: linear-gradient(180deg, #ffffff 0%, #fffafb 100%);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 16px 16px 10px 16px;
    box-shadow: var(--shadow);
    height: 100%;
}

.panel-title {
    font-size: 1.45rem;
    font-weight: 900;
    color: var(--text);
    margin-bottom: 2px;
}

.panel-subtitle {
    font-size: 0.88rem;
    color: var(--muted);
    margin-bottom: 10px;
}

.note-box {
    background: linear-gradient(180deg, #fff7f9 0%, #fff1f4 100%);
    border: 1px solid var(--maroon-soft-2);
    border-radius: 18px;
    padding: 14px 16px;
    margin-top: 10px;
    margin-bottom: 16px;
    color: var(--text);
}

.note-box b {
    color: var(--maroon);
}

.mini-stat {
    background: #fffafd;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 14px 14px;
    margin-bottom: 10px;
}

.mini-stat-label {
    font-size: 0.84rem;
    color: var(--muted);
    margin-bottom: 4px;
}

.mini-stat-value {
    font-size: 1.55rem;
    font-weight: 900;
    color: var(--maroon);
}

.section-head {
    font-size: 1.4rem;
    font-weight: 900;
    color: var(--text);
    margin-top: 8px;
    margin-bottom: 8px;
}

.table-caption {
    color: var(--muted);
    font-size: 0.9rem;
    margin-bottom: 10px;
}

.status-chip {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 800;
    border: 1px solid transparent;
    white-space: nowrap;
}

.chip-lunas {
    background: var(--success-bg);
    color: var(--success-text);
    border-color: #bfe3ca;
}

.chip-belum {
    background: var(--warning-bg);
    color: var(--warning-text);
    border-color: #f3d59d;
}

.chip-jatuh {
    background: var(--danger-bg);
    color: var(--danger-text);
    border-color: #f0c3cf;
}

.custom-table-wrap {
    background: white;
    border: 1px solid var(--line);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: var(--shadow);
}

.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.custom-table th {
    background: linear-gradient(180deg, #8b2847 0%, #6f1836 100%);
    color: white;
    text-align: left;
    padding: 12px 14px;
    font-weight: 800;
    white-space: nowrap;
}

.custom-table td {
    padding: 12px 14px;
    border-bottom: 1px solid #f0e1e6;
    color: var(--text);
    vertical-align: top;
}

.custom-table tr:nth-child(even) td {
    background: #fffafc;
}

.custom-table tr:last-child td {
    border-bottom: none;
}

.search-card {
    background: linear-gradient(180deg, #ffffff 0%, #fffafb 100%);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 12px 14px 6px 14px;
    box-shadow: var(--shadow);
    margin-bottom: 12px;
}

.footer-note {
    color: var(--muted);
    font-size: 0.86rem;
    margin-top: 12px;
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

def dataframe_to_html(df):
    return df.to_html(index=False, escape=False, classes="custom-table")

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
    st.caption("Tema maroon • clean layout")
    st.markdown("---")
    st.markdown("Filter utama ada di area atas dashboard.")

# =========================
# TOP AREA MIRIP CONTOH
# =========================
top_left, top_mid, top_right = st.columns([1.8, 0.9, 0.9])

with top_left:
    st.markdown("""
    <div class="brand-box">
        <div class="brand-icon">📊</div>
        <div>
            <div class="brand-title">DASHBOARD BANTUAN</div>
            <div class="brand-subtitle">Monitoring status bantuan dan prioritas tindak lanjut</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with top_mid:
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    selected_tahun = st.selectbox("Tahun", ["Semua", 2023, 2024, 2025, 2026], label_visibility="collapsed")
    st.caption("Semua Tahun" if selected_tahun == "Semua" else f"Tahun {selected_tahun}")
    st.markdown('</div>', unsafe_allow_html=True)

with top_right:
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    selected_status = st.selectbox(
        "Kondisi",
        ["Semua", "Lunas", "Belum Lunas", "Jatuh Tempo"],
        label_visibility="collapsed"
    )
    st.caption("Semua Kondisi" if selected_status == "Semua" else selected_status)
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
# KPI
# =========================
total_penerima = len(filtered)
total_lunas = len(filtered[filtered["Status Pembayaran"] == "Lunas"])
total_belum_lunas = len(filtered[filtered["Status Pembayaran"] == "Belum Lunas"])
total_jatuh_tempo = len(filtered[filtered["Kondisi Tenggat"] == "Jatuh Tempo"])

total_nominal = filtered["Jumlah Bantuan (Rp)"].fillna(0).sum()

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Nominal Bantuan</div>
        <div class="kpi-value">{format_rupiah(total_nominal)}</div>
        <div class="kpi-note">Akumulasi nominal data terfilter</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Penerima</div>
        <div class="kpi-value">{total_penerima}</div>
        <div class="kpi-note">Jumlah penerima bantuan</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Lunas</div>
        <div class="kpi-value">{total_lunas}</div>
        <div class="kpi-note">Sudah selesai</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Jatuh Tempo</div>
        <div class="kpi-value">{total_jatuh_tempo}</div>
        <div class="kpi-note">Perlu prioritas follow-up</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# CHART ROW - 3 PANEL
# =========================
chart_df = filtered["Status Pembayaran"].value_counts().reset_index()
chart_df.columns = ["Status", "Jumlah"]

status_compare_df = (
    filtered["Label Tampilan"]
    .value_counts()
    .reindex(["Lunas", "Belum Lunas", "Jatuh Tempo"], fill_value=0)
    .reset_index()
)
status_compare_df.columns = ["Status", "Jumlah"]

monthly_df = filtered.copy()
monthly_df["Bulan"] = monthly_df["Tanggal Dibantu"].dt.month
monthly_df = (
    monthly_df.dropna(subset=["Bulan"])
    .groupby("Bulan", as_index=False)["Jumlah Bantuan (Rp)"]
    .sum()
)
month_map = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
    7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"
}
monthly_df["Nama Bulan"] = monthly_df["Bulan"].map(month_map)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Komposisi Status (%)</div>
        <div class="panel-subtitle">Perbandingan status pembayaran utama</div>
    """, unsafe_allow_html=True)

    if not chart_df.empty:
        fig_donut = px.pie(
            chart_df,
            names="Status",
            values="Jumlah",
            hole=0.62,
            color="Status",
            color_discrete_map={
                "Lunas": "#7a1f3d",
                "Belum Lunas": "#d7a6b5",
            }
        )
        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(line=dict(color="white", width=3))
        )
        fig_donut.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="v", title="", font=dict(size=12))
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("Tidak ada data.")

    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Perbandingan Status</div>
        <div class="panel-subtitle">Lunas, belum lunas, dan jatuh tempo</div>
    """, unsafe_allow_html=True)

    fig_bar = px.bar(
        status_compare_df,
        x="Status",
        y="Jumlah",
        color="Status",
        color_discrete_map={
            "Lunas": "#7a1f3d",
            "Belum Lunas": "#c77f96",
            "Jatuh Tempo": "#e6b7c5",
        }
    )
    fig_bar.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="",
        yaxis_title="Jumlah",
        showlegend=False
    )
    fig_bar.update_traces(marker_line_width=0)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    lunas_pct = round((total_lunas / total_penerima) * 100, 1) if total_penerima else 0
    belum_lunas_pct = round((total_belum_lunas / total_penerima) * 100, 1) if total_penerima else 0
    jatuh_tempo_pct = round((total_jatuh_tempo / total_penerima) * 100, 1) if total_penerima else 0

    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">Ringkasan Cepat</div>
        <div class="panel-subtitle">Persentase dan prioritas saat ini</div>
        <div class="mini-stat">
            <div class="mini-stat-label">Persentase Lunas</div>
            <div class="mini-stat-value">{lunas_pct}%</div>
        </div>
        <div class="mini-stat">
            <div class="mini-stat-label">Persentase Belum Lunas</div>
            <div class="mini-stat-value">{belum_lunas_pct}%</div>
        </div>
        <div class="mini-stat">
            <div class="mini-stat-label">Persentase Jatuh Tempo</div>
            <div class="mini-stat-value">{jatuh_tempo_pct}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# COMBO CHART
# =========================
st.markdown("""
<div class="panel" style="margin-top:14px;">
    <div class="panel-title">Nominal Bantuan Bulanan</div>
    <div class="panel-subtitle">Akumulasi nominal berdasarkan tanggal dibantu</div>
""", unsafe_allow_html=True)

if not monthly_df.empty:
    fig_monthly = go.Figure()
    fig_monthly.add_trace(
        go.Bar(
            x=monthly_df["Nama Bulan"],
            y=monthly_df["Jumlah Bantuan (Rp)"],
            name="Nominal Bantuan",
            marker_color="#d8a3b3"
        )
    )
    fig_monthly.add_trace(
        go.Scatter(
            x=monthly_df["Nama Bulan"],
            y=monthly_df["Jumlah Bantuan (Rp)"],
            name="Trend",
            mode="lines+markers",
            line=dict(color="#7a1f3d", width=3),
            marker=dict(size=8, color="#7a1f3d")
        )
    )
    fig_monthly.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Bulan",
        yaxis_title="Nominal",
        legend_title_text=""
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
else:
    st.info("Data bulanan belum tersedia.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# NOTE
# =========================
st.markdown("""
<div class="note-box">
    <b>Catatan:</b> Status utama dibagi menjadi <b>Lunas</b> dan <b>Belum Lunas</b>.
    Label <b>Jatuh Tempo</b> dipakai untuk data yang belum lunas dan sudah melewati tenggat.
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

st.markdown('<div class="section-head">Penerima Bantuan Jatuh Tempo - Segera Hubungi</div>', unsafe_allow_html=True)
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

    st.markdown(
        f'<div class="custom-table-wrap">{dataframe_to_html(prioritas_view)}</div>',
        unsafe_allow_html=True
    )

# =========================
# SEARCH
# =========================
st.markdown('<div class="section-head">Data Semua Penerima Bantuan</div>', unsafe_allow_html=True)
st.markdown('<div class="search-card">', unsafe_allow_html=True)
search = st.text_input("Cari nama bantuan, PIC, nomor HP penerima, atau status...", label_visibility="collapsed", placeholder="Cari nama bantuan, PIC, nomor HP penerima, atau status...")
st.markdown('</div>', unsafe_allow_html=True)

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
    f'<div class="custom-table-wrap">{dataframe_to_html(display_df)}</div>',
    unsafe_allow_html=True
)

# =========================
# BELUM LUNAS
# =========================
st.markdown('<div class="section-head">Daftar Penerima Bantuan Belum Lunas</div>', unsafe_allow_html=True)

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
    f'<div class="custom-table-wrap">{dataframe_to_html(belum_lunas_df)}</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="footer-note">Versi ini dibuat lebih mendekati layout contoh: filter di atas, kartu KPI putih, panel chart terpisah, dan tema maroon yang lebih konsisten.</div>', unsafe_allow_html=True)
