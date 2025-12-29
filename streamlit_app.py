import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import qrcode
import io
import zipfile
import base64
import random

st.set_page_config(page_title="QR Card Generator", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Dark Theme ---
st.markdown("""
<style>
    /* General */
    body {
        color: #fff;
        background-color: #1E1E1E;
    }
    .stApp {
        background-color: #1E1E1E;
    }
    .st-emotion-cache-1jicfl2 {
        background-color: #2E2E2E;
    }

    /* Sidebar */
    .st-emotion-cache-16txtl3 {
        background-color: #252526;
        border-right: 1px solid #333;
    }
    .st-emotion-cache-16txtl3 .st-emotion-cache-1d8k8t2 {
        color: #fff;
    }

    /* Buttons */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 16px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }

    /* Special button for Generate All */
    .st-emotion-cache-1clstt5 .stButton>button {
        background-color: #007ACC;
    }
    .st-emotion-cache-1clstt5 .stButton>button:hover {
        background-color: #005f9e;
    }


    /* Sliders */
    .st-emotion-cache-1v0mbdj {
        background-color: #3e3e3e;
    }

    /* Text Input */
    .stTextInput>div>div>input {
        background-color: #3c3c3c;
        color: #fff;
        border: 1px solid #555;
    }

    /* Title */
    h1 {
        color: #00A36C;
        text-align: center;
        padding-bottom: 20px;
    }

    /* Expander */
    .st-emotion-cache-p5msec {
        background-color: #2E2E2E;
        border: 1px solid #444;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ QR Code Card Generator ✨")

# --- Instructions ---
with st.expander("📜 How to Use This App", expanded=False):
    st.markdown("""
    **Welcome to the QR Code Card Generator!** This tool helps you create beautiful cards with unique QR codes.

    ### 🛠️ **Setup Instructions**

    1.  **Template Image**: Upload a PNG image that will serve as the background for your cards. A resolution of `2272 x 3200` pixels is recommended for best results.
    2.  **Data File**: Upload a CSV file with `ID`, `Text`, and `URL` columns. Each row will be used to generate a unique card.
    3.  **Font (Optional)**: Upload a `.ttf` font file. If you don't provide one, the app will use its default `Poppins` font.

    ### 🎨 **Customization**

    -   Use the sidebar controls to adjust the font size, text color, QR code position, and more.
    -   You can drag the sliders to position elements or enable **Auto-scale QR Code** for automatic sizing.

    ### ▶️ **Actions**

    -   **Preview First/Random**: Check how your card looks with the first or a random data entry.
    -   **Preview Layout**: See the placement of QR codes and text areas with visual guides.
    -   **Generate All**: Create all cards and download them as a ZIP file.
    """)


# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")

    with st.expander("📁 1. Upload Files", expanded=True):
        template_file = st.file_uploader("Template Image (PNG)", type=["png"])
        autocorrect_resolution = st.checkbox("Auto-correct to 2272x3200px", value=True)
        csv_file = st.file_uploader("Data CSV", type=["csv"])
        font_file = st.file_uploader("Font File (TTF) - Optional", type=["ttf"])
        logo_file = st.file_uploader("Logo File (PNG) - Optional", type=["png"])

    with st.expander("🎨 2. Layout & Style", expanded=True):
        font_size = st.slider("Font Size", 20, 300, 120)
        text_prefix = st.text_input("Text Prefix", "ID: ")
        
        st.subheader("Text Appearance")
        text_color = st.color_picker("Text Color", "#FFFFFF")
        text_bg_color = st.color_picker("Text Background Color", "#000000")
        transparent_bg = st.checkbox("Transparent Text Background", value=False)
        
    # Placeholder for positioning controls
    positioning_placeholder = st.empty()


# --- Main Content Area ---
main_col1, main_col2, main_col3 = st.columns([1, 4, 1])
with main_col2:
    preview_placeholder = st.empty()

    with st.expander("▶️ 3. Actions", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            preview_first = st.button("🔍 Preview First")
            preview_layout = st.button("📐 Preview Layout")
        with col2:
            preview_random = st.button("🎲 Preview Random")
            generate_all = st.button("🚀 Generate All")


# --- Logic ---
if template_file and csv_file:
    def open_template():
        template = Image.open(template_file).convert("RGB")
        if autocorrect_resolution:
            if template.size != (2272, 3200):
                template = template.resize((2272, 3200))
        return template
    with st.sidebar:
        with positioning_placeholder.container():
            st.header("🎯 3. Position Elements")
            
            try:
                template_img = open_template()
                img_width, img_height = template_img.size
                
                # QR Code Positioning
                st.subheader("🔲 QR Code Position")
                auto_scale_qr = st.checkbox("Auto-scale QR Code", value=True)

                if auto_scale_qr:
                    qr_size_percent = st.slider("QR Code Size (% of width)", 1, 100, 50)
                    qr_x1 = st.slider("QR Left X", 0, img_width, min(542, img_width-100))
                    qr_y1 = st.slider("QR Top Y", 0, img_height, min(1453, img_height-100))
                    
                    qr_width = int(img_width * (qr_size_percent / 100))
                    qr_x2 = qr_x1 + qr_width
                    qr_y2 = qr_y1 + qr_width
                    
                    if qr_x2 > img_width: qr_x2 = img_width
                    if qr_y2 > img_height: qr_y2 = img_height
                else:
                    qr_x1 = st.slider("QR Left X", 0, img_width, min(542, img_width-100))
                    qr_y1 = st.slider("QR Top Y", 0, img_height, min(1453, img_height-100))
                    qr_x2 = st.slider("QR Right X", qr_x1+50, img_width, min(1729, img_width))
                    qr_y2 = st.slider("QR Bottom Y", qr_y1+50, img_height, min(2662, img_height))
                
                # Text Positioning
                st.subheader("📝 Text Position")
                text_y_top = st.slider("Text Top Y", 0, img_height, min(2762, img_height-50))
                text_y_bottom = st.slider("Text Bottom Y", text_y_top+20, img_height, min(2906, img_height))

                # Logo Positioning
                if logo_file:
                    st.subheader("🖼️ Logo Position")
                    logo_size = st.slider("Logo Size", 10, 500, 150)
                    logo_x = st.slider("Logo X", 0, img_width - logo_size, 100)
                    logo_y = st.slider("Logo Y", 0, img_height - logo_size, 100)

                # Guides
                st.subheader("📐 Guides")
                show_layout_guides = st.checkbox("Show Layout Guides in Previews", value=True)

            except Exception as e:
                st.error(f"Error loading template: {e}")
                st.stop()
    try:
        df = pd.read_csv(csv_file)
        if not all(col in df.columns for col in ["ID", "Text", "URL"]):
            st.error("CSV must have 'ID', 'Text', and 'URL' columns.")
            st.stop()
        if df.empty:
            st.error("CSV file is empty.")
            st.stop()
        if df.isnull().values.any():
            st.warning("CSV has empty cells.")
        
        # Load font
        try:
            if font_file:
                font = ImageFont.truetype(io.BytesIO(font_file.read()), font_size)
            else:
                with open("assets/Poppins-Regular.ttf", "rb") as f:
                    font = ImageFont.truetype(io.BytesIO(f.read()), font_size)
        except Exception as e:
            st.error(f"Error loading font: {e}")
            st.stop()
        
        def generate_card(row, show_guides=False):
            # ... (rest of the function remains the same, ensure it's defined here)
            try:
                display_text = f"{text_prefix}{row['Text']}" if text_prefix else row['Text']
                url = str(row['URL']) if pd.notna(row['URL']) else ""

                if not url:
                    raise ValueError("Missing URL")

                template = open_template()
                draw = ImageDraw.Draw(template)

                # --- QR Code Generation ---
                qr_width = qr_x2 - qr_x1
                qr_height = qr_y2 - qr_y1

                if qr_width > 0 and qr_height > 0:
                    qr_img = qrcode.make(url).resize((qr_width, qr_height))
                    template.paste(qr_img, (qr_x1, qr_y1))
                else:
                    st.warning("QR code dimensions are invalid. Skipping QR code generation.")
                
                # --- Logo ---
                if logo_file:
                    logo_img = Image.open(logo_file).convert("RGBA")
                    logo_img = logo_img.resize((logo_size, logo_size))
                    template.paste(logo_img, (logo_x, logo_y), logo_img)

                # --- Text Rendering ---
                text_area_height = text_y_bottom - text_y_top
                if text_area_height > 0:
                    bbox = draw.textbbox((0, 0), display_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    x_center = template.width // 2
                    text_x = x_center - text_width // 2
                    
                    text_y_center = text_y_top + (text_area_height // 2)
                    text_y = text_y_center - text_height // 2

                    # Background for text
                    if not transparent_bg:
                        padding = 10
                        bg_x1 = x_center - text_width//2 - padding
                        bg_y1 = text_y_center - text_height//2 - padding
                        bg_x2 = x_center + text_width//2 + padding
                        bg_y2 = text_y_center + text_height//2 + padding
                        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=text_bg_color)

                    draw.text((text_x, text_y), display_text, fill=text_color, font=font)

                # --- Guides ---
                if show_guides:
                    # QR code guide
                    draw.rectangle([qr_x1, qr_y1, qr_x2, qr_y2], outline="blue", width=5)
                    draw.text((qr_x1, qr_y1 - 30), "QR Area", fill="blue", font=font)
                    
                    # Text area guide
                    draw.rectangle([0, text_y_top, template.width, text_y_bottom], outline="red", width=5)
                    draw.text((10, text_y_top - 30), "Text Area", fill="red", font=font)

                    # Logo guide
                    if logo_file:
                        draw.rectangle([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], outline="green", width=5)
                        draw.text((logo_x, logo_y - 30), "Logo Area", fill="green", font=font)

                return template
            except Exception as e:
                raise ValueError(f"Error generating card for {row.get('ID', 'Unknown')}: {str(e)}")


        if preview_layout:
            with preview_placeholder.container():
                st.subheader("📐 Layout Preview")
                card = generate_card(df.iloc[0], show_guides=True)
                st.image(card, caption="Layout with positioning guides", width='stretch')
        elif preview_first:
            with preview_placeholder.container():
                st.subheader("🖼️ First Card Preview")
                card = generate_card(df.iloc[0], show_guides=show_layout_guides)
                st.image(card, caption=f"Card for {df.iloc[0]['ID']}", width='stretch')
        elif preview_random:
            with preview_placeholder.container():
                st.subheader("🎲 Random Card Preview")
                random_row = df.sample(1).iloc[0]
                card = generate_card(random_row, show_guides=show_layout_guides)
                st.image(card, caption=f"Card for {random_row['ID']}", width='stretch')
        else: # Default auto-preview
             with preview_placeholder.container():
                st.subheader("👁️ Auto Preview (First Card)")
                card = generate_card(df.iloc[0], show_guides=show_layout_guides)
                st.image(card, caption=f"Auto-preview for {df.iloc[0]['ID']}", width='stretch')

        if generate_all:
            with preview_placeholder.container():
                st.subheader("📦 Generating Cards...")
                # ... (generation logic remains the same)
                progress = st.progress(0)
                status_text = st.empty()
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    total = len(df)
                    success_count = 0
                    error_items = []
                    
                    for i, (_, row) in enumerate(df.iterrows()):
                        try:
                            # Generate final cards without guides
                            card = generate_card(row, show_guides=False)
                            img_bytes = io.BytesIO()
                            card.save(img_bytes, format="PNG")
                            img_bytes.seek(0)
                            zipf.writestr(f"{row['ID']}.png", img_bytes.read())
                            success_count += 1
                        except Exception as e:
                            error_items.append(f"{row['ID']}: {str(e)}")
                        
                        progress.progress((i + 1) / total)
                        status_text.text(f"Processed {i+1}/{total} cards...")
                
                zip_buffer.seek(0)
                
                st.success(f"✅ Successfully generated {success_count}/{total} cards!")
                
                if error_items:
                    st.warning(f"⚠️ {len(error_items)} items had errors:")
                    for error in error_items[:5]:
                        st.caption(f"• {error}")
                    if len(error_items) > 5:
                        st.caption(f"... and {len(error_items)-5} more")
                
                st.download_button(
                    label="📥 Download ZIP",
                    data=zip_buffer,
                    file_name="qr_cards.zip",
                    mime="application/zip",
                )

    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    with preview_placeholder.container():
        st.markdown("<h3 style='text-align: center; color: #555;'>Upload your files to get started!</h3>", unsafe_allow_html=True)
        
    if csv_file:
        st.sidebar.header("📋 CSV Preview")
        try:
            df_preview = pd.read_csv(csv_file)
            st.sidebar.dataframe(df_preview.head())
        except Exception as e:
            st.sidebar.error(f"Error reading CSV: {str(e)}")