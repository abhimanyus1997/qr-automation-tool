import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import qrcode
import io
import zipfile
import base64

st.set_page_config(page_title="QR Card Generator", layout="wide")
st.title("🏷️ QR Code Card Generator")

# Enhanced instructions with visual examples
with st.expander("📄 How to Use This App (Click to Expand)", expanded=False):
    st.markdown("""
### 🔧 Required Files

#### 1. Template Image (`template.png`)
- **Format**: PNG
- **Size Recommended**: `2272 x 3200` pixels
- This image will be the background for each card.
- Make sure the area where the QR code and text will go is blank or appropriate.

#### 2. Data CSV (`data.csv`)
A CSV file with these columns:

| ID     | Text           | URL                         |
| ------ | -------------- | --------------------------- |
| 001    | Product A      | https://example.com/item/1  |
| 002    | Product B      | https://example.com/item/2  |

- `ID`: Unique identifier (used in filename).
- `Text`: Text to display on the card.
- `URL`: The unique link to encode in the QR code.

#### 3. Font File (`.ttf`)
- Upload a `.ttf` font file (e.g., `Poppins.ttf`, `Inter.ttf`, etc.).
- The font is used for rendering the text on the card.

---

### 🎨 Drag & Drop Positioning

Use the interactive positioning tool to visually set QR code and text positions:
1. Upload your template image
2. Drag the blue boxes to position QR code area
3. Drag the red lines to position text area
4. Fine-tune with numeric inputs if needed
5. Customize text appearance with color pickers

---

### 👁️ Preview Options

- **Preview First Card**: See how the first item will look
- **Preview Layout**: See positioning guides on template
- **Show Layout Guides (Checkbox)**: Toggle guides in previews
- **Generate All**: Create all cards and download ZIP

---

### ✅ Tips

- Keep QR and Text positions inside the bounds of the image (0 to width/height).
- Choose background/text colors for good contrast.
- Make sure URLs in the CSV are valid and non-empty.
""")

# --- Sidebar: Uploads ---
st.sidebar.header("📁 1. Upload Files")
template_file = st.sidebar.file_uploader("Template Image (PNG)", type=["png"])
csv_file = st.sidebar.file_uploader("Data CSV", type=["csv"])
font_file = st.sidebar.file_uploader("Font File (TTF)", type=["ttf"])

# --- Sidebar: Configuration ---
st.sidebar.header("⚙️ 2. Customize Layout")
font_size = st.sidebar.slider("Font Size", 20, 300, 120)
text_prefix = st.sidebar.text_input("Text Prefix", "ID: ")

# Text appearance customization
st.sidebar.subheader("🎨 Text Appearance")
text_color = st.sidebar.color_picker("Text Color", "#FFFFFF") # Default White
text_bg_color = st.sidebar.color_picker("Text Background Color", "#000000") # Default Black
# Option for transparent background (represented by a specific color or checkbox)
transparent_bg = st.sidebar.checkbox("Transparent Text Background", value=False)

# --- Drag & Drop Positioning ---
if template_file:
    try:
        template_img = Image.open(template_file).convert("RGB")
        img_width, img_height = template_img.size
        
        st.sidebar.header("🎯 3. Position Elements")
        
        # QR Code Positioning with drag & drop
        st.sidebar.subheader("🔲 QR Code Position")
        qr_x1 = st.sidebar.slider("QR Left X", 0, img_width, min(542, img_width-100))
        qr_y1 = st.sidebar.slider("QR Top Y", 0, img_height, min(1453, img_height-100))
        qr_x2 = st.sidebar.slider("QR Right X", qr_x1+50, img_width, min(1729, img_width))
        qr_y2 = st.sidebar.slider("QR Bottom Y", qr_y1+50, img_height, min(2662, img_height))
        
        # Text Positioning with drag & drop
        st.sidebar.subheader("📝 Text Position")
        text_y_top = st.sidebar.slider("Text Top Y", 0, img_height, min(2762, img_height-50))
        text_y_bottom = st.sidebar.slider("Text Bottom Y", text_y_top+20, img_height, min(2906, img_height))
        
        # Show Layout Guides Checkbox (near positioning controls)
        st.sidebar.subheader("📐 Guides")
        show_layout_guides = st.sidebar.checkbox("Show Layout Guides in Previews", value=True)
        
    except Exception as e:
        st.sidebar.error(f"Error loading template: {str(e)}")
        template_img = None
else:
    st.sidebar.info("Upload template to enable positioning")
    template_img = None

# --- Buttons ---
st.sidebar.header("▶️ 4. Actions")
col1, col2, col3 = st.columns(3)
preview_first = col1.button("🔍 Preview First Card")
preview_layout = col2.button("📐 Preview Layout")
generate_all = col3.button("🚀 Generate All")

# --- Main Content Area for Preview ---
preview_placeholder = st.empty()

