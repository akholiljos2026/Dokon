import streamlit as st
import os
import shutil
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document

# ---------------------- KONFIGURASI HALAMAN ----------------------
st.set_page_config(page_title="Pengelolaan Dokumen", layout="wide", initial_sidebar_state="expanded")

# ---------------------- FUNGSI BANTUAN ----------------------
@st.cache_data(show_spinner=False)
def baca_isi_dokumen(jalur_berkas):
    teks = ""
    try:
        if jalur_berkas.lower().endswith(".pdf"):
            pembaca = PdfReader(jalur_berkas)
            for hal in pembaca.pages:
                isi = hal.extract_text()
                if isi:
                    teks += isi + "\n"
        elif jalur_berkas.lower().endswith(".docx"):
            dok = Document(jalur_berkas)
            for paragraf in dok.paragraphs:
                teks += paragraf.text + "\n"
        elif jalur_berkas.lower().endswith(".txt"):
            with open(jalur_berkas, "r", encoding="utf-8", errors="ignore") as f:
                teks = f.read()
    except Exception as e:
        teks = f"⚠️ Gagal membaca: {str(e)}"
    return teks

def buka_dokumen_langsung(jalur_berkas):
    try:
        if os.name == "nt":
            os.startfile(jalur_berkas)
        else:
            import subprocess
            subprocess.run(["xdg-open", jalur_berkas], check=True)
        return True, "✅ Dokumen dibuka!"
    except Exception as e:
        return False, f"❌ Gagal membuka: {str(e)}"

# ---------------------- INISIALISASI SESI ----------------------
if "folder_induk" not in st.session_state:
    st.session_state.folder_induk = "./dokumen"
if "jalur_aktif" not in st.session_state:
    st.session_state.jalur_aktif = ""
if "daftar_berkas" not in st.session_state:
    st.session_state.daftar_berkas = []
if "daftar_sub" not in st.session_state:
    st.session_state.daftar_sub = []
if "mulai" not in st.session_state:
    st.session_state.mulai = False

