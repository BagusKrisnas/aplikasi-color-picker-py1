import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import io

# --- Konfigurasi Halaman & Styling (CSS) ---

st.set_page_config(layout="wide", page_title="Color Inspector")

def local_css():
    st.markdown("""
    <style>
    /* ... (CSS dari versi sebelumnya tetap sama) ... */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        background-color: #1E1E1E; color: #EAEAEA;
    }
    .stApp { background-color: #1E1E1E; }
    .block-container { padding: 2rem 4rem; }
    h1 { font-size: 2.5rem; font-weight: 700; }
    h2 { font-weight: 600; }
    .stFileUploader > div { border: 2px dashed #444; background-color: #2E2E2E; padding: 2rem; border-radius: 10px; }
    .color-box {
        background-color: #2E2E2E; padding: 1.5rem; border-radius: 10px;
        border-left: 8px solid var(--swatch-color, #555);
    }
    .color-box p { margin-bottom: 0.5rem; font-size: 1.1rem; }
    .color-box .hex-code {
        background-color: #444; padding: 0.5rem 1rem; border-radius: 5px;
        font-family: monospace; font-weight: 600; display: inline-block;
    }
    div[data-testid="stImage"] img { cursor: crosshair; }
    .stButton>button { border-radius: 5px; }

    .grid-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .grid-header h2 {
        margin: 0;
    }
    .grid-header .icon-buttons button {
        background-color: #333;
        border: 1px solid #555;
        color: #EAEAEA;
        margin-left: 5px;
        width: 40px;
        height: 40px;
    }
    .scrollable-grid-container {
        max-height: 400px;
        overflow: auto;
        border: 1px solid #444;
        border-radius: 8px;
        background-color: #2E2E2E;
    }
    .color-grid-table {
        border-collapse: collapse;
        width: 100%;
        table-layout: fixed;
    }
    .color-grid-table th, .color-grid-table td {
        border: 1px solid #444;
        padding: 8px;
        text-align: center;
        width: 90px;
        height: 40px;
        font-family: monospace;
        font-size: 0.8rem;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .color-grid-table th {
        background-color: #1E1E1E;
        position: sticky;
        top: -1px;
        left: -1px;
        z-index: 10;
    }
    .color-grid-table td.highlight {
        border: 2px solid #00A2FF;
        box-shadow: 0 0 10px #00A2FF;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- Fungsi Bantuan ---

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2]).upper()

def calculate_average_color(img):
    np_img = np.array(img)
    avg_color = np_img.mean(axis=(0, 1))
    return tuple(int(c) for c in avg_color)

def create_color_grid(img, cols=10, rows=10):
    width, height = img.size
    grid_data = []
    x_step = width / cols
    y_step = height / rows
    for i in range(rows):
        row_list = []
        for j in range(cols):
            x = min(int(j * x_step + x_step / 2), width - 1)
            y = min(int(i * y_step + y_step / 2), height - 1)
            rgb_val = img.getpixel((x, y))
            row_list.append({"x": x, "y": y, "rgb": rgb_val, "hex": rgb_to_hex(rgb_val)})
        grid_data.append(row_list)
    return grid_data

def create_html_table(data_2d, search_term=""):
    if not data_2d or not data_2d[0]: # Pemeriksaan keamanan jika data kosong
        return "Tidak ada data untuk ditampilkan."
    html = '<table class="color-grid-table">'
    html += '<thead><tr><th>(y,x)</th>'
    for item in data_2d[0]: html += f"<th>{item['x']}</th>"
    html += '</tr></thead><tbody>'
    for row in data_2d:
        html += f"<tr><th>{row[0]['y']}</th>"
        for item in row:
            text_color = "#FFFFFF" if (item['rgb'][0]*0.299 + item['rgb'][1]*0.587 + item['rgb'][2]*0.114) < 128 else "#000000"
            highlight_class = "highlight" if search_term and search_term in item['hex'] else ""
            html += f"<td class='{highlight_class}' style='background-color:{item['hex']}; color:{text_color};' title='RGB: {item['rgb']}'>{item['hex']}</td>"
        html += '</tr>'
    html += '</tbody></table>'
    return html

# --- Inisialisasi State Aplikasi ---
if 'last_color_info' not in st.session_state:
    st.session_state.last_color_info = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'default'
if 'fullscreen_data' not in st.session_state:
    st.session_state.fullscreen_data = None


# --- Logika Utama Aplikasi ---

# Tampilan Fullscreen
if st.session_state.view_mode == 'fullscreen_grid':
    st.title("Tampilan Penuh - Grid Sampel Warna")
    if st.button("⬅️ Kembali ke Tampilan Utama"):
        st.session_state.view_mode = 'default'
        st.rerun() # Menggunakan rerun di sini aman
    
    if st.session_state.fullscreen_data:
        html_table_fullscreen = create_html_table(st.session_state.fullscreen_data, st.session_state.search_query)
        st.markdown(html_table_fullscreen, unsafe_allow_html=True)
    else:
        st.warning("Tidak ada data grid untuk ditampilkan. Silakan kembali dan unggah gambar.")

# Tampilan Default
elif st.session_state.view_mode == 'default':
    st.title("🎨 Color Inspector (RGB/HEX)")
    st.write("Unggah gambar -> klik titik untuk melihat detail warna -> lihat grid -> unduh CSV.")
    st.divider()

    uploaded_file = st.file_uploader("Tarik & letakkan gambar (PNG/JPG/JPEG) di sini", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('RGB')
        
        st.info(f"File: **{uploaded_file.name}** | Dimensi Asli: **{image.width}x{image.height}px**")
        st.divider()

        main_col1, main_col2 = st.columns([2, 1])

        with main_col1:
            st.header("Ambil Warna per Titik", anchor=False)
            
            # --- PERBAIKAN UTAMA DI SINI ---
            MAX_WIDTH = 800
            # Hitung tinggi baru secara proporsional
            aspect_ratio = image.height / image.width
            new_height = int(MAX_WIDTH * aspect_ratio)
            # Selalu resize gambar yang akan ditampilkan ke lebar maksimum yang konsisten
            display_image = image.resize((MAX_WIDTH, new_height))

            from streamlit_image_coordinates import streamlit_image_coordinates
            value = streamlit_image_coordinates(display_image, key="img_picker")

            if value:
                scale_factor = image.width / display_image.width
                original_x = int(value['x'] * scale_factor)
                original_y = int(value['y'] * scale_factor)
                rgb = image.getpixel((original_x, original_y))
                hex_val = rgb_to_hex(rgb)
                st.session_state.last_color_info = {
                    "coord": f"({original_x}, {original_y})", "rgb": rgb, "hex": hex_val
                }
                
            st.header("Warna Titik Terpilih", anchor=False)
            if st.session_state.last_color_info:
                color_data = st.session_state.last_color_info
                st.markdown(f"""
                <div class="color-box" style="--swatch-color: {color_data['hex']};">
                    <p>Koordinat: <strong>{color_data['coord']}</strong></p>
                    <p>RGB: <strong>{color_data['rgb']}</strong> | HEX: <strong>{color_data['hex']}</strong></p>
                    <div class="hex-code">{color_data['hex']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Klik pada gambar untuk melihat detail warna di sini.")

            st.header("Rata-rata Warna Gambar", anchor=False)
            avg_rgb = calculate_average_color(image)
            avg_hex = rgb_to_hex(avg_rgb)
            st.markdown(f"""
            <div class="color-box" style="--swatch-color: {avg_hex};">
                <p>RGB: <strong>{avg_rgb}</strong> | HEX: <strong>{avg_hex}</strong></p>
                <div class="hex-code">{avg_hex}</div>
            </div>
            """, unsafe_allow_html=True)

        with main_col2:
            grid_cols_slider = st.slider("Kepadatan Grid (Kolom)", min_value=5, max_value=200, value=15)
            
            grid_data_2d = create_color_grid(image, cols=grid_cols_slider, rows=grid_cols_slider)
            flat_grid_data = [item for sublist in grid_data_2d for item in sublist]
            
            st.session_state.fullscreen_data = grid_data_2d

            st.markdown('<div class="grid-header">', unsafe_allow_html=True)
            st.subheader("Grid Sampel Warna", anchor=False)
            
            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                df = pd.DataFrame(flat_grid_data)
                df[['R', 'G', 'B']] = pd.DataFrame(df['rgb'].tolist(), index=df.index)
                csv = df[['x', 'y', 'R', 'G', 'B', 'hex']].to_csv(index=False).encode('utf-8')
                st.download_button(label="📥", data=csv, 
                                   file_name=f"color_grid_{uploaded_file.name.split('.')[0]}.csv", 
                                   mime='text/csv', help="Unduh data grid sebagai CSV", use_container_width=True)
            with b_col2:
                with st.popover("🔍", help="Cari warna HEX"):
                    st.session_state.search_query = st.text_input("Masukkan kode HEX:", value=st.session_state.search_query).upper()
            with b_col3:
                if st.button("⛶", help="Tampilan Penuh", use_container_width=True):
                    st.session_state.view_mode = 'fullscreen_grid'
                    st.rerun() # Menggunakan rerun di sini juga aman
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            html_table_main = create_html_table(grid_data_2d, st.session_state.search_query)
            st.markdown(f'<div class="scrollable-grid-container">{html_table_main}</div>', unsafe_allow_html=True)

    else:
        st.info("☝️ Silakan mulai dengan mengunggah sebuah gambar.")