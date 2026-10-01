from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")
BASE = Path(__file__).parent
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
MUSIM = ["Semi", "Panas", "Gugur", "Dingin"]
CUACA = ["Cerah", "Berkabut/Mendung", "Hujan/Salju Ringan"]
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")


@st.cache_data
def load_data():
    day = pd.read_csv(BASE / "main_data.csv", parse_dates=["dteday"])
    hour = pd.read_csv(BASE / "hour_clean.csv", parse_dates=["dteday"])
    return day, hour


day_df, hour_df = load_data()

# ---------------- Sidebar ----------------
st.sidebar.title("🚲 Filter Data")
min_d, max_d = day_df["dteday"].min().date(), day_df["dteday"].max().date()
rentang = st.sidebar.date_input("Rentang tanggal", (min_d, max_d), min_value=min_d, max_value=max_d)
if isinstance(rentang, tuple) and len(rentang) == 2:
    start, end = rentang
else:
    start, end = min_d, max_d
musim_pilih = st.sidebar.multiselect("Musim", MUSIM, default=MUSIM)
cuaca_pilih = st.sidebar.multiselect("Kondisi cuaca", CUACA, default=CUACA)

mask_d = (
    day_df["dteday"].between(pd.Timestamp(start), pd.Timestamp(end))
    & day_df["season"].isin(musim_pilih)
    & day_df["weathersit"].isin(cuaca_pilih)
)
mask_h = (
    hour_df["dteday"].between(pd.Timestamp(start), pd.Timestamp(end))
    & hour_df["season"].isin(musim_pilih)
    & hour_df["weathersit"].isin(cuaca_pilih)
)
day_f, hour_f = day_df[mask_d], hour_df[mask_h]

st.title("🚲 Dashboard Analisis Bike Sharing 2011-2012")
st.caption("Capital Bikeshare, Washington D.C. Gunakan filter di sidebar untuk mengeksplorasi data.")

if day_f.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah filter di sidebar.")
    st.stop()

# ---------------- KPI ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Penyewaan", f"{day_f['cnt'].sum():,}")
c2.metric("Rata-rata per Hari", f"{day_f['cnt'].mean():,.0f}")
c3.metric("Pengguna Registered", f"{day_f['registered'].sum() / day_f['cnt'].sum():.0%}")
c4.metric("Pengguna Casual", f"{day_f['casual'].sum() / day_f['cnt'].sum():.0%}")

tab1, tab2, tab3, tab4 = st.tabs(["⏰ Pola Per Jam", "🌦️ Cuaca & Musim", "📈 Pertumbuhan Bulanan", "🔎 Analisis Lanjutan"])

# ---------------- Tab 1 ----------------
with tab1:
    st.subheader("Kapan permintaan sewa sepeda memuncak?")
    pola = hour_f.pivot_table(index="hr", columns="day_type", values="cnt", aggfunc="mean")
    warna = {"Hari Kerja": "#1f77b4", "Libur/Akhir Pekan": "#ff7f0e"}
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for tipe in pola.columns:
        ax.plot(pola.index, pola[tipe], marker="o", lw=2.2, label=tipe, color=warna[tipe])
        jp = pola[tipe].idxmax()
        ax.annotate(f"{jp}:00 ({pola[tipe].max():.0f})", xy=(jp, pola[tipe].max()),
                    xytext=(jp, pola[tipe].max() + 30), ha="center", color=warna[tipe], fontsize=9)
    ax.set_xticks(range(24)); ax.set_xlabel("Jam"); ax.set_ylabel("Rata-rata penyewaan per jam")
    ax.set_title("Pola Rata-rata Penyewaan per Jam", fontweight="bold"); ax.legend(); sns.despine()
    st.pyplot(fig)

    heat = hour_f.pivot_table(index="weekday", columns="hr", values="cnt", aggfunc="mean").reindex(HARI)
    fig, ax = plt.subplots(figsize=(10, 3.8))
    sns.heatmap(heat, cmap="YlOrRd", ax=ax, cbar_kws={"label": "Rata-rata sewa/jam"})
    ax.set_xlabel("Jam"); ax.set_ylabel(""); ax.set_title("Heatmap Hari x Jam", fontweight="bold")
    st.pyplot(fig)
    st.info("Hari kerja punya dua puncak (08:00 dan 17:00, pola komuter), sedangkan libur/akhir pekan memuncak sekitar 13:00.")

