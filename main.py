import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib.parse
from io import StringIO

st.set_page_config(
    page_title="Dashboard Bantuan",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from sidebar_component import render_sidebar

# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
if "detail_nama" not in st.session_state:
    st.session_state.detail_nama = None
if "notif_dismissed" not in st.session_state:
    st.session_state.notif_dismissed = set()
if "toast_shown" not in st.session_state:
    st.session_state.toast_shown = False

# ─── HANDLE QUERY PARAM ───────────────────────────────────────────────────────
_qp = st.query_params

if "detail" in _qp:
    _nama = urllib.parse.unquote(_qp["detail"])
    st.session_state.detail_nama = _nama
    st.query_params.clear()
    st.switch_page("pages/database.py")

if "dismiss" in _qp:
    _dismiss_nama = urllib.parse.unquote(_qp["dismiss"])
    st.session_state.notif_dismissed.add(_dismiss_nama)
    st.session_state.toast_shown = False
    st.query_params.clear()
    st.rerun()

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@400;600;700;800&display=swap');

:root {
    --crimson:      #8B1A3A;
    --crimson-dark: #5E0F26;
    --crimson-mid:  #B5476A;
    --crimson-pale: #F9EEF2;
    --crimson-tint: #FDF5F7;
    --bg:           #F7F3F5;
    --surface:      #FFFFFF;
    --border:       #EAD8DF;
    --border-dark:  #D9BEC9;
    --text-primary: #1C0A12;
    --text-secondary:#6B4558;
    --text-muted:   #9E7080;
    --success:      #5E0F26;
    --success-bg:   #F9EEF2;
    --success-bdr:  #D9BEC9;
    --warning:      #8B1A3A;
    --warning-bg:   #FDF0F4;
    --warning-bdr:  #C4849A;
    --danger:       #5E0F26;
    --danger-bg:    #F9EEF2;
    --danger-bdr:   #D9BEC9;
    --info:         #8B1A3A;
    --info-bg:      #FDF0F4;
    --info-bdr:     #C4849A;
    --indigo:       #6B1530;
    --indigo-bg:    #FAF0F3;
    --indigo-bdr:   #CFAAB8;
    --amber:        #7C1F3F;
    --amber-bg:     #FDF5F7;
    --amber-bdr:    #D9BEC9;
    --shadow-sm:    0 1px 3px rgba(92,18,41,0.08), 0 1px 2px rgba(92,18,41,0.04);
    --shadow-md:    0 4px 16px rgba(92,18,41,0.10), 0 2px 6px rgba(92,18,41,0.05);
    --shadow-lg:    0 12px 40px rgba(92,18,41,0.14), 0 4px 12px rgba(92,18,41,0.06);
    --radius-sm:    10px;
    --radius-md:    16px;
    --radius-lg:    22px;
    --radius-xl:    28px;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text-primary);
}

.stApp { background: var(--bg); }

.block-container {
    padding: 0 2rem 3rem 2rem !important;
    max-width: 1480px !important;
}

footer { visibility: hidden; }

div[data-testid="stPlotlyChart"] { border-radius: var(--radius-md); overflow: hidden; }

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--border-dark) !important;
    background: #fff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.88rem !important;
}

/* ── HERO HEADER ── */
.hero-header {
    background: linear-gradient(135deg, var(--crimson-dark) 0%, var(--crimson) 55%, var(--crimson-mid) 100%);
    border-radius: var(--radius-xl);
    padding: 28px 32px;
    margin: 16px 0 20px 0;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: "";
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.hero-header::after {
    content: "";
    position: absolute;
    bottom: -60px; right: 120px;
    width: 160px; height: 160px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero-icon {
    font-size: 2rem;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: var(--radius-md);
    padding: 12px 16px;
    line-height: 1;
    flex-shrink: 0;
}
.hero-eyebrow {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.6);
    margin-bottom: 4px;
}
.hero-title {
    font-family: 'Sora', sans-serif;
    color: #fff;
    font-size: 1.6rem;
    font-weight: 800;
    line-height: 1.15;
    margin: 0;
    letter-spacing: -0.02em;
}
.hero-sub {
    color: rgba(255,255,255,0.65);
    font-size: 0.84rem;
    margin-top: 5px;
    font-weight: 500;
}
.hero-right { margin-left: auto; position: relative; z-index: 1; }

/* ── FILTER BAR ── */
.filter-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 5px;
}

