import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard Debt Collector",
    page_icon="💳",
    layout="wide",
)

# =========================
# Dummy data generators
# =========================
TODAY = datetime.now()
random.seed(42)


def format_rupiah(amount: int) -> str:
    return f"Rp {amount:,.0f}".replace(",", ".")


customers = [
    "Budi Santoso", "Siti Aminah", "Andi Pratama", "Rina Marlina", "Yanto Wijaya",
    "Dewi Lestari", "Rudi Hartono", "Nina Kurnia", "Fajar Nugroho", "Lukman Hakim",
    "Tika Ramadhani", "Hendra Saputra", "Maya Sari", "Riko Setiawan", "Putri Ayu",
    "Bagus Mahendra", "Intan Permata", "Asep Suhendar", "Rahmat Hidayat", "Desi Anggraini",
]

areas = ["Jakarta Timur", "Jakarta Barat", "Bekasi", "Depok", "Tangerang"]
collectors = ["Aldi", "Bayu", "Citra", "Dimas"]
statuses = ["Lunas", "Belum Lunas"]

rows = []
for i, name in enumerate(customers, start=1):
    due_days = random.randint(-15, 10)
    due_date = TODAY + timedelta(days=due_days)
    loan_amount = random.randint(1_500_000, 15_000_000)
    paid = random.choice([True, False, False])
    status = "Lunas" if paid else "Belum Lunas"
    contacted = random.choice([True, False]) if not paid else True
    promised = random.choice([True, False]) if contacted and not paid else False
    promised_date = TODAY + timedelta(days=random.randint(0, 5)) if promised else None
    visit_deadline = TODAY + timedelta(hours=random.randint(2, 72)) if contacted and promised and not paid else None

    rows.append(
        {
            "id": i,
            "nama": name,
            "wilayah": random.choice(areas),
            "collector": random.choice(collectors),
            "nominal": loan_amount,
            "jatuh_tempo": due_date,
            "status": status,
            "sudah_dichat": contacted,
            "janji_bayar": promised,
            "tanggal_janji_bayar": promised_date,
            "deadline_samperin": visit_deadline,
            "prioritas": random.choice(["Tinggi", "Sedang", "Rendah"]),
            "skor_risiko": random.randint(45, 98),
        }
    )


df = pd.DataFrame(rows)

# =========================
# Derived data
# =========================
total_outstanding = int(df.loc[df["status"] == "Belum Lunas", "nominal"].sum())
total_accounts = int(len(df))
paid_accounts = int((df["status"] == "Lunas").sum())
unpaid_accounts = int((df["status"] == "Belum Lunas").sum())
contacted_today = int(df[(df["status"] == "Belum Lunas") & (df["sudah_dichat"])].shape[0])
need_visit = int(df["deadline_samperin"].notna().sum())

paid_pct = round((paid_accounts / total_accounts) * 100, 1) if total_accounts else 0
unpaid_pct = round((unpaid_accounts / total_accounts) * 100, 1) if total_accounts else 0

jatuh_tempo_chat = df[
    (df["status"] == "Belum Lunas")
    & (df["sudah_dichat"] == False)
    & (df["jatuh_tempo"] <= TODAY + timedelta(days=3))
].copy()

sudah_chat_visit = df[
    (df["status"] == "Belum Lunas")
    & (df["sudah_dichat"])
    & (df["deadline_samperin"].notna())
].copy()


def countdown_text(target_time):
    if pd.isna(target_time):
        return "-"
    delta = target_time - TODAY
    seconds = int(delta.total_seconds())
    if seconds <= 0:
        return "Lewat deadline"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    if days > 0:
        return f"{days}h {hours}j {minutes}m"
    return f"{hours}j {minutes}m"


sudah_chat_visit["countdown_samperin"] = sudah_chat_visit["deadline_samperin"].apply(countdown_text)

collector_perf = (
    df.groupby("collector", as_index=False)
    .agg(
        total_debitur=("id", "count"),
        total_lunas=("status", lambda x: (x == "Lunas").sum()),
        total_belum_lunas=("status", lambda x: (x == "Belum Lunas").sum()),
        total_nominal=("nominal", "sum"),
    )
)
collector_perf["success_rate"] = (
    (collector_perf["total_lunas"] / collector_perf["total_debitur"]) * 100
).round(1)

priority_breakdown = (
    df[df["status"] == "Belum Lunas"]
    .groupby("prioritas", as_index=False)
    .agg(jumlah=("id", "count"))
)

recent_activities = pd.DataFrame(
    [
        {"waktu": "10 menit lalu", "aktivitas": "Chat pengingat dikirim ke Andi Pratama"},
        {"waktu": "25 menit lalu", "aktivitas": "Rina Marlina janji bayar besok"},
        {"waktu": "45 menit lalu", "aktivitas": "Jadwal kunjungan dibuat untuk Yanto Wijaya"},
        {"waktu": "1 jam lalu", "aktivitas": "Pembayaran masuk dari Budi Santoso"},
        {"waktu": "2 jam lalu", "aktivitas": "Data kontak Dewi Lestari diperbarui"},
    ]
)

# =========================
# UI
# =========================
st.title("💳 Dashboard Admin Debt Collector")
st.caption("Versi dummy data untuk kebutuhan prototyping")

with st.sidebar:
    st.header("Filter")
    selected_area = st.multiselect("Wilayah", options=sorted(df["wilayah"].unique()), default=sorted(df["wilayah"].unique()))
    selected_collector = st.multiselect("Collector", options=sorted(df["collector"].unique()), default=sorted(df["collector"].unique()))
    selected_priority = st.multiselect("Prioritas", options=sorted(df["prioritas"].unique()), default=sorted(df["prioritas"].unique()))

