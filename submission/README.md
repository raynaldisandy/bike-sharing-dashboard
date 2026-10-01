# Proyek Analisis Data: Bike Sharing Dataset

Analisis data penyewaan sepeda (Capital Bikeshare, Washington D.C., 2011-2012) beserta dashboard interaktif menggunakan Streamlit.

**Pertanyaan bisnis**
1. Pada jam berapa permintaan sewa memuncak di hari kerja dibanding libur/akhir pekan?
2. Berapa persen penurunan penyewaan pada cuaca buruk dibanding cuaca cerah di tiap musim?
3. Berapa pertumbuhan penyewaan bulanan 2012 dibanding 2011 (YoY)?

## Struktur Direktori
```
submission
├── dashboard
│   ├── main_data.csv      # data harian bersih
│   ├── hour_clean.csv     # data per jam bersih
│   └── dashboard.py
├── data
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment
```
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Menjalankan Notebook
Buka `notebook.ipynb` dari folder `submission` (agar path `data/day.csv` terbaca), lalu jalankan semua sel. Jika memakai Google Colab, unggah folder `data` terlebih dahulu.

## Menjalankan Dashboard
Jalankan dari folder `submission`:
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`.
