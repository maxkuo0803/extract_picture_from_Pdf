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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, Helvetica, Arial, sans-serif;
        background-color: #ffffff !important; /* Force white background */
        color: #000000 !important; /* Force black text */
    }

    /* Main Container */
    .stApp {
        background-color: #ffffff !important;
    }

    /* Header Styling */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: #000000 !important;
        margin-bottom: 0.5em;
    }
    
    p, label, span {
        font-weight: 500 !important;
        color: #333333 !important; /* Dark gray for body text to ensure readability */
        font-size: 1.1em !important;
    }

    /* File Uploader - elegant drop zone */
    [data-testid='stFileUploader'] {
        background-color: #f5f5f7 !important; /* Light gray background for contrast against white page */
        border-radius: 18px;
        padding: 30px;
        border: 2px dashed #d2d2d7;
    }
    
    /* Force text color inside uploader */
    [data-testid='stFileUploader'] section, 
    [data-testid='stFileUploader'] div,
    [data-testid='stFileUploader'] label {
        color: #000000 !important;
    }
    
    [data-testid='stFileUploader']:hover {
        border-color: #0071e3;
        background-color: #f0f0f5 !important;
    }
    
    /* Buttons - iOS Style */
    div.stButton > button {
        background-color: #0071e3 !important; /* iOS Blue */
        color: white !important;
        border-radius: 12px;
        height: 55px;
        font-size: 18px !important;
        font-weight: 600 !important;
        border: none;
        width: 100%;
        margin-top: 20px;
    }
    
    div.stButton > button:hover {
        background-color: #0077ED !important;
        color: white !important;
    }
    
    /* Secondary Button (Download) */
    div.stDownloadButton > button {
        background-color: #ffffff !important;
        color: #0071e3 !important;
        border: 2px solid #0071e3 !important;
        border-radius: 12px;
        height: 55px;
        font-size: 18px !important;
        font-weight: 600 !important;
        width: 100%;
    }

    div.stDownloadButton > button:hover {
        background-color: #f5f9ff !important;
    }
    
    /* Fix for drag label specifically */
    .st-emotion-cache-1gulkj5 {
       color: #000000 !important; 
    }

    /* Remove default streamlit branding hooks if possible */
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
