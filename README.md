# 🛃 E-Tranzit Monitoring Tizimi v2.0

O'zbekiston Respublikasi Davlat Bojxona Qo'mitasi uchun Elektron Tranzit Monitoring Dashboard.

## 📁 Fayl tuzilmasi

```
e_transit_app/
├── app.py                    # Asosiy Streamlit ilova
├── requirements.txt          # Python kutubxonalar
├── .streamlit/
│   └── config.toml           # Streamlit konfiguratsiya (dark tema)
└── data/                     # Tasniflagich fayllar papkasi
    ├── Post_coordinates.xlsx
    ├── Davlatlar_tasniflagichi_qitalar_bilan.xlsx
    └── Countries_Classification_PowerBI.xlsx
```

## 🚀 Ishga tushirish

1. Kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

2. Tasniflagich fayllarni `data/` papkasiga joylashtiring:
   - `Post_coordinates.xlsx` — Chegara postlari koordinatalari
   - `Davlatlar_tasniflagichi_qitalar_bilan.xlsx` — Davlatlar tasniflagichi
   - `Countries_Classification_PowerBI.xlsx` — Countries Classification

3. Ilovani ishga tushiring:
```bash
streamlit run app.py
```



## 📊 Dashboard imkoniyatlari

- **Postlar xaritasi**: O'zbekiston chegara postlari bubble map (Brutto bo'yicha)
- **Davlatlar xaritasi**: Yuboruvchi davlatlar dunyo xaritasida
- **Vaqt tahlili**: Kunlik, haftalik, oylik, yillik dinamika
- **Analitika**: Top davlatlar, postlar, xavf yo'lagi, toifa tahlillari
- **Ma'lumotlar**: Qidiruv va saralash imkoniyatli jadval

## ⚙️ Texnik talablar

- Python 3.9+
- Streamlit 1.30+
- Internet (Plotly xaritalar uchun)
