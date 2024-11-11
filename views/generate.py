import streamlit as st
import zipfile
import os
from io import BytesIO
from docx import Document as Document_compose
from docxcompose.composer import Composer

# File uploader for ZIP file
uploaded_zip = st.file_uploader("Upload a ZIP file containing DOCX files", type=["zip"])

if uploaded_zip:
    # Create a temporary directory to extract the ZIP file
    with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
        # Extract all the files into a temporary directory
        temp_dir = "extracted_files"
        os.makedirs(temp_dir, exist_ok=True)
        zip_ref.extractall(temp_dir)
        
        # Get all DOCX files in the extracted directory
        docx_files = [f for f in os.listdir(temp_dir) if f.endswith(".docx")]
        
        # Ensure there's at least one DOCX file
        if docx_files:
            # Sort files to ensure the first one is the master
            docx_files.sort()
            
            # Treat the first DOCX file as the master
            master_file = os.path.join(temp_dir, docx_files[0])
            master = Document_compose(master_file)
            composer = Composer(master)
            
            # Append the rest of the DOCX files
            for docx_file in docx_files[1:]:
                doc2 = Document_compose(os.path.join(temp_dir, docx_file))
                composer.append(doc2)
            
            # Save the merged document to a BytesIO object
            combined_doc_stream = BytesIO()
            composer.save(combined_doc_stream)
            combined_doc_stream.seek(0)
            
            # Provide a download button for the merged document
            st.download_button(
                label="Download Combined DOCX",
                data=combined_doc_stream,
                file_name="combined_referee_sheet.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            st.error("No DOCX files found in the ZIP archive.")
        
        # Clean up the temporary extracted files
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)