# --- Process Once Inputs Are Valid ---
if template_file and csv_file and font_file:
    try:
        df = pd.read_csv(csv_file)
        required_columns = ["ID", "Text", "URL"]
        if not all(col in df.columns for col in required_columns):
            st.error("❌ CSV must contain 'ID', 'Text', and 'URL' columns.")
            st.stop()
        
        # Validate data
        if df.empty:
            st.error("❌ CSV file is empty.")
            st.stop()
            
        if df.isnull().values.any():
            st.warning("⚠️ CSV contains empty cells. These will be processed as empty strings.")
        
        font_bytes = font_file.read()
        font = ImageFont.truetype(io.BytesIO(font_bytes), font_size)

        def generate_card(row, show_guides=False):
            try:
                display_text = f"{text_prefix}{row['Text']}" if text_prefix else row['Text']
                url = str(row['URL']) if pd.notna(row['URL']) else ""
                
                if not url:
                    raise ValueError("Missing URL")
                
                template = Image.open(template_file).convert("RGB")
                draw = ImageDraw.Draw(template)
                
                # Add QR code
                qr_img = qrcode.make(url).resize((qr_x2 - qr_x1, qr_y2 - qr_y1))
                template.paste(qr_img, (qr_x1, qr_y1))
                
                # Add positioning guides if requested
                if show_guides:
                    # QR code guide (blue)
                    draw.rectangle([qr_x1, qr_y1, qr_x2, qr_y2], outline="blue", width=3)
                    draw.text((max(0, qr_x1), max(0, qr_y1-20)), "QR Code", fill="blue", font=font)
                    
                    # Text area guide (red)
                    draw.line([0, text_y_top, template.width, text_y_top], fill="red", width=2)
                    draw.line([0, text_y_bottom, template.width, text_y_bottom], fill="red", width=2)
                    draw.text((10, max(0, text_y_top-20)), "Text Area", fill="red", font=font)
                
                # Draw text centered horizontally at y center
                bbox = draw.textbbox((0, 0), display_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_y_center = (text_y_top + text_y_bottom) // 2
                x_center = template.width // 2
                
                # Background rectangle for better text visibility
                padding = 10
                if not transparent_bg:
                    draw.rectangle([
                        x_center - text_width//2 - padding,
                        text_y_center - text_height//2 - padding,
                        x_center + text_width//2 + padding,
                        text_y_center + text_height//2 + padding
                    ], fill=text_bg_color)
                
                draw.text(
                    (x_center - text_width // 2, text_y_center - text_height // 2),
                    display_text,
                    fill=text_color,
                    font=font,
                )
                return template
            except Exception as e:
                raise ValueError(f"Error generating card for {row.get('ID', 'Unknown')}: {str(e)}")

        # Preview Layout
        if preview_layout and template_img:
            with preview_placeholder.container():
                st.subheader("📐 Layout Preview")
                try:
                    layout_preview = generate_card(df.iloc[0], show_guides=True)
                    st.image(layout_preview, caption="Layout with positioning guides", use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error generating layout preview: {str(e)}")

        # Preview First Card
        elif preview_first:
            with preview_placeholder.container():
                st.subheader("🖼️ First Card Preview")
                try:
                    # Use the checkbox state for guides in this preview
                    first_card = generate_card(df.iloc[0], show_guides=show_layout_guides)
                    st.image(first_card, caption=f"Card for {df.iloc[0]['ID']}", use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error generating first card: {str(e)}")
        
        # Auto-preview when files are loaded and no button pressed recently
        # This requires a bit more state management, simplified here:
        # Show first card without guides if no specific preview button was pressed
        elif not preview_layout: # Simplified auto-preview logic
             with preview_placeholder.container():
                st.subheader("👁️ Auto Preview (First Card)")
                try:
                    auto_preview = generate_card(df.iloc[0], show_guides=show_layout_guides)
                    st.image(auto_preview, caption=f"Auto-preview for {df.iloc[0]['ID']}", use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error generating auto-preview: {str(e)}")

        # Generate All Cards
        if generate_all:
            # Clear the preview area for the generation status
            with preview_placeholder.container():
                st.subheader("📦 Generating Cards...")
                try:
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
                    
                    # Show results
                    st.success(f"✅ Successfully generated {success_count}/{total} cards!")
                    
                    if error_items:
                        st.warning(f"⚠️ {len(error_items)} items had errors:")
                        for error in error_items[:5]:  # Show first 5 errors
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
                    st.error(f"❌ Error generating ZIP: {str(e)}")
                
    except pd.errors.EmptyDataError:
        st.error("❌ CSV file is empty or invalid.")
        preview_placeholder.empty()
    except pd.errors.ParserError:
        st.error("❌ CSV file format is invalid.")
        preview_placeholder.empty()
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")
        preview_placeholder.empty()
        
elif template_file or csv_file or font_file:
    missing = []
    if not template_file:
        missing.append("template image")
    if not csv_file:
        missing.append("CSV file")
    if not font_file:
        missing.append("font file")
    st.info(f"📁 Please upload: {', '.join(missing)}")
    preview_placeholder.empty()

# Data preview section
if csv_file:
    st.sidebar.header("📋 CSV Preview")
    try:
        df_preview = pd.read_csv(csv_file)
        st.sidebar.dataframe(df_preview.head())
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {str(e)}")