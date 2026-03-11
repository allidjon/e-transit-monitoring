"""
╔══════════════════════════════════════════════════════════════╗
║  O'zbekiston Respublikasi Bojxona Qo'mitasi          ║
║  E-Tranzit Monitoring Tizimi v2.1                           ║
║  Streamlit Professional Analytics Dashboard                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings
warnings.filterwarnings('ignore')

from github import Github
import base64

def push_to_github(local_path, repo_path="data/cached_data.parquet"):
    token = st.secrets.get("GITHUB_TOKEN")
    repo_name = st.secrets.get("GITHUB_REPO")
    if not token or not repo_name:
        return
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        with open(local_path, "rb") as f:
            content = f.read()
        try:
            existing = repo.get_contents(repo_path)
            repo.update_file(repo_path, "Update cached data", content, existing.sha)
        except:
            repo.create_file(repo_path, "Add cached data", content)
        st.sidebar.success("✅ GitHub ga saqlandi!")
    except Exception as e:
        st.sidebar.warning(f"GitHub saqlash: {e}")



# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="E-Tranzit Monitoring | DBQ",
    page_icon="🛃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Manrope:wght@300;400;500;600;700;800&display=swap');
    :root {
        --bg-primary: #0a0e1a; --bg-secondary: #111827; --bg-card: #1a2035;
        --bg-card-hover: #1e2745; --accent-cyan: #00d4aa; --accent-blue: #3b82f6;
        --text-primary: #f1f5f9; --text-secondary: #94a3b8; --border-color: #1e293b;
    }
    .stApp { background: linear-gradient(135deg, var(--bg-primary) 0%, #0f172a 50%, var(--bg-primary) 100%); }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1320 0%, #111827 100%) !important;
        border-right: 1px solid rgba(0,212,170,0.15);
    }
    .main-header {
        background: linear-gradient(135deg, rgba(0,212,170,0.08) 0%, rgba(59,130,246,0.08) 100%);
        border: 1px solid rgba(0,212,170,0.2); border-radius: 16px; padding: 24px 32px; margin-bottom: 24px;
    }
    .main-header h1 {
        font-family: 'Manrope', sans-serif; font-weight: 800; font-size: 28px;
        background: linear-gradient(135deg, #00d4aa, #3b82f6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
    }
    .main-header p { color: var(--text-secondary); margin: 4px 0 0 0; font-size: 14px; }
    .kpi-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-hover) 100%);
        border: 1px solid var(--border-color); border-radius: 14px; padding: 20px 24px;
        text-align: center; position: relative; overflow: hidden;
    }
    .kpi-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue));
        border-radius: 14px 14px 0 0;
    }
    .kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; color: var(--accent-cyan); margin: 8px 0; }
    .kpi-label { font-size: 13px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }
    .kpi-icon { font-size: 24px; margin-bottom: 4px; }
    .section-header {
        font-family: 'Manrope', sans-serif; font-weight: 700; font-size: 20px;
        color: var(--text-primary); padding: 12px 0 8px 0;
        border-bottom: 2px solid rgba(0,212,170,0.2); margin-bottom: 16px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: var(--bg-secondary); border-radius: 12px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px; font-family: 'Manrope', sans-serif; font-weight: 600; }
    [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; color: var(--accent-cyan) !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .custom-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(0,212,170,0.3), transparent); margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "sanjar1989")
USER_PASSWORD  = st.secrets.get("USER_PASSWORD",  "ilmiymarkaz")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CYAN_SCALE   = ['#064e3b','#065f46','#047857','#059669','#10b981','#34d399','#6ee7b7','#a7f3d0','#00d4aa']
MAIN_COLORS  = ['#00d4aa','#3b82f6','#f59e0b','#ef4444','#8b5cf6','#ec4899','#14b8a6','#f97316','#06b6d4','#84cc16']
RISK_COLORS  = {'Yashil':'#10b981','Sariq':'#f59e0b','Qizil':'#ef4444'}
TOIFA_COLORS = {'Import':'#3b82f6','Tranzit':'#f59e0b','Eksport':'#10b981'}
OY_NOMI = {1:'Yanvar',2:'Fevral',3:'Mart',4:'Aprel',5:'May',6:'Iyun',
           7:'Iyul',8:'Avgust',9:'Sentabr',10:'Oktabr',11:'Noyabr',12:'Dekabr'}

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
for _k, _v in [('authenticated',False),('role',None),('data',None),('data_loaded',False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def fmt(n, d=0):
    if pd.isna(n): return "—"
    return f"{n:,.{d}f}".replace(",", " ")

def make_dark(fig, height=420):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0', family='Manrope, sans-serif', size=12),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.08)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.08)'),
        margin=dict(l=50, r=20, t=50, b=50), height=height,
        hoverlabel=dict(bgcolor='#1a2035', bordercolor='#00d4aa', font=dict(color='#e0e0e0', size=13)),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=11)),
    )
    return fig

def load_reference_data():
    post_coords = countries_uz = countries_en = None
    fmap = {
        "Post_coordinates.xlsx": "post",
        "Davlatlar_tasniflagichi_qitalar_bilan.xlsx": "uz",
        "Countries_Classification_PowerBI.xlsx": "en",
    }
    for fname, key in fmap.items():
        fpath = os.path.join(DATA_DIR, fname)
        if os.path.exists(fpath):
            try:
                tmp = pd.read_excel(fpath)
                if key == "post":   post_coords  = tmp
                elif key == "uz":   countries_uz = tmp
                elif key == "en":   countries_en = tmp
            except Exception as e:
                st.sidebar.warning(f"{fname}: {e}")
    return post_coords, countries_uz, countries_en

def _find_col(df, exact, partial=None, dtype_hint=None):
    for c in exact:
        for col in df.columns:
            if col.strip().lower() == c.strip().lower():
                return col
    if partial:
        for kw in partial:
            for col in df.columns:
                if kw.lower() in col.strip().lower():
                    return col
    if dtype_hint:
        for col in df.columns:
            if str(df[col].dtype) in dtype_hint:
                try:
                    if df[col].max() > 100: return col
                except Exception:
                    pass
    return df.columns[0]

def get_post_code_col(df):
    return _find_col(df, ['Post kodi','Post_kodi','POST_KODI','Kod','KOD'],
                     dtype_hint=['int64','float64','int32'])

def get_post_name_col(df):
    return _find_col(df, ['Post nomi','Post_nomi','POST_NOMI','Nomi','Chegara post nomi'],
                     partial=['nomi','post'])

def get_lat_lon(df):
    lat = lon = None
    for col in df.columns:
        cl = col.strip().lower()
        if 'lat' in cl: lat = col
        if 'lon' in cl or 'lng' in cl: lon = col
    return lat, lon

def get_country_code_col(df):
    return _find_col(df,
        ['Raqamli kodi','Raqamli kod','Raqamli_kod','ISO_Numeric','ISO Numeric','Numeric'],
        partial=['raqamli'], dtype_hint=['int64','float64','int32'])

def get_country_name_col(df):
    return _find_col(df,
        ["Mamlakatning qisqa nomi","Davlat nomi","Davlat_nomi","Country","Mamlakat"],
        partial=['qisqa','nom'])

def get_continent_col(df):
    return _find_col(df, ["Qit'a","Qita","Continent","continent"],
                     partial=["qit","cont"])

def build_country_name_map(countries_uz):
    if countries_uz is None:
        return {}, None, None
    cc = get_country_code_col(countries_uz)
    cn = get_country_name_col(countries_uz)
    ref = countries_uz[[cc, cn]].copy()
    ref[cc] = pd.to_numeric(ref[cc], errors='coerce')
    nm = dict(zip(ref[cc], ref[cn]))
    return nm, cc, cn

def merge_country_names(df_agg, countries_uz, key='YUBORUVCHI_DAVLAT'):
    nm, cc, cn = build_country_name_map(countries_uz)
    if not nm:
        df_agg['Davlat'] = 'Davlat ' + df_agg[key].astype(str)
        return df_agg
    ref = countries_uz[[cc, cn]].copy()
    ref[cc] = pd.to_numeric(ref[cc], errors='coerce')
    df_agg = df_agg.copy()
    df_agg[key] = pd.to_numeric(df_agg[key], errors='coerce')
    merged = df_agg.merge(ref, left_on=key, right_on=cc, how='left')
    merged['Davlat'] = merged[cn].fillna('Davlat ' + merged[key].astype(str))
    return merged

def normalize_risk(df):
    """yolak_yoq va NaN qiymatlarni Sariq deb hisoblash."""
    df = df.copy()
    if 'HAVF_YOLAGI' in df.columns:
        df['HAVF_YOLAGI'] = df['HAVF_YOLAGI'].fillna('Sariq')
        df['HAVF_YOLAGI'] = df['HAVF_YOLAGI'].replace('yolak_yoq', 'Sariq')
    return df

# ══════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════
def login_page():
    st.markdown("""
    <div style="text-align:center; margin-top:60px;">
        <div style="font-size:64px; margin-bottom:16px;">🛃</div>
        <h1 style="font-family:'Manrope',sans-serif; font-weight:800; font-size:32px;
            background:linear-gradient(135deg,#00d4aa,#3b82f6);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            E-Tranzit Monitoring Tizimi
        </h1>
        <p style="color:#94a3b8; font-size:15px; margin-bottom:40px;">
            O'zbekiston Respublikasi Bojxona Qo'mitasi
        </p>
    </div>""", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        role = st.radio("Rol", ["👑 Admin", "👤 User"], horizontal=True, label_visibility="collapsed")
        pw   = st.text_input("Parol", type="password", placeholder="••••••••")
        if st.button("🔐  Kirish", use_container_width=True, type="primary"):
            r   = "admin" if "Admin" in role else "user"
            cpw = ADMIN_PASSWORD if r == "admin" else USER_PASSWORD
            if pw == cpw:
                st.session_state.authenticated = True
                st.session_state.role = r
                st.rerun()
            else:
                st.error("❌ Parol noto'g'ri!")
        st.caption("Admin: Ma'lumot yuklash | User: Dashboard ko'rish")

# ══════════════════════════════════════════════════════════════
# ADMIN UPLOAD
# ══════════════════════════════════════════════════════════════
def admin_upload_section():
    st.sidebar.markdown("### 📂 Ma'lumot yuklash")
    uploaded = st.sidebar.file_uploader("Parquet fayl", type=['parquet'])
    if uploaded:
        try:
            df = pd.read_parquet(uploaded)
            if 'CHECKINTIME' in df.columns:
                df['CHECKINTIME'] = pd.to_datetime(df['CHECKINTIME'], errors='coerce')
            for c in ['Brutto','Netto']:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce')
            st.session_state.data = df
            st.session_state.data_loaded = True
            st.sidebar.success(f"✅ {len(df):,} qator yuklandi!")
            df.to_parquet(os.path.join(DATA_DIR, "cached_data.parquet"), index=False)
        except Exception as e:
            st.sidebar.error(f"Xatolik: {e}")

    with st.sidebar.expander("📋 Tasniflagich fayllar"):
        for key, label, fname in [
            ('ref_post','Post_coordinates.xlsx','Post_coordinates.xlsx'),
            ('ref_uz','Davlatlar tasniflagichi','Davlatlar_tasniflagichi_qitalar_bilan.xlsx'),
            ('ref_en','Countries Classification','Countries_Classification_PowerBI.xlsx'),
        ]:
            f = st.file_uploader(label, type=['xlsx'], key=key)
            if f:
                try:
                    pd.read_excel(f).to_excel(os.path.join(DATA_DIR, fname), index=False)
                    st.success(f"{label} saqlandi!")
                except Exception as e:
                    st.error(str(e))
    push_to_github(os.path.join(DATA_DIR, "cached_data.parquet"))

def user_load_data():
    p = os.path.join(DATA_DIR, "cached_data.parquet")
    if os.path.exists(p):
        df = pd.read_parquet(p)
        if 'CHECKINTIME' in df.columns:
            df['CHECKINTIME'] = pd.to_datetime(df['CHECKINTIME'], errors='coerce')
        for c in ['Brutto','Netto']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
        st.session_state.data = df
        st.session_state.data_loaded = True

# ══════════════════════════════════════════════════════════════
# SIDEBAR GLOBAL FILTERS
# ══════════════════════════════════════════════════════════════
def sidebar_global_filters(df, post_coords, countries_uz):
    st.sidebar.markdown('<hr style="border-color:rgba(0,212,170,0.2);">', unsafe_allow_html=True)
    st.sidebar.markdown("### 🔍 Umumiy filtrlar")

    if 'Yil' in df.columns:
        years = sorted(df['Yil'].dropna().unique())
        sel = st.sidebar.multiselect("📅 Yil", years, default=years)
        df = df[df['Yil'].isin(sel)] if sel else df

    if 'Oy' in df.columns:
        months = sorted(df['Oy'].dropna().unique())
        sel = st.sidebar.multiselect("🗓 Oy", months, default=months,
                                     format_func=lambda x: OY_NOMI.get(int(x), str(x)))
        df = df[df['Oy'].isin(sel)] if sel else df

    if 'Toifa' in df.columns:
        toifalar = df['Toifa'].dropna().unique().tolist()
        sel = st.sidebar.multiselect("📦 Toifa", toifalar, default=toifalar)
        df = df[df['Toifa'].isin(sel)] if sel else df

    if 'HAVF_YOLAGI' in df.columns:
        # Show only Sariq/Qizil/Yashil (yolak_yoq already merged into Sariq)
        lanes = sorted([l for l in df['HAVF_YOLAGI'].dropna().unique() if l != 'yolak_yoq'])
        sel = st.sidebar.multiselect("🚦 Xavf yo'lagi", lanes, default=lanes)
        df = df[df['HAVF_YOLAGI'].isin(sel)] if sel else df

    if 'CHEGARA_POST' in df.columns and post_coords is not None:
        pc = get_post_code_col(post_coords)
        pn = get_post_name_col(post_coords)
        pm = dict(zip(post_coords[pc].astype(str), post_coords[pn]))
        all_posts = df['CHEGARA_POST'].dropna().unique()
        plabels = {str(p): pm.get(str(p), f"Post {p}") for p in all_posts}
        sel = st.sidebar.multiselect("🏛 Chegara post",
            options=list(plabels.keys()), format_func=lambda x: plabels.get(x, x),
            default=list(plabels.keys()))
        if sel:
            df = df[df['CHEGARA_POST'].astype(str).isin(sel)]

    if countries_uz is not None:
        cc2 = get_continent_col(countries_uz)
        if cc2:
            conts = sorted(countries_uz[cc2].dropna().unique().tolist())
            sel = st.sidebar.multiselect("🌍 Qit'a", conts, default=conts)
            if sel:
                ccode_col = get_country_code_col(countries_uz)
                valid = pd.to_numeric(
                    countries_uz[countries_uz[cc2].isin(sel)][ccode_col], errors='coerce'
                ).dropna().tolist()
                df = df[pd.to_numeric(df['YUBORUVCHI_DAVLAT'], errors='coerce').isin(valid)]
    return df

# ══════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════
def render_kpis(df):
    brutto  = df['Brutto'].sum()  if 'Brutto'           in df.columns else 0
    netto   = df['Netto'].sum()   if 'Netto'            in df.columns else 0
    corps   = df['QQ_NAME'].nunique()          if 'QQ_NAME'         in df.columns else 0
    cntries = df['YUBORUVCHI_DAVLAT'].nunique() if 'YUBORUVCHI_DAVLAT' in df.columns else 0
    posts   = df['CHEGARA_POST'].nunique()     if 'CHEGARA_POST'    in df.columns else 0
    hazard  = int(df['Havfli_yuk'].sum())      if 'Havfli_yuk'      in df.columns else 0

    cols = st.columns(7)
    for i, (icon, lbl, val) in enumerate([
        ("📊","Deklaratsiya", fmt(len(df))),
        ("⚖️","Brutto (t)",   fmt(brutto/1000,1)),
        ("📦","Netto (t)",    fmt(netto/1000,1)),
        ("🏢","Korxonalar",   fmt(corps)),
        ("🌍","Davlatlar",    fmt(cntries)),
        ("🏛","Postlar",      fmt(posts)),

    ]):
        with cols[i]:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 1 — POSTLAR XARITASI (interaktiv)
# ══════════════════════════════════════════════════════════════
def render_post_map(df, post_coords, countries_uz):
    if post_coords is None:
        st.warning("⚠️ Post_coordinates.xlsx topilmadi.")
        return

    st.markdown(
        '<div class="section-header">🗺 O\'zbekiston Chegara Postlari — Interaktiv Bubble Map</div>',
        unsafe_allow_html=True)

    # ── Ichki filtrlar ──────────────────────────────────────────
    with st.expander("🎛 Xarita filtrlari", expanded=True):
        fc1, fc2, fc3 = st.columns(3)

        # Yil filter
        with fc1:
            dff = df.copy()
            if 'Yil' in dff.columns:
                yopts = sorted(dff['Yil'].dropna().unique())
                sely = st.multiselect("📅 Yil", yopts, default=yopts, key="pm_yil")
                if sely: dff = dff[dff['Yil'].isin(sely)]

        # Toifa filter
        with fc2:
            if 'Toifa' in dff.columns:
                topts = sorted(dff['Toifa'].dropna().unique().tolist())
                selt = st.multiselect("📦 Toifa", topts, default=topts, key="pm_toifa")
                if selt: dff = dff[dff['Toifa'].isin(selt)]

        # Davlat filter
        with fc3:
            if 'YUBORUVCHI_DAVLAT' in dff.columns and countries_uz is not None:
                cc  = get_country_code_col(countries_uz)
                cn  = get_country_name_col(countries_uz)
                ref = countries_uz[[cc, cn]].copy()
                ref[cc] = pd.to_numeric(ref[cc], errors='coerce')
                tmp = dff.copy()
                tmp['_code'] = pd.to_numeric(tmp['YUBORUVCHI_DAVLAT'], errors='coerce')
                tmp = tmp.merge(ref, left_on='_code', right_on=cc, how='left')
                tmp['DavlatNom'] = tmp[cn].fillna('Davlat ' + tmp['_code'].astype(str))
                all_davlatlar = sorted(tmp['DavlatNom'].dropna().unique().tolist())
                seld = st.multiselect("🌍 Yuboruvchi davlat",
                    all_davlatlar, default=all_davlatlar, key="pm_davlat")
                if seld:
                    vcodes = tmp[tmp['DavlatNom'].isin(seld)]['_code'].dropna().unique()
                    dff = dff[pd.to_numeric(dff['YUBORUVCHI_DAVLAT'], errors='coerce').isin(vcodes)]

    # ── Aggregate ──────────────────────────────────────────────
    pc  = get_post_code_col(post_coords)
    pn  = get_post_name_col(post_coords)
    lat, lon = get_lat_lon(post_coords)

    if lat is None or lon is None:
        st.error("Post_coordinates faylida Latitude/Longitude topilmadi!")
        return

    agg = dff.groupby('CHEGARA_POST').agg(
        Brutto_sum=('Brutto','sum'), Netto_sum=('Netto','sum'),
        Count=('ID','count'), Korxona=('QQ_NAME','nunique')
    ).reset_index()
    agg['CHEGARA_POST'] = agg['CHEGARA_POST'].astype(str)

    pcc = post_coords.copy()
    pcc[pc] = pcc[pc].astype(str)
    merged = agg.merge(pcc, left_on='CHEGARA_POST', right_on=pc, how='left')
    merged = merged.dropna(subset=[lat, lon])

    if merged.empty:
        st.warning("Post koordinatalari bilan bog'lanish amalga oshmadi.")
        return

    mx = merged['Brutto_sum'].max()
    merged['bsize'] = ((merged['Brutto_sum'] / mx * 55).clip(lower=8)).fillna(8)
    name_col = pn if pn in merged.columns else 'CHEGARA_POST'

    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat=merged[lat], lon=merged[lon],
        mode='markers+text',
        marker=dict(
            size=merged['bsize'],
            color=merged['Brutto_sum'],
            colorscale=[[0,'#064e3b'],[0.3,'#059669'],[0.6,'#f59e0b'],[1,'#ef4444']],
            colorbar=dict(
                title=dict(text="Brutto (kg)", font=dict(color='#e0e0e0')),
                tickfont=dict(color='#e0e0e0')
            ),
            opacity=0.88, sizemode='diameter',
        ),
        text=merged[name_col],
        textposition='top center',
        textfont=dict(size=11, color='#e0e0e0'),
        customdata=np.column_stack([
            merged[name_col],
            merged['Brutto_sum'].apply(fmt),
            merged['Netto_sum'].apply(fmt),
            merged['Count'].apply(fmt),
            merged['Korxona'].apply(fmt),
        ]),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "─────────────────<br>"
            "⚖️ Brutto: <b>%{customdata[1]} kg</b><br>"
            "📦 Netto:  <b>%{customdata[2]} kg</b><br>"
            "📊 Deklaratsiya: <b>%{customdata[3]}</b><br>"
            "🏢 Korxonalar: <b>%{customdata[4]}</b><br>"
            "<extra></extra>"
        ),
    ))
    fig.update_layout(
        mapbox=dict(style='carto-darkmatter', center=dict(lat=41.0, lon=64.5), zoom=5.2),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0),
        height=560, font=dict(color='#e0e0e0'),
    )
    st.plotly_chart(fig, use_container_width=True, key="post_map_main")

    # Mini stats
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Jami postlar",      f"{len(merged):,}")
    mc2.metric("Umumiy Brutto",     f"{merged['Brutto_sum'].sum()/1e6:.1f} ming t")
    mc3.metric("Jami deklaratsiya", f"{merged['Count'].sum():,}")

# ══════════════════════════════════════════════════════════════
# TAB 2 — DAVLATLAR XARITASI (bubble, interaktiv)
# ══════════════════════════════════════════════════════════════
def render_world_map(df, countries_uz, countries_en):
    if 'YUBORUVCHI_DAVLAT' not in df.columns:
        st.warning("YUBORUVCHI_DAVLAT ustuni mavjud emas.")
        return

    st.markdown(
        '<div class="section-header">🌍 Yuboruvchi Davlatlar — Interaktiv Bubble Map</div>',
        unsafe_allow_html=True)

    country_ref = countries_uz if countries_uz is not None else countries_en
    if country_ref is None:
        st.warning("Davlatlar tasniflagichi fayli topilmadi.")
        return

    cc       = get_country_code_col(country_ref)
    cn       = get_country_name_col(country_ref)
    lat, lon = get_lat_lon(country_ref)
    cont_col = get_continent_col(country_ref)

    ref = country_ref.copy()
    ref[cc] = pd.to_numeric(ref[cc], errors='coerce')
    extra_cols = [c for c in [cont_col, lat, lon] if c and c in ref.columns]
    ref_sub = ref[[cc, cn] + extra_cols].drop_duplicates(cc)

    # Merge reference info onto df
    dfw = df.copy()
    dfw['_code'] = pd.to_numeric(dfw['YUBORUVCHI_DAVLAT'], errors='coerce')
    dfw = dfw.merge(ref_sub, left_on='_code', right_on=cc, how='left')
    dfw['DavlatNom'] = dfw[cn].fillna('Davlat ' + dfw['_code'].astype(str))

    # ── Ichki filtrlar ──────────────────────────────────────────
    with st.expander("🎛 Xarita filtrlari", expanded=True):
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            if 'Yil' in dfw.columns:
                yopts = sorted(dfw['Yil'].dropna().unique())
                sely = st.multiselect("📅 Yil", yopts, default=yopts, key="wm_yil")
                if sely: dfw = dfw[dfw['Yil'].isin(sely)]
        with r1c2:
            if 'Toifa' in dfw.columns:
                topts = sorted(dfw['Toifa'].dropna().unique().tolist())
                selt = st.multiselect("📦 Toifa", topts, default=topts, key="wm_toifa")
                if selt: dfw = dfw[dfw['Toifa'].isin(selt)]
        with r1c3:
            if cont_col and cont_col in dfw.columns:
                copts = sorted(dfw[cont_col].dropna().unique().tolist())
                selc = st.multiselect("🌐 Qit'a", copts, default=copts, key="wm_cont")
                if selc: dfw = dfw[dfw[cont_col].isin(selc)]

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            if 'Oy' in dfw.columns:
                mopts = sorted(dfw['Oy'].dropna().unique())
                selm = st.multiselect("🗓 Oy", mopts, default=mopts, key="wm_oy",
                                      format_func=lambda x: OY_NOMI.get(int(x), str(x)))
                if selm: dfw = dfw[dfw['Oy'].isin(selm)]
        with r2c2:
            if 'Hafta_raqam' in dfw.columns:
                wopts = sorted(dfw['Hafta_raqam'].dropna().unique())
                selw = st.multiselect("📆 Hafta", wopts, default=wopts, key="wm_hafta")
                if selw: dfw = dfw[dfw['Hafta_raqam'].isin(selw)]
        with r2c3:
            if 'CHECKINTIME' in dfw.columns:
                mn = dfw['CHECKINTIME'].min()
                mx = dfw['CHECKINTIME'].max()
                if pd.notna(mn) and pd.notna(mx):
                    dr = st.date_input("📅 Sana oralig'i",
                        value=(mn.date(), mx.date()),
                        min_value=mn.date(), max_value=mx.date(), key="wm_date")
                    if isinstance(dr, (list, tuple)) and len(dr) == 2:
                        dfw = dfw[(dfw['CHECKINTIME'].dt.date >= dr[0]) &
                                  (dfw['CHECKINTIME'].dt.date <= dr[1])]

    # ── Aggregate ──────────────────────────────────────────────
    agg = dfw.groupby('DavlatNom').agg(
        Brutto=('Brutto','sum'), Count=('ID','count'), _code=('_code','first')
    ).reset_index()

    # Get lat/lon per country
    if lat and lon and lat in dfw.columns and lon in dfw.columns:
        coords = dfw[['DavlatNom', lat, lon]].drop_duplicates('DavlatNom')
        agg = agg.merge(coords, on='DavlatNom', how='left')
        lat_c, lon_c = lat, lon
    else:
        lat_c = lon_c = None

    # ── Bubble map ──────────────────────────────────────────────
    if lat_c and lon_c and lat_c in agg.columns and lon_c in agg.columns:
        agg_v = agg.dropna(subset=[lat_c, lon_c]).copy()
        if len(agg_v) > 0:
            mx_b = agg_v['Brutto'].max()
            agg_v['bsize'] = ((agg_v['Brutto'] / mx_b * 50).clip(lower=5)).fillna(5)

            fig = go.Figure()
            fig.add_trace(go.Scattermapbox(
                lat=agg_v[lat_c], lon=agg_v[lon_c],
                mode='markers+text',
                marker=dict(
                    size=agg_v['bsize'],
                    color=agg_v['Brutto'],
                    colorscale=[[0,'#064e3b'],[0.3,'#059669'],[0.6,'#3b82f6'],[1,'#00d4aa']],
                    colorbar=dict(
                        title=dict(text="Brutto (kg)", font=dict(color='#e0e0e0')),
                        tickfont=dict(color='#e0e0e0')
                    ),
                    opacity=0.85, sizemode='diameter',
                ),
                text=agg_v['DavlatNom'],
                textposition='top center',
                textfont=dict(size=10, color='#e0e0e0'),
                customdata=np.column_stack([
                    agg_v['DavlatNom'],
                    agg_v['Brutto'].apply(fmt),
                    agg_v['Count'].apply(fmt),
                ]),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "⚖️ Brutto: <b>%{customdata[1]} kg</b><br>"
                    "📊 Deklaratsiya: <b>%{customdata[2]}</b><br>"
                    "<extra></extra>"
                ),
            ))
            fig.update_layout(
                mapbox=dict(style='carto-darkmatter', center=dict(lat=30, lon=60), zoom=1.8),
                paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0),
                height=540, font=dict(color='#e0e0e0'),
            )
            st.plotly_chart(fig, use_container_width=True, key="world_bubble_map")
        else:
            st.warning("Tanlangan filtrlar bo'yicha davlat koordinatalari topilmadi.")
    else:
        # Fallback: ISO-3 choropleth
        def to_iso3(code):
            m = {156:'CHN',643:'RUS',860:'UZB',398:'KAZ',762:'TJK',795:'TKM',
                 417:'KGZ',804:'UKR',276:'DEU',792:'TUR',364:'IRN',356:'IND',
                 586:'PAK',410:'KOR',392:'JPN',840:'USA',826:'GBR',250:'FRA',
                 380:'ITA',724:'ESP',616:'POL',528:'NLD',56:'BEL',40:'AUT',
                 203:'CZE',348:'HUN',642:'ROU',100:'BGR',112:'BLR',31:'AZE',
                 268:'GEO',51:'ARM',496:'MNG',784:'ARE',682:'SAU',818:'EGY',
                 788:'TUN',504:'MAR',710:'ZAF',76:'BRA',36:'AUS',124:'CAN',
                 484:'MEX',756:'CHE',300:'GRC',620:'PRT',578:'NOR',752:'SWE'}
            try: return m.get(int(code))
            except Exception: return None
        agg['iso3'] = agg['_code'].apply(to_iso3)
        av = agg.dropna(subset=['iso3'])
        if len(av):
            fig = px.choropleth(av, locations='iso3', locationmode='ISO-3',
                color='Brutto', color_continuous_scale=CYAN_SCALE,
                hover_name='DavlatNom',
                labels={'Brutto':'Brutto (kg)','Count':'Deklaratsiya'})
            fig.update_geos(bgcolor='rgba(0,0,0,0)', landcolor='#1a2035',
                            oceancolor='#0a0e1a', showcoastlines=True,
                            coastlinecolor='#2d3748', countrycolor='#2d3748')
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0),
                height=540, font=dict(color='#e0e0e0'),
                coloraxis_colorbar=dict(
                    title=dict(text="Brutto (kg)", font=dict(color='#e0e0e0')),
                    tickfont=dict(color='#e0e0e0')))
            st.plotly_chart(fig, use_container_width=True, key="world_choropleth")

    # Top-20 davlat barchart
    st.markdown('<div class="section-header">📊 Top-20 davlat Brutto bo\'yicha</div>',
                unsafe_allow_html=True)
    top20 = agg.nlargest(20, 'Brutto')
    f2 = px.bar(top20, x='Brutto', y='DavlatNom', orientation='h',
                color='Brutto', color_continuous_scale=CYAN_SCALE,
                text=top20['Brutto'].apply(fmt),
                labels={'Brutto':'Brutto (kg)','DavlatNom':''})
    f2.update_traces(textposition='outside', textfont=dict(size=10,color='#e0e0e0'))
    f2 = make_dark(f2, height=520)
    f2.update_layout(yaxis=dict(autorange='reversed'), coloraxis_showscale=False)
    st.plotly_chart(f2, use_container_width=True, key="world_top20")

# ══════════════════════════════════════════════════════════════
# TAB 3 — VAQT TAHLILI
# ══════════════════════════════════════════════════════════════
def render_time_analysis(df, post_coords, countries_uz=None):
    post_name_map = {}
    if post_coords is not None:
        pc = get_post_code_col(post_coords)
        pn = get_post_name_col(post_coords)
        post_name_map = dict(zip(post_coords[pc].astype(str), post_coords[pn]))

    time_mode = st.radio("Vaqt davri",
        ["📅 Kunlik","📆 Haftalik","🗓 Oylik","📅 Yillik"],
        horizontal=True, label_visibility="collapsed", key="time_mode_radio")

    if 'CHECKINTIME' not in df.columns:
        st.warning("CHECKINTIME ustuni mavjud emas.")
        return

    dfc = df.dropna(subset=['CHECKINTIME']).copy()
    if   "Kunlik"   in time_mode:
        dfc['period'] = dfc['CHECKINTIME'].dt.date.astype(str); pl = "Sana"
    elif "Haftalik" in time_mode:
        dfc['period'] = (dfc['CHECKINTIME'].dt.year.astype(str) + '-H' +
                         dfc['CHECKINTIME'].dt.isocalendar().week.astype(int).astype(str).str.zfill(2))
        pl = "Hafta"
    elif "Oylik" in time_mode:
        dfc['period'] = dfc['CHECKINTIME'].dt.to_period('M').astype(str); pl = "Oy"
    else:
        dfc['period'] = dfc['CHECKINTIME'].dt.year.astype(str); pl = "Yil"

    trend = dfc.groupby('period').agg(
        Brutto=('Brutto','sum'), Netto=('Netto','sum'), Count=('ID','count')
    ).reset_index().sort_values('period')

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="section-header">📈 {pl} bo\'yicha dinamika</div>', unsafe_allow_html=True)
        ft = go.Figure()
        ft.add_trace(go.Bar(x=trend['period'], y=trend['Brutto'], name='Brutto',
            marker_color='#00d4aa', opacity=0.85, yaxis='y1',
            hovertemplate="%{x}<br>Brutto: %{y:,.0f} kg<extra></extra>"))
        ft.add_trace(go.Scatter(x=trend['period'], y=trend['Count'], name='Deklaratsiya',
            yaxis='y2', line=dict(color='#f59e0b',width=2),
            mode='lines+markers', marker=dict(size=5),
            hovertemplate="%{x}<br>Soni: %{y:,.0f}<extra></extra>"))
        ft.update_layout(
            yaxis=dict(title='Brutto (kg)', gridcolor='rgba(255,255,255,0.05)'),
            yaxis2=dict(title='Deklaratsiya', overlaying='y', side='right', showgrid=False),
            legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center'))
        ft = make_dark(ft, height=380)
        st.plotly_chart(ft, use_container_width=True, key="ta_trend")

    with c2:
        st.markdown(f'<div class="section-header">🏛 Top-10 post: {pl}</div>', unsafe_allow_html=True)
        bp = dfc.groupby(['period','CHEGARA_POST'])['Brutto'].sum().reset_index()
        bp['Post'] = bp['CHEGARA_POST'].astype(str).map(lambda x: post_name_map.get(x, f"Post {x}"))
        tops = bp.groupby('Post')['Brutto'].sum().nlargest(10).index
        fl = px.line(bp[bp['Post'].isin(tops)], x='period', y='Brutto', color='Post',
            color_discrete_sequence=MAIN_COLORS,
            labels={'Brutto':'Brutto (kg)','period':pl,'Post':'Post'})
        fl.update_traces(line=dict(width=2), mode='lines+markers', marker=dict(size=4))
        fl = make_dark(fl, height=380)
        fl.update_layout(legend=dict(font=dict(size=10)))
        st.plotly_chart(fl, use_container_width=True, key="ta_post_line")

    # Heatmap
    st.markdown('<div class="section-header">🗺 Post × Vaqt Heatmap</div>', unsafe_allow_html=True)
    hd = dfc.groupby(['CHEGARA_POST','period'])['Brutto'].sum().reset_index()
    hd['Post'] = hd['CHEGARA_POST'].astype(str).map(lambda x: post_name_map.get(x, f"Post {x}"))
    pivot = hd.pivot_table(index='Post', columns='period', values='Brutto', fill_value=0)
    pivot = pivot.loc[pivot.sum(axis=1).nlargest(15).index]
    fh = go.Figure(data=go.Heatmap(
        z=pivot.values, x=pivot.columns.astype(str), y=pivot.index,
        colorscale=[[0,'#0a0e1a'],[0.2,'#064e3b'],[0.5,'#059669'],[0.8,'#f59e0b'],[1,'#ef4444']],
        hovertemplate="Post: %{y}<br>Davr: %{x}<br>Brutto: %{z:,.0f} kg<extra></extra>",
        colorbar=dict(title=dict(text="Brutto (kg)", font=dict(color='#e0e0e0')),
                      tickfont=dict(color='#e0e0e0'))))
    fh = make_dark(fh, height=460)
    st.plotly_chart(fh, use_container_width=True, key="ta_heatmap")

# ══════════════════════════════════════════════════════════════
# TAB 4 — ANALITIKA
# ══════════════════════════════════════════════════════════════
def render_analytics(df, post_coords, countries_uz, countries_en):
    post_name_map = {}
    if post_coords is not None:
        pc = get_post_code_col(post_coords)
        pn = get_post_name_col(post_coords)
        post_name_map = dict(zip(post_coords[pc].astype(str), post_coords[pn]))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">🌍 Top-15 davlat (Brutto)</div>', unsafe_allow_html=True)
        by_c = df.groupby('YUBORUVCHI_DAVLAT').agg(
            Brutto=('Brutto','sum'), Count=('ID','count')).reset_index()
        by_c = merge_country_names(by_c, countries_uz)
        top15 = by_c.nlargest(15,'Brutto')
        fa = px.bar(top15, x='Brutto', y='Davlat', orientation='h',
                    color='Brutto', color_continuous_scale=CYAN_SCALE,
                    labels={'Brutto':'Brutto (kg)','Davlat':''},
                    text=top15['Brutto'].apply(fmt))
        fa.update_traces(textposition='outside', textfont=dict(size=10,color='#e0e0e0'))
        fa = make_dark(fa, height=480)
        fa.update_layout(yaxis=dict(autorange='reversed'), coloraxis_showscale=False)
        st.plotly_chart(fa, use_container_width=True, key="an_country")

    with c2:
        st.markdown('<div class="section-header">🏛 Top-15 post (Brutto)</div>', unsafe_allow_html=True)
        by_p = df.groupby('CHEGARA_POST').agg(
            Brutto=('Brutto','sum'), Count=('ID','count')).reset_index()
        by_p['Post'] = by_p['CHEGARA_POST'].astype(str).map(
            lambda x: post_name_map.get(x, f"Post {x}"))
        top15p = by_p.nlargest(15,'Brutto')
        fb = px.bar(top15p, x='Brutto', y='Post', orientation='h',
                    color='Brutto',
                    color_continuous_scale=[[0,'#1e3a5f'],[0.5,'#3b82f6'],[1,'#93c5fd']],
                    labels={'Brutto':'Brutto (kg)','Post':''},
                    text=top15p['Brutto'].apply(fmt))
        fb.update_traces(textposition='outside', textfont=dict(size=10,color='#e0e0e0'))
        fb = make_dark(fb, height=480)
        fb.update_layout(yaxis=dict(autorange='reversed'), coloraxis_showscale=False)
        st.plotly_chart(fb, use_container_width=True, key="an_post")

    # Risk pie (yolak_yoq → Sariq)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-header">🚦 Xavf yo\'lagi taqsimoti</div>', unsafe_allow_html=True)
        if 'HAVF_YOLAGI' in df.columns:
            # normalize already done globally, but apply here too for safety
            df_risk = normalize_risk(df)
            risk_d = df_risk.groupby('HAVF_YOLAGI').agg(
                Count=('ID','count'), Brutto=('Brutto','sum')).reset_index()
            colors = [RISK_COLORS.get(r,'#6b7280') for r in risk_d['HAVF_YOLAGI']]
            fc = go.Figure(data=[go.Pie(
                labels=risk_d['HAVF_YOLAGI'], values=risk_d['Count'],
                hole=0.55,
                marker=dict(colors=colors, line=dict(color='#0a0e1a',width=2)),
                textinfo='label+percent', textfont=dict(color='#e0e0e0',size=13),
                hovertemplate="%{label}<br>Soni: %{value:,}<br>%{percent}<extra></extra>",
            )])
            fc.update_layout(annotations=[dict(
                text=fmt(risk_d['Count'].sum()), x=0.5, y=0.5,
                font_size=22, font_color='#00d4aa', font_family='JetBrains Mono',
                showarrow=False)])
            fc = make_dark(fc, height=380)
            st.plotly_chart(fc, use_container_width=True, key="an_risk")

    with c4:
        st.markdown('<div class="section-header">📦 Toifa taqsimoti</div>', unsafe_allow_html=True)
        if 'Toifa' in df.columns:
            td = df.groupby('Toifa').agg(Count=('ID','count'), Brutto=('Brutto','sum')).reset_index()
            colors_t = [TOIFA_COLORS.get(t,'#6b7280') for t in td['Toifa']]
            fd = go.Figure(data=[go.Pie(
                labels=td['Toifa'], values=td['Brutto'], hole=0.55,
                marker=dict(colors=colors_t, line=dict(color='#0a0e1a',width=2)),
                textinfo='label+percent', textfont=dict(color='#e0e0e0',size=13),
                hovertemplate="%{label}<br>Brutto: %{value:,.0f} kg<br>%{percent}<extra></extra>",
            )])
            fd.update_layout(annotations=[dict(
                text="Brutto", x=0.5, y=0.5, font_size=16, font_color='#3b82f6',
                font_family='Manrope', showarrow=False)])
            fd = make_dark(fd, height=380)
            st.plotly_chart(fd, use_container_width=True, key="an_toifa")

    # Qit'alar
    if countries_uz is not None:
        cont_c = get_continent_col(countries_uz)
        if cont_c and 'YUBORUVCHI_DAVLAT' in df.columns:
            st.markdown('<div class="section-header">🌐 Qit\'alar bo\'yicha tahlil</div>',
                        unsafe_allow_html=True)
            ccode = get_country_code_col(countries_uz)
            ref2  = countries_uz[[ccode, cont_c]].copy()
            ref2[ccode] = pd.to_numeric(ref2[ccode], errors='coerce')
            dfc2 = df.copy()
            dfc2['_code'] = pd.to_numeric(dfc2['YUBORUVCHI_DAVLAT'], errors='coerce')
            m2 = dfc2.merge(ref2, left_on='_code', right_on=ccode, how='left')
            ca = m2.groupby(cont_c).agg(Brutto=('Brutto','sum'), Count=('ID','count')).reset_index()
            ca = ca.dropna().sort_values('Brutto', ascending=False)
            q1, q2 = st.columns(2)
            with q1:
                fe = px.bar(ca, x=cont_c, y='Brutto', color=cont_c,
                    color_discrete_sequence=MAIN_COLORS, text=ca['Brutto'].apply(fmt),
                    labels={'Brutto':'Brutto (kg)', cont_c:"Qit'a"},
                    title="Qit'alar bo'yicha brutto")
                fe.update_traces(textposition='outside', textfont=dict(size=10,color='#e0e0e0'))
                fe = make_dark(fe, height=350)
                fe.update_layout(showlegend=False)
                st.plotly_chart(fe, use_container_width=True, key="an_cont_bar")
            with q2:
                ff = px.treemap(ca, path=[cont_c], values='Brutto', color='Brutto',
                    color_continuous_scale=CYAN_SCALE, title="Qit'alar treemap")
                ff = make_dark(ff, height=350)
                ff.update_layout(coloraxis_showscale=False)
                st.plotly_chart(ff, use_container_width=True, key="an_cont_tree")

    # Og'irlik farqi


# ══════════════════════════════════════════════════════════════
# TAB 5 — MA'LUMOTLAR
# ══════════════════════════════════════════════════════════════
def render_data_table(df, post_coords, countries_uz):
    st.markdown('<div class="section-header">📋 Ma\'lumotlar jadvali</div>', unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    with tc1: search = st.text_input("🔍 Qidirish", "")
    with tc2: psize  = st.selectbox("Qatorlar soni", [25,50,100,250], index=0)
    with tc3:
        sopts = [c for c in ['CHECKINTIME','Brutto','Netto','QQ_NAME'] if c in df.columns]
        scol  = st.selectbox("Saralash", sopts)
    dfd = df.copy()
    if search:
        mask = dfd.astype(str).apply(lambda x: x.str.contains(search,case=False,na=False)).any(axis=1)
        dfd = dfd[mask]
    dfd = dfd.sort_values(scol, ascending=False).head(psize)
    st.dataframe(dfd, use_container_width=True, height=430, hide_index=True)
    st.caption(f"Ko'rsatilmoqda: {len(dfd):,} / {len(df):,} qator")

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    if not st.session_state.authenticated:
        login_page()
        return

    st.sidebar.markdown(f"""
    <div style="text-align:center; padding:16px 0;">
        <div style="font-size:36px;">🛃</div>
        <div style="font-family:'Manrope',sans-serif; font-weight:700; font-size:16px;
            color:#00d4aa; margin-top:4px;">E-Tranzit Monitor</div>
        <div style="font-size:12px; color:#94a3b8;">
            {'👑 Admin rejim' if st.session_state.role=='admin' else '👤 User rejim'}
        </div>
    </div>""", unsafe_allow_html=True)

    if st.sidebar.button("🚪 Chiqish", use_container_width=True):
        for k in ['authenticated','role','data','data_loaded']:
            st.session_state[k] = False if k != 'role' else None
        st.rerun()

    os.makedirs(DATA_DIR, exist_ok=True)
    post_coords, countries_uz, countries_en = load_reference_data()

    if st.session_state.role == 'admin':
        admin_upload_section()
    else:
        if not st.session_state.data_loaded:
            user_load_data()

    if not st.session_state.data_loaded or st.session_state.data is None:
        st.markdown("""<div style="text-align:center; margin-top:100px;">
            <div style="font-size:72px;">📂</div>
            <h2 style="color:#94a3b8;">Ma'lumot yuklanmagan</h2>
            <p style="color:#475569;">Admin paneliga kirib parquet fayl yuklang.</p>
        </div>""", unsafe_allow_html=True)
        return

    # Normalize risk column globally
    df_raw = normalize_risk(st.session_state.data.copy())

    # Global sidebar filters
    df_filtered = sidebar_global_filters(df_raw, post_coords, countries_uz)

    # Header
    st.markdown("""<div class="main-header">
        <h1>📊 E-Tranzit Monitoring Dashboard</h1>
        <p>O'zbekiston Respublikasi Bojxona Qo'mitasi — Elektron Tranzit Monitoring Tizimi v2.1</p>
    </div>""", unsafe_allow_html=True)

    render_kpis(df_filtered)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺 Postlar xaritasi",
        "🌍 Davlatlar xaritasi",
        "📈 Vaqt tahlili",
        "📊 Analitika",
        "📋 Ma'lumotlar",
    ])
    with tab1: render_post_map(df_filtered, post_coords, countries_uz)
    with tab2: render_world_map(df_filtered, countries_uz, countries_en)
    with tab3: render_time_analysis(df_filtered, post_coords, countries_uz)
    with tab4: render_analytics(df_filtered, post_coords, countries_uz, countries_en)
    with tab5: render_data_table(df_filtered, post_coords, countries_uz)

    st.markdown("""<div style="text-align:center; margin-top:40px; padding:16px;
        border-top:1px solid rgba(255,255,255,0.05);">
        <p style="color:#475569; font-size:12px;">
            © 2025-2026 O'zbekiston Respublikasi Bojxona Qo'mitasi | E-Tranzit v2.1
        </p></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