# ---------------- Tab 2 ----------------
with tab2:
    st.subheader("Seberapa besar cuaca menurunkan penyewaan?")
    mc = day_f.pivot_table(index="season", columns="weathersit", values="cnt", aggfunc="mean")
    mc = mc.reindex(index=[m for m in MUSIM if m in mc.index], columns=[c for c in CUACA if c in mc.columns])
    col_a, col_b = st.columns(2)
    with col_a:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        mc.plot(kind="bar", ax=ax, color=["#2a9d8f", "#e9c46a", "#e76f51"][: mc.shape[1]], width=.8)
        ax.set_xlabel(""); ax.set_ylabel("Rata-rata penyewaan harian"); ax.tick_params(axis="x", rotation=0)
        ax.set_title("Rata-rata Penyewaan per Musim & Cuaca", fontweight="bold"); ax.legend(title="Cuaca", fontsize=8); sns.despine()
        st.pyplot(fig)
    with col_b:
        if "Cerah" in mc.columns and mc.shape[1] > 1:
            pen = (mc.div(mc["Cerah"], axis=0) - 1).mul(100).drop(columns="Cerah")
            fig, ax = plt.subplots(figsize=(6, 4.5))
            pen.plot(kind="bar", ax=ax, color=["#e9c46a", "#e76f51"][: pen.shape[1]], width=.7)
            for c in ax.containers:
                ax.bar_label(c, fmt="%.0f%%", fontsize=9)
            ax.set_xlabel(""); ax.set_ylabel("% selisih"); ax.tick_params(axis="x", rotation=0)
            ax.set_title("Selisih terhadap Cuaca Cerah (%)", fontweight="bold"); ax.legend(title="Cuaca", fontsize=8); sns.despine()
            st.pyplot(fig)
        else:
            st.write("Pilih cuaca 'Cerah' dan minimal satu cuaca lain untuk melihat persentase selisih.")
    st.info("Cuaca berkabut menurunkan penyewaan sekitar 17% dan hujan/salju ringan sekitar 63% dibanding cuaca cerah (seluruh periode).")

# ---------------- Tab 3 ----------------
with tab3:
    st.subheader("Bagaimana pertumbuhan 2012 dibanding 2011?")
    bln = day_df.pivot_table(index="mnth", columns="yr", values="cnt", aggfunc="sum").reindex(BULAN)
    bln["yoy"] = (bln[2012] / bln[2011] - 1) * 100
    col_a, col_b = st.columns(2)
    with col_a:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        x = np.arange(12)
        ax.bar(x - .2, bln[2011], .4, label="2011", color="#8ecae6")
        ax.bar(x + .2, bln[2012], .4, label="2012", color="#023047")
        ax.set_xticks(x); ax.set_xticklabels(BULAN, fontsize=8); ax.set_ylabel("Total penyewaan")
        ax.set_title("Total Penyewaan Bulanan", fontweight="bold"); ax.legend(); sns.despine()
        st.pyplot(fig)
    with col_b:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        ax.bar(bln.index, bln["yoy"], color=np.where(bln["yoy"] == bln["yoy"].max(), "#e76f51", "#8ecae6"))
        for i, v in enumerate(bln["yoy"]):
            ax.text(i, v + 2, f"{v:.0f}%", ha="center", fontsize=8)
        ax.set_ylabel("% pertumbuhan YoY"); ax.tick_params(axis="x", labelsize=8)
        ax.set_title("Pertumbuhan Year-over-Year", fontweight="bold"); sns.despine()
        st.pyplot(fig)
    st.caption("Grafik tab ini selalu memakai seluruh data (2011 vs 2012) agar perbandingan tahunan tetap utuh.")
    st.info(f"Total 2012 tumbuh {(bln[2012].sum() / bln[2011].sum() - 1) * 100:.0f}% dibanding 2011; "
            f"tertinggi {bln['yoy'].idxmax()} ({bln['yoy'].max():.0f}%), terendah {bln['yoy'].idxmin()} ({bln['yoy'].min():.0f}%).")

# ---------------- Tab 4 ----------------
with tab4:
    st.subheader("Manual Grouping & Binning")
    hf = hour_f.copy()
    hf["segmen_waktu"] = pd.cut(hf["hr"], bins=[-1, 5, 9, 15, 19, 23],
                                labels=["Dini Hari (00-05)", "Pagi (06-09)", "Siang (10-15)", "Sore (16-19)", "Malam (20-23)"])
    seg = hf.pivot_table(index="segmen_waktu", columns="day_type", values="cnt", aggfunc="mean", observed=True)
    df2 = day_f.copy()
    df2["kategori_suhu"] = pd.cut(df2["temp"], bins=[0, 10, 20, 30, 50],
                                  labels=["Dingin (<10°C)", "Sejuk (10-20°C)", "Hangat (20-30°C)", "Panas (>30°C)"])
    suhu = df2.groupby("kategori_suhu", observed=True)["cnt"].mean()
    c_a, c_b = st.columns(2)
    with c_a:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        seg.plot(kind="bar", ax=ax, color=["#1f77b4", "#ff7f0e"])
        ax.set_xlabel(""); ax.tick_params(axis="x", rotation=30); ax.set_ylabel("Rata-rata sewa/jam")
        ax.set_title("Per Segmen Waktu", fontweight="bold"); ax.legend(fontsize=8); sns.despine()
        st.pyplot(fig)
    with c_b:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        suhu.plot(kind="bar", ax=ax, color="#2a9d8f")
        ax.set_xlabel(""); ax.tick_params(axis="x", rotation=20); ax.set_ylabel("Rata-rata penyewaan harian")
        ax.set_title("Per Kategori Suhu", fontweight="bold"); sns.despine()
        st.pyplot(fig)
    st.info("Penyewaan tertinggi pada suhu hangat (20-30 °C); pada suhu di bawah 10 °C hanya sekitar sepertiganya.")

st.caption("Data: UCI Bike Sharing Dataset (2011-2012)")
