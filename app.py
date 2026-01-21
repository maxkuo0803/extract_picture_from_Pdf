import streamlit as st
import os
import tempfile
import shutil
import zipfile
from extract_images import process_pdf

# Set page configuration
st.set_page_config(
    page_title="PDF Image Extractor",
    page_icon="📷",
    layout="centered"
)

# Apple-inspired Design System (CSS)
st.markdown("""
    <style>
    /* Global Reset & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, Helvetica, Arial, sans-serif;
        color: #1d1d1f;
        background-color: #f5f5f7; /* Apple Light Gray Background */
    }

    /* Main Container */
    .stApp {
        background-color: #f5f5f7;
    }

    /* Header Styling */
    h1 {
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #1d1d1f;
        margin-bottom: 0.5em;
    }
    
    p {
        font-weight: 400;
        color: #86868b; /* Apple Subtitle Gray */
        font-size: 1.1em;
    }

    /* File Uploader - elegant drop zone */
    [data-testid='stFileUploader'] {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 30px;
        border: 1px solid #d2d2d7;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    
    [data-testid='stFileUploader']:hover {
        border-color: #0071e3; /* iOS Blue Focus */
        box-shadow: 0 4px 16px rgba(0, 113, 227, 0.1);
    }
    
    /* Buttons - iOS Style */
    div.stButton > button {
        background-color: #0071e3; /* iOS Blue */
        color: white;
        border-radius: 980px; /* Pill shape */
        height: 50px;
        padding: 0 30px;
        font-size: 17px;
        font-weight: 500;
        border: none;
        box-shadow: none;
        transition: all 0.2s cubic-bezier(0.645, 0.045, 0.355, 1);
        width: 100%;
        margin-top: 10px;
    }
    
    div.stButton > button:hover {
        background-color: #0077ED; /* Slightly lighter on hover */
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
    }
    
    div.stButton > button:active {
        transform: scale(0.98);
        background-color: #006edb;
    }
    
    /* Secondary Button (Download) */
    div.stDownloadButton > button {
        background-color: #ffffff;
        color: #0071e3;
        border: 1px solid #0071e3;
        border-radius: 980px;
        height: 50px;
        font-size: 17px;
        font-weight: 500;
        width: 100%;
    }

    div.stDownloadButton > button:hover {
        background-color: #f5f9ff;
        border-color: #0071e3;
        color: #0071e3;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #0071e3;
    }

    /* Cards/Success Messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 14px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Remove default streamlit menu for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
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
    # Elegant Title Section
    st.title("Image Extractor")
    st.markdown("<p style='text-align: center; margin-top: -10px; margin-bottom: 40px;'>Effortlessly extract images from your PDF documents.</p>", unsafe_allow_html=True)
    
    # 1. Drag and Drop Zone
    uploaded_files = st.file_uploader(
        "Drop your PDF files here", 
        type=['pdf'], 
        accept_multiple_files=True,
        label_visibility="hidden"
    )

    # 2. Convert Button
    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} file{'s' if len(uploaded_files) > 1 else ''}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        convert_btn = st.button("Extract Images")

    if convert_btn:
        if not uploaded_files:
            st.warning("Please upload a PDF file first.")
        else:
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Create temporary directories for processing
            with tempfile.TemporaryDirectory() as temp_input_dir, \
                 tempfile.TemporaryDirectory() as temp_output_dir:
                
                # Save uploaded files to temp input
                pdf_paths = []
                
                total_files = len(uploaded_files)
                processed_count = 0
                
                for i, uploaded_file in enumerate(uploaded_files):
                    file_path = os.path.join(temp_input_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    status_text.markdown(f"<span style='color:#86868b'>Processing {uploaded_file.name}...</span>", unsafe_allow_html=True)
                    
                    # Run extraction logic
                    try:
                        process_pdf(file_path, output_root=temp_output_dir, move_to_completed=False)
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")
                    
                    processed_count += 1
                    progress_bar.progress(int(processed_count / total_files * 100))

                # After all processing, zip the output
                status_text.markdown("<span style='color:#0071e3'><b>All done! Preparing download...</b></span>", unsafe_allow_html=True)
                
                zip_filename = "extracted_images.zip"
                zip_path = os.path.join(temp_input_dir, zip_filename)
                
                zip_directory(temp_output_dir, zip_path)
                
                # Read the zip file to bytes for download
                with open(zip_path, "rb") as f:
                    zip_data = f.read()
                
                # 3. Download Button
                st.markdown("---")
                st.download_button(
                    label="Download All Images",
                    data=zip_data,
                    file_name="extracted_images.zip",
                    mime="application/zip",
                    type="primary"
                )

if __name__ == "__main__":
    main()