# ==================================================
# LAYAR PEMBUKA (SPLASH SCREEN) — SUDAH DIPERBAIKI
# ==================================================
if not st.session_state.mulai:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none;}

        .splash-bg {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #6dd5ed 100%);
            padding: 90px 30px 90px 30px;
            border-radius: 18px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.25);
            text-align: center;
            margin-top: 70px;
        }
        .splash-judul {
            font-size: 52px;
            font-weight: 900;
            letter-spacing: 3px;
            color: #ffffff;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.35);
            margin: 0;
        }
        .splash-sub {
            font-size: 22px;
            color: #e8f4ff;
            margin-top: 20px;
            font-style: italic;
        }
        /* Tombol Lanjut jadi biru sesuai tema */
        .stButton > button {
            background: linear-gradient(90deg, #2a5298, #6dd5ed) !important;
            border: none !important;
            color: white !important;
            font-weight: bold !important;
            font-size: 18px !important;
            padding: 12px !important;
            border-radius: 8px !important;
        }
        </style>

        <div class="splash-bg">
            <div class="splash-judul">APLIKASI PENGELOLAAN DOKUMEN</div>
            <div class="splash-sub">By : @Matera</div>
        </div>
    """, unsafe_allow_html=True)

    # Tombol Lanjut di tengah
    kosong1, tengah, kosong2 = st.columns([1, 2, 1])
    with tengah:
        st.write("")
        if st.button("🚀 Lanjut", use_container_width=True, type="primary"):
            st.session_state.mulai = True
            st.rerun()
    st.stop()


# ==================================================
# HEADER UTAMA — SELALU MUNCUL DI SETIAP MENU
# ==================================================
st.markdown("""
    <style>
    .header-utama {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        padding: 14px;
        border-radius: 10px;
        letter-spacing: 2px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    </style>
    <div class="header-utama">📂 PENGKELOLAAN DOKUMEN</div>
""", unsafe_allow_html=True)

# ---------------------- MENU SAMPING KIRI ----------------------
with st.sidebar:
    st.title("📂 Menu Utama")
    menu = st.radio(
        "Pilih Fitur",
        [
            "🏠 1. Pilih Lokasi & Subfolder",
            "📋 2. Daftar Dokumen",
            "➡️ 3. Pindahkan Dokumen",
            "👁️ 4. Baca Sepintas Dokumen",
            "🔍 5. Cari Isi Dokumen",
            "📖 6. Buka Lengkap"
        ],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption(f"📍 Folder Aktif: {st.session_state.jalur_aktif or 'Belum dipilih'}")
    if st.button("🔄 Kembali ke Layar Awal"):
        st.session_state.mulai = False
        st.rerun()

# ==================================================
# HALAMAN 1: PILIH LOKASI & SUBFOLDER
# ==================================================
if menu.startswith("🏠"):
    st.header("Pilih Lokasi Dokumen")
    
    st.session_state.folder_induk = st.text_input(
        "Jalur Folder Utama",
        value=st.session_state.folder_induk,
        help="Contoh: C:/Dokumen/Arsip atau ./berkas"
    )
    
    if not os.path.exists(st.session_state.folder_induk):
        st.error("❌ Folder tidak ditemukan! Periksa jalur yang dimasukkan.")
        st.stop()
    
    st.session_state.daftar_sub = []
    for jalur, _, _ in os.walk(st.session_state.folder_induk):
        jalur_rel = os.path.relpath(jalur, st.session_state.folder_induk)
        st.session_state.daftar_sub.append(jalur_rel)
    
    st.session_state.daftar_sub.insert(0, st.session_state.daftar_sub.pop(st.session_state.daftar_sub.index(".")))
    
    sub_terpilih = st.selectbox("Pilih Subfolder", st.session_state.daftar_sub)
    
    st.session_state.jalur_aktif = (
        st.session_state.folder_induk 
        if sub_terpilih == "." 
        else os.path.join(st.session_state.folder_induk, sub_terpilih)
    )
    
    semua_isi = os.listdir(st.session_state.jalur_aktif)
    st.session_state.daftar_berkas = [
        f for f in semua_isi 
        if os.path.isfile(os.path.join(st.session_state.jalur_aktif, f))
    ]
    daftar_folder = [f for f in semua_isi if os.path.isdir(os.path.join(st.session_state.jalur_aktif, f))]
    
    st.success(f"✅ Siap! — Subfolder: {len(daftar_folder)} | Dokumen: {len(st.session_state.daftar_berkas)}")
    st.info("👉 Pilih menu lain di sebelah kiri untuk memproses dokumen.")

# ==================================================
# HALAMAN 2: DAFTAR DOKUMEN
# ==================================================
elif menu.startswith("📋"):
    st.header("Daftar Dokumen")
    
    if not st.session_state.daftar_berkas:
        st.warning("⚠️ Silakan pilih subfolder dulu di menu 1!")
        st.stop()
    
    df = pd.DataFrame({
        "No": range(1, len(st.session_state.daftar_berkas)+1),
        "Nama Dokumen": st.session_state.daftar_berkas,
        "Jalur Lengkap": [
            os.path.join(st.session_state.jalur_aktif, f) 
            for f in st.session_state.daftar_berkas
        ]
    })
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.info(f"📄 Total: {len(st.session_state.daftar_berkas)} dokumen")

# ==================================================
# HALAMAN 3: PINDAHKAN DOKUMEN
# ==================================================
elif menu.startswith("➡️"):
    st.header("Pindahkan Dokumen Terpilih")
    
    if not st.session_state.daftar_berkas:
        st.warning("⚠️ Silakan pilih subfolder dulu di menu 1!")
        st.stop()
    
    folder_tujuan = st.text_input("Jalur Folder Tujuan", value="./dokumen/dipindahkan")
    
    df_pilih = pd.DataFrame({
        "Pilih": [False]*len(st.session_state.daftar_berkas),
        "Nama Dokumen": st.session_state.daftar_berkas
    })
    
    editor = st.data_editor(
        df_pilih,
        column_config={
            "Pilih": st.column_config.CheckboxColumn("Pilih", width=60),
            "Nama Dokumen": st.column_config.TextColumn("Nama Dokumen", width="large")
        },
        use_container_width=True,
        hide_index=True
    )
    
    terpilih = editor[editor["Pilih"]]
    
    if st.button("🚀 Pindahkan yang Dicentang", type="primary"):
        if terpilih.empty:
            st.warning("⚠️ Belum ada yang dicentang!")
        else:
            os.makedirs(folder_tujuan, exist_ok=True)
            berhasil = 0
            for _, baris in terpilih.iterrows():
                try:
                    shutil.move(
                        os.path.join(st.session_state.jalur_aktif, baris["Nama Dokumen"]),
                        os.path.join(folder_tujuan, baris["Nama Dokumen"])
                    )
                    berhasil += 1
                    st.session_state.daftar_berkas.remove(baris["Nama Dokumen"])
                except Exception as e:
                    st.error(f"Gagal: {baris['Nama Dokumen']} — {str(e)}")
            st.success(f"✅ Berhasil memindahkan {berhasil} dokumen!")
            st.rerun()

# ==================================================
# HALAMAN 4: BACA SEPINTAS
# ==================================================
elif menu.startswith("👁️"):
    st.header("Baca Isi Secara Sepintas")
    
    if not st.session_state.daftar_berkas:
        st.warning("⚠️ Silakan pilih subfolder dulu di menu 1!")
        st.stop()
    
    pilih = st.selectbox("Pilih Dokumen", ["— Pilih —"] + st.session_state.daftar_berkas)
    
    if pilih != "— Pilih —":
        isi = baca_isi_dokumen(os.path.join(st.session_state.jalur_aktif, pilih))
        if isi:
            st.text_area(
                "Cuplikan Isi:",
                isi[:1500] + ("\n...(terpotong)" if len(isi) > 1500 else ""),
                height=250
            )
        else:
            st.info("Tidak ada teks yang dapat dibaca.")

# ==================================================
# HALAMAN 5: CARI ISI DOKUMEN
# ==================================================
elif menu.startswith("🔍"):
    st.header("Cari Kata/Kalimat di Dokumen")
    
    if not st.session_state.daftar_berkas:
        st.warning("⚠️ Silakan pilih subfolder dulu di menu 1!")
        st.stop()
    
    kata_kunci = st.text_input("Masukkan kata atau kalimat yang dicari")
    
    if kata_kunci:
        with st.spinner(f"Mencari di {len(st.session_state.daftar_berkas)} dokumen..."):
            hasil = []
            for nama in st.session_state.daftar_berkas:
                jalur = os.path.join(st.session_state.jalur_aktif, nama)
                isi = baca_isi_dokumen(jalur).lower()
                if kata_kunci.lower() in isi:
                    pos = isi.find(kata_kunci.lower())
                    cuplikan = isi[max(0, pos-50):pos+100]
                    hasil.append({
                        "Nama Dokumen": nama,
                        "Cuplikan": f"...{cuplikan}...",
                        "Jalur": jalur
                    })
        
        if hasil:
            st.success(f"✅ Ditemukan {len(hasil)} dokumen:")
            st.dataframe(pd.DataFrame(hasil), use_container_width=True)
        else:
            st.info("Tidak ditemukan.")

# ==================================================
# HALAMAN 6: BUKA LENGKAP
# ==================================================
elif menu.startswith("📖"):
    st.header("Buka Dokumen Secara Keseluruhan")
    
    if not st.session_state.daftar_berkas:
        st.warning("⚠️ Silakan pilih subfolder dulu di menu 1!")
        st.stop()
    
    pilih = st.selectbox(
        "Pilih Dokumen",
        ["— Pilih —"] + st.session_state.daftar_berkas,
        key="buka_lengkap"
    )
    
    if pilih != "— Pilih —":
        jalur = os.path.join(st.session_state.jalur_aktif, pilih)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📖 Tampilkan Isi Lengkap"):
                isi = baca_isi_dokumen(jalur)
                if isi:
                    st.text_area("Isi Lengkap:", isi, height=500)
                else:
                    st.info("Tidak dapat menampilkan isi.")
        
        with col2:
            if st.button("📂 Buka dengan Aplikasi Sistem"):
                sukses, pesan = buka_dokumen_langsung(jalur)
                if sukses:
                    st.success(pesan)
                else:
                    st.error(pesan)
