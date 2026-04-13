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
# CUSTOM CSS
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}
.sub-title {
    color: #94a3b8;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: #111827;
    padding: 18px 20px;
    border-radius: 18px;
    border: 1px solid rgba(148,163,184,0.15);
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.metric-label {
    font-size: 0.95rem;
    color: #cbd5e1;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: white;
}
.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 1.2rem;
    margin-bottom: 0.8rem;
}
.info-box {
    background: #0f172a;
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 18px;
    padding: 18px;
    margin-top: 10px;
    margin-bottom: 20px;
}
.small-note {
    color: #94a3b8;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Dashboard Penerima Bantuan</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Monitoring status bantuan, tenggat, dan daftar penerima bantuan yang perlu segera dihubungi.</div>', unsafe_allow_html=True)

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
    s = series.astype(str).str.strip()
    s = s.replace(["nan", "NaN", "None", "<NA>"], "", regex=False)
    s = s.str.replace(".0", "", regex=False)
    return s


def normalize_status(status):
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
# Status pembayaran utama hanya dua: Lunas / Belum Lunas
data["Status Pembayaran"] = data["Status"].apply(normalize_status)

# Kondisi tenggat: apakah sudah jatuh tempo?
data["Kondisi Tenggat"] = data.apply(
    lambda row: "Jatuh Tempo"
    if row["Status Pembayaran"] == "Belum Lunas" and pd.notna(row["Tenggat"]) and row["Tenggat"] < today
    else "Belum Jatuh Tempo",
    axis=1
)

data["Terlambat Hari"] = data["Tenggat"].apply(
    lambda x: (today - x).days if pd.notna(x) and x < today else 0
)

# Label tampilan untuk tabel/filter
def get_label_tampilan(row):
    if row["Status Pembayaran"] == "Lunas":
        return "Lunas"
    if row["Kondisi Tenggat"] == "Jatuh Tempo":
        return "Jatuh Tempo"
    return "Belum Lunas"

data["Label Tampilan"] = data.apply(get_label_tampilan, axis=1)

# =========================
# FILTER
# =========================
st.markdown('<div class="section-title">🔎 Filter Data</div>', unsafe_allow_html=True)

f1, f2 = st.columns(2)

with f1:
    selected_tahun = st.selectbox("Pilih Tahun", ["Semua", 2023, 2024, 2025, 2026])

with f2:
    selected_status = st.selectbox(
        "Pilih Kondisi",
        ["Semua", "Lunas", "Belum Lunas", "Jatuh Tempo"]
    )

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
    <div class="metric-card">
        <div class="metric-label">Total Penerima Bantuan</div>
        <div class="metric-value">{total_penerima}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Lunas</div>
        <div class="metric-value">{total_lunas}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Belum Lunas</div>
        <div class="metric-value">{total_belum_lunas}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Jatuh Tempo</div>
        <div class="metric-value">{total_jatuh_tempo}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# CHART
# =========================
st.markdown('<div class="section-title">📈 Persentase Status Bantuan</div>', unsafe_allow_html=True)

chart_df = filtered["Status Pembayaran"].value_counts().reset_index()
chart_df.columns = ["Status", "Jumlah"]

if not chart_df.empty:
    fig = px.pie(
        chart_df,
        names="Status",
        values="Jumlah",
        hole=0.55
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Tidak ada data untuk ditampilkan.")

# =========================
# INFO BOX
# =========================
st.markdown(f"""
<div class="info-box">
    <div><b>Catatan:</b> <span class="small-note">
    Status utama dibagi menjadi <b>Lunas</b> dan <b>Belum Lunas</b>. 
    Sementara <b>Jatuh Tempo</b> adalah penerima bantuan yang <b>Belum Lunas</b> dan sudah melewati tenggat.
    </span></div>
</div>
""", unsafe_allow_html=True)

# =========================
# SEGERA HUBUNGI
# =========================
st.markdown('<div class="section-title">🚨 Penerima Bantuan Jatuh Tempo - Segera Hubungi</div>', unsafe_allow_html=True)

prioritas = filtered[
    (filtered["Status Pembayaran"] == "Belum Lunas") &
    (filtered["Kondisi Tenggat"] == "Jatuh Tempo")
].copy()

prioritas = prioritas.sort_values(
    by=["Terlambat Hari", "Tenggat"],
    ascending=[False, True]
)

st.caption(f"{len(prioritas)} penerima bantuan perlu segera dihubungi")

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

# =========================
# SEMUA DATA
# =========================
st.markdown('<div class="section-title">📋 Data Semua Penerima Bantuan</div>', unsafe_allow_html=True)

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

st.caption(f"Menampilkan {len(table_df)} dari {len(filtered)} penerima bantuan")

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

display_df = display_df.rename(columns={
    "Label Tampilan": "Status"
})

st.dataframe(display_df, use_container_width=True, hide_index=True)

# =========================
# BELUM LUNAS
# =========================
st.markdown('<div class="section-title">📞 Daftar Penerima Bantuan Belum Lunas</div>', unsafe_allow_html=True)

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
belum_lunas_df = belum_lunas_df.rename(columns={"Label Tampilan": "Status"})

st.dataframe(belum_lunas_df, use_container_width=True, hide_index=True)