/* ── KPI CARDS ── */
.kpi-card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
    height: 100%;
}
.kpi-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
.kpi-card-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--crimson-dark), var(--crimson-mid));
}
.kpi-card-accent-success { background: linear-gradient(90deg, #5E0F26, #8B1A3A); }
.kpi-card-accent-warning { background: linear-gradient(90deg, #7C1F3F, #B5476A); }
.kpi-card-accent-info    { background: linear-gradient(90deg, #8B1A3A, #C4617F); }
.kpi-card-accent-indigo  { background: linear-gradient(90deg, #6B1530, #A8355A); }
.kpi-card-accent-amber   { background: linear-gradient(90deg, #5E0F26, #9E3055); }

.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'Sora', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.1;
    letter-spacing: -0.03em;
}
.kpi-note {
    font-size: 0.76rem;
    color: var(--text-muted);
    margin-top: 6px;
    font-weight: 500;
}

/* ── NOMINAL HIGHLIGHT ── */
.nominal-card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    padding: 20px 24px;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
    height: 100%;
}
.nominal-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--crimson-dark), var(--crimson-mid));
}
.nominal-eyebrow {
    font-size: 0.7rem;
    font-weight: 800;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}
.nominal-value {
    font-family: 'Sora', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--crimson-dark);
    line-height: 1.1;
    letter-spacing: -0.03em;
}
.nominal-total {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-top: 4px;
}
.nominal-note {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 8px;
    font-weight: 500;
}

/* ── SECTION HEADER ── */
.section-wrapper { margin-top: 8px; margin-bottom: 12px; }
.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--danger-bg);
    color: var(--danger);
    border: 1px solid var(--danger-bdr);
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 2px 9px;
    min-width: 24px;
}
.section-desc {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 3px;
    font-weight: 500;
}

/* ── PANEL CARDS ── */
.panel {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    padding: 18px 20px 14px 20px;
    box-shadow: var(--shadow-sm);
    height: 100%;
}
.panel-title {
    font-family: 'Sora', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 2px;
    letter-spacing: -0.01em;
}
.panel-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-bottom: 14px;
    font-weight: 500;
}

/* ── TABLE ── */
.tbl-container { border-radius: var(--radius-md); border: 1.5px solid var(--border); box-shadow: var(--shadow-sm); overflow: hidden; }
.tbl-scroll {
    max-height: 360px;
    overflow-y: auto;
    overflow-x: auto;
}
.tbl-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
.tbl-scroll::-webkit-scrollbar-track { background: var(--bg); }
.tbl-scroll::-webkit-scrollbar-thumb { background: var(--border-dark); border-radius: 10px; }
.tbl-scroll::-webkit-scrollbar-thumb:hover { background: var(--crimson-mid); }

.tbl { width: 100%; border-collapse: collapse; font-size: 13px; }
.tbl thead { position: sticky; top: 0; z-index: 2; }
.tbl th {
    background: var(--crimson-dark);
    color: rgba(255,255,255,0.92);
    font-weight: 700;
    padding: 11px 14px;
    text-align: left;
    white-space: nowrap;
    font-size: 11.5px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.tbl td {
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text-primary);
    vertical-align: middle;
    white-space: nowrap;
    font-weight: 500;
}
.tbl tr:last-child td { border-bottom: none; }
.tbl tr:nth-child(even) td { background: var(--crimson-tint); }
.tbl tr:hover td { background: var(--crimson-pale); }

/* ── CHIPS ── */
.chip { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; letter-spacing: 0.01em; }
.chip-lpj          { background: #F0E6EA; color: #5E0F26;  border: 1px solid #C4849A; }
.chip-belum        { background: #FDF5F7; color: #8B1A3A;  border: 1px solid #D9BEC9; }
.chip-jatuh        { background: #F9EEF2; color: #5E0F26;  border: 1px solid #C4849A; font-weight:800; }
.chip-menunggu     { background: #FAF0F3; color: #6B1530;  border: 1px solid #CFAAB8; }
.chip-follow       { background: #F9EEF2; color: #8B1A3A;  border: 1px solid #C4849A; }
.chip-blacklist    { background: #2A0D18; color: #f9fafb;  border: 1px solid #5E0F26; }
.chip-muted        { background: #f5f0f2; color: #9E7080;  border: 1px solid #e5d8dd; }
.chip-konfirmasi   { background: #FDF0F4; color: #7C1F3F;  border: 1px solid #D9BEC9; }
.chip-sudah-followup { background: #FDF5F7; color: #8B1A3A; border: 1px solid #C4849A; }
.chip-lpj-diterima { background: #F0E6EA; color: #5E0F26;  border: 1px solid #C4849A; font-weight:800; }
.chip-bl-konfirmasi { background: #2A0D18; color: #f9fafb; border: 1px solid #5E0F26; }
.chip-belum-diisi  { background: #f5f0f2; color: #9E7080;  border: 1px solid #e0d0d6; font-style: italic; }

/* ── SUB-SECTION HEADERS ── */
.sub-section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1.5px solid var(--border);
}
.sub-section-icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
}
.sub-section-icon-danger  { background: var(--danger-bg); }
.sub-section-icon-success { background: var(--success-bg); }
.sub-section-label { font-weight: 700; font-size: 0.88rem; color: var(--text-primary); }
.sub-section-count {
    margin-left: auto;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-muted);
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 2px 9px;
}

/* ── EMPTY STATE ── */
.empty-state {
    text-align: center;
    padding: 32px 20px;
    color: var(--text-muted);
    font-size: 0.85rem;
    font-weight: 500;
}
.empty-icon { font-size: 2rem; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS CONFIG ────────────────────────────────────────────────────
SHEET_ID = "1wi4id0XqYlTuw_KO89-cOLSPTFAQ6ODv_tH09LK_2Ao"
GID      = "0"
CSV_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
GVIZ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"

VALID_TAHAP = [
    "Menunggu Balasan", "Sudah Konfirmasi", "Sudah Followup",
    "LPJ Diterima", "Blacklist Dikonfirmasi"
]

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_rupiah(x):
    if pd.isna(x): return "-"
    return "Rp {:,}".format(int(float(x))).replace(",", ".")

def fmt_tgl(x):
    if pd.isna(x): return "-"
    bulan = {1:"Januari",2:"Februari",3:"Maret",4:"April",5:"Mei",6:"Juni",
             7:"Juli",8:"Agustus",9:"September",10:"Oktober",11:"November",12:"Desember"}
    return f"{x.day} {bulan[x.month]} {x.year}"

def clean_currency(s):
    return pd.to_numeric(
        s.astype(str)
         .str.replace("Rp","",regex=False).str.replace(".","",regex=False)
         .str.replace(",","",regex=False).str.replace(" ","",regex=False).str.strip(),
        errors="coerce"
    )

def clean_phone(s):
    s = s.astype(str).str.strip()
    return s.replace(["nan","NaN","None","<NA>"],"",regex=False).str.replace(".0","",regex=False)

def normalize_status(st_val):
    v = str(st_val).strip().lower()
    return "LPJ" if v in ["lpj","sudah lpj"] else "Belum LPJ"

def normalize_chat(val):
    v = str(val).strip().lower()
    if v in ["sudah di chat","sudah","sudah chat","sudah dichat","sudah dihubungi"]:
        return "Sudah di Chat"
    return "Belum di Chat"

def chip_status(val):
    if val == "LPJ":         return '<span class="chip chip-lpj">✓ LPJ</span>'
    if val == "Jatuh Tempo": return '<span class="chip chip-jatuh">⚠ Jatuh Tempo</span>'
    return '<span class="chip chip-belum">Belum LPJ</span>'

def chip_aksi_prioritas(val, chat_normal=None):
    if chat_normal == "Belum di Chat":
        return '<span class="chip chip-jatuh">Segera Hubungi</span>'
    if val == "Menunggu LPJ":  return '<span class="chip chip-menunggu">Menunggu LPJ</span>'
    if val == "Follow Up LPJ": return '<span class="chip chip-follow">Follow Up LPJ</span>'
    if val == "BlackList":     return '<span class="chip chip-blacklist">Blacklist</span>'
    return '<span class="chip chip-muted">—</span>'

def chip_tahap_followup(val):
    if not val or val in ["nan", "", "-"]:
        return '<span class="chip chip-belum-diisi">Belum diisi</span>'
    if val == "Blacklist Dikonfirmasi":
        return '<span class="chip chip-bl-konfirmasi">✓ Blacklist</span>'
    if val == "LPJ Diterima":
        return '<span class="chip chip-lpj-diterima">✓ LPJ Diterima</span>'
    if val == "Sudah Konfirmasi":
        return '<span class="chip chip-konfirmasi">✓ Konfirmasi</span>'
    if val == "Sudah Followup":
        return '<span class="chip chip-sudah-followup">Sudah Followup</span>'
    if val == "Menunggu Balasan":
        return '<span class="chip chip-menunggu">Menunggu Balasan</span>'
    return '<span class="chip chip-muted">—</span>'

def df_to_html(df, max_height=360):
    rows = ""
    for _, r in df.iterrows():
        cells = "".join(f"<td>{v}</td>" for v in r)
        rows += f"<tr>{cells}</tr>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return (
        f'<div class="tbl-container">'
        f'<div class="tbl-scroll" style="max-height:{max_height}px">'
        f'<table class="tbl"><thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows}</tbody></table>'
        f'</div></div>'
    )

def detail_btn_html(nama):
    enc = urllib.parse.quote(nama)
    return (
        f'<a href="?detail={enc}" target="_self" '
        f'style="display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:7px;'
        f'background:var(--crimson);color:#fff;font-size:11.5px;font-weight:700;'
        f'text-decoration:none;white-space:nowrap;letter-spacing:0.01em;">Detail →</a>'
    )

def hitung_jeda_chat(tanggal_chat, chat_status, today):
    if chat_status != "Sudah di Chat" or pd.isna(tanggal_chat): return None
    return max((today - tanggal_chat).days, 0)

def label_jeda_chat(hari):
    if hari is None: return ""
    if 7 <= hari < 14:  return "1 Minggu"
    if 14 <= hari < 21: return "2 Minggu"
    if hari >= 21:      return "3 Minggu"
    return "< 1 Minggu"

def klasifikasi_chat(hari):
    if hari is None:    return ""
    if 0 <= hari < 14:  return "Menunggu LPJ"
    if 14 <= hari < 21: return "Follow Up LPJ"
    if hari >= 21:      return "BlackList"
    return ""

@st.cache_data(ttl=60)
def load_data():
    for url in [CSV_URL, GVIZ_URL]:
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            df = pd.read_csv(StringIO(r.text), dtype=str)
            if not df.empty: return df
        except Exception:
            continue
    raise Exception("Gagal mengambil data dari Google Sheets.")

# ─── LOAD & PREPARE ──────────────────────────────────────────────────────────
try:
    data = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

data.columns = [str(c).strip() for c in data.columns]
aliases = {
    "No HP Penerima":"No Hp Penerima","No Hp":"No Hp Penerima","No HP":"No Hp Penerima",
    "Nomor HP Penerima":"No Hp Penerima","jumlah Bantuan (Rp)":"Jumlah Bantuan (Rp)",
    "Tanggal dibantu":"Tanggal Dibantu","StatusChat":"Status Chat","Status_Chat":"Status Chat"
}
data = data.rename(columns={k:v for k,v in aliases.items() if k in data.columns})

required_cols = ["Nama Bantuan","Jumlah Bantuan (Rp)","Tanggal Dibantu","Tenggat",
                 "PIC","No Hp Penerima","Status","Chat","Status Chat",
                 "Tahap Followup","Catatan Followup"]
for col in required_cols:
    if col not in data.columns: data[col] = ""

data["Nama Bantuan"]        = data["Nama Bantuan"].astype(str).str.strip()
data["PIC"]                 = data["PIC"].astype(str).str.strip()
data["No Hp Penerima"]      = clean_phone(data["No Hp Penerima"])
data["Status"]              = data["Status"].astype(str).str.strip()
data["Chat"]                = data["Chat"].astype(str).str.strip()
data["Status Chat"]         = data["Status Chat"].astype(str).str.strip()
data["Jumlah Bantuan (Rp)"] = clean_currency(data["Jumlah Bantuan (Rp)"])
data["Tanggal Dibantu"]     = pd.to_datetime(data["Tanggal Dibantu"], errors="coerce", dayfirst=True)
data["Tenggat"]             = pd.to_datetime(data["Tenggat"], errors="coerce", dayfirst=True)
data["Tanggal Chat"]        = pd.to_datetime(data["Status Chat"], errors="coerce", dayfirst=True)
data["Tahun"]               = data["Tanggal Dibantu"].dt.year
data["Status Pembayaran"]   = data["Status"].apply(normalize_status)
data["Chat Normal"]         = data["Chat"].apply(normalize_chat)

data["Tahap Followup"] = data["Tahap Followup"].astype(str).str.strip()
data["Tahap Followup"] = data["Tahap Followup"].apply(
    lambda x: x if x in VALID_TAHAP else ""
)
data["Catatan Followup"] = data["Catatan Followup"].astype(str).str.strip().replace("nan", "")

today = pd.Timestamp.today().normalize()

data["Kondisi Tenggat"] = data.apply(
    lambda r: "Jatuh Tempo"
    if r["Status Pembayaran"] == "Belum LPJ" and pd.notna(r["Tenggat"]) and r["Tenggat"] < today
    else "Belum Jatuh Tempo", axis=1
)
data["Terlambat Hari"] = data["Tenggat"].apply(
    lambda x: (today - x).days if pd.notna(x) and x < today else 0
)
data["Hari Setelah Chat"] = data.apply(
    lambda r: hitung_jeda_chat(r["Tanggal Chat"], r["Chat Normal"], today), axis=1
)
data["Label Jeda Chat"]  = data["Hari Setelah Chat"].apply(label_jeda_chat)
data["Klasifikasi Chat"] = data["Hari Setelah Chat"].apply(klasifikasi_chat)
data["Label Tampilan"]   = data.apply(
    lambda r: "LPJ" if r["Status Pembayaran"] == "LPJ"
    else ("Jatuh Tempo" if r["Kondisi Tenggat"] == "Jatuh Tempo" else "Belum LPJ"), axis=1
)
data = data.reset_index(drop=True)

# ─── HITUNG NOTIFIKASI ────────────────────────────────────────────────────────
total_notif = len(data[
    (data["Status Pembayaran"] == "Belum LPJ") &
    (
        (data["Kondisi Tenggat"] == "Jatuh Tempo") |
        (data["Klasifikasi Chat"].isin(["BlackList", "Follow Up LPJ", "Menunggu LPJ"]))
    ) &
    (~data["Nama Bantuan"].isin(st.session_state.notif_dismissed))
])

render_sidebar(active_page="main", notif_count=total_notif)

notif_kritis = data[
    (data["Status Pembayaran"] == "Belum LPJ") &
    (data["Kondisi Tenggat"] == "Jatuh Tempo") &
    (data["Chat Normal"] == "Belum di Chat") &
    (~data["Nama Bantuan"].isin(st.session_state.notif_dismissed))
]
if not notif_kritis.empty and not st.session_state.toast_shown:
    st.toast(
        f"🔴 {len(notif_kritis)} penerima bantuan jatuh tempo belum dihubungi!",
        icon="⚠️"
    )
    st.session_state.toast_shown = True

# ═════════════════════════════════════════════════════════════════════════════
#  LAYOUT
# ═════════════════════════════════════════════════════════════════════════════

# ── HERO HEADER ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <div class="hero-icon">📊</div>
    <div>
        <div class="hero-eyebrow">Sistem Monitoring</div>
        <div class="hero-title">Dashboard Bantuan</div>
        <div class="hero-sub">Pantau status bantuan, progres LPJ, dan prioritas tindak lanjut secara real-time</div>
    </div>
    <div class="hero-right"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── FILTER + TOMBOL DALAM SATU BARIS ─────────────────────────────────────────
_notif_col, _refresh_col, f2, f3, f4 = st.columns([1.6, 0.38, 1, 1, 1], gap="small")

with _notif_col:
    st.markdown('<div class="filter-label">Notifikasi</div>', unsafe_allow_html=True)
    notif_label = f"🔔  Notifikasi  {total_notif}" if total_notif > 0 else "🔔  Notifikasi"
    if st.button(notif_label, key="btn_notif", use_container_width=True,
                 type="primary" if total_notif > 0 else "secondary"):
        st.switch_page("pages/notifikasi.py")

with _refresh_col:
    st.markdown('<div class="filter-label">&nbsp;</div>', unsafe_allow_html=True)
    if st.button("↺", key="btn_refresh", use_container_width=True, help="Refresh data dari Google Sheets"):
        st.cache_data.clear()
        st.rerun()

with f2:
    st.markdown('<div class="filter-label">Tahun</div>', unsafe_allow_html=True)
    selected_tahun = st.selectbox("Tahun", ["Semua", 2023, 2024, 2025, 2026], label_visibility="collapsed")

with f3:
    st.markdown('<div class="filter-label">Kondisi</div>', unsafe_allow_html=True)
    selected_status = st.selectbox("Kondisi", ["Semua", "LPJ", "Belum LPJ", "Jatuh Tempo"], label_visibility="collapsed")

with f4:
    st.markdown('<div class="filter-label">Status Chat</div>', unsafe_allow_html=True)
    selected_chat = st.selectbox(
        "Status Chat",
        ["Semua","Belum di Chat","Sudah di Chat","Menunggu LPJ","Follow Up LPJ","BlackList"],
        label_visibility="collapsed"
    )

# ── BUILD FILTERED ─────────────────────────────────────────────────────────
def make_filtered(tahun, status, chat):
    f = data.copy()
    if tahun != "Semua":    f = f[f["Tahun"] == tahun]
    if status == "LPJ":     f = f[f["Status Pembayaran"] == "LPJ"]
    elif status == "Belum LPJ":
        f = f[(f["Status Pembayaran"]=="Belum LPJ") & (f["Kondisi Tenggat"]=="Belum Jatuh Tempo")]
    elif status == "Jatuh Tempo": f = f[f["Kondisi Tenggat"] == "Jatuh Tempo"]
    if chat == "Belum di Chat":   f = f[f["Chat Normal"] == "Belum di Chat"]
    elif chat == "Sudah di Chat": f = f[f["Chat Normal"] == "Sudah di Chat"]
    elif chat == "Menunggu LPJ":  f = f[f["Klasifikasi Chat"] == "Menunggu LPJ"]
    elif chat == "Follow Up LPJ": f = f[f["Klasifikasi Chat"] == "Follow Up LPJ"]
    elif chat == "BlackList":     f = f[f["Klasifikasi Chat"] == "BlackList"]
    return f

filtered = make_filtered(selected_tahun, selected_status, selected_chat)

total_nominal_semua = filtered["Jumlah Bantuan (Rp)"].fillna(0).sum()
total_nominal_lpj   = filtered.loc[filtered["Status Pembayaran"]=="LPJ","Jumlah Bantuan (Rp)"].fillna(0).sum()

total_penerima    = len(filtered)
total_lpj         = len(filtered[filtered["Status Pembayaran"]=="LPJ"])
total_belum_lpj   = len(filtered[filtered["Status Pembayaran"]=="Belum LPJ"])
total_jatuh_tempo = len(filtered[filtered["Kondisi Tenggat"]=="Jatuh Tempo"])
total_menunggu    = len(filtered[filtered["Klasifikasi Chat"]=="Menunggu LPJ"])
total_follow_up   = len(filtered[filtered["Klasifikasi Chat"]=="Follow Up LPJ"])
total_blacklist   = len(filtered[filtered["Klasifikasi Chat"]=="BlackList"])

# ── NOMINAL + KPI ROW ────────────────────────────────────────────────────────
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
n_col, k1, k2, k3, k4, k5, k6 = st.columns([2.2, 1, 1, 1, 1, 1, 1], gap="small")

with n_col:
    st.markdown(f"""
    <div class="nominal-card">
        <div class="nominal-eyebrow">Realisasi LPJ</div>
        <div class="nominal-value">{fmt_rupiah(total_nominal_lpj)}</div>
        <div class="nominal-total">dari {fmt_rupiah(total_nominal_semua)} total</div>
        <div class="nominal-note">Nominal bantuan yang telah dikembalikan</div>
    </div>
    """, unsafe_allow_html=True)

kpi_data = [
    (k1, "Total Penerima", str(total_penerima), "Terdaftar dalam sistem", ""),
    (k2, "Sudah LPJ", str(total_lpj), "Selesai dikembalikan", "kpi-card-accent-success"),
    (k3, "Belum LPJ", str(total_belum_lpj), "Belum selesai", "kpi-card-accent-warning"),
    (k4, "Jatuh Tempo", str(total_jatuh_tempo), "Perlu segera ditindak", "kpi-card-accent-warning"),
    (k5, "Menunggu LPJ", str(total_menunggu), "Sudah 1 minggu setelah chat", "kpi-card-accent-indigo"),
    (k6, "Follow Up / BL", f"{total_follow_up} / {total_blacklist}", "2 minggu / 3 minggu ke atas", "kpi-card-accent-amber"),
]

for col, label, val, note, accent in kpi_data:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-card-accent {accent}"></div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── CHARTS ──────────────────────────────────────────────────────────────────
import streamlit.components.v1 as components
import math

PALETTE_BAR = {"LPJ":"#5E0F26","Belum LPJ":"#8B1A3A","Jatuh Tempo":"#C4617F"}
PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=10, b=10, l=0, r=0),
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#1C0A12"),
)

status_dist_df = (
    filtered["Label Tampilan"].value_counts()
    .reindex(["LPJ","Belum LPJ","Jatuh Tempo"], fill_value=0).reset_index()
)
status_dist_df.columns = ["Kategori","Jumlah"]

def make_gauge_html(items, cols=2):
    def one_gauge(pct, color, size=88, stroke=9, track="#EAD8DF"):
        if cols == 4:
            size, stroke = 75, 8
        r = (size - stroke * 2) / 2
        cx = cy = size / 2
        circ = 2 * math.pi * r
        pct = max(0, min(100, pct))
        fill = circ * pct / 100
        gap  = circ - fill
        pct_txt = f"{pct:.1f}".rstrip("0").rstrip(".") + "%"
        return f"""
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
          <circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
            stroke="{track}" stroke-width="{stroke}" stroke-linecap="round"/>
          <circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
            stroke="{color}" stroke-width="{stroke}" stroke-linecap="round"
            stroke-dasharray="{fill:.3f} {gap:.3f}"
            transform="rotate(-90 {cx} {cy})"/>
          <text x="{cx}" y="{cy+1}" text-anchor="middle" dominant-baseline="middle"
            font-family="Sora, sans-serif" font-size="13" font-weight="800" fill="#1C0A12">{pct_txt}</text>
        </svg>"""

    cards = ""
    for label, pct, color, count in items:
        svg = one_gauge(pct, color)
        cards += f"""
        <div style="text-align:center;display:flex;flex-direction:column;align-items:center;
                    justify-content:flex-start;padding:4px 6px;">
          {svg}
          <div style="font-size:10px;font-weight:700;color:{color};margin-top:4px;
                      letter-spacing:0.05em;text-transform:uppercase;line-height:1.3;
                      white-space:nowrap;">{label}</div>
          <div style="font-size:11px;font-weight:600;color:#9E7080;margin-top:1px;">{count} orang</div>
        </div>"""

    grid_style = (
        f"display:grid;"
        f"grid-template-columns:repeat({cols}, 1fr);"
        f"gap:4px 0;"
        f"align-items:start;"
        f"justify-items:center;"
        f"padding:6px 4px 6px 4px;"
    )

    return f"""
    <html><head>
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@800&family=Plus+Jakarta+Sans:wght@600;700&display=swap" rel="stylesheet">
    <style>body{{margin:0;padding:0;background:transparent;font-family:'Plus Jakarta Sans',sans-serif;}}</style>
    </head><body>
    <div style="{grid_style}">
      {cards}
    </div>
    </body></html>"""

total_belum_dichat = len(filtered[
    (filtered["Status Pembayaran"] == "Belum LPJ") &
    (filtered["Kondisi Tenggat"] == "Jatuh Tempo") &
    (filtered["Chat Normal"] == "Belum di Chat")
])

pct_lpj          = round((total_lpj / total_penerima) * 100, 1)          if total_penerima else 0
pct_belum        = round((total_belum_lpj / total_penerima) * 100, 1)    if total_penerima else 0
pct_belum_dichat = round((total_belum_dichat / total_penerima) * 100, 1) if total_penerima else 0
pct_jt           = round((total_jatuh_tempo / total_penerima) * 100, 1)  if total_penerima else 0
pct_fu           = round((total_follow_up / total_penerima) * 100, 1)    if total_penerima else 0
pct_bl           = round((total_blacklist / total_penerima) * 100, 1)    if total_penerima else 0
pct_menunggu     = round((total_menunggu / total_penerima) * 100, 1)     if total_penerima else 0

c1, c2, c3 = st.columns([0.7, 1, 1.3], gap="medium")

with c1:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Indikator Realisasi LPJ</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Persentase penerima yang telah menyelesaikan LPJ</div>', unsafe_allow_html=True)
        html_gauge = make_gauge_html([
            ("Sudah LPJ",  pct_lpj,   "#5E0F26", total_lpj),
            ("Belum LPJ",  pct_belum, "#B5476A", total_belum_lpj),
        ], cols=2)
        components.html(html_gauge, height=210, scrolling=False)

with c2:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Distribusi Status</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">LPJ, belum LPJ, dan jatuh tempo</div>', unsafe_allow_html=True)
        if not status_dist_df.empty:
            fig2 = px.bar(status_dist_df, x="Kategori", y="Jumlah", color="Kategori",
                          color_discrete_map=PALETTE_BAR)
            fig2.update_layout(**PLOTLY_BASE, height=210, xaxis_title="", yaxis_title="", showlegend=False)
            fig2.update_traces(marker_line_width=0, marker_cornerradius=6)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("Tidak ada data.")

with c3:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Indikator Risiko Tindak Lanjut</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Proporsi berdasarkan urgensi tindak lanjut</div>', unsafe_allow_html=True)
        html_risk = make_gauge_html([
            ("Belum di Chat",  pct_belum_dichat, "#5E0F26", total_belum_dichat),
            ("Menunggu LPJ",   pct_menunggu,     "#8B1A3A", total_menunggu),
            ("Follow Up LPJ",  pct_fu,           "#A8355A", total_follow_up),
            ("Blacklist",      pct_bl,           "#C4617F", total_blacklist),
        ], cols=4)
        components.html(html_risk, height=210, scrolling=False)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── TABEL PRIORITAS JATUH TEMPO ─────────────────────────────────────────────
prioritas = (
    filtered[
        (filtered["Status Pembayaran"]=="Belum LPJ") &
        (filtered["Kondisi Tenggat"]=="Jatuh Tempo")
    ]
    .copy()
    .sort_values(["Terlambat Hari","Tenggat"], ascending=[False,True])
)

st.markdown(f"""
<div class="section-wrapper">
    <div class="section-title">
        ⚠️ Penerima Bantuan Jatuh Tempo
        <span class="section-badge">{len(prioritas)}</span>
    </div>
    <div class="section-desc">Daftar penerima yang melewati tenggat waktu dan perlu segera ditindaklanjuti</div>
</div>
""", unsafe_allow_html=True)

if prioritas.empty:
    st.success("✅ Tidak ada penerima bantuan yang jatuh tempo saat ini.")
else:
    prioritas_belum_chat = prioritas[prioritas["Chat Normal"]=="Belum di Chat"].copy()
    prioritas_sudah_chat = prioritas[prioritas["Chat Normal"]=="Sudah di Chat"].copy()

    col_kiri, col_kanan = st.columns(2, gap="large")

    with col_kiri:
        st.markdown(f"""
        <div class="sub-section-header">
            <div class="sub-section-icon sub-section-icon-danger">📩</div>
            <div class="sub-section-label">Belum Dihubungi</div>
            <div class="sub-section-count">{len(prioritas_belum_chat)} orang</div>
        </div>
        """, unsafe_allow_html=True)

        if prioritas_belum_chat.empty:
            st.markdown('<div class="empty-state"><div class="empty-icon">✅</div>Semua sudah dihubungi</div>', unsafe_allow_html=True)
        else:
            pv_belum = prioritas_belum_chat[[
                "Nama Bantuan","Jumlah Bantuan (Rp)","No Hp Penerima",
                "Chat Normal","Klasifikasi Chat","Tahap Followup"
            ]].copy()
            pv_belum["Jumlah Bantuan (Rp)"] = pv_belum["Jumlah Bantuan (Rp)"].apply(fmt_rupiah)
            pv_belum["No Hp Penerima"]      = pv_belum["No Hp Penerima"].replace("","-")
            pv_belum["Status"]              = pv_belum.apply(
                lambda r: chip_aksi_prioritas(r["Klasifikasi Chat"], r["Chat Normal"]), axis=1
            )
            pv_belum["Tahap"]               = pv_belum["Tahap Followup"].apply(chip_tahap_followup)
            pv_belum[""]                    = prioritas_belum_chat["Nama Bantuan"].apply(detail_btn_html)
            pv_belum = pv_belum[["Nama Bantuan","Jumlah Bantuan (Rp)","No Hp Penerima","Status","Tahap",""]]
            st.markdown(df_to_html(pv_belum, max_height=340), unsafe_allow_html=True)

    with col_kanan:
        st.markdown(f"""
        <div class="sub-section-header">
            <div class="sub-section-icon sub-section-icon-success">💬</div>
            <div class="sub-section-label">Sudah Dihubungi</div>
            <div class="sub-section-count">{len(prioritas_sudah_chat)} orang</div>
        </div>
        """, unsafe_allow_html=True)

        if prioritas_sudah_chat.empty:
            st.markdown('<div class="empty-state"><div class="empty-icon">📭</div>Belum ada yang dihubungi</div>', unsafe_allow_html=True)
        else:
            pv_sudah = prioritas_sudah_chat[[
                "Nama Bantuan","Jumlah Bantuan (Rp)","No Hp Penerima",
                "Chat Normal","Klasifikasi Chat","Tahap Followup"
            ]].copy()
            pv_sudah["Jumlah Bantuan (Rp)"] = pv_sudah["Jumlah Bantuan (Rp)"].apply(fmt_rupiah)
            pv_sudah["No Hp Penerima"]      = pv_sudah["No Hp Penerima"].replace("","-")
            pv_sudah["Status"]              = pv_sudah.apply(
                lambda r: chip_aksi_prioritas(r["Klasifikasi Chat"], r["Chat Normal"]), axis=1
            )
            pv_sudah["Tahap"]               = pv_sudah["Tahap Followup"].apply(chip_tahap_followup)
            pv_sudah[""]                    = prioritas_sudah_chat["Nama Bantuan"].apply(detail_btn_html)
            pv_sudah = pv_sudah[["Nama Bantuan","Jumlah Bantuan (Rp)","No Hp Penerima","Status","Tahap",""]]
            st.markdown(df_to_html(pv_sudah, max_height=340), unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── CTA KE DATABASE ───────────────────────────────────────────────────────────
st.markdown("""
<div class="section-wrapper">
    <div class="section-title">📋 Data Lengkap</div>
    <div class="section-desc">Lihat semua data penerima bantuan termasuk dokumen pendukung di halaman Database.</div>
</div>
""", unsafe_allow_html=True)

if st.button("Buka Database Lengkap →", key="btn_to_db", type="primary"):
    st.switch_page("pages/database.py")

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
