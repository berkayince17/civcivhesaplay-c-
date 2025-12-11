import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
import uuid

# -----------------------------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI & TASARIM (CSS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Berkay OS",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cyberpunk / Neon Tema CSS Enjeksiyonu
def local_css():
    st.markdown("""
    <style>
        /* Ana Arka Plan */
        .stApp {
            background: linear-gradient(135deg, #130428 0%, #250b48 100%);
            color: #e0e0e0;
        }
        
        /* Sidebar (Kenar Çubuğu) */
        [data-testid="stSidebar"] {
            background-color: #0f021f;
            border-right: 1px solid #00f2ff;
        }
        
        /* Metrik Kartları (KPI) */
        div[data-testid="stMetricValue"] {
            color: #00f2ff !important;
            font-family: 'Courier New', monospace;
            text-shadow: 0 0 10px #00f2ff;
        }
        div[data-testid="stMetricLabel"] {
            color: #ff00ff !important;
        }
        
        /* Konteynerlar / Kartlar (Glassmorphism) */
        .stDataFrame, .stPlotlyChart {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
        }

        /* Butonlar */
        .stButton>button {
            background: transparent;
            border: 1px solid #00ff9d;
            color: #00ff9d;
            border-radius: 5px;
            width: 100%;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background: #00ff9d;
            color: #000;
            box-shadow: 0 0 15px #00ff9d;
        }

        /* Tablolar (Data Editor) */
        [data-testid="stDataFrame"] {
            border: 1px solid #ff00ff;
        }
        
        /* Başlıklar */
        h1, h2, h3 {
            color: #ffffff;
            font-family: 'Verdana', sans-serif;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        h1 {
            text-shadow: 2px 2px 0px #ff00ff;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# -----------------------------------------------------------------------------
# 2. VERİ YÖNETİMİ (CSV CRUD İŞLEMLERİ)
# -----------------------------------------------------------------------------
# NOT: Streamlit Cloud'da yerel dosyalar geçicidir (ephemeral). 
# Uygulama yeniden başlatıldığında veriler sıfırlanabilir.
# Kalıcı depolama için Google Sheets veya SQL veritabanı önerilir.

FILES = {
    "tasks": "gorevler.csv",
    "staff": "personel.csv"
}

def load_data():
    # Görevler Dosyası Kontrolü
    if not os.path.exists(FILES["tasks"]):
        df_tasks = pd.DataFrame(columns=["ID", "GorevAdi", "Kisi", "Baslangic", "Bitis", "Durum", "Yuzde"])
        # İlk oluşturmada boş kalmasın diye örnek veri atalım
        try:
             df_tasks.to_csv(FILES["tasks"], index=False)
        except:
             pass # Yazma izni hatası olursa geç
    else:
        df_tasks = pd.read_csv(FILES["tasks"])
        if not df_tasks.empty:
            df_tasks['Baslangic'] = pd.to_datetime(df_tasks['Baslangic'])
            df_tasks['Bitis'] = pd.to_datetime(df_tasks['Bitis'])

    # Personel Dosyası Kontrolü
    if not os.path.exists(FILES["staff"]):
        df_staff = pd.DataFrame(columns=["Isim", "Rol", "Yetenekler"])
        # Örnek veriler
        df_staff.loc[0] = ["Ahmet Yılmaz", "Geliştirici", "Python"]
        df_staff.loc[1] = ["Zeynep Kaya", "Tasarımcı", "UI/UX"]
        try:
            df_staff.to_csv(FILES["staff"], index=False)
        except:
            pass
    else:
        df_staff = pd.read_csv(FILES["staff"])
        
    return df_tasks, df_staff

def save_data(df, file_key):
    filename = FILES[file_key]
    try:
        df.to_csv(filename, index=False)
    except Exception as e:
        st.error(f"Kayıt hatası: {e}")

# Verileri Yükle
df_tasks, df_staff = load_data()

# -----------------------------------------------------------------------------
# 3. KENAR ÇUBUĞU MENÜSÜ
# -----------------------------------------------------------------------------
st.sidebar.title("BERKAY OS")
st.sidebar.caption("v1.2 Cloud Edition")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigasyon",
    ["📊 Dashboard", "📝 Görev Yönetimi", "👥 Personel", "⏳ Gantt Şeması", "🏭 Üretim Planlayıcı"]
)
st.sidebar.markdown("---")

# -----------------------------------------------------------------------------
# 4. MODÜLLER
# -----------------------------------------------------------------------------

# --- A. DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("Sistem Genel Bakış")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(df_tasks)
    completed_tasks = len(df_tasks[df_tasks['Durum'] == 'Tamamlandı']) if not df_tasks.empty else 0
    active_staff = len(df_staff)
    pending_tasks = total_tasks - completed_tasks
    
    success_rate = int((completed_tasks/total_tasks)*100) if total_tasks > 0 else 0
    
    col1.metric("Toplam Görev", total_tasks)
    col2.metric("Tamamlanan", f"%{success_rate}")
    col3.metric("Personel", active_staff)
    col4.metric("Bekleyen", pending_tasks)
    
    st.markdown("---")
    
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.subheader("İş Yükü Dağılımı")
        if not df_tasks.empty:
            task_counts = df_tasks['Kisi'].value_counts().reset_index()
            task_counts.columns = ['Kisi', 'GorevSayisi']
            
            fig_bar = px.bar(task_counts, x='Kisi', y='GorevSayisi', 
                             color='GorevSayisi',
                             color_continuous_scale=['#00f2ff', '#00ff9d'])
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='#e0e0e0', xaxis_title="", yaxis_title="Görev Sayısı"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Henüz görev verisi yok.")

    with g_col2:
        st.subheader("Durum Analizi")
        if not df_tasks.empty:
            status_counts = df_tasks['Durum'].value_counts().reset_index()
            status_counts.columns = ['Durum', 'Sayi']
            
            fig_pie = px.pie(status_counts, values='Sayi', names='Durum', hole=0.6,
                             color_discrete_sequence=['#ff00ff', '#00f2ff', '#00ff9d', '#ffd700'])
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='#e0e0e0'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Grafik için veri bekleniyor.")

# --- B. GÖREV YÖNETİMİ ---
elif menu == "📝 Görev Yönetimi":
    st.title("Görev Merkezi")
    
    with st.expander("➕ YENİ GÖREV EKLE", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1: new_task_name = st.text_input("Görev Adı")
        with c2: 
            staff_list = df_staff['Isim'].tolist()
            new_task_person = st.selectbox("Atanan Kişi", staff_list if staff_list else ["Tanımsız"])
        with c3: new_task_start = st.date_input("Başlangıç", datetime.now())
        with c4: new_task_days = st.number_input("Süre (Gün)", min_value=1, value=3)
            
        if st.button("Görevi Kaydet"):
            new_end_date = new_task_start + timedelta(days=int(new_task_days))
            new_row = {
                "ID": str(uuid.uuid4())[:8],
                "GorevAdi": new_task_name,
                "Kisi": new_task_person,
                "Baslangic": pd.to_datetime(new_task_start),
                "Bitis": pd.to_datetime(new_end_date),
                "Durum": "Bekliyor",
                "Yuzde": 0
            }
            df_tasks = pd.concat([df_tasks, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df_tasks, "tasks")
            st.success("Kayıt Başarılı!")
            st.rerun()

    st.subheader("Aktif Görev Listesi")
    edited_df = st.data_editor(
        df_tasks,
        column_config={
            "Yuzde": st.column_config.ProgressColumn("İlerleme", min_value=0, max_value=100, format="%d%%"),
            "Durum": st.column_config.SelectboxColumn("Durum", options=["Bekliyor", "Devam Ediyor", "Tamamlandı", "İptal"]),
            "Baslangic": st.column_config.DateColumn("Başlangıç"),
            "Bitis": st.column_config.DateColumn("Bitiş"),
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="data_editor_tasks"
    )

    if not edited_df.equals(df_tasks):
        save_data(edited_df, "tasks")
        st.toast("Değişiklikler Kaydedildi", icon="💾")
        st.rerun()

# --- C. PERSONEL ---
elif menu == "👥 Personel":
    st.title("Personel Yönetimi")
    col_add, col_list = st.columns([1, 2])
    
    with col_add:
        st.markdown("### Personel Ekle")
        p_name = st.text_input("Ad Soyad")
        p_role = st.text_input("Rol")
        p_skills = st.text_area("Yetenekler")
        if st.button("Ekle"):
            if p_name:
                new_p = pd.DataFrame([{"Isim": p_name, "Rol": p_role, "Yetenekler": p_skills}])
                df_staff = pd.concat([df_staff, new_p], ignore_index=True)
                save_data(df_staff, "staff")
                st.rerun()
                
    with col_list:
        st.dataframe(df_staff, use_container_width=True, hide_index=True)

# --- D. GANTT ---
elif menu == "⏳ Gantt Şeması":
    st.title("Proje Takvimi")
    if not df_tasks.empty:
        colors = {"Bekliyor": "#e0e0e0", "Devam Ediyor": "#00f2ff", "Tamamlandı": "#00ff9d", "İptal": "#ff004c"}
        fig_gantt = px.timeline(
            df_tasks, x_start="Baslangic", x_end="Bitis", y="GorevAdi",
            color="Durum", color_discrete_map=colors
        )
        fig_gantt.update_yaxes(autorange="reversed")
        fig_gantt.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e0e0e0', xaxis_title="Zaman Çizelgesi", height=600
        )
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.info("Gantt şeması için görev ekleyin.")

# --- E. ÜRETİM ---
elif menu == "🏭 Üretim Planlayıcı":
    st.title("Üretim Simülasyonu")
    col_in, col_out = st.columns([1, 2])
    
    with col_in:
        st.subheader("Veri Girişi")
        siparis = st.number_input("Sipariş Adedi", 50)
        s1 = st.number_input("1. Kesim (dk)", 10)
        s2 = st.number_input("2. Montaj (dk)", 25)
        s3 = st.number_input("3. Boya (dk)", 15)
        
    with col_out:
        bottleneck = max(s1, s2, s3)
        total_time = (s1+s2+s3) + ((siparis-1) * bottleneck)
        
        st.metric("Tahmini Toplam Süre", f"{int(total_time)} Dakika", f"{total_time/60:.1f} Saat")
        
        sim_data = pd.DataFrame([
            {"Islem": "Kesim", "Sure": s1*siparis},
            {"Islem": "Montaj", "Sure": s2*siparis},
            {"Islem": "Boya", "Sure": s3*siparis}
        ])
        fig_sim = px.bar(sim_data, x="Islem", y="Sure", color="Islem",
                         color_discrete_sequence=['#00f2ff', '#ff00ff', '#00ff9d'])
        fig_sim.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig_sim, use_container_width=True)