filtered_df = df[
    df["wilayah"].isin(selected_area)
    & df["collector"].isin(selected_collector)
    & df["prioritas"].isin(selected_priority)
].copy()

# Recalculate after filters
ftotal_outstanding = int(filtered_df.loc[filtered_df["status"] == "Belum Lunas", "nominal"].sum())
ftotal_accounts = int(len(filtered_df))
ffully_paid = int((filtered_df["status"] == "Lunas").sum())
funpaid = int((filtered_df["status"] == "Belum Lunas").sum())
fpaid_pct = round((ffully_paid / ftotal_accounts) * 100, 1) if ftotal_accounts else 0
funpaid_pct = round((funpaid / ftotal_accounts) * 100, 1) if ftotal_accounts else 0
fcontacted = int(filtered_df[(filtered_df["status"] == "Belum Lunas") & (filtered_df["sudah_dichat"])].shape[0])
fneed_visit = int(filtered_df["deadline_samperin"].notna().sum())

fjatuh_tempo_chat = filtered_df[
    (filtered_df["status"] == "Belum Lunas")
    & (filtered_df["sudah_dichat"] == False)
    & (filtered_df["jatuh_tempo"] <= TODAY + timedelta(days=3))
].copy()

fsudah_chat_visit = filtered_df[
    (filtered_df["status"] == "Belum Lunas")
    & (filtered_df["sudah_dichat"])
    & (filtered_df["deadline_samperin"].notna())
].copy()
fsudah_chat_visit["countdown_samperin"] = fsudah_chat_visit["deadline_samperin"].apply(countdown_text)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tunggakan", format_rupiah(ftotal_outstanding))
col2.metric("Total Debitur", ftotal_accounts)
col3.metric("Sudah Dichat", fcontacted)
col4.metric("Perlu Disamperin", fneed_visit)

left, right = st.columns([1, 1])

with left:
    st.subheader("Persentase Pelunasan")
    pie_df = pd.DataFrame(
        {
            "status": ["Lunas", "Belum Lunas"],
            "jumlah": [ffully_paid, funpaid],
        }
    )
    fig_pie = px.pie(
        pie_df,
        names="status",
        values="jumlah",
        hole=0.45,
        title=None,
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.progress(int(fpaid_pct), text=f"Lunas {fpaid_pct}%")
    st.progress(int(funpaid_pct), text=f"Belum Lunas {funpaid_pct}%")

with right:
    st.subheader("Distribusi Prioritas Debitur")
    pr_df = (
        filtered_df[filtered_df["status"] == "Belum Lunas"]
        .groupby("prioritas", as_index=False)
        .agg(jumlah=("id", "count"))
    )
    if not pr_df.empty:
        fig_bar = px.bar(pr_df, x="prioritas", y="jumlah", text="jumlah")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Tidak ada data prioritas untuk filter ini.")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Tabel yang Harus Dichat (Jatuh Tempo)")
    chat_table = fjatuh_tempo_chat[[
        "nama", "wilayah", "collector", "nominal", "jatuh_tempo", "prioritas", "skor_risiko"
    ]].copy()
    if not chat_table.empty:
        chat_table["nominal"] = chat_table["nominal"].apply(format_rupiah)
        chat_table["jatuh_tempo"] = pd.to_datetime(chat_table["jatuh_tempo"]).dt.strftime("%d-%m-%Y")
        st.dataframe(chat_table, use_container_width=True, hide_index=True)
    else:
        st.success("Tidak ada debitur jatuh tempo yang belum dichat.")

with col_b:
    st.subheader("Tabel yang Sudah Dichat dan Countdown Disamperin")
    visit_table = fsudah_chat_visit[[
        "nama", "wilayah", "collector", "tanggal_janji_bayar", "countdown_samperin", "prioritas"
    ]].copy()
    if not visit_table.empty:
        visit_table["tanggal_janji_bayar"] = pd.to_datetime(visit_table["tanggal_janji_bayar"]).dt.strftime("%d-%m-%Y")
        st.dataframe(visit_table, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data follow-up kunjungan.")

bottom_left, bottom_right = st.columns([1.1, 0.9])

with bottom_left:
    st.subheader("Performa Collector")
    cperf = (
        filtered_df.groupby("collector", as_index=False)
        .agg(
            total_debitur=("id", "count"),
            lunas=("status", lambda x: (x == "Lunas").sum()),
            belum_lunas=("status", lambda x: (x == "Belum Lunas").sum()),
            total_nominal=("nominal", "sum"),
        )
    )
    if not cperf.empty:
        cperf["success_rate"] = ((cperf["lunas"] / cperf["total_debitur"]) * 100).round(1)
        cperf["total_nominal"] = cperf["total_nominal"].apply(format_rupiah)
        st.dataframe(cperf, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data collector.")

with bottom_right:
    st.subheader("Aktivitas Terbaru")
    st.dataframe(recent_activities, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Semua Data Debitur")
all_table = filtered_df[[
    "id", "nama", "wilayah", "collector", "nominal", "status", "jatuh_tempo",
    "sudah_dichat", "janji_bayar", "prioritas", "skor_risiko"
]].copy()
all_table["nominal"] = all_table["nominal"].apply(format_rupiah)
all_table["jatuh_tempo"] = pd.to_datetime(all_table["jatuh_tempo"]).dt.strftime("%d-%m-%Y")
st.dataframe(all_table, use_container_width=True, hide_index=True)

st.caption("Catatan: ini masih dummy data. Langkah berikutnya tinggal saya sambungkan ke database/API Anda.")
