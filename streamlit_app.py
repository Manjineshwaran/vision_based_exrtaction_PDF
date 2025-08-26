# import streamlit as st
# import os
# import tempfile
# from PIL import Image
# from main import process_pdf
# from src.config import Config

# # Page configuration
# st.set_page_config(
#     page_title="Document Layout Analyzer",
#     page_icon="📄",
#     layout="wide"
# )

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 3rem;
#         color: #1f77b4;
#         text-align: center;
#     }
#     .entity-button {
#         width: 100%;
#         margin-bottom: 10px;
#     }
#     .image-grid {
#         display: grid;
#         grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
#         gap: 10px;
#         margin-top: 20px;
#     }
#     .image-container {
#         border: 1px solid #ddd;
#         border-radius: 5px;
#         padding: 5px;
#         text-align: center;
#     }
# </style>
# """, unsafe_allow_html=True)

# # App title
# st.markdown('<h1 class="main-header">Document Layout Analyzer</h1>', unsafe_allow_html=True)

# # File upload
# uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

# if uploaded_file is not None:
#     # Save uploaded file to temporary location
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#         tmp_file.write(uploaded_file.getvalue())
#         pdf_path = tmp_file.name
    
#     # Process button
#     if st.button("Analyze Document Layout", type="primary"):
#         with st.spinner("Processing document..."):
#             # Process the PDF
#             entities = process_pdf(pdf_path)
            
#             # Store in session state
#             st.session_state.entities = entities
#             st.session_state.processed = True
    
#     # Display results if processing is complete
#     if hasattr(st.session_state, 'processed') and st.session_state.processed:
#         st.success("Document processing complete!")
        
#         # Create buttons for each entity type
#         entity_types = sorted(st.session_state.entities.keys())
        
#         # Display entity type buttons
#         cols = st.columns(4)
#         for i, entity_type in enumerate(entity_types):
#             with cols[i % 4]:
#                 if st.button(
#                     f"{entity_type} ({len(st.session_state.entities[entity_type])})", 
#                     key=f"btn_{entity_type}",
#                     use_container_width=True
#                 ):
#                     st.session_state.selected_entity = entity_type
        
#         # Display images for selected entity type
#         if hasattr(st.session_state, 'selected_entity'):
#             st.subheader(f"{st.session_state.selected_entity} Entities")
            
#             # Create image grid
#             st.markdown('<div class="image-grid">', unsafe_allow_html=True)
            
#             entity_files = st.session_state.entities[st.session_state.selected_entity]
#             for img_path in entity_files:
#                 try:
#                     img = Image.open(img_path)
#                     st.image(img, caption=os.path.basename(img_path), use_column_width=True)
#                 except Exception as e:
#                     st.error(f"Error loading image {img_path}: {e}")
            
#             st.markdown('</div>', unsafe_allow_html=True)
    
#     # Clean up temporary file
#     os.unlink(pdf_path)
# else:
#     st.info("Please upload a PDF document to begin analysis.")

# # Footer
# st.markdown("---")
# st.markdown("### How to use:")
# st.markdown("""
# 1. Upload a PDF document
# 2. Click the 'Analyze Document Layout' button
# 3. Click on any entity type button to view extracted elements
# """)

import streamlit as st
import time
import os
import tempfile
from PIL import Image
from main import process_pdf
from src.config import Config

# Page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="Document Layout Analyzer",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'progress' not in st.session_state:
    st.session_state.progress = {
        'current_page': 0,
        'total_pages': 0,
        'items_extracted': 0,
        'status': 'Ready',
        'page_entities': {},
        'all_entities': {}
    }

# Version info for diagnostics
try:
    import torch
    import ultralytics as _ul
    _ultralytics_ver = getattr(_ul, "__version__", "unknown")
    # st.sidebar.info(f"torch: {getattr(torch, '__version__', 'unknown')} | ultralytics: {_ultralytics_ver}")
