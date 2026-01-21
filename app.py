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

# Custom CSS to match the requested UI (Pinkish theme)
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #EAC7C7; /* Soft pink background */
    }
    
    /* Upload Drop Zone */
    [data-testid='stFileUploader'] {
        background-color: #F8EDED;
        border-radius: 20px;
        padding: 40px;
        border: 2px dashed #ffffff;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.4);
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Convert Button */
    div.stButton > button {
        background-color: #1A050A; /* Dark button color */
        color: white;
        border-radius: 30px;
        height: 60px;
        width: 100%;
        font-size: 20px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #3D101A;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.4);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #1A050A;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #1A050A;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Success Message */
    .stSuccess {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
    }
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
    # Centered Title (optional, can be removed if strictly following the minimal UI)
    # st.title("PDF to Image Converter")
    
    # Space for visual balance
    st.write("")
    st.write("")
    
    # 1. Drag and Drop Zone
    uploaded_files = st.file_uploader(
        "Drag-and drop zone", 
        type=['pdf'], 
        accept_multiple_files=True,
        label_visibility="visible" # Or "collapsed" if we want to hide the label text
    )

    # 2. Convert Button
    if st.button("Convert"):
        if not uploaded_files:
            st.warning("Please upload at least one PDF file.")
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
                    
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Run extraction logic
                    # We pass move_to_completed=False because we don't need to archive the temp file
                    try:
                        process_pdf(file_path, output_root=temp_output_dir, move_to_completed=False)
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")
                    
                    processed_count += 1
                    progress_bar.progress(int(processed_count / total_files * 100))

                # After all processing, zip the output
                status_text.text("Creating download archive...")
                
                zip_filename = "extracted_images.zip"
                zip_path = os.path.join(temp_input_dir, zip_filename) # Save zip in temp_input which is safe
                
                zip_directory(temp_output_dir, zip_path)
                
                # Read the zip file to bytes for download
                with open(zip_path, "rb") as f:
                    zip_data = f.read()
                
                # 3. Download Button (Appears after conversion)
                st.success("Conversion complete!")
                st.download_button(
                    label="Download Folder",
                    data=zip_data,
                    file_name="extracted_images.zip",
                    mime="application/zip",
                    type="primary" # Makes it stand out
                )
                
                # Clear progress
                # status_text.empty()
                # progress_bar.empty()

if __name__ == "__main__":
    main()
