import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Debt Collector",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Debt Collector")

# =========================
# GOOGLE SHEET CONFIG
# =========================
SHEET_ID = "1wi4id0XqYlTuw_KO89-cOLSPTFAQ6ODv_tH09LK_2Ao"
GID = "0"

# Format CSV export dari Google Sheets
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"


@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)

    # Rapikan nama kolom biar lebih fleksibel
    df.columns = [str(col).strip() for col in df.columns]

    # Mapping nama kolom alternatif -> nama standar
    column_aliases = {
        "Nama": "Nama Nasabah",
        "Nasabah": "Nama Nasabah",
        "Nama_Nasabah": "Nama Nasabah",
        "No HP": "Kontak",
        "No_HP": "Kontak",
        "Phone": "Kontak",
        "Nominal": "Pinjaman",
        "Total Pinjaman": "Pinjaman",
        "Total": "Pinjaman",
        "Sisa Pinjaman": "Sisa",
        "Outstanding": "Sisa",
    }

    df = df.rename(columns={k: v for k, v in column_aliases.items() if k in df.columns})

    # Pastikan semua kolom penting ada
    required_cols = [
        "ID", "Nama Nasabah", "Tahun", "Pinjaman",
        "Dibayar", "Sisa", "Jatuh Tempo", "Status", "Kontak"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Email optional
    if "Email" not in df.columns:
        df["Email"] = ""

    # Konversi angka
    for col in ["Pinjaman", "Dibayar", "Sisa", "Tahun"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("Rp", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Konversi tanggal
    df["Jatuh Tempo"] = pd.to_datetime(df["Jatuh Tempo"], errors="coerce")

    return df


def format_rupiah(x):
    if pd.isna(x):
        return "-"
    return f"Rp {int(x):,}".replace(",", ".")


def normalize_status(row):
    """
    Standarisasi status:
    - Lunas
    - Belum Lunas
    - Jatuh Tempo
    """
    status = str(row.get("Status", "")).strip().lower()
    sisa = row.get("Sisa", 0)
    jatuh_tempo = row.get("Jatuh Tempo", pd.NaT)

    today = pd.Timestamp.today().normalize()

    if pd.notna(sisa) and sisa <= 0:
        return "Lunas"

    if status in ["lunas"]:
        return "Lunas"

    if pd.notna(jatuh_tempo) and jatuh_tempo < today:
        return "Jatuh Tempo"

    return "Belum Lunas"


def badge_status_html(status):
    styles = {
        "Lunas": ("#dcfce7", "#166534"),
        "Belum Lunas": ("#fef3c7", "#92400e"),
        "Jatuh Tempo": ("#fee2e2", "#b91c1c"),
    }
    bg, color = styles.get(status, ("#e5e7eb", "#374151"))
    return f"""
        <span style="
            background:{bg};
            color:{color};
            padding:6px 12px;
            border-radius:999px;
            font-size:14px;
            font-weight:600;
            display:inline-block;
        ">
            {status}
        </span>
    """


# =========================
# LOAD DATA
# =========================
try:
    data = load_data()
except Exception as e:
    st.error("Gagal mengambil data dari Google Sheets.")
    st.code(str(e))
    st.stop()

if data.empty:
    st.warning("Data Google Sheets kosong.")
    st.stop()

# Status hasil normalisasi
data["Status Final"] = data.apply(normalize_status, axis=1)

# Hari keterlambatan
today = pd.Timestamp.today().normalize()
data["Terlambat Hari"] = data["Jatuh Tempo"].apply(
    lambda x: (today - x).days if pd.notna(x) and x < today else 0
)

# =========================
# FILTER
# =========================
st.markdown("## 🔎 Filter Data")

colf1, colf2 = st.columns([1, 1])

with colf1:
    tahun_options = ["Semua", 2023, 2024, 2025, 2026]
    selected_tahun = st.selectbox("Pilih Tahun", tahun_options)

with colf2:
    status_options = ["Semua", "Lunas", "Belum Lunas", "Jatuh Tempo"]
    selected_status = st.selectbox("Pilih Status", status_options)

filtered = data.copy()

if selected_tahun != "Semua":
    filtered = filtered[filtered["Tahun"] == selected_tahun]

if selected_status != "Semua":
    filtered = filtered[filtered["Status Final"] == selected_status]

# =========================
# METRICS
# =========================
total_nasabah = len(filtered)
total_lunas = len(filtered[filtered["Status Final"] == "Lunas"])
total_belum = len(filtered[filtered["Status Final"] == "Belum Lunas"])
total_jatuh_tempo = len(filtered[filtered["Status Final"] == "Jatuh Tempo"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Nasabah", total_nasabah)
c2.metric("Lunas", total_lunas)
c3.metric("Belum Lunas", total_belum)
c4.metric("Jatuh Tempo", total_jatuh_tempo)

# =========================
# CHART
# =========================
st.markdown("## 📈 Persentase Status Pembayaran")

chart_df = (
    filtered["Status Final"]
    .value_counts()
    .reset_index()
)
chart_df.columns = ["Status", "Jumlah"]

if not chart_df.empty:
    fig = px.pie(chart_df, names="Status", values="Jumlah", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Tidak ada data untuk chart.")

# =========================
# SEGERA HUBUNGI
# =========================
st.markdown("## 🚨 Nasabah Jatuh Tempo - Segera Hubungi")

prioritas = filtered[
    filtered["Status Final"].isin(["Belum Lunas", "Jatuh Tempo"])
].copy()

# prioritaskan yang sudah jatuh tempo dulu
prioritas["Urutan"] = prioritas["Status Final"].map({
    "Jatuh Tempo": 0,
    "Belum Lunas": 1
})

prioritas = prioritas.sort_values(
    by=["Urutan", "Terlambat Hari", "Jatuh Tempo"],
    ascending=[True, False, True]
)

st.caption(f"{len(prioritas)} nasabah memerlukan tindak lanjut")

if prioritas.empty:
    st.success("Tidak ada nasabah yang perlu segera dihubungi.")
else:
    rows = []
    for _, row in prioritas.iterrows():
        whatsapp = ""
        email_link = ""

        kontak = str(row["Kontak"]) if pd.notna(row["Kontak"]) else ""
        kontak_clean = (
            kontak.replace("+", "")
            .replace(" ", "")
            .replace("-", "")
        )

        if kontak_clean:
            whatsapp = f"https://wa.me/{kontak_clean}"

        if row["Email"]:
            email_link = f"mailto:{row['Email']}"

        rows.append({
            "Nasabah": f"{row['Nama Nasabah']}\nID: {row['ID']}",
            "Sisa Pinjaman": f"{format_rupiah(row['Sisa'])}\ndari {format_rupiah(row['Pinjaman'])}",
            "Jatuh Tempo": row["Jatuh Tempo"].strftime("%d %b %Y") if pd.notna(row["Jatuh Tempo"]) else "-",
            "Terlambat": f"{int(row['Terlambat Hari'])} hari" if row["Terlambat Hari"] > 0 else "-",
            "Kontak": whatsapp if whatsapp else kontak
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True
    )

# =========================
# TABEL SEMUA NASABAH
# =========================
st.markdown("## 📋 Data Semua Nasabah")

search = st.text_input("Cari nama, ID, email, atau kontak...")

table_df = filtered.copy()

if search:
    keyword = search.lower()
    table_df = table_df[
        table_df["ID"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["Nama Nasabah"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["Email"].astype(str).str.lower().str.contains(keyword, na=False) |
        table_df["Kontak"].astype(str).str.lower().str.contains(keyword, na=False)
    ]

st.caption(f"Menampilkan {len(table_df)} dari {len(filtered)} nasabah")

display_df = table_df[[
    "ID", "Nama Nasabah", "Email", "Tahun",
    "Pinjaman", "Dibayar", "Sisa",
    "Jatuh Tempo", "Status Final", "Kontak"
]].copy()

display_df["Pinjaman"] = display_df["Pinjaman"].apply(format_rupiah)
display_df["Dibayar"] = display_df["Dibayar"].apply(format_rupiah)
display_df["Sisa"] = display_df["Sisa"].apply(format_rupiah)
display_df["Jatuh Tempo"] = display_df["Jatuh Tempo"].apply(
    lambda x: x.strftime("%d %b %Y") if pd.notna(x) else "-"
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# =========================
# RINGKASAN KHUSUS BELUM LUNAS
# =========================
st.markdown("## 📞 Daftar Nasabah Belum Lunas")

belum_lunas_df = filtered[
    filtered["Status Final"].isin(["Belum Lunas", "Jatuh Tempo"])
][["ID", "Nama Nasabah", "Tahun", "Sisa", "Jatuh Tempo", "Status Final", "Kontak"]].copy()

belum_lunas_df["Sisa"] = belum_lunas_df["Sisa"].apply(format_rupiah)
belum_lunas_df["Jatuh Tempo"] = belum_lunas_df["Jatuh Tempo"].apply(
    lambda x: x.strftime("%d %b %Y") if pd.notna(x) else "-"
)

st.dataframe(
    belum_lunas_df,
    use_container_width=True,
    hide_index=True
)