except Exception as _e:
    st.sidebar.warning(f"Version check failed: {_e}")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
    }
    .entity-button {
        width: 100%;
        margin-bottom: 10px;
    }
    .image-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr); /* 2 columns = half screen each */
        gap: 10px;
        margin-top: 20px;
        width: 80%;
        margin-left: auto;
        margin-right: auto;
    }
    .image-container {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 5px;
        text-align: center;
    }
    /* Force images to respect grid sizing */
    .stImage {
        width: 100% !important;
        max-width: 100% !important;
        display: block !important;
    }
    .stImage img {
        width: 100% !important;
        height: auto !important;
        max-width: 100% !important;
        object-fit: contain !important;
        border-radius: 5px;
        display: block !important;
    }
    /* Ensure grid items don't overflow and maintain quarter size */
    .image-grid > div {
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden !important;
        min-width: 0 !important;
    }
    /* Additional constraint for Streamlit image containers */
    .stImage > div {
        width: 20% !important;
        max-width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">Document Layout Analyzer</h1>', unsafe_allow_html=True)

# Global variable to store progress updates
progress_data = {
    'current_page': 0,
    'total_pages': 0,
    'items_extracted': 0,
    'status': 'Ready',
    'page_entities': {},
    'all_entities': {}
}

def update_progress(data):
    """Callback function to update progress during processing"""
    global progress_data
    progress_data.update({
        'current_page': data.get('current_page', 0),
        'total_pages': data.get('total_pages', 0),
        'items_extracted': data.get('items_extracted', 0),
        'status': data.get('status', 'Processing...'),
        'page_entities': data.get('page_entities', {}),
        'all_entities': data.get('all_entities', {})
    })

def process_pdf_file(uploaded_file):
    """Process the uploaded PDF file"""
    pdf_path = None
    try:
        # Create a temporary file and ensure it's closed after writing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            pdf_path = tmp_file.name
        
        # Process the PDF with progress callback
        entities = process_pdf(pdf_path, progress_callback=update_progress)
        
        # Update global progress with final state
        update_progress({
            'status': 'Processing complete!',
            'all_entities': entities
        })
        
        # Store results in session state (this will be picked up in the main thread)
        st.session_state.entities = entities
        st.session_state.processed = True
        
    except Exception as e:
        error_msg = str(e)
        update_progress({
            'status': f'Error: {error_msg}'
        })
        print(f"Error processing PDF: {error_msg}")
    finally:
        # Clean up temporary file if it was created
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.unlink(pdf_path)
            except Exception as e:
                print(f"Warning: Could not delete temporary file: {e}")
        
        # Update processing state
        st.session_state.processing = False

# Main UI
st.title("Document Layout Analyzer")

# File upload
uploaded_file = st.file_uploader("Upload a PDF document", type="pdf", disabled=st.session_state.processing)

if uploaded_file is not None and not st.session_state.get('processing', False):
    # Initialize processing state
    st.session_state.processing = True
    
    # Reset progress data
    update_progress({
        'current_page': 0,
        'total_pages': 0,
        'items_extracted': 0,
        'status': 'Starting processing...',
        'page_entities': {},
        'all_entities': {}
    })
    
    # Start processing in a separate thread
    import threading
    thread = threading.Thread(
        target=process_pdf_file, 
        args=(uploaded_file,),
        daemon=True  # Make thread a daemon so it doesn't block program exit
    )
    thread.start()
    
    # Store the thread in session state to prevent garbage collection
    st.session_state.processing_thread = thread
    
    # Process button
    if st.button("Analyze Document Layout", type="primary"):
        with st.spinner("Processing document..."):
            # Process the PDF
            try:
                entities = process_pdf(pdf_path)
            except Exception as e:
                import traceback, sys
                st.error(f"Model load/processing failed: {e}")
                tb = "".join(traceback.format_exception(*sys.exc_info()))
                st.code(tb[:4000])
                st.stop()
            
            # Store in session state
            st.session_state.entities = entities
            st.session_state.processed = True
    
    # Display results if processing is complete
    if hasattr(st.session_state, 'processed') and st.session_state.processed:
        st.success("Document processing complete!")
        
        # Create buttons for each entity type
        entity_types = sorted(st.session_state.entities.keys())
        
        # Display entity type buttons and Detections button
        cols = st.columns(5)  # Changed from 4 to 5 to accommodate the new button
        
        # Add entity type buttons
        for i, entity_type in enumerate(entity_types):
            with cols[i % 4]:  # Still use 4 columns for entity buttons
                if st.button(
                    f"{entity_type} ({len(st.session_state.entities[entity_type])})", 
                    key=f"btn_{entity_type}",
                    use_container_width=True
                ):
                    st.session_state.selected_entity = entity_type
        
        # Add Detections button in the 5th column
        with cols[4]:  # 5th column for Detections button
            if st.button(
                "Detections",
                key="btn_detections",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.selected_entity = "detections"
        
        # Display content based on selection
        if hasattr(st.session_state, 'selected_entity'):
            if st.session_state.selected_entity == "detections":
                st.subheader("Detection Results")
                detection_dir = os.path.join(os.getcwd(), "detections")
                
                if os.path.exists(detection_dir):
                    # Find all predict* folders and sort them
                    predict_folders = sorted([f for f in os.listdir(detection_dir) 
                                           if os.path.isdir(os.path.join(detection_dir, f)) 
                                           and f.startswith('predict')])
                    
                    if predict_folders:
                        st.markdown('<div class="image-grid">', unsafe_allow_html=True)
                        
                        for folder in predict_folders:
                            folder_path = os.path.join(detection_dir, folder)
                            # Look for image files in the folder
                            image_files = [f for f in os.listdir(folder_path) 
                                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                            
                            if image_files:
                                # Take the first image in each predict folder
                                img_path = os.path.join(folder_path, image_files[0])
                                try:
                                    img = Image.open(img_path)
                                    # Reduce image size by using a smaller width
                                    st.image(img, caption=f"{folder} - {os.path.basename(img_path)}", width=600)
                                except Exception as e:
                                    st.error(f"Error loading image {img_path}: {e}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning("No prediction folders found in the detections directory.")
                else:
                    st.warning("Detections directory not found.")
            else:
                # Original entity display code
                st.subheader(f"{st.session_state.selected_entity} Entities")
                st.markdown('<div class="image-grid">', unsafe_allow_html=True)
                
                entity_files = st.session_state.entities[st.session_state.selected_entity]
                for img_path in entity_files:
                    try:
                        img = Image.open(img_path)
                        st.image(img, caption=os.path.basename(img_path), use_column_width=True)
                    except Exception as e:
                        st.error(f"Error loading image {img_path}: {e}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Processing is handled in the background
    pass
else:
    st.info("Please upload a PDF document to begin analysis.")
    
    # Reset processing state if no file is uploaded
    if 'processed' in st.session_state:
        del st.session_state.processed
    if 'entities' in st.session_state:
        del st.session_state.entities
    if 'processing' in st.session_state:
        del st.session_state.processing

# Footer
st.markdown("---")
st.markdown("### How to use:")
st.markdown("""
1. Upload a PDF document
2. Click the 'Analyze Document Layout' button
3. Click on any entity type button to view extracted elements
""")
