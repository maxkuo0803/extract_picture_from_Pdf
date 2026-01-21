import streamlit as st
import os
import tempfile
import shutil
import zipfile
from extract_images import process_pdf

# Set page configuration
st.set_page_config(
    page_title="Glass Converter",
    page_icon="✨",
    layout="centered"
)

# Glassmorphism Design System (CSS)
st.markdown("""
    <style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%); /* Purple to Blue Gradient */
        background-attachment: fixed;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main "Glass" Card Container */
    /* Target the main content block to look like a card */
    .block-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        padding: 40px !important;
        margin-top: 40px;
        max-width: 700px;
    }

    /* Typography - Force White */
    h1, h2, h3, p, span, label, div {
        color: #ffffff !important;
    }
    
    h1 {
        font-weight: 700;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    
    p {
        text-align: center;
        opacity: 0.9;
        margin-bottom: 2rem;
    }

    /* File Uploader - Dashed Inner Zone */
    [data-testid='stFileUploader'] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed rgba(255, 255, 255, 0.4);
        border-radius: 16px;
        padding: 30px;
        transition: border 0.3s ease;
    }
    
    [data-testid='stFileUploader']:hover {
        border-color: #ffffff;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Default uploaded file list text styling */
    section[data-testid="stFileUploader"] div {
        color: white !important;
    }
    
    /* Buttons - Glass Buttons */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 50px;
        height: 50px;
        font-weight: 600;
        width: 100%;
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    div.stDownloadButton > button {
        background: #ffffff !important;
        color: #7c3aed !important; /* Matches gradient purple */
        border: none !important;
        border-radius: 50px;
        height: 50px;
        font-weight: 700 !important;
        width: 100%;
    }
    
    div.stDownloadButton > button:hover {
        background: #f3e8ff !important;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: white;
    }

    /* Remove Default Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

def main():
    # Header
    st.title("Glass Converter")
    st.markdown("<p>Transform your files instantly</p>", unsafe_allow_html=True)
    
    # 1. Drag and Drop Zone
    uploaded_files = st.file_uploader(
        "Click or drag file\nSupports PDF", 
        type=['pdf'], 
        accept_multiple_files=True,
        label_visibility="visible"
    )

    # 2. Convert Button
    
    # Spacing
    st.write("")
    
    if uploaded_files:
        st.markdown(f"<div style='text-align:center; margin-bottom:10px; opacity:0.8'>Ready to process {len(uploaded_files)} files</div>", unsafe_allow_html=True)
        
        if st.button("Convert Now"):
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Create temporary directories for processing
            with tempfile.TemporaryDirectory() as temp_input_dir, \
                 tempfile.TemporaryDirectory() as temp_output_dir:
                
                # Save uploaded files to temp input
                total_files = len(uploaded_files)
                processed_count = 0
                
                for i, uploaded_file in enumerate(uploaded_files):
                    file_path = os.path.join(temp_input_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    status_text.markdown(f"<p style='margin-bottom:0'>Processing {uploaded_file.name}...</p>", unsafe_allow_html=True)
                    
                    # Run extraction logic
                    try:
                        process_pdf(file_path, output_root=temp_output_dir, move_to_completed=False)
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")
                    
                    processed_count += 1
                    progress_bar.progress(int(processed_count / total_files * 100))

                # After all processing, zip the output
                status_text.markdown("<p style='font-weight:bold'>Success! Preparing download...</p>", unsafe_allow_html=True)
                
                zip_filename = "extracted_images.zip"
                zip_path = os.path.join(temp_input_dir, zip_filename)
                
                zip_directory(temp_output_dir, zip_path)
                
                # Read the zip file to bytes for download
                with open(zip_path, "rb") as f:
                    zip_data = f.read()
                
                # 3. Download Button
                st.write("")
                st.download_button(
                    label="Download Result",
                    data=zip_data,
                    file_name="extracted_images.zip",
                    mime="application/zip",
                    type="primary"
                )
    
    # Footer
    st.markdown("<p style='font-size: 0.8em; margin-top: 40px; letter-spacing: 2px; opacity: 0.6;'>SECURE • FAST • PRIVATE</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
