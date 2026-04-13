import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(
    page_title="Database Bantuan",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
if "detail_nama" not in st.session_state:
    st.session_state.detail_nama = None

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
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

.stApp { background: var(--bg); }

.block-container {
    padding: 0.5rem 2rem 2rem 2rem !important;
    max-width: 1440px !important;
}

footer { visibility: hidden; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--maroon-dark) 0%, var(--maroon) 100%) !important;
}
section[data-testid="stSidebar"] * { color: #fff !important; }

div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] { gap: 0 !important; }

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
    max-height: 480px;
    overflow-y: auto;
    overflow-x: auto;
    border-radius: 0 0 14px 14px;
}
.tbl-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
.tbl-scroll::-webkit-scrollbar-track { background: #f5eaef; border-radius: 10px; }
.tbl-scroll::-webkit-scrollbar-thumb { background: var(--maroon-mid); border-radius: 10px; }
.tbl-scroll::-webkit-scrollbar-thumb:hover { background: var(--maroon); }

.tbl {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
}
.tbl thead { position: sticky; top: 0; z-index: 2; }
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

/* Detail card */
.detail-card {
    background: #fff;
    border-radius: 20px;
    border: 1.5px solid var(--line);
    box-shadow: var(--shadow);
    padding: 24px 28px;
    margin-bottom: 20px;
}
.detail-card-title {
    font-size: 1.4rem;
    font-weight: 900;
    color: var(--text);
    margin-bottom: 6px;
}
.detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-top: 16px;
}
.detail-field {
    background: var(--maroon-soft);
    border-radius: 12px;
    padding: 12px 14px;
}
.detail-field-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 5px;
}
.detail-field-value {
    font-size: 0.98rem;
    font-weight: 700;
    color: var(--text);
    word-break: break-word;
}

/* Banner info filter aktif */
.filter-banner {
    background: linear-gradient(135deg, #fff8fa, #fdf0f4);
    border: 1.5px solid #e8c8d4;
    border-radius: 16px;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}
.filter-banner-icon { font-size: 1.4rem; }
.filter-banner-text { flex: 1; font-size: 0.9rem; color: var(--text); }
.filter-banner-text b { color: var(--maroon); }
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS CONFIG ────────────────────────────────────────────────────
SHEET_ID = "1wi4id0XqYlTuw_KO89-cOLSPTFAQ6ODv_tH09LK_2Ao"
GID      = "0"
CSV_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
GVIZ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"

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
        s.astype(str).str.replace("Rp","",regex=False).str.replace(".","",regex=False)
         .str.replace(",","",regex=False).str.replace(" ","",regex=False).str.strip(),
        errors="coerce"
    )

def clean_phone(s):
    s = s.astype(str).str.strip()
    return s.replace(["nan","NaN","None","<NA>"],"",regex=False).str.replace(".0","",regex=False)

def normalize_status(st_val):
    v = str(st_val).strip().lower()
    return "Lunas" if v in ["lunas","sudah lunas"] else "Belum Lunas"

def normalize_chat(val):
    v = str(val).strip().lower()
    if v in ["sudah di chat","sudah","sudah chat","sudah dichat","sudah dihubungi"]:
        return "Sudah di Chat"
    return "Belum di Chat"

def chip_status(val):
    if val == "Lunas":       return '<span class="chip chip-lunas">Lunas</span>'
    if val == "Jatuh Tempo": return '<span class="chip chip-jatuh">Jatuh Tempo</span>'
    return '<span class="chip chip-belum">Belum Lunas</span>'

def chip_aksi_chat(val):
    if val == "Menunggu LPJ":  return '<span class="chip chip-menunggu">Menunggu LPJ</span>'
    if val == "Follow Up LPJ": return '<span class="chip chip-follow">Follow Up LPJ</span>'
    if val == "BlackList":     return '<span class="chip chip-blacklist">BlackList</span>'
    return '<span class="chip chip-muted">-</span>'

