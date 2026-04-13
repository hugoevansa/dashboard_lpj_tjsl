import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

st.set_page_config(
    page_title="Dashboard Bantuan",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
.detail-card {
    background: linear-gradient(135deg, #fff8fa, #fdf0f4);
    border: 1.5px solid #e8c8d4;
    border-radius: 18px;
    padding: 18px 20px;
    margin: 8px 0 14px 0;
    box-shadow: 0 4px 20px rgba(92,18,41,0.08);
}

.detail-title {
    font-size: 1.02rem;
    font-weight: 900;
    color: var(--maroon-dark);
    margin-bottom: 12px;
}

.detail-grid {
    display: grid;
    grid-template-columns: 180px 1fr;
    gap: 8px 14px;
    align-items: start;
}

.detail-label {
    font-weight: 800;
    color: var(--muted);
}

.detail-value {
    color: var(--text);
    font-weight: 600;
}

.detail-link {
    display: inline-block;
    margin-top: 12px;
    background: linear-gradient(180deg, var(--maroon) 0%, var(--maroon-dark) 100%);
    color: white !important;
    padding: 9px 14px;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 800;
    font-size: 0.88rem;
}
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&family=DM+Mono:wght@500&display=swap');

:root {
    --maroon:       #7c1f3f;
    --maroon-dark:  #5a1229;
    --maroon-mid:   #a14f6a;
    --maroon-soft:  #f5e8ed;
    --bg:           #f6eef2;
    --card:         #ffffff;
    --line:         #e8d0da;
    --text:         #2a0d18;
    --muted:        #8a6672;
    --success:      #1b7a45;
    --warning:      #92600a;
    --danger:       #b42318;
    --info:         #175cd3;
    --shadow:       0 4px 24px rgba(92,18,41,0.10);
    --radius:       18px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text);
}

.stApp {
    background: var(--bg);
}

.block-container {
    padding: 0.5rem 2rem 2rem 2rem !important;
    max-width: 1440px !important;
}

footer { visibility: hidden; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--maroon-dark) 0%, var(--maroon) 100%) !important;
}
section[data-testid="stSidebar"] * { color: #fff !important; }

div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

div[data-testid="stPlotlyChart"] {
    border-radius: var(--radius);
    overflow: hidden;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: 12px !important;
    border: 1.5px solid var(--line) !important;
    background: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
}

.page-header {
    background: linear-gradient(135deg, var(--maroon-dark) 0%, var(--maroon) 60%, var(--maroon-mid) 100%);
    border-radius: 22px;
    padding: 22px 28px;
    margin-top: 14px;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow: 0 8px 32px rgba(92,18,41,0.22);
}

.page-header-icon {
    font-size: 2.2rem;
    background: rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 10px 14px;
}

.page-header-title {
    color: #fff;
    font-size: 1.7rem;
    font-weight: 900;
    line-height: 1.1;
    margin: 0;
}

.page-header-sub {
    color: rgba(255,255,255,0.75);
    font-size: 0.9rem;
    margin-top: 3px;
}

.kpi-wrap {
    background: #fff;
    border-radius: var(--radius);
    border: 1.5px solid var(--line);
    box-shadow: var(--shadow);
    padding: 18px 20px 14px 20px;
    position: relative;
    overflow: hidden;
    height: 100%;
}

.kpi-wrap::after {
    content: "";
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 5px;
    background: linear-gradient(180deg, var(--maroon) 0%, var(--maroon-mid) 100%);
    border-radius: 4px 0 0 4px;
}

.kpi-label {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 900;
    color: var(--text);
    line-height: 1.1;
}

.kpi-note {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 6px;
}

.panel-title {
    font-size: 1.05rem;
    font-weight: 900;
    color: var(--text);
    margin-bottom: 2px;
}

.panel-sub {
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 10px;
}

.mini-stat {
    background: var(--maroon-soft);
    border: 1px solid #e2c4cf;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
}

.mini-stat-label {
    font-size: 0.8rem;
    color: var(--muted);
    font-weight: 600;
    margin-bottom: 4px;
}

.mini-stat-value {
    font-size: 1.55rem;
    font-weight: 900;
    color: var(--maroon);
}

.section-head {
    font-size: 1.15rem;
    font-weight: 900;
    color: var(--text);
    margin: 0;
    padding: 0;
}

.section-sub {
    font-size: 0.86rem;
    color: var(--muted);
    margin-top: 2px;
    margin-bottom: 10px;
}

.filter-label {
    font-size: 0.78rem;
    font-weight: 800;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
}

.note-box {
    background: linear-gradient(135deg, #fff8fa, #fdf0f4);
    border: 1.5px solid #e8c8d4;
    border-radius: 16px;
    padding: 14px 18px;
    font-size: 0.9rem;
    color: var(--text);
}
.note-box b { color: var(--maroon); }

.chip {
    display: inline-block;
    padding: 4px 11px;
    border-radius: 999px;
    font-size: 0.77rem;
    font-weight: 800;
    white-space: nowrap;
}
.chip-lunas      { background: #e6f5ec; color: var(--success); border: 1px solid #b0dfc0; }
.chip-belum      { background: #fff4e0; color: var(--warning); border: 1px solid #f0d49a; }
.chip-jatuh      { background: #fde8ec; color: var(--danger);  border: 1px solid #f0bfc9; }
.chip-chat       { background: #eef4ff; color: var(--info); border: 1px solid #c7d7fe; }
.chip-menunggu   { background: #eef2ff; color: #4338ca; border: 1px solid #c7d2fe; }
.chip-follow     { background: #fff7e6; color: #b36b00; border: 1px solid #f1d193; }
.chip-blacklist  { background: #111827; color: #fff; border: 1px solid #374151; }
.chip-muted      { background: #f5f5f5; color: #6b7280; border: 1px solid #d1d5db; }

.tbl-wrap {
    border-radius: 16px;
    border: 1.5px solid var(--line);
    box-shadow: var(--shadow);
    overflow: hidden;
}

.tbl-scroll {
    max-height: 360px;
    overflow-y: auto;
    overflow-x: auto;
    border-radius: 0 0 14px 14px;
}

.tbl-scroll::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
.tbl-scroll::-webkit-scrollbar-track {
    background: #f5eaef;
    border-radius: 10px;
}
.tbl-scroll::-webkit-scrollbar-thumb {
    background: var(--maroon-mid);
    border-radius: 10px;
}
.tbl-scroll::-webkit-scrollbar-thumb:hover {
    background: var(--maroon);
}

.tbl {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
}

.tbl thead {
    position: sticky;
    top: 0;
    z-index: 2;
}

.tbl th {
    background: linear-gradient(180deg, var(--maroon) 0%, var(--maroon-dark) 100%);
    color: #fff;
    font-weight: 800;
    padding: 11px 14px;
    text-align: left;
    white-space: nowrap;
    font-size: 13px;
}

.tbl td {
    padding: 10px 14px;
    border-bottom: 1px solid #f2e2e8;
    color: var(--text);
    vertical-align: middle;
    white-space: nowrap;
}

.tbl tr:last-child td { border-bottom: none; }
.tbl tr:nth-child(even) td { background: #fffafc; }
.tbl tr:hover td { background: #fff5f8; }

.footer {
    color: var(--muted);
    font-size: 0.82rem;
    text-align: center;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS CONFIG ────────────────────────────────────────────────────
SHEET_ID = "1wi4id0XqYlTuw_KO89-cOLSPTFAQ6ODv_tH09LK_2Ao"
GID      = "0"
CSV_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
GVIZ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_rupiah(x):
    if pd.isna(x):
        return "-"
    return "Rp {:,}".format(int(float(x))).replace(",", ".")

def fmt_tgl(x):
    if pd.isna(x):
        return "-"
    bulan = {
        1:"Januari", 2:"Februari", 3:"Maret", 4:"April",
        5:"Mei", 6:"Juni", 7:"Juli", 8:"Agustus",
        9:"September", 10:"Oktober", 11:"November", 12:"Desember"
    }
    return f"{x.day} {bulan[x.month]} {x.year}"

def clean_currency(s):
    return pd.to_numeric(
        s.astype(str)
         .str.replace("Rp", "", regex=False)
         .str.replace(".", "", regex=False)
         .str.replace(",", "", regex=False)
         .str.replace(" ", "", regex=False)
         .str.strip(),
        errors="coerce"
    )

def clean_phone(s):
    s = s.astype(str).str.strip()
    return (
        s.replace(["nan", "NaN", "None", "<NA>"], "", regex=False)
         .str.replace(".0", "", regex=False)
    )

def normalize_status(st_val):
    v = str(st_val).strip().lower()
    return "Lunas" if v in ["lunas", "sudah lunas"] else "Belum Lunas"

def normalize_chat(val):
    v = str(val).strip().lower()
    if v in ["sudah di chat", "sudah", "sudah chat", "sudah dichat", "sudah dihubungi"]:
        return "Sudah di Chat"
    return "Belum di Chat"

def chip_status(val):
    if val == "Lunas":
        return '<span class="chip chip-lunas">Lunas</span>'
    if val == "Jatuh Tempo":
        return '<span class="chip chip-jatuh">Jatuh Tempo</span>'
    return '<span class="chip chip-belum">Belum Lunas</span>'

def chip_chat(val):
    if val == "Sudah di Chat":
        return '<span class="chip chip-chat">Sudah di Chat</span>'
    return '<span class="chip chip-muted">Belum di Chat</span>'

def chip_aksi_chat(val):
    if val == "Menunggu LPJ":
        return '<span class="chip chip-menunggu">Menunggu LPJ</span>'
    if val == "Follow Up LPJ":
        return '<span class="chip chip-follow">Follow Up LPJ</span>'
    if val == "BlackList":
        return '<span class="chip chip-blacklist">BlackList</span>'
    return '<span class="chip chip-muted">-</span>'

def df_to_html(df, max_height=360):
    rows = ""
    for _, r in df.iterrows():
        cells = "".join(f"<td>{v}</td>" for v in r)
        rows += f"<tr>{cells}</tr>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return (
        f'<div class="tbl-wrap">'
        f'<div class="tbl-scroll" style="max-height:{max_height}px">'
        f'<table class="tbl"><thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows}</tbody></table>'
        f'</div></div>'
    )

def hitung_jeda_chat(tanggal_chat, chat_status, today):
    if chat_status != "Sudah di Chat" or pd.isna(tanggal_chat):
        return None
    selisih = (today - tanggal_chat).days
    return max(selisih, 0)

def label_jeda_chat(hari):
    if hari is None:
        return ""
    if 7 <= hari < 14:
        return "1 Minggu"
    if 14 <= hari < 21:
        return "2 Minggu"
    if hari >= 21:
        return "3 Minggu"
    return "< 1 Minggu"

def klasifikasi_chat(hari):
    if hari is None:
        return ""
    if 7 <= hari < 14:
        return "Menunggu LPJ"
    if 14 <= hari < 21:
        return "Follow Up LPJ"
    if hari >= 21:
        return "BlackList"
    return ""

@st.cache_data(ttl=300)
def load_data():
    for url in [CSV_URL, GVIZ_URL]:
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            df = pd.read_csv(StringIO(r.text), dtype=str)
            if not df.empty:
                return df
        except Exception:
            continue
    raise Exception("Gagal mengambil data dari Google Sheets.")

DOKUMEN_BANTUAN_URL = "https://drive.google.com/drive/folders/1lK2DACKjYI4vLVDhlW-XtXyIal_cpmA4?usp=sharing"

def nama_penerima_dari_row(row):
    # Karena sheet belum punya kolom "Nama Penerima", sementara pakai PIC sebagai fallback
    # Kalau nanti kamu tambahkan kolom "Nama Penerima", tinggal ganti fungsi ini.
    return row.get("PIC", "-") if pd.notna(row.get("PIC", None)) else "-"


def render_prioritas_interaktif(df, title_key="prioritas"):
    if df.empty:
        st.info("Tidak ada data.")
        return

    for idx, row in df.reset_index(drop=True).iterrows():
        nama_bantuan = row.get("Nama Bantuan", "-")
        jumlah = fmt_rupiah(row.get("Jumlah Bantuan (Rp)", None))
        aksi_chat = row.get("Klasifikasi Chat", "")
        tanggal_chat = fmt_tgl(row.get("Tanggal Chat", pd.NaT)) if pd.notna(row.get("Tanggal Chat", pd.NaT)) else "-"
        jeda_chat = row.get("Label Jeda Chat", "")
        if not jeda_chat:
            jeda_chat = "-"

        aksi_chip = chip_aksi_chat(aksi_chat)

        judul = f"{nama_bantuan} | {jumlah}"

        with st.expander(judul, expanded=False):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])

            with c1:
                st.markdown(f"**Informasi Nama**  \n{nama_bantuan}")
            with c2:
                st.markdown(f"**Jumlah**  \n{jumlah}")
            with c3:
                st.markdown(f"**Aksi Chat**  \n{aksi_chip}", unsafe_allow_html=True)
            with c4:
                st.markdown(f"**Tanggal Chat**  \n{tanggal_chat}")
            with c5:
                st.markdown(f"**Jeda Chat**  \n{jeda_chat}")

            st.markdown(f"""
            <div class="detail-card">
                <div class="detail-title">Detail Penerima Bantuan</div>
                <div class="detail-grid">
                    <div class="detail-label">Nama Bantuan</div>
                    <div class="detail-value">{nama_bantuan}</div>

                    <div class="detail-label">Jumlah Bantuan</div>
                    <div class="detail-value">{jumlah}</div>

                    <div class="detail-label">Nama Penerima</div>
                    <div class="detail-value">{nama_penerima_dari_row(row)}</div>

                    <div class="detail-label">No HP</div>
                    <div class="detail-value">{row.get("No Hp Penerima", "-") if row.get("No Hp Penerima", "") != "" else "-"}</div>

                    <div class="detail-label">Tanggal Di Bantu</div>
                    <div class="detail-value">{fmt_tgl(row.get("Tanggal Dibantu", pd.NaT)) if pd.notna(row.get("Tanggal Dibantu", pd.NaT)) else "-"}</div>

                    <div class="detail-label">Tenggat</div>
                    <div class="detail-value">{fmt_tgl(row.get("Tenggat", pd.NaT)) if pd.notna(row.get("Tenggat", pd.NaT)) else "-"}</div>

                    <div class="detail-label">Telat Berapa Hari</div>
                    <div class="detail-value">{int(row.get("Terlambat Hari", 0))} hari</div>

                    <div class="detail-label">Aksi Chat</div>
                    <div class="detail-value">{aksi_chip}</div>
                </div>

                <a class="detail-link" href="{DOKUMEN_BANTUAN_URL}" target="_blank">
                    📁 Link Dokumen Bantuan
                </a>
            </div>
            """, unsafe_allow_html=True)

# ─── LOAD & PREPARE ──────────────────────────────────────────────────────────
try:
    data = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

data.columns = [str(c).strip() for c in data.columns]

aliases = {
    "No HP Penerima": "No Hp Penerima",
    "No Hp": "No Hp Penerima",
    "No HP": "No Hp Penerima",
    "Nomor HP Penerima": "No Hp Penerima",
    "jumlah Bantuan (Rp)": "Jumlah Bantuan (Rp)",
    "Tanggal dibantu": "Tanggal Dibantu",
    "StatusChat": "Status Chat",
    "Status_Chat": "Status Chat"
}
data = data.rename(columns={k: v for k, v in aliases.items() if k in data.columns})

required_cols = [
    "Nama Bantuan", "Jumlah Bantuan (Rp)", "Tanggal Dibantu", "Tenggat",
    "PIC", "No Hp Penerima", "Status", "Chat", "Status Chat"
]

for col in required_cols:
    if col not in data.columns:
        data[col] = ""

data["Nama Bantuan"]         = data["Nama Bantuan"].astype(str).str.strip()
data["PIC"]                  = data["PIC"].astype(str).str.strip()
data["No Hp Penerima"]       = clean_phone(data["No Hp Penerima"])
data["Status"]               = data["Status"].astype(str).str.strip()
data["Chat"]                 = data["Chat"].astype(str).str.strip()
data["Status Chat"]          = data["Status Chat"].astype(str).str.strip()

data["Jumlah Bantuan (Rp)"]  = clean_currency(data["Jumlah Bantuan (Rp)"])
data["Tanggal Dibantu"]      = pd.to_datetime(data["Tanggal Dibantu"], errors="coerce", dayfirst=True)
data["Tenggat"]              = pd.to_datetime(data["Tenggat"], errors="coerce", dayfirst=True)

# Status Chat sekarang adalah tanggal
data["Tanggal Chat"]         = pd.to_datetime(data["Status Chat"], errors="coerce", dayfirst=True)

data["Tahun"]                = data["Tanggal Dibantu"].dt.year
data["Status Pembayaran"]    = data["Status"].apply(normalize_status)
data["Chat Normal"]          = data["Chat"].apply(normalize_chat)

today = pd.Timestamp.today().normalize()

data["Kondisi Tenggat"] = data.apply(
    lambda r: "Jatuh Tempo"
    if r["Status Pembayaran"] == "Belum Lunas" and pd.notna(r["Tenggat"]) and r["Tenggat"] < today
    else "Belum Jatuh Tempo",
    axis=1
)

data["Terlambat Hari"] = data["Tenggat"].apply(
    lambda x: (today - x).days if pd.notna(x) and x < today else 0
)

data["Hari Setelah Chat"] = data.apply(
    lambda r: hitung_jeda_chat(r["Tanggal Chat"], r["Chat Normal"], today),
    axis=1
)

data["Label Jeda Chat"] = data["Hari Setelah Chat"].apply(label_jeda_chat)
data["Klasifikasi Chat"] = data["Hari Setelah Chat"].apply(klasifikasi_chat)

data["Label Tampilan"] = data.apply(
    lambda r: "Lunas" if r["Status Pembayaran"] == "Lunas"
    else ("Jatuh Tempo" if r["Kondisi Tenggat"] == "Jatuh Tempo" else "Belum Lunas"),
    axis=1
)

# ═════════════════════════════════════════════════════════════════════════════
#  LAYOUT
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="page-header">
    <div class="page-header-icon">📊</div>
    <div>
        <div class="page-header-title">DASHBOARD BANTUAN</div>
        <div class="page-header-sub">Monitoring status bantuan, status chat, dan prioritas tindak lanjut</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ── FILTER ───────────────────────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns([2, 1, 1, 1], gap="medium")

with f2:
    st.markdown('<div class="filter-label">TAHUN</div>', unsafe_allow_html=True)
    selected_tahun = st.selectbox(
        "Tahun",
        ["Semua", 2023, 2024, 2025, 2026],
        label_visibility="collapsed"
    )

with f3:
    st.markdown('<div class="filter-label">KONDISI</div>', unsafe_allow_html=True)
    selected_status = st.selectbox(
        "Kondisi",
        ["Semua", "Lunas", "Belum Lunas", "Jatuh Tempo"],
        label_visibility="collapsed"
    )

with f4:
    st.markdown('<div class="filter-label">STATUS CHAT</div>', unsafe_allow_html=True)
    selected_chat = st.selectbox(
        "Status Chat",
        ["Semua", "Belum di Chat", "Sudah di Chat", "Menunggu LPJ", "Follow Up LPJ", "BlackList"],
        label_visibility="collapsed"
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

if selected_chat == "Belum di Chat":
    filtered = filtered[filtered["Chat Normal"] == "Belum di Chat"]
elif selected_chat == "Sudah di Chat":
    filtered = filtered[filtered["Chat Normal"] == "Sudah di Chat"]
elif selected_chat == "Menunggu LPJ":
    filtered = filtered[filtered["Klasifikasi Chat"] == "Menunggu LPJ"]
elif selected_chat == "Follow Up LPJ":
    filtered = filtered[filtered["Klasifikasi Chat"] == "Follow Up LPJ"]
elif selected_chat == "BlackList":
    filtered = filtered[filtered["Klasifikasi Chat"] == "BlackList"]

# ── KPI ──────────────────────────────────────────────────────────────────────
total_penerima    = len(filtered)
total_lunas       = len(filtered[filtered["Status Pembayaran"] == "Lunas"])
total_belum_lunas = len(filtered[filtered["Status Pembayaran"] == "Belum Lunas"])
total_jatuh_tempo = len(filtered[filtered["Kondisi Tenggat"] == "Jatuh Tempo"])
total_menunggu    = len(filtered[filtered["Klasifikasi Chat"] == "Menunggu LPJ"])
total_follow_up   = len(filtered[filtered["Klasifikasi Chat"] == "Follow Up LPJ"])
total_blacklist   = len(filtered[filtered["Klasifikasi Chat"] == "BlackList"])

k1, k2, k3, k4, k5, k6 = st.columns(6, gap="medium")

cards = [
    ("Total Penerima", str(total_penerima), "Jumlah penerima bantuan"),
    ("Sudah Lunas", str(total_lunas), "Selesai dikembalikan"),
    ("Belum Lunas", str(total_belum_lunas), "Belum selesai"),
    ("Jatuh Tempo", str(total_jatuh_tempo), "Perlu segera follow-up"),
    ("Menunggu LPJ", str(total_menunggu), "Sudah 1 minggu setelah chat"),
    ("Follow Up / BlackList", f"{total_follow_up} / {total_blacklist}", "2 minggu / 3 minggu ke atas"),
]

for col, (label_txt, val, note) in zip([k1, k2, k3, k4, k5, k6], cards):
    with col:
        st.markdown(f"""
        <div class="kpi-wrap">
            <div class="kpi-label">{label_txt}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ── CHART ────────────────────────────────────────────────────────────────────
MAROON_COLORS = {
    "Lunas": "#7c1f3f",
    "Belum Lunas": "#c07090",
    "Jatuh Tempo": "#e8c0cf",
}

chart_df = filtered["Status Pembayaran"].value_counts().reset_index()
chart_df.columns = ["Status", "Jumlah"]

status_dist_df = (
    filtered["Label Tampilan"]
    .value_counts()
    .reindex(["Lunas", "Belum Lunas", "Jatuh Tempo"], fill_value=0)
    .reset_index()
)
status_dist_df.columns = ["Kategori", "Jumlah"]

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=8, b=8, l=0, r=0),
    font=dict(family="DM Sans, sans-serif", color="#2a0d18"),
)

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Komposisi Status</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Lunas vs belum lunas</div>', unsafe_allow_html=True)
        if not chart_df.empty:
            fig = px.pie(chart_df, names="Status", values="Jumlah", hole=0.62,
                         color="Status", color_discrete_map=MAROON_COLORS)
            fig.update_traces(textposition="inside", textinfo="percent",
                              marker=dict(line=dict(color="white", width=3)))
            fig.update_layout(**PLOTLY_BASE, height=280)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Tidak ada data.")

with c2:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Distribusi Status</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Lunas, belum lunas, dan jatuh tempo</div>', unsafe_allow_html=True)

        if not status_dist_df.empty:
            fig2 = px.bar(
                status_dist_df,
                x="Kategori",
                y="Jumlah",
                color="Kategori",
                color_discrete_map={
                    "Lunas": "#7c1f3f",
                    "Belum Lunas": "#c07090",
                    "Jatuh Tempo": "#e8c0cf",
                }
            )
            fig2.update_layout(
                **PLOTLY_BASE,
                height=280,
                xaxis_title="",
                yaxis_title="Jumlah",
                showlegend=False
            )
            fig2.update_traces(marker_line_width=0)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Tidak ada data.")

with c3:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Ringkasan Cepat</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Prioritas tindak lanjut</div>', unsafe_allow_html=True)

        pct_jt = round((total_jatuh_tempo / total_penerima) * 100, 1) if total_penerima else 0
        pct_fu = round((total_follow_up / total_penerima) * 100, 1) if total_penerima else 0
        pct_bl = round((total_blacklist / total_penerima) * 100, 1) if total_penerima else 0

        for label_ms, value_ms in [
            ("Persentase Jatuh Tempo", f"{pct_jt}%"),
            ("Persentase Follow Up LPJ", f"{pct_fu}%"),
            ("Persentase BlackList", f"{pct_bl}%"),
        ]:
            st.markdown(f"""
            <div class="mini-stat">
                <div class="mini-stat-label">{label_ms}</div>
                <div class="mini-stat-value">{value_ms}</div>
            </div>
            """, unsafe_allow_html=True)


st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── TABEL PRIORITAS ──────────────────────────────────────────────────────────
# ── TABEL PRIORITAS ──────────────────────────────────────────────────────────
prioritas = (
    filtered[
        (filtered["Status Pembayaran"] == "Belum Lunas") &
        (filtered["Kondisi Tenggat"] == "Jatuh Tempo")
    ]
    .copy()
    .sort_values(["Terlambat Hari", "Tenggat"], ascending=[False, True])
)

st.markdown('<div class="section-head">🔴 Penerima Bantuan Jatuh Tempo — Segera Hubungi</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-sub">{len(prioritas)} penerima bantuan perlu segera dihubungi</div>', unsafe_allow_html=True)

if prioritas.empty:
    st.success("✅ Tidak ada penerima bantuan yang jatuh tempo.")
else:
    prioritas_belum_chat = prioritas[prioritas["Chat Normal"] == "Belum di Chat"].copy()
    prioritas_sudah_chat = prioritas[prioritas["Chat Normal"] == "Sudah di Chat"].copy()

    kiri, kanan = st.columns(2, gap="large")

    with kiri:
        st.markdown('<div class="section-head">📩 Belum di Chat</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-sub">{len(prioritas_belum_chat)} penerima bantuan belum dihubungi</div>',
            unsafe_allow_html=True
        )
        render_prioritas_interaktif(prioritas_belum_chat, title_key="belum_chat")

    with kanan:
        st.markdown('<div class="section-head">💬 Sudah di Chat</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-sub">{len(prioritas_sudah_chat)} penerima bantuan sudah dihubungi</div>',
            unsafe_allow_html=True
        )
        render_prioritas_interaktif(prioritas_sudah_chat, title_key="sudah_chat")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    # =========================
    # KANAN — SUDAH DI CHAT
    # =========================
    with col_kanan:
        st.markdown('<div class="section-head">💬 Sudah di Chat</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-sub">{len(prioritas_sudah_chat)} penerima bantuan sudah dihubungi</div>',
            unsafe_allow_html=True
        )

        if prioritas_sudah_chat.empty:
            st.info("Tidak ada penerima bantuan di kategori ini.")
        else:
            pv_sudah = prioritas_sudah_chat[
                [
                    "Nama Bantuan", "Jumlah Bantuan (Rp)", "Tanggal Dibantu", "Tenggat",
                    "PIC", "No Hp Penerima", "Tanggal Chat",
                    "Label Jeda Chat", "Klasifikasi Chat", "Terlambat Hari"
                ]
            ].copy()

            pv_sudah["Jumlah Bantuan (Rp)"] = pv_sudah["Jumlah Bantuan (Rp)"].apply(fmt_rupiah)
            pv_sudah["Tanggal Dibantu"]     = pv_sudah["Tanggal Dibantu"].apply(fmt_tgl)
            pv_sudah["Tenggat"]             = pv_sudah["Tenggat"].apply(fmt_tgl)
            pv_sudah["Tanggal Chat"]        = pv_sudah["Tanggal Chat"].apply(fmt_tgl)
            pv_sudah["No Hp Penerima"]      = pv_sudah["No Hp Penerima"].replace("", "-")
            pv_sudah["Jeda Chat"]           = pv_sudah["Label Jeda Chat"].replace("", "-")
            pv_sudah["Aksi Chat"]           = pv_sudah["Klasifikasi Chat"].apply(chip_aksi_chat)
            pv_sudah["Terlambat Hari"]      = pv_sudah["Terlambat Hari"].apply(lambda x: f"{int(x)} hari")
            pv_sudah["Status"]              = '<span class="chip chip-jatuh">Jatuh Tempo</span>'

            pv_sudah = pv_sudah.drop(columns=["Label Jeda Chat", "Klasifikasi Chat"])

            pv_sudah = pv_sudah[
                [
                    "Nama Bantuan", "Jumlah Bantuan (Rp)", "Tanggal Dibantu", "Tenggat",
                    "PIC", "No Hp Penerima", "Tanggal Chat", "Jeda Chat",
                    "Aksi Chat", "Terlambat Hari", "Status"
                ]
            ]

            st.markdown(df_to_html(pv_sudah, max_height=360), unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── SEMUA DATA ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-head">📋 Data Semua Penerima Bantuan</div>', unsafe_allow_html=True)

search = st.text_input(
    "Cari",
    label_visibility="collapsed",
    placeholder="🔍 Cari nama bantuan, PIC, nomor HP, status, atau status chat..."
)

table_df = filtered.copy()

if search:
    kw = search.lower()
    table_df = table_df[
        table_df["Nama Bantuan"].astype(str).str.lower().str.contains(kw, na=False) |
        table_df["PIC"].astype(str).str.lower().str.contains(kw, na=False) |
        table_df["No Hp Penerima"].astype(str).str.lower().str.contains(kw, na=False) |
        table_df["Label Tampilan"].astype(str).str.lower().str.contains(kw, na=False) |
        table_df["Chat Normal"].astype(str).str.lower().str.contains(kw, na=False) |
        table_df["Label Jeda Chat"].astype(str).str.lower().str.contains(kw, na=False) |
        table_df["Klasifikasi Chat"].astype(str).str.lower().str.contains(kw, na=False)
    ]

st.markdown(f'<div class="section-sub">Menampilkan {len(table_df)} dari {len(filtered)} penerima bantuan</div>', unsafe_allow_html=True)

disp = table_df[
    [
        "Nama Bantuan", "Jumlah Bantuan (Rp)", "Tanggal Dibantu", "Tenggat",
        "PIC", "No Hp Penerima", "Tahun", "Label Tampilan", "Klasifikasi Chat"
    ]
].copy()

disp["Jumlah Bantuan (Rp)"] = disp["Jumlah Bantuan (Rp)"].apply(fmt_rupiah)
disp["Tanggal Dibantu"]     = disp["Tanggal Dibantu"].apply(fmt_tgl)
disp["Tenggat"]             = disp["Tenggat"].apply(fmt_tgl)
disp["No Hp Penerima"]      = disp["No Hp Penerima"].replace("", "-")
disp["Status"]              = disp["Label Tampilan"].apply(chip_status)

disp = disp.drop(columns=["Label Tampilan", "Klasifikasi Chat"])

disp = disp[
    [
        "Nama Bantuan", "Jumlah Bantuan (Rp)", "Tanggal Dibantu", "Tenggat",
        "PIC", "No Hp Penerima", "Tahun", "Status"
    ]
]

st.markdown(df_to_html(disp), unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
