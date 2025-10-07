import streamlit as st
from PIL import Image
import colorsys
from streamlit_image_coordinates import streamlit_image_coordinates

# --- Konfigurasi Halaman & Styling (CSS) ---

# Mengatur konfigurasi halaman agar lebih lebar dan memberikan judul pada tab browser
st.set_page_config(layout="wide", page_title="Advanced Color Picker")

# Fungsi untuk menyuntikkan CSS kustom ke dalam aplikasi Streamlit
def local_css():
    st.markdown("""
    <style>
    /* Menghilangkan padding bawaan streamlit */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Background utama halaman */
    body {
        background: linear-gradient(to right, #6a82fb, #fc5c7d);
    }
    
    /* Kontainer utama aplikasi yang berwarna putih dengan bayangan */
    .main-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px B20px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    
    /* Header aplikasi dengan latar belakang gelap */
    .app-header {
        background-color: #2c3e50;
        color: white;
        padding: 1rem;
        border-radius: 10px 10px 0 0;
        text-align: center;
    }
    .app-header h1 {
        margin: 0;
        font-size: 24px;
    }
    .app-header p {
        margin: 5px 0 0 0;
        font-size: 14px;
        color: #bdc3c7;
    }

    /* Styling untuk tombol */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
    /* Styling khusus untuk tombol "Hapus Semua" */
    .stButton>button[kind="primary"] {
        background-color: #e74c3c;
        border: none;
    }
    
    /* Mengubah kursor menjadi crosshair saat diarahkan ke gambar */
    div[data-testid="stImage"] img {
        cursor: crosshair;
    }
    
    </style>
    """, unsafe_allow_html=True)

# Memanggil fungsi CSS agar styling diterapkan
local_css()

# --- Fungsi Bantuan (Helper Functions) ---

def rgb_to_hex(rgb):
    """Mengubah tuple RGB menjadi kode warna HEX."""
    return '#%02x%02x%02x' % rgb

def rgb_to_hsl(rgb):
    """Mengubah tuple RGB (0-255) menjadi HSL (H:0-360, S:0-100, L:0-100)."""
    r, g, b = [x / 255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    # Mengembalikan nilai dalam format yang mudah dibaca
    return (int(h * 360), int(s * 100), int(l * 100))

# --- Inisialisasi State Aplikasi ---

# st.session_state digunakan untuk menyimpan data agar tidak hilang saat terjadi interaksi
# Inisialisasi daftar kosong untuk menyimpan warna jika belum ada
if 'selected_colors' not in st.session_state:
    st.session_state.selected_colors = []
# Inisialisasi state untuk menyimpan posisi klik terakhir
if 'last_click' not in st.session_state:
    st.session_state.last_click = None

# --- UI (User Interface) Aplikasi ---

# Bungkus semua elemen dalam satu div agar bisa menerapkan styling dari .main-container
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Bagian Header Aplikasi
    st.markdown("""
    <div class="app-header">
        <h1>Color Picker</h1>
        <p>Unggah dan klik pada gambar untuk memilih kode warna</p>
    </div>
    """, unsafe_allow_html=True)

    # Membagi layout utama menjadi dua kolom
    col1, col2 = st.columns([1, 1])

    # --- KOLOM KIRI (Upload dan Tampilan Gambar) ---
    with col1:
        st.subheader("Pilih Gambar", anchor=False)
        uploaded_file = st.file_uploader(
            "Klik untuk memilih gambar dari komputer Anda", 
            type=["jpg", "jpeg", "png"], 
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            # Konversi gambar ke mode RGB untuk konsistensi
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Menampilkan gambar dan menangkap koordinat saat diklik
            value = streamlit_image_coordinates(image, key="img_picker")

            # Logika untuk menambahkan warna baru ke dalam tabel saat ada klik baru
            if value and value != st.session_state.last_click:
                st.session_state.last_click = value
                x, y = value['x'], value['y']
                
                rgb = image.getpixel((x, y))
                hex_val = rgb_to_hex(rgb)
                hsl = rgb_to_hsl(rgb)
                
                # Menambahkan data warna baru ke dalam session_state
                st.session_state.selected_colors.append({
                    "coord": f"({x}, {y})",
                    "rgb": rgb,
                    "hex": hex_val,
                    "hsl": hsl,
                })
        else:
            # Placeholder yang tampil saat belum ada gambar yang diunggah
            st.markdown("""
            <div style="height: 300px; border: 2px dashed #bdc3c7; border-radius: 10px; display: flex; justify-content: center; align-items: center; color: #7f8c8d;">
                Area gambar akan muncul di sini
            </div>
            """, unsafe_allow_html=True)

    # --- KOLOM KANAN (Tabel Warna yang Dipilih) ---
    with col2:
        st.subheader("Tabel Warna yang Telah Dipilih", anchor=False)
        
        # Membuat Header Tabel secara manual menggunakan kolom
        header_cols = st.columns([0.5, 1, 1.5, 1.5, 1.5, 1.5, 1])
        headers = ["No", "Warna", "Koordinat", "RGB", "HEX", "HSL", "Aksi"]
        for col, header in zip(header_cols, headers):
            col.markdown(f"**{header}**")
        
        st.divider() # Garis pemisah antara header dan data

        # Menampilkan data warna jika ada, atau pesan informasi jika kosong
        if not st.session_state.selected_colors:
            st.info("Belum ada warna yang dipilih. Klik pada gambar untuk menambahkan warna.")
        else:
            # Melakukan iterasi untuk setiap warna yang tersimpan dan menampilkannya dalam baris
            for i, color_data in enumerate(st.session_state.selected_colors):
                row_cols = st.columns([0.5, 1, 1.5, 1.5, 1.5, 1.5, 1])
                
                # Kolom Nomor Urut
                row_cols[0].write(f"{i + 1}")
                
                # Kolom Swatch Warna (menggunakan HTML untuk membuat kotak berwarna)
                row_cols[1].markdown(
                    f'<div style="width:100%; height:25px; background-color:{color_data["hex"]}; border: 1px solid #ddd; border-radius: 3px;"></div>',
                    unsafe_allow_html=True
                )
                
                # Kolom data warna lainnya
                row_cols[2].text(color_data["coord"])
                row_cols[3].text(f"{color_data['rgb']}")
                row_cols[4].text(color_data["hex"])
                row_cols[5].text(f"{color_data['hsl']}")

                # Kolom Tombol Hapus per baris, dengan key unik agar tidak bentrok
                if row_cols[6].button("🗑️", key=f"del_{i}", help="Hapus warna ini"):
                    st.session_state.selected_colors.pop(i) # Hapus item dari list
                    st.rerun() # Muat ulang aplikasi untuk memperbarui tampilan

        # Menampilkan tombol "Hapus Semua" hanya jika ada warna yang dipilih
        if st.session_state.selected_colors:
            if st.button("Hapus Semua", type="primary"):
                st.session_state.selected_colors.clear() # Kosongkan list
                st.rerun() # Muat ulang aplikasi

    # Tag penutup untuk div .main-container
    st.markdown('</div>', unsafe_allow_html=True)