def chip_aksi_prioritas(val, chat_normal=None):
    # khusus untuk tabel prioritas
    if chat_normal == "Belum di Chat":
        return '<span class="chip chip-jatuh">Segera di Chat</span>'
    if val == "Menunggu LPJ":
        return '<span class="chip chip-menunggu">Menunggu LPJ</span>'
    if val == "Follow Up LPJ":
        return '<span class="chip chip-follow">Follow Up LPJ</span>'
    if val == "BlackList":
        return '<span class="chip chip-blacklist">BlackList</span>'
    return '<span class="chip chip-muted">-</span>'

def chip_aksi_database(val, chat_normal=None):
    # untuk halaman database/detail
    if chat_normal == "Belum di Chat":
        return '<span class="chip chip-jatuh">Segera di Chat</span>'
    if val == "Menunggu LPJ":
        return '<span class="chip chip-menunggu">Menunggu LPJ</span>'
    if val == "Follow Up LPJ":
        return '<span class="chip chip-follow">Follow Up LPJ</span>'
    if val == "BlackList":
        return '<span class="chip chip-blacklist">BlackList</span>'
    return '<span class="chip chip-muted">-</span>'

def df_to_html(df, max_height=480):
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
    if chat_status != "Sudah di Chat" or pd.isna(tanggal_chat): return None
    return max((today - tanggal_chat).days, 0)

def label_jeda_chat(hari):
    if hari is None: return ""
    if 7 <= hari < 14: return "1 Minggu"
    if 14 <= hari < 21: return "2 Minggu"
    if hari >= 21: return "3 Minggu"
    return "< 1 Minggu"

def klasifikasi_chat(hari):
    if hari is None:
        return ""
    if 0 <= hari < 14:
        return "Menunggu LPJ"
    if 14 <= hari < 21:
        return "Follow Up LPJ"
    if hari >= 21:
        return "BlackList"
    return ""
    
@st.cache_data(ttl=30)
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
                 "PIC","No Hp Penerima","Status","Chat","Status Chat"]
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

today = pd.Timestamp.today().normalize()

data["Kondisi Tenggat"] = data.apply(
    lambda r: "Jatuh Tempo"
    if r["Status Pembayaran"] == "Belum Lunas" and pd.notna(r["Tenggat"]) and r["Tenggat"] < today
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
    lambda r: "Lunas" if r["Status Pembayaran"] == "Lunas"
    else ("Jatuh Tempo" if r["Kondisi Tenggat"] == "Jatuh Tempo" else "Belum Lunas"), axis=1
)
data = data.reset_index(drop=True)

# ═════════════════════════════════════════════════════════════════════════════
#  LAYOUT DATABASE
# ═════════════════════════════════════════════════════════════════════════════

nama_filter = st.session_state.get("detail_nama", None)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-header-icon">📋</div>
    <div>
        <div class="page-header-title">DATABASE LENGKAP BANTUAN</div>
        <div class="page-header-sub">Detail lengkap seluruh data penerima bantuan</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ── Tombol Kembali ────────────────────────────────────────────────────────────
if st.button("← Kembali ke Dashboard", key="btn_back", type="secondary"):
    st.session_state.detail_nama = None
    st.switch_page("main.py")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Banner filter aktif ───────────────────────────────────────────────────────
table_df = data.copy()

