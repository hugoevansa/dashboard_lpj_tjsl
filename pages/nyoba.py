from datetime import datetime, timedelta
import random

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Nagih Utang Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CSS PALING ATAS
# =========================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #edf2f8 0%, #e7edf5 100%);
    }

    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    div[data-testid="stToolbar"] {
        visibility: visible;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071425 0%, #0b1c31 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    section[data-testid="stSidebar"] * {
        color: #dbe7f5;
    }

    .topbar {
        background: linear-gradient(90deg, #1f5daa 0%, #2f73c7 100%);
        padding: 18px 24px;
        border-radius: 22px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 14px 34px rgba(20, 63, 125, 0.18);
        margin-bottom: 20px;
    }

    .topbar-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .logo-box {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        background: rgba(255,255,255,0.18);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }

    .topbar-title {
        font-size: 24px;
        font-weight: 700;
        line-height: 1.2;
    }

    .topbar-sub {
        font-size: 13px;
        opacity: 0.9;
    }

    .admin-box {
        text-align: right;
        font-size: 15px;
        line-height: 1.15;
    }

    .admin-box span {
        display: block;
        font-size: 12px;
        opacity: 0.88;
        margin-top: 4px;
    }

    .kpi-card {
        background: #ffffff;
        border: 1px solid #d8e0ea;
        border-radius: 18px;
        padding: 18px 18px 16px 18px;
        box-shadow: 0 6px 18px rgba(64, 90, 122, 0.08);
        min-height: 116px;
    }

    .kpi-label {
        color: #4b6078;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .kpi-value {
        color: #143e73;
        font-size: 22px;
        font-weight: 800;
        line-height: 1.2;
    }

    .kpi-note {
        margin-top: 8px;
        font-size: 12px;
        color: #6d7f95;
    }

    .panel {
        background: #ffffff;
        border: 1px solid #d8e0ea;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 8px 24px rgba(64, 90, 122, 0.08);
        height: 100%;
    }

    .panel-title {
        color: #23456b;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 14px;
    }

    .stat-list {
        margin-top: 8px;
    }

    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 0;
        border-bottom: 1px solid #e7edf5;
        color: #304762;
        font-size: 15px;
    }

    .stat-row:last-child {
        border-bottom: none;
    }

    .stat-value {
        color: #1c477e;
        font-weight: 800;
        font-size: 21px;
    }

    .mini-progress-wrap {
        margin-top: 18px;
    }

    .mini-progress-row {
        display: grid;
        grid-template-columns: 92px 1fr 56px;
        align-items: center;
        gap: 12px;
        margin: 10px 0;
        color: #304762;
        font-weight: 700;
    }

    .mini-progress {
        width: 100%;
        height: 22px;
        background: #ecf1f6;
        border-radius: 999px;
        overflow: hidden;
    }

    .mini-progress > div {
        height: 100%;
        border-radius: 999px;
    }

    .green {
        background: linear-gradient(90deg, #5fbf53, #46a93d);
    }

    .red {
        background: linear-gradient(90deg, #ef5757, #da3f3f);
    }

    table.custom-table {
        width: 100%;
        border-collapse: collapse;
        overflow: hidden;
        border-radius: 14px;
        font-size: 14px;
    }

    table.custom-table thead th {
        background: linear-gradient(180deg, #2e6db8, #245b9b);
        color: white;
        text-align: left;
        padding: 12px 14px;
        font-weight: 700;
        white-space: nowrap;
    }

    table.custom-table tbody td {
        padding: 12px 14px;
        border-bottom: 1px solid #e5edf6;
        color: #304762;
        background: #fff;
    }

    table.custom-table tbody tr:nth-child(even) td {
        background: #f7fafd;
    }

    table.custom-table tbody tr:last-child td {
        border-bottom: none;
    }

    .name-cell {
        font-weight: 700;
        color: #173c6a;
    }

    .countdown-pill {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        color: white;
        font-weight: 800;
        font-size: 14px;
        min-width: 94px;
        text-align: center;
    }

    .countdown-pill.success {
        background: #59b95a;
    }

    .countdown-pill.warning {
        background: #dda134;
    }

    .countdown-pill.danger {
        background: #d84a4a;
    }

    .reminder-item, .activity-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 12px;
        border-top: 1px solid #e7edf5;
        color: #304762;
        font-size: 15px;
    }

    .reminder-item:first-child, .activity-item:first-child {
        border-top: none;
    }

    .bullet {
        font-size: 18px;
        margin-right: 10px;
        color: #365983;
    }

    .muted {
        color: #6c7f95;
        font-size: 13px;
    }

    .sidebar-note {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 12px;
        font-size: 13px;
        line-height: 1.45;
        margin-top: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

NOW = datetime.now()
random.seed(12)

# =========================
# HELPERS
# =========================
def format_rupiah(amount: int) -> str:
    return f"Rp {amount:,.0f}".replace(",", ".")


def countdown_text(target_time):
    if pd.isna(target_time):
        return "-"
    delta = target_time - NOW
    seconds = int(delta.total_seconds())
    if seconds <= 0:
        return "Lewat"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days > 0:
        return f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def countdown_badge(value: str) -> str:
    if value == "Lewat":
        css = "danger"
    else:
        try:
            parts = [int(x) for x in value.split(":")]
            total_hours = 0
            if len(parts) == 4:
                total_hours = parts[0] * 24 + parts[1]
            elif len(parts) == 3:
                total_hours = parts[0]
            css = "success" if total_hours <= 24 else "warning"
        except Exception:
            css = "warning"
    return f'<span class="countdown-pill {css}">{value}</span>'


def render_table(df_show, columns, countdown_col=None):
    header = "".join([f"<th>{c}</th>" for c in columns])
    rows_html = ""
    if df_show.empty:
        rows_html = f'<tr><td colspan="{len(columns)}" style="text-align:center; color:#6c7f95;">Tidak ada data</td></tr>'
    else:
        for _, row in df_show.iterrows():
            cells = []
            for col in columns:
                val = row[col]
                if col == columns[0]:
                    cells.append(f'<td class="name-cell">{val}</td>')
                elif countdown_col and col == countdown_col:
                    cells.append(f"<td>{countdown_badge(str(val))}</td>")
                else:
                    cells.append(f"<td>{val}</td>")
            rows_html += f"<tr>{''.join(cells)}</tr>"
    return f'<table class="custom-table"><thead><tr>{header}</tr></thead><tbody>{rows_html}</tbody></table>'


# =========================
# DUMMY DATA
# =========================
customers = [
    "Budi", "Siti", "Andi", "Rina", "Yanto", "Dewi", "Rudi", "Nina",
    "Fajar", "Lukman", "Tika", "Hendra", "Maya", "Riko", "Putri",
    "Bagus", "Intan", "Asep", "Rahmat", "Desi",
]
collectors = ["Aldi", "Bayu", "Citra", "Dimas"]
priorities = ["Tinggi", "Sedang", "Rendah"]
areas = ["Jakarta Timur", "Jakarta Barat", "Bekasi", "Depok"]

rows = []
for i, name in enumerate(customers, start=1):
    nominal = random.randint(2_000_000, 12_000_000)
    paid = random.choice([True, False, False])
    status = "Lunas" if paid else "Belum Lunas"
    due_date = NOW + timedelta(days=random.randint(-7, 6))
    sudah_dichat = True if paid else random.choice([True, False])
    janji_bayar = False if paid else (sudah_dichat and random.choice([True, False]))
    promise_date = NOW + timedelta(days=random.randint(1, 4)) if janji_bayar else None
    visit_deadline = NOW + timedelta(hours=random.randint(2, 72)) if janji_bayar else None

    rows.append(
        {
            "id": i,
            "nama": name,
            "wilayah": random.choice(areas),
            "collector": random.choice(collectors),
            "nominal": nominal,
            "status": status,
            "jatuh_tempo": due_date,
            "sudah_dichat": sudah_dichat,
            "janji_bayar": janji_bayar,
            "tanggal_janji_bayar": promise_date,
            "deadline_samperin": visit_deadline,
            "prioritas": random.choices(priorities, weights=[4, 3, 2])[0],
            "skor_risiko": random.randint(52, 98),
        }
    )

# Showcase rows biar tampilan stabil
rows[3].update({"status": "Belum Lunas", "sudah_dichat": False, "jatuh_tempo": NOW + timedelta(days=1), "prioritas": "Tinggi", "nominal": 5_000_000})
rows[4].update({"status": "Belum Lunas", "sudah_dichat": False, "jatuh_tempo": NOW + timedelta(days=2), "prioritas": "Sedang", "nominal": 3_500_000})
rows[5].update({"status": "Belum Lunas", "sudah_dichat": False, "jatuh_tempo": NOW + timedelta(days=3), "prioritas": "Tinggi", "nominal": 7_200_000})
rows[6].update({"status": "Belum Lunas", "sudah_dichat": True, "janji_bayar": True, "tanggal_janji_bayar": NOW + timedelta(days=2), "deadline_samperin": NOW + timedelta(hours=2, minutes=15, seconds=30)})
rows[7].update({"status": "Belum Lunas", "sudah_dichat": True, "janji_bayar": True, "tanggal_janji_bayar": NOW + timedelta(days=3), "deadline_samperin": NOW + timedelta(hours=28, minutes=30, seconds=12)})
rows[8].update({"status": "Belum Lunas", "sudah_dichat": True, "janji_bayar": True, "tanggal_janji_bayar": NOW + timedelta(days=4), "deadline_samperin": NOW + timedelta(hours=54, minutes=28, seconds=45)})

df = pd.DataFrame(rows)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## Debt Collector App")
    st.markdown("Navigasi multipage tetap aktif.")
    st.markdown(
        """
        <div class="sidebar-note">
            Halaman utama ini fokus ke layout dashboard.
            Nanti data asli bisa dipisah ke folder <b>pages/</b> tanpa bongkar ulang UI utama.
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# DERIVED DATA
# =========================
paid_count = int((df["status"] == "Lunas").sum())
unpaid_count = int((df["status"] == "Belum Lunas").sum())
total_accounts = len(df)
paid_pct = round((paid_count / total_accounts) * 100)
unpaid_pct = 100 - paid_pct

outstanding = int(df.loc[df["status"] == "Belum Lunas", "nominal"].sum())
payment_this_month = int(df.loc[df["status"] == "Lunas", "nominal"].sum() * 0.38)
active_debtors = unpaid_count
weekly_target = 80
weekly_target_total = 100

chat_due = df[
    (df["status"] == "Belum Lunas")
    & (~df["sudah_dichat"])
    & (df["jatuh_tempo"] <= NOW + timedelta(days=3))
].copy().sort_values(["jatuh_tempo", "skor_risiko"], ascending=[True, False])

visit_followup = df[
    (df["status"] == "Belum Lunas")
    & (df["sudah_dichat"])
    & (df["deadline_samperin"].notna())
].copy().sort_values("deadline_samperin")
visit_followup["countdown"] = visit_followup["deadline_samperin"].apply(countdown_text)

priority_counts = (
    df[df["status"] == "Belum Lunas"]
    .groupby("prioritas")
    .size()
    .reindex(["Tinggi", "Sedang", "Rendah"], fill_value=0)
)

trend_values = [8, 12, 15, 21]

# =========================
# LAYOUT
# =========================
st.markdown(
    """
    <div class="topbar">
        <div class="topbar-left">
            <div class="logo-box">📄</div>
            <div>
                <div class="topbar-title">Nagih Utang Dashboard</div>
                <div class="topbar-sub">Monitoring admin debt collector • dummy data</div>
            </div>
        </div>
        <div class="admin-box">
            Admin<br><span>Collector</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns([1, 1, 1, 1.7])
with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Tunggakan</div>
            <div class="kpi-value">{format_rupiah(outstanding)}</div>
            <div class="kpi-note">Akumulasi debitur belum lunas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Pembayaran Bulan Ini</div>
            <div class="kpi-value">{format_rupiah(payment_this_month)}</div>
            <div class="kpi-note">Realisasi pembayaran masuk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Debitur Aktif</div>
            <div class="kpi-value">{active_debtors} Orang</div>
            <div class="kpi-note">Masih butuh follow-up</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Target Minggu Ini</div>
            <div class="kpi-value">{weekly_target} / {weekly_target_total} Tercapai</div>
            <div class="kpi-note">Progress penagihan mingguan</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

left_big, mid_big, right_big = st.columns([1.25, 1.25, 0.9])

with left_big:
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Lunas", "Belum Lunas"],
                values=[paid_count, unpaid_count],
                hole=0.45,
                marker=dict(colors=["#5dbb50", "#ea5252"]),
                textinfo="label+percent",
                textfont=dict(size=16, color="white"),
                sort=False,
            )
        ]
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(orientation="v", x=0.95, y=0.5, font=dict(size=14)),
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=360,
    )
    st.markdown('<div class="panel"><div class="panel-title">Status Pelunasan</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(
        f"""
        <div class="mini-progress-wrap">
            <div class="mini-progress-row">
                <div>Lunas</div>
                <div class="mini-progress"><div class="green" style="width:{paid_pct}%;"></div></div>
                <div>{paid_pct}%</div>
            </div>
            <div class="mini-progress-row">
                <div>Belum Lunas</div>
                <div class="mini-progress"><div class="red" style="width:{unpaid_pct}%;"></div></div>
                <div>{unpaid_pct}%</div>
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with mid_big:
    st.markdown('<div class="panel"><div class="panel-title">Tren Follow Up</div></div>', unsafe_allow_html=True)
    fig_line = go.Figure()
    fig_line.add_trace(
        go.Scatter(
            x=["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"],
            y=trend_values,
            mode="lines+markers",
            line=dict(color="#2f73c7", width=4),
            marker=dict(size=12, color="#ffffff", line=dict(color="#2f73c7", width=4)),
            fill="tozeroy",
            fillcolor="rgba(47,115,199,0.18)",
        )
    )
    fig_line.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=250,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor="#dfe8f2", zeroline=False, title=None),
    )
    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

with right_big:
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">Statistik</div>
            <div class="stat-list">
                <div class="stat-row"><span>Chat Terkirim Hari Ini</span><span class="stat-value">25</span></div>
                <div class="stat-row"><span>Janji Bayar</span><span class="stat-value">18 Orang</span></div>
                <div class="stat-row"><span>Kunjungan Dijadwalkan</span><span class="stat-value">7 Debitur</span></div>
                <div class="stat-row"><span>Prioritas Tinggi</span><span class="stat-value">{int(priority_counts['Tinggi'])}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

chat_table = chat_due[["nama", "nominal", "jatuh_tempo"]].copy()
chat_table["nominal"] = chat_table["nominal"].apply(format_rupiah)
chat_table["jatuh_tempo"] = pd.to_datetime(chat_table["jatuh_tempo"]).dt.strftime("%d %b %Y")
chat_table.columns = ["Nama Debitur", "Nominal", "Tgl Jatuh Tempo"]

visit_table = visit_followup[["nama", "tanggal_janji_bayar", "countdown"]].copy()
visit_table["tanggal_janji_bayar"] = pd.to_datetime(visit_table["tanggal_janji_bayar"]).dt.strftime("%d %b %Y")
visit_table.columns = ["Nama Debitur", "Janji Bayar", "Countdown"]

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        f'<div class="panel"><div class="panel-title">Jatuh Tempo - Harus Dichat</div>{render_table(chat_table, list(chat_table.columns))}</div>',
        unsafe_allow_html=True,
    )
with col_b:
    st.markdown(
        f'<div class="panel"><div class="panel-title">Sudah Dichat - Siap Disamperin</div>{render_table(visit_table, list(visit_table.columns), countdown_col="Countdown")}</div>',
        unsafe_allow_html=True,
    )

bottom_left, bottom_right = st.columns([1.1, 1.2])

with bottom_left:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Reminder Kunjungan</div>
            <div class="reminder-item"><div><span class="bullet">●</span>Kunjungi Rina sebelum jam 3 sore</div></div>
            <div class="reminder-item"><div><span class="bullet">●</span>Siapkan berkas untuk Yanto</div></div>
            <div class="reminder-item"><div><span class="bullet">●</span>Prioritaskan debitur skor risiko di atas 90</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with bottom_right:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Aktivitas Terbaru</div>
            <div class="activity-item"><div>💬 Mengirim chat ke Andi</div><div class="muted">10 Menit Lalu</div></div>
            <div class="activity-item"><div>✅ Konfirmasi janji bayar Siti</div><div class="muted">30 Menit Lalu</div></div>
            <div class="activity-item"><div>🗓️ Set jadwal kunjungan untuk Dewi</div><div class="muted">1 Jam Lalu</div></div>
            <div class="activity-item"><div>💵 Pembayaran masuk dari Budi</div><div class="muted">2 Jam Lalu</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption("Struktur dibuat ulang dari awal. CSS ditaruh paling atas. Sidebar/pages tetap aktif. Data masih dummy.")
