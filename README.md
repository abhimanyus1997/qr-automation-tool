# ✨ QR Code Card Generator ✨

This Streamlit application allows you to generate beautiful cards with unique QR codes and text. You can upload your own template, a CSV file with data, and customize the layout to create personalized cards in bulk.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

## 🚀 Features

-   **Bulk Card Generation**: Create hundreds or thousands of unique cards from a single template and a CSV file.
-   **Customizable Template**: Use your own PNG image as a background template.
-   **Auto-Resolution Correction**: Automatically resize the template to a recommended resolution of 2272x3200 for best results.
-   **Dynamic QR Codes**: Generate a unique QR code for each card based on data from your CSV file.
-   **Custom Text**: Add custom text to each card, with adjustable font size, color, and background.
-   **Logo Integration**: Add your own logo to the cards.
-   **Live Preview**: Preview your cards in real-time before generating all of them.
-   **Easy Download**: Download all generated cards as a single ZIP file.

## 🛠️ How to Use

1.  **Install the requirements**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the app**:
    ```bash
    streamlit run streamlit_app.py
    ```
3.  **Upload your files**:
    -   **Template Image**: A PNG image to be used as the card background.
    -   **Data CSV**: A CSV file with `ID`, `Text`, and `URL` columns.
    -   **Font File (Optional)**: A `.ttf` font file.
    -   **Logo File (Optional)**: A PNG image for your logo.
4.  **Customize the layout**:
    -   Use the controls in the sidebar to adjust the position and appearance of the QR code, text, and logo.
5.  **Generate and download**:
    -   Preview your cards using the "Preview" buttons.
    -   Click "Generate All" to create all the cards and download them as a ZIP file.

## 🎨 Customization

The sidebar offers a variety of options to customize your cards:

-   **File Uploads**: Upload your template, CSV, font, and logo.
-   **Layout & Style**: Adjust font size, text prefix, text color, and background color.
-   **Position Elements**: Fine-tune the position of the QR code, text, and logo on the card.
-   **Guides**: Toggle layout guides to help with positioning.