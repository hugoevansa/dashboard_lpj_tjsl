"""
notifikasi.py  ─  Halaman Notifikasi & Tindak Lanjut
======================================================
Letakkan di folder  pages/notifikasi.py
"""

import streamlit as st
import pandas as pd
import requests
import urllib.parse
from io import StringIO

st.set_page_config(
    page_title="Notifikasi",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
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

/* ── Banner ─────────────────────────────────────────────────────── */
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
.page-header-icon  { font-size:2.2rem; background:rgba(255,255,255,0.15); border-radius:16px; padding:10px 14px; }
.page-header-title { color:#fff; font-size:1.7rem; font-weight:900; line-height:1.1; margin:0; }
.page-header-sub   { color:rgba(255,255,255,0.75); font-size:0.9rem; margin-top:3px; }

/* ── KPI ────────────────────────────────────────────────────────── */
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
.kpi-label { font-size:0.82rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px; }
.kpi-value { font-size:1.85rem; font-weight:900; color:var(--text); line-height:1.1; }
.kpi-note  { font-size:0.8rem; color:var(--muted); margin-top:6px; }

.section-head { font-size:1.1rem; font-weight:900; color:var(--text); margin:0; }
.section-sub  { font-size:0.85rem; color:var(--muted); margin-top:2px; margin-bottom:10px; }

/* ── Badges ─────────────────────────────────────────────────────── */
.badge-urgent   { display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#fde8ec;color:#b42318;border:1px solid #f0bfc9; }
.badge-followup { display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#fff4e0;color:#92600a;border:1px solid #f0d49a; }
.badge-blacklist{ display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#111827;color:#fff;border:1px solid #374151; }
.badge-belum    { display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#fde8ec;color:#b42318;border:1px solid #f0bfc9; }
.badge-konfirmasi    { display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#e0f2fe;color:#0369a1;border:1px solid #7dd3fc; }
.badge-sudah-followup     { display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#fef9c3;color:#854d0e;border:1px solid #fde047; }
.badge-lpj-diterima  { display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#dcfce7;color:#15803d;border:1px solid #86efac; }
.badge-bl-konfirmasi { display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#1f2937;color:#f9fafb;border:1px solid #6b7280; }
.badge-belum-diisi   { display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#f3f4f6;color:#9ca3af;border:1px solid #d1d5db;font-style:italic; }
.badge-menunggu-balasan { display:inline-block;padding:4px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;background:#eef2ff;color:#4338ca;border:1px solid #c7d2fe; }

/* ── Notif cards ─────────────────────────────────────────────────── */
.notif-card {
    background: #fff;
    border-radius: 16px;
    border: 1.5px solid var(--line);
    box-shadow: var(--shadow);
    padding: 16px 20px;
    margin-bottom: 12px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
    transition: box-shadow 0.2s;
}
.notif-card:hover { box-shadow: 0 6px 32px rgba(92,18,41,0.16); }
.notif-card-urgent   { border-left: 5px solid #b42318 !important; }
.notif-card-followup { border-left: 5px solid #92600a !important; }
.notif-card-blacklist{ border-left: 5px solid #111827 !important; }
.notif-card-belum    { border-left: 5px solid #b42318 !important; }

.notif-icon { font-size:1.6rem; min-width:40px; text-align:center; padding-top:2px; }
.notif-body { flex:1; min-width:0; }
.notif-name { font-size:1rem; font-weight:900; color:var(--text); margin:0 0 4px 0; }
.notif-badges { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:6px; }
.notif-meta { font-size:0.82rem; color:var(--muted); margin:0; display:flex; gap:14px; flex-wrap:wrap; }
.notif-meta span { display:flex; align-items:center; gap:4px; }
.notif-tahap {
    margin-top: 8px;
    padding: 8px 12px;
    background: #faf5f7;
    border-radius: 10px;
    border: 1px solid var(--line);
    font-size: 0.82rem;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}
.notif-tahap-label { font-weight:700; color:var(--muted); }
.notif-catatan { font-size:0.8rem; color:var(--text); font-style:italic; margin-top:2px; }
.notif-actions { display:flex; gap:8px; flex-wrap:wrap; align-items:center; padding-top:2px; }

.btn-wa {
    display:inline-block; padding:7px 14px; border-radius:10px;
    background:#25d366; color:#fff; font-size:12.5px; font-weight:800;
    text-decoration:none; white-space:nowrap;
}
.btn-detail {
    display:inline-block; padding:7px 14px; border-radius:10px;
    background:var(--maroon); color:#fff; font-size:12.5px; font-weight:800;
    text-decoration:none; white-space:nowrap;
}
.btn-dismiss {
    display:inline-block; padding:7px 14px; border-radius:10px;
    background:#1b7a45; color:#fff; font-size:12.5px; font-weight:800;
    text-decoration:none; white-space:nowrap;
}
.btn-dismissed {
    display:inline-block; padding:7px 14px; border-radius:10px;
    background:#e6f5ec; color:#1b7a45; font-size:12.5px; font-weight:800;
    border:1px solid #b0dfc0; white-space:nowrap;
}

.group-divider {
    display:flex; align-items:center; gap:12px;
    margin: 20px 0 14px 0;
}
.group-divider-line { flex:1; height:1.5px; background:var(--line); border-radius:2px; }
.group-divider-label {
    font-size:0.88rem; font-weight:900; color:var(--muted);
    text-transform:uppercase; letter-spacing:0.08em; white-space:nowrap;
}

.empty-state {
    text-align:center; padding:48px 24px;
    background:#fff; border-radius:var(--radius);
    border:1.5px solid var(--line); box-shadow:var(--shadow);
    color:var(--muted);
}
.empty-state-icon  { font-size:3rem; margin-bottom:12px; }
.empty-state-title { font-size:1.1rem; font-weight:900; color:var(--text); margin-bottom:6px; }
.empty-state-sub   { font-size:0.88rem; }

::-webkit-scrollbar       { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#f5eaef; border-radius:10px; }
::-webkit-scrollbar-thumb { background:#a14f6a; border-radius:10px; }
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
    bulan = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
             7:"Jul",8:"Ags",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
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

def hitung_jeda_chat(tanggal_chat, chat_status, today):
    if chat_status != "Sudah di Chat" or pd.isna(tanggal_chat): return None
    return max((today - tanggal_chat).days, 0)

def klasifikasi_chat(hari):
    if hari is None:    return ""
    if 0 <= hari < 14:  return "Menunggu LPJ"
    if 14 <= hari < 21: return "Follow Up LPJ"
    if hari >= 21:      return "BlackList"
    return ""

def wa_link(nomor):
    if not nomor or nomor == "-": return None
    clean = str(nomor).replace(" ","").replace("-","")
    if clean.startswith("0"): clean = "62" + clean[1:]
    if not clean.startswith("62"): clean = "62" + clean
    return f"https://wa.me/{clean}"

def badge_tahap_html(val):
    if not val or val in ["nan", "", "-"]:
        return '<span class="badge-belum-diisi">Tahap: Belum diisi</span>'
    if val == "Blacklist Dikonfirmasi":
        return '<span class="badge-bl-konfirmasi">✓ Blacklist Dikonfirmasi</span>'
    if val == "LPJ Diterima":
        return '<span class="badge-lpj-diterima">✓ LPJ Diterima</span>'
    if val == "Sudah Konfirmasi":
        return '<span class="badge-konfirmasi">✓ Sudah Konfirmasi</span>'
    if val == "Sudah Followup":
        return '<span class="badge-sudah-followup">Sudah Followup</span>'
    if val == "Menunggu Balasan":
        return '<span class="badge-menunggu-balasan">Menunggu Balasan</span>'
    return '<span class="badge-belum-diisi">Belum diisi</span>'

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
data["Klasifikasi Chat"] = data["Hari Setelah Chat"].apply(klasifikasi_chat)
data = data.reset_index(drop=True)

# ─── FILTER ───────────────────────────────────────────────────────────────────
def is_resolved(row, auto_status):
    tahap = str(row.get("Tahap Followup", "") or "").strip()
    if auto_status == "BlackList":      return tahap == "Blacklist Dikonfirmasi"
    if auto_status == "Follow Up LPJ": return tahap in ("Sudah Followup","LPJ Diterima")
    if auto_status == "Menunggu LPJ":  return tahap == "LPJ Diterima"
    if auto_status == "Belum di Chat": return tahap in ("Sudah Konfirmasi","LPJ Diterima")
    return False

belum_chat = data[
    (data["Status Pembayaran"] == "Belum LPJ") &
    (data["Kondisi Tenggat"] == "Jatuh Tempo") &
    (data["Chat Normal"] == "Belum di Chat") &
    (~data.apply(lambda r: is_resolved(r,"Belum di Chat"), axis=1))
].copy().sort_values("Terlambat Hari", ascending=False)

blacklist = data[
    (data["Status Pembayaran"] == "Belum LPJ") &
    (data["Klasifikasi Chat"] == "BlackList") &
    (~data.apply(lambda r: is_resolved(r,"BlackList"), axis=1))
].copy().sort_values("Hari Setelah Chat", ascending=False)

follow_up = data[
    (data["Status Pembayaran"] == "Belum LPJ") &
    (data["Klasifikasi Chat"] == "Follow Up LPJ") &
    (~data.apply(lambda r: is_resolved(r,"Follow Up LPJ"), axis=1))
].copy().sort_values("Hari Setelah Chat", ascending=False)

menunggu = data[
    (data["Status Pembayaran"] == "Belum LPJ") &
    (data["Klasifikasi Chat"] == "Menunggu LPJ") &
    (~data.apply(lambda r: is_resolved(r,"Menunggu LPJ"), axis=1))
].copy().sort_values("Hari Setelah Chat", ascending=False)

total_notif = len(belum_chat) + len(blacklist) + len(follow_up) + len(menunggu)

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR  ← baru
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏛️ Dashboard Bantuan")
    st.page_link("main.py",              label="🏠 Main")
    st.page_link("pages/database.py",    label="🗄️ Database")
    st.page_link("pages/notifikasi.py",  label="🔔 Notifikasi")
    st.page_link("pages/sebaran.py",     label="🗺️ Sebaran Bantuan")

# ═════════════════════════════════════════════════════════════════════════════
#  LAYOUT
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
    <div class="page-header-icon">🔔</div>
    <div>
        <div class="page-header-title">NOTIFIKASI & TINDAK LANJUT</div>
        <div class="page-header-sub">Pantau seluruh penerima bantuan yang perlu dihubungi segera</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── KPI ───────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4, gap="medium")
kpi_cards = [
    ("🔴 Segera di Chat",  str(len(belum_chat)), "Jatuh tempo, belum dihubungi"),
    ("⚫ BlackList",       str(len(blacklist)),  "Tidak ada respons 21+ hari"),
    ("🟡 Follow Up LPJ",   str(len(follow_up)),  "14–20 hari setelah chat"),
    ("🔵 Menunggu LPJ",    str(len(menunggu)),   "0–13 hari setelah chat"),
]
for col, (label_k, val_k, note_k) in zip([k1,k2,k3,k4], kpi_cards):
    with col:
        st.markdown(f"""
        <div class="kpi-wrap">
            <div class="kpi-label">{label_k}</div>
            <div class="kpi-value">{val_k}</div>
            <div class="kpi-note">{note_k}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

if total_notif == 0:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🎉</div>
        <div class="empty-state-title">Semua beres!</div>
        <div class="empty-state-sub">Tidak ada notifikasi yang perlu ditindaklanjuti saat ini.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

st.markdown(
    f'<div class="section-head">📋 Total {total_notif} penerima bantuan perlu perhatian</div>',
    unsafe_allow_html=True
)
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ─── HELPER RENDER KARTU ─────────────────────────────────────────────────────
def card_html(row, card_class, icon_code, badge_status_html, show_dismiss=False):
    nama      = str(row["Nama Bantuan"])
    pic       = str(row.get("PIC","-") or "-")
    hp        = str(row.get("No Hp Penerima","-") or "-")
    jumlah    = fmt_rupiah(row.get("Jumlah Bantuan (Rp)"))
    tenggat   = fmt_tgl(row.get("Tenggat")) if pd.notna(row.get("Tenggat")) else "-"
    terlambat = int(row.get("Terlambat Hari",0)) if pd.notna(row.get("Terlambat Hari",0)) else 0
    jeda_raw  = row.get("Hari Setelah Chat")
    jeda_chat = int(jeda_raw) if pd.notna(jeda_raw) else None
    tahap     = str(row.get("Tahap Followup","") or "")
    catatan   = str(row.get("Catatan Followup","") or "").strip()
    badge_tahap = badge_tahap_html(tahap)

    wa_url  = wa_link(hp)
    wa_html = (
        f'<a href="{wa_url}" target="_blank" class="btn-wa">&#x1F4AC; WhatsApp</a>'
        if wa_url else ""
    )
    enc_nama = urllib.parse.quote(nama)
    det_html = f'<a href="?detail={enc_nama}" target="_self" class="btn-detail">&#x1F50D; Detail</a>'

    if show_dismiss:
        if nama in st.session_state.notif_dismissed:
            dis_html = '<span class="btn-dismissed">&#x2713; Dicatat</span>'
        else:
            dis_html = (
                f'<a href="?dismiss={enc_nama}" target="_self" class="btn-dismiss">'
                f'&#x2705; Sudah Chat</a>'
            )
    else:
        dis_html = ""

    terlambat_html = f'<span>&#x1F534; Terlambat {terlambat} hari</span>' if terlambat > 0 else ""
    jeda_html      = f'<span>&#x23F1; {jeda_chat} hari sejak chat</span>' if jeda_chat is not None else ""
    catatan_html   = (
        f'<span class="notif-catatan">📝 {catatan}</span>'
        if catatan and catatan not in ["nan","-",""] else ""
    )

    return (
        f'<div class="notif-card {card_class}">'
        f'<div class="notif-icon">{icon_code}</div>'
        f'<div class="notif-body">'
        f'<div class="notif-name">{nama}</div>'
        f'<div class="notif-badges">{badge_status_html}</div>'
        f'<div class="notif-meta">'
        f'<span>&#x1F464; PIC: <b>{pic}</b></span>'
        f'<span>&#x1F4F1; {hp}</span>'
        f'<span>&#x1F4B0; {jumlah}</span>'
        f'<span>&#x1F4C5; Tenggat: {tenggat}</span>'
        f'{terlambat_html}{jeda_html}'
        f'</div>'
        f'<div class="notif-tahap">'
        f'<span class="notif-tahap-label">Tahap kamu:</span>'
        f'{badge_tahap}'
        f'</div>'
        f'{catatan_html}'
        f'</div>'
        f'<div class="notif-actions">{wa_html}{det_html}{dis_html}</div>'
        f'</div>'
    )


def render_grup(df, divider_label, sub_text, card_class, icon_code, badge_status_html, show_dismiss=False):
    if df.empty: return
    cards = "".join(
        card_html(row, card_class, icon_code, badge_status_html, show_dismiss)
        for _, row in df.iterrows()
    )
    st.markdown(
        f'<div class="group-divider">'
        f'<div class="group-divider-line"></div>'
        f'<div class="group-divider-label">{divider_label}</div>'
        f'<div class="group-divider-line"></div>'
        f'</div>'
        f'<div class="section-sub">{sub_text}</div>'
        f'{cards}',
        unsafe_allow_html=True,
    )


# ── RENDER GRUP ───────────────────────────────────────────────────────────────
render_grup(
    belum_chat,
    divider_label=f"&#x1F534; Segera di Chat &mdash; {len(belum_chat)} orang",
    sub_text="Penerima bantuan yang jatuh tempo dan <b>belum</b> dihubungi sama sekali.",
    card_class="notif-card-belum",
    icon_code="&#x1F534;",
    badge_status_html='<span class="badge-belum">Belum di Chat</span>',
    show_dismiss=True,
)
render_grup(
    blacklist,
    divider_label=f"&#x26AB; BlackList &mdash; {len(blacklist)} orang",
    sub_text="Sudah dihubungi tapi tidak ada respons selama <b>21 hari atau lebih</b>.",
    card_class="notif-card-blacklist",
    icon_code="&#x26AB;",
    badge_status_html='<span class="badge-blacklist">🤖 Auto: Blacklist</span>',
)
render_grup(
    follow_up,
    divider_label=f"&#x1F7E1; Follow Up LPJ &mdash; {len(follow_up)} orang",
    sub_text="Sudah dihubungi, belum ada LPJ selama <b>14&ndash;20 hari</b>.",
    card_class="notif-card-followup",
    icon_code="&#x1F7E1;",
    badge_status_html='<span class="badge-followup">🤖 Auto: Follow Up</span>',
)
render_grup(
    menunggu,
    divider_label=f"&#x1F535; Menunggu LPJ &mdash; {len(menunggu)} orang",
    sub_text="Sudah dihubungi dan masih dalam periode tunggu LPJ (<b>0&ndash;13 hari</b>).",
    card_class="notif-card-menunggu",
    icon_code="&#x1F535;",
    badge_status_html='<span class="badge-urgent">🤖 Auto: Menunggu</span>',
)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
