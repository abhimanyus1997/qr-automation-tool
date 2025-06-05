import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import qrcode
import io
import zipfile

st.set_page_config(page_title="QR Card Generator", layout="wide")
st.title("🏨 QR Code Card Generator")

with st.expander("📄 How to Use This App (Click to Expand)", expanded=False):
    st.markdown("""
### 🔧 Required Files

#### 1. Template Image (`template.png`)
- **Format**: PNG
- **Size Recommended**: `2272 x 3200` pixels
- This image will be the background for each card.
- Make sure the area where the QR code and Room number will go is blank or appropriate.

#### 2. Rooms CSV (`rooms.csv`)
A simple CSV with these **3 columns**:

| Number | Floor | URL                                                  |
| ------ | ----- | ---------------------------------------------------- |
| 1101   | 1     | [https://example.com/1101](https://example.com/1101) |
| 1102   | 1     | [https://example.com/1102](https://example.com/1102) |


...

yaml
Copy
Edit

- `Number`: The room number (used in text and filename).
- `Floor`: Optional; not used by the script but may be useful for grouping.
- `URL`: The unique link to encode in the QR code.

#### 3. Font File (`.ttf`)
- Upload a `.ttf` font file (e.g., `Poppins.ttf`, `Inter.ttf`, etc.).
- The font is used for rendering the room number on the card.

---

### ✏️ Customize Layout

You can set:
- **QR code position** by entering the top-left and bottom-right coordinates.
- **Text position** by specifying top and bottom Y bounds.
- **Font size** using the slider.

---

### 👁️ Preview & Export

- Use **"🔍 Preview First Card"** to see how your layout looks.
- Use **"🚀 Generate All"** to process all rows and get a `.zip` file of images.

---

### ✅ Tips

- Keep QR and Text positions inside the bounds of the image (0 to width/height).
- White or light background behind text is better for readability.
- Make sure URLs in the CSV are valid and non-empty.

""")

# --- Sidebar: Uploads ---
st.sidebar.header("1. Upload Files")
template_file = st.sidebar.file_uploader("Template Image (PNG)", type=["png"])
csv_file = st.sidebar.file_uploader("Rooms CSV", type=["csv"])
font_file = st.sidebar.file_uploader("Font File (TTF)", type=["ttf"])

# --- Sidebar: Configuration ---
st.sidebar.header("2. Customize Layout")
font_size = st.sidebar.slider("Font Size", 40, 200, 120)

qr_x1 = st.sidebar.number_input("QR Top-Left X", 0, 3000, 542)
qr_y1 = st.sidebar.number_input("QR Top-Left Y", 0, 4000, 1453)
qr_x2 = st.sidebar.number_input("QR Bottom-Right X", 0, 3000, 1729)
qr_y2 = st.sidebar.number_input("QR Bottom-Right Y", 0, 4000, 2662)

text_y_top = st.sidebar.number_input("Text Y Top", 0, 4000, 2762)
text_y_bottom = st.sidebar.number_input("Text Y Bottom", 0, 4000, 2906)

# --- Buttons ---
col1, col2 = st.columns(2)
preview = col1.button("🔍 Preview First Card")
generate_all = col2.button("🚀 Generate All & Download ZIP")

# --- Process Once Inputs Are Valid ---
if template_file and csv_file and font_file:
    df = pd.read_csv(csv_file)
    font_bytes = font_file.read()
    font = ImageFont.truetype(io.BytesIO(font_bytes), font_size)

    def generate_card(row):
        room_number = f"ROOM NO: {row['Number']}"
        url = row['URL']

        template = Image.open(template_file).convert("RGB")
        draw = ImageDraw.Draw(template)

        qr = qrcode.make(url).resize((qr_x2 - qr_x1, qr_y2 - qr_y1))
        template.paste(qr, (qr_x1, qr_y1))

        # Draw text centered horizontally at y center
        bbox = draw.textbbox((0, 0), room_number, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_y_center = (text_y_top + text_y_bottom) // 2
        x_center = template.width // 2

        draw.text(
            (x_center - text_width // 2, text_y_center - text_height // 2),
            room_number,
            fill="white",
            font=font,
        )
        return template

    if preview:
        st.subheader("🖼️ Preview First Card")
        card_img = generate_card(df.iloc[0])
        st.image(card_img, use_container_width =True)

    if generate_all:
        st.subheader("📦 Download Generated Cards")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for _, row in df.iterrows():
                card = generate_card(row)
                img_bytes = io.BytesIO()
                card.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                zipf.writestr(f"{row['Number']}.png", img_bytes.read())
        zip_buffer.seek(0)

        st.success("✅ Cards generated successfully!")
        st.download_button(
            label="📥 Download ZIP",
            data=zip_buffer,
            file_name="qr_cards.zip",
            mime="application/zip",
        )
else:
    st.info("Upload template image, CSV file, and font to continue.")