if nama_filter:
    table_df = table_df[table_df["Nama Bantuan"] == nama_filter]

    st.markdown(f"""
    <div class="filter-banner">
        <div class="filter-banner-icon">🔍</div>
        <div class="filter-banner-text">
            Menampilkan detail untuk: <b>{nama_filter}</b><br>
            <span style="font-size:0.82rem;color:var(--muted);">
                Klik "Hapus filter" untuk melihat semua data.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✕ Hapus filter — tampilkan semua data", key="btn_clear"):
        st.session_state.detail_nama = None
        st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Detail Card (hanya muncul kalau 1 data terfilter) ────────────────────────
if nama_filter and len(table_df) >= 1:
    # Ambil baris pertama yang cocok
    r = table_df.iloc[0]

    jumlah_str  = fmt_rupiah(r["Jumlah Bantuan (Rp)"])
    tgl_bantu   = fmt_tgl(r["Tanggal Dibantu"])
    tgl_tenggat = fmt_tgl(r["Tenggat"])
    tgl_chat    = fmt_tgl(r["Tanggal Chat"])
    terlambat   = f"{int(r['Terlambat Hari'])} hari" if r["Terlambat Hari"] > 0 else "—"
    jeda_chat   = r["Label Jeda Chat"] if r["Label Jeda Chat"] else "—"
    no_hp       = r["No Hp Penerima"] if r["No Hp Penerima"] else "—"
    tahun_str   = str(int(r["Tahun"])) if pd.notna(r["Tahun"]) else "—"

    chip_s  = chip_status(r["Label Tampilan"])
    chip_ac = chip_aksi_database(r["Klasifikasi Chat"], r["Chat Normal"])

    st.markdown(f"""
    <div class="detail-card">
        <div class="detail-card-title">{r['Nama Bantuan']}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px;margin-bottom:4px;">
            {chip_s} {chip_ac}
        </div>
        <div class="detail-grid">
            <div class="detail-field">
                <div class="detail-field-label">Jumlah Bantuan</div>
                <div class="detail-field-value">{jumlah_str}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">PIC</div>
                <div class="detail-field-value">{r['PIC']}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">No HP Penerima</div>
                <div class="detail-field-value">{no_hp}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Tanggal Dibantu</div>
                <div class="detail-field-value">{tgl_bantu}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Tenggat Pengembalian</div>
                <div class="detail-field-value">{tgl_tenggat}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Terlambat</div>
                <div class="detail-field-value">{terlambat}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Tanggal Dihubungi</div>
                <div class="detail-field-value">{tgl_chat}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Jeda Setelah Chat</div>
                <div class="detail-field-value">{jeda_chat}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Tahun</div>
                <div class="detail-field-value">{tahun_str}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Search & Tabel ────────────────────────────────────────────────────────────
if not nama_filter:
    st.markdown('<div class="section-head">📋 Data Semua Penerima Bantuan</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

search = st.text_input(
    "Cari",
    label_visibility="collapsed",
    placeholder="🔍 Cari nama bantuan, PIC, nomor HP, status, atau status chat...",
    key="db_search"
)

# Jika tidak ada filter aktif, search dari semua data
if not nama_filter:
    table_df = data.copy()

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

total_label = f"Menampilkan {len(table_df)} dari {len(data)} data" if not nama_filter else f"{len(table_df)} data ditemukan"
st.markdown(f'<div class="section-sub">{total_label}</div>', unsafe_allow_html=True)

# ── Build tabel tampilan ──────────────────────────────────────────────────────
disp = table_df[[
    "Nama Bantuan","Jumlah Bantuan (Rp)","Tanggal Dibantu","Tenggat",
    "PIC","No Hp Penerima","Tahun","Label Tampilan","Klasifikasi Chat",
    "Label Jeda Chat","Tanggal Chat"
]].copy()

disp["Jumlah Bantuan (Rp)"] = disp["Jumlah Bantuan (Rp)"].apply(fmt_rupiah)
disp["Tanggal Dibantu"]     = disp["Tanggal Dibantu"].apply(fmt_tgl)
disp["Tenggat"]             = disp["Tenggat"].apply(fmt_tgl)
disp["Tanggal Chat"]        = disp["Tanggal Chat"].apply(fmt_tgl)
disp["No Hp Penerima"]      = disp["No Hp Penerima"].replace("","-")
disp["Status"]              = disp["Label Tampilan"].apply(chip_status)
disp["Aksi Chat"] = table_df.apply(
    lambda r: chip_aksi_database(r["Klasifikasi Chat"], r["Chat Normal"]),
    axis=1
)
disp["Jeda Chat"]           = disp["Label Jeda Chat"].replace("","-")

disp = disp.drop(columns=["Label Tampilan","Klasifikasi Chat","Label Jeda Chat"])

disp = disp[[
    "Nama Bantuan","Jumlah Bantuan (Rp)","Tanggal Dibantu","Tenggat",
    "PIC","No Hp Penerima","Tahun","Tanggal Chat","Jeda Chat","Aksi Chat","Status"
]]

st.markdown(df_to_html(disp, max_height=480), unsafe_allow_html=True)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
