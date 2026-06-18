import streamlit as st
import pandas as pd
import numpy as np
import os

# Paksa Matplotlib menggunakan backend non-interaktif
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA DASHBOARD
# ==========================================
st.set_page_config(page_title="SRIS Engine - Dashboard Audit ISO 27001", layout="wide", page_icon="🔒")

# Desain Tema Premium Corporate Cyber Security
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-box { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); border-left: 6px solid #0a4b78; }
    .security-banner { background-color: #0f2027; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; background: linear-gradient(to right, #203a43, #0f2027); }
    .chat-bubble-user { background-color: #0a4b78; color: white; padding: 12px; border-radius: 15px; margin-bottom: 10px; text-align: right; }
    .chat-bubble-bot { background-color: #e9ecef; color: #333; padding: 12px; border-radius: 15px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class='security-banner'>
        <h2>🔒 SRIS Engine: Dashboard Temuan & Risiko Audit ISO 27001:2022</h2>
        <p>Sistem Informasi Risiko Strategis (SRIS) | Integrasi Otomatis Kontrol Annex A & Chatbot AI Consultant</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. DETEKSI & PEMBACAAN DATA SECARA OTOMATIS (SMART LOADER)
# ==========================================
st.sidebar.header("📂 Sumber Data Audit")
uploaded_file = st.sidebar.file_uploader("Unggah File CSV Hasil Audit Terbaru:", type=["csv", "xlsx"])

df = None
status_pembacaan = ""

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        status_pembacaan = f"Berhasil memuat file unggahan: {uploaded_file.name}"
    except Exception as e:
        st.sidebar.error(f"Gagal membaca file unggahan: {e}")

if df is None:
    for file in os.listdir('.'):
        if (file.endswith('.csv') or file.endswith('.xlsx')) and file != 'app.py' and "Simulasi" not in file:
            if any(kunci in file for kunci in ["Formulir", "Responses", "Jawaban", "kompilasi"]):
                try:
                    if file.endswith('.csv'):
                        df = pd.read_csv(file)
                    else:
                        df = pd.read_excel(file)
                    status_pembacaan = f"Otomatis mendeteksi file workspace: {file}"
                    break
                except:
                    pass

if df is None:
    for file in os.listdir('.'):
        if (file.endswith('.csv') or file.endswith('.xlsx')) and file != 'app.py':
            try:
                if file.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                status_pembacaan = f"Memuat file yang tersedia: {file}"
                break
            except:
                pass

# KONDISI AWAL VARIABEL SEBELUM PROSES FILTERING
df_filtered = None

# DEFINISI NAMA KOLOM SECARA GLOBAL SEJAK AWAL AGAR BEBAS DARI NAMEERROR
kolom_dept = 'Departemen Divisi/Area'
kolom_status = 'Posisi Status NC'
kolom_cyber = 'Cybersecurity Consepts'  
kolom_pilar = 'Pillars Information Security'
kolom_ops = 'Operational Capabilities'
kolom_annex = 'Kategori Kontrol ( Annex A ) ISO 27001'
kolom_auditor = 'Nama Auditor'
kolom_standar = 'STANDARD'
kolom_temuan = 'Detail Temuan Ketidaksesuaian'
kolom_no_annex = 'No Annex dan No Control ( ISO 27001)'

# ==========================================
# 3. CORE PROCESSING ENGINE & DATA CLEANING
# ==========================================
if df is not None:
    df.columns = [col.strip() for col in df.columns]
    
    if kolom_dept in df.columns:
        df[kolom_dept] = df[kolom_dept].astype(str).str.strip()
        mapping_mr = {
            'Management Representatif /MR': 'Management Representative (MR)',
            'MR Management Representatif': 'Management Representative (MR)',
            'MR': 'Management Representative (MR)'
        }
        df[kolom_dept] = df[kolom_dept].replace(mapping_mr)
    
    # PROSES EKSTRAKSI SKOR PENTAGON
    pilar_skor = {
        'P1_Regulasi': 'Skoring Pentagon Analisis [P1- Regulasi & Kepatuhan]',
        'P2_Finansial': 'Skoring Pentagon Analisis [P2- Finansial & Kerugian]',
        'P3_Integritas': 'Skoring Pentagon Analisis [P3- Integritas data & System]',
        'P4_Operasional': 'Skoring Pentagon Analisis [P4- Operational]',
        'P5_Reputasi': 'Skoring Pentagon Analisis [P5 Reputasi & Nama Baik]'
    }
    for key, nama_kolom in pilar_skor.items():
        if nama_kolom in df.columns:
            df[key] = df[nama_kolom].astype(str).str.extract(r'(\d+)')[0].astype(float)
            df[key] = df[key].fillna(0.0)
        else:
            df[key] = 0.0

    st.sidebar.success("🔌 Status Data: Terhubung")
    st.sidebar.info(f"ℹ️ {status_pembacaan}")
    
    # PANEL KONTROL FILTER DEPARTEMEN
    if kolom_dept in df.columns:
        list_dept = ["Semua Departemen"] + sorted(list(df[kolom_dept].dropna().unique()))
        selected_dept = st.sidebar.selectbox("Pilih Departemen/Divisi:", list_dept)
        if selected_dept != "Semua Departemen":
            df_filtered = df[df[kolom_dept] == selected_dept].copy()
        else:
            df_filtered = df.copy()
    else:
        df_filtered = df.copy()

    # Kunci hasil akhir ke Session State agar aman saat navigasi dipindah
    st.session_state['df_filtered_saved'] = df_filtered
    st.session_state['df'] = df

# ==========================================
# 4. MENU NAVIGASI UTAMA
# ==========================================
menu = st.sidebar.radio("Pilih Navigasi Dashboard:", [
    "📊 Ringkasan Eksekutif & Status Temuan",
    "🕸️ Analisis Radar Pentagon (SRIS Model)",
    "🔍 Audit Deep Dive & Manajemen Annex A",
    "🤖 SRIS Chatbot AI (Tanya Jawab Audit)"
])

# Ambil data pengaman dari session state
if 'df_filtered_saved' in st.session_state:
    df_filtered = st.session_state['df_filtered_saved']

# Eksekusi Menu Hanya Jika Data Berhasil Dimuat
if df_filtered is not None:

    if menu == "📊 Ringkasan Eksekutif & Status Temuan":
        st.subheader("📊 Metrik Utama Hasil Audit Sistem Manajemen")
        total_temuan = len(df_filtered)
        if kolom_status in df_filtered.columns:
            open_nc = len(df_filtered[df_filtered[kolom_status].astype(str).str.contains('Open|On Progress', case=False, na=False)])
            closed_nc = total_temuan - open_nc
        else:
            open_nc = total_temuan; closed_nc = 0
            
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            st.metric(label="Total Kasus Temuan Audit", value=f"{total_temuan} Temuan")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            st.metric(label="Status Open / On Progress", value=f"{open_nc} Kasus", delta="Risk Exposure", delta_color="inverse")
            st.markdown("</div>", unsafe_allow_html=True)
        with c3:
            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            st.metric(label="Status Closed (Selesai Perbaikan)", value=f"{closed_nc} Kasus", delta="Mitigated")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # BARIS GRAFIK 1: DEPARTEMEN & CYBERSECURITY CONCEPT
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.write("##### 🏢 Distribusi Temuan Berdasarkan Departemen")
            fig1, ax1 = plt.subplots(figsize=(6, 3.5))
            if kolom_dept in df_filtered.columns and not df_filtered[kolom_dept].isna().all():
                df_filtered[kolom_dept].value_counts().sort_values(ascending=True).plot(kind='barh', color='#0a4b78', ax=ax1)
            plt.tight_layout()
            st.pyplot(fig1); plt.close(fig1)
        with col_g2:
            st.write("##### 🛡️ Profil Temuan Berdasarkan Cybersecurity Concepts")
            fig2, ax2 = plt.subplots(figsize=(6, 3.5))
            if kolom_cyber in df_filtered.columns and not df_filtered[kolom_cyber].isna().all():
                df_filtered[kolom_cyber].value_counts().plot(kind='bar', color='#00a8cc', edgecolor='black', ax=ax2)
                plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig2); plt.close(fig2)

        # BARIS GRAFIK 2: INFORMATION SECURITY PILAR (CIA) & OPERATIONAL CAPABILITIES
        st.markdown("<br>", unsafe_allow_html=True)
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            st.write("##### 🔑 Distribusi Berdasarkan Pillars Information Security (CIA)")
            fig3, ax3 = plt.subplots(figsize=(6, 3.5))
            if kolom_pilar in df_filtered.columns and not df_filtered[kolom_pilar].isna().all():
                pilar_series = df_filtered[kolom_pilar].dropna().astype(str).str.split(',\s*').explode()
                pilar_series.value_counts().plot(kind='bar', color='#4b86b4', edgecolor='black', ax=ax3)
                plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig3); plt.close(fig3)
        with col_g4:
            st.write("##### ⚙️ Distribusi Berdasarkan Operational Capabilities")
            fig4, ax4 = plt.subplots(figsize=(6, 3.5))
            if kolom_ops in df_filtered.columns and not df_filtered[kolom_ops].isna().all():
                df_filtered[kolom_ops].value_counts().plot(kind='bar', color='#2a9d8f', edgecolor='black', ax=ax4)
                plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig4); plt.close(fig4)

    elif menu == "🕸️ Analisis Radar Pentagon (SRIS Model)":
        st.subheader("🕸️ Pemetaan Profil Risiko Organisasi (Pentagon Model)")
        
        p1 = df_filtered['P1_Regulasi'].mean() if 'P1_Regulasi' in df_filtered.columns else 0
        p2 = df_filtered['P2_Finansial'].mean() if 'P2_Finansial' in df_filtered.columns else 0
        p3 = df_filtered['P3_Integritas'].mean() if 'P3_Integritas' in df_filtered.columns else 0
        p4 = df_filtered['P4_Operasional'].mean() if 'P4_Operasional' in df_filtered.columns else 0
        p5 = df_filtered['P5_Reputasi'].mean() if 'P5_Reputasi' in df_filtered.columns else 0
        
        scores = [p1, p2, p3, p4, p5]
        categories = ['P1: Regulasi', 'P2: Finansial', 'P3: Integritas Data', 'P4: Operasional', 'P5: Reputasi']
        categories_loop = categories + [categories[0]]; scores_loop = scores + [scores[0]]
        angles = np.linspace(start=0, stop=2*np.pi, num=len(categories_loop))
        
        c_chart, c_narrative = st.columns([1.2, 1])
        with c_chart:
            fig_radar, ax_radar = plt.subplots(figsize=(5.5, 5.5), subplot_kw=dict(polar=True))
            ax_radar.plot(angles, scores_loop, color='#00a8cc', linewidth=2.5, marker='o')
            ax_radar.fill(angles, scores_loop, color='#00a8cc', alpha=0.3)
            ax_radar.set_thetagrids(np.degrees(angles[:-1]), categories, fontsize=9, fontweight='bold')
            ax_radar.set_ylim(0, 5); st.pyplot(fig_radar); plt.close(fig_radar)
        with c_narrative:
            st.write("##### 💡 Analisis Strategis Senior Management")
            if sum(scores) > 0:
                max_idx = np.argmax(scores)
                st.error(f"**Pilar Kerentanan Utama:** Area **{categories[max_idx]}** menunjukkan nilai eksposur risiko tertinggi ({scores[max_idx]:.2f}/5.0).")
            else:
                st.info("Belum ada data nilai skor untuk departemen terpilih.")

    elif menu == "🔍 Audit Deep Dive & Manajemen Annex A":
        st.subheader("🛠️ Kelemahan Kontrol Berdasarkan Annex A ISO 27001")
        fig_annex, ax_annex = plt.subplots(figsize=(10, 4.5))
        if kolom_annex in df_filtered.columns and not df_filtered[kolom_annex].isna().all():
            df_filtered[kolom_annex].value_counts().plot(kind='bar', color='#ff7e67', edgecolor='black', ax=ax_annex)
        st.pyplot(fig_annex); plt.close(fig_annex)
        
        st.write("##### 🗂️ Tabel Inventori Temuan Audit")
        kolom_tampilan = [kolom_auditor, kolom_dept, kolom_standar, kolom_temuan, kolom_status, kolom_no_annex]
        st.dataframe(df_filtered[[c for c in kolom_tampilan if c in df_filtered.columns]], use_container_width=True)

    elif menu == "🤖 SRIS Chatbot AI (Tanya Jawab Audit)":
        st.subheader("🤖 SRIS Executive AI Consultant")
        st.info("Asisten AI siap membantu Anda menganalisis temuan audit secara instan berbasis data & aspek Keamanan Informasi.")
        
        if "GEMINI_API_KEY" in st.secrets:
            api_key_input = st.secrets["GEMINI_API_KEY"]
        else:
            api_key_input = st.text_input("🔑 Masukkan Google Gemini API Key Anda:", type="password")
        
        if api_key_input:
            try:
                from google import genai
                client = genai.Client(api_key=api_key_input)
                
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []
                
                for chat in st.session_state.chat_history:
                    if chat["role"] == "user":
                        st.markdown(f"<div class='chat-bubble-user'>🧑‍💼 <b>Anda:</b> {chat['text']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='chat-bubble-bot'>🤖 <b>SRIS AI:</b> {chat['text']}</div>", unsafe_allow_html=True)
                
                user_query = st.chat_input("Ketik pertanyaan audit Anda di sini...")
                
                if user_query:
                    st.markdown(f"<div class='chat-bubble-user'>🧑‍💼 <b>Anda:</b> {user_query}</div>", unsafe_allow_html=True)
                    
                    kolom_ks = [kolom_dept, kolom_temuan, kolom_status, kolom_annex]
                    kolom_tersedia = [c for c in kolom_ks if c in df_filtered.columns]
                    ringkasan_data = df_filtered[kolom_tersedia].to_string(index=False) if kolom_tersedia else "Data kolom tidak sesuai."
                    
                    system_instruction = f"""
                    Anda adalah SRIS Executive AI Consultant, seorang ahli strategi tata kelola keamanan informasi senior dan auditor ISO 27001:2022.
                    Tugas Anda adalah menganalisis pertanyaan pengguna berbasis data audit berikut:
                    
                    --- DATA AUDIT AKTIF ---
                    {ringkasan_data[:25000]}
                    --- AKHIR DATA ---
                    
                    Setiap memberikan jawaban, Anda WAJIB menyertakan blok taksonomi keamanan informasi di bagian paling atas jawaban dengan format berikut:
                    
                    [TAG_ANALISIS]
                    - Cybersecurity Concept: [Identify / Protect / Detect / Respond / Recover]
                    - Pilar Security (CIA): [Confidentiality / Integrity / Availability]
                    - Operational Capability: [Governance & Risk, Asset Management, Human Security, Physical Security, Technology Protection, Incident Management, Business Continuity]
                    [AKHIR_TAG]
                    
                    Jawablah menggunakan Bahasa Indonesia profesional tingkat tinggi (Executive Level).
                    """
                    
                    with st.spinner("Mengonfirmasi ke AI Cyber Security Engine..."):
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=user_query,
                            config={'system_instruction': system_instruction}
                        )
                        bot_response = response.text
                    
                    if "[TAG_ANALISIS]" in bot_response:
                        try:
                            parts = bot_response.split("[AKHIR_TAG]")
                            tag_part = parts[0].replace("[TAG_ANALISIS]", "").strip()
                            isi_jawaban = parts[1].strip()
                            
                            st.markdown("##### 🛡️ Klasifikasi Risiko & Kapabilitas Keamanan:")
                            lines = tag_part.split("\n")
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                val_cyber = next((line.split(":")[1].strip() for line in lines if "Cybersecurity Concept" in line), "Identify")
                                st.metric("Cybersecurity Concept", val_cyber)
                            with c2:
                                val_cia = next((line.split(":")[1].strip() for line in lines if "Pilar Security (CIA)" in line), "Integrity")
                                st.metric("Pilar Security (CIA)", val_cia)
                            with c3:
                                val_op = next((line.split(":")[1].strip() for line in lines if "Operational Capability" in line), "Governance & Risk")
                                st.metric("Operational Capability", val_op)
                                
                            st.markdown(f"<div class='chat-bubble-bot'>🤖 <b>SRIS AI:</b><br><br>{isi_jawaban}</div>", unsafe_allow_html=True)
                        except:
                            st.markdown(f"<div class='chat-bubble-bot'>🤖 <b>SRIS AI:</b><br><br>{bot_response}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='chat-bubble-bot'>🤖 <b>SRIS AI:</b><br><br>{bot_response}</div>", unsafe_allow_html=True)
                    
                    st.session_state.chat_history.append({"role": "user", "text": user_query})
                    st.session_state.chat_history.append({"role": "bot", "text": bot_response})
                    
            except Exception as error_ai:
                st.error(f"Gagal menghubungkan ke AI Engine: {error_ai}")
        else:
            st.warning("⚠️ Silakan masukkan Gemini API Key Anda terlebih dahulu untuk mengaktifkan fungsi Chatbot AI.")
else:
    st.error("🚨 File data audit tidak ditemukan di direktori! Silakan unggah file CSV/XLSX hasil audit Anda di sidebar sebelah kiri.")
