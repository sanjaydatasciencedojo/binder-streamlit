import os
import streamlit as st
import subprocess
import markdown
from datetime import datetime

# Application Constants
INPUT_FILE = "resume.md"
OUTPUT_FILE = "professional_resume.pdf"
SAVE_DIR = "/home/jovyan/streamlit"  # Directory to save files on the server
os.makedirs(SAVE_DIR, exist_ok=True)  # Create the directory if it doesn't exist <button class="citation-flag" data-index="5">

DEFAULT_TEMPLATE = """# Your Full Name
## Professional Title
### Core Skills
- Project Management, Team Leadership
- Technical Writing, Data Analysis
- Software Development, Cloud Solutions
### Work Experience
**Senior Developer**, Tech Innovations (2020-Present)
- Led team of 15+ developers
- Implemented automated deployment systems
- Designed cloud architecture solutions
**Junior Developer**, Startup Hub (2018-2020)
- Developed customer-facing web applications
- Managed database optimization
### Education
**Computer Science Degree**  
University of Technology (2014-2018)  
Dean's List: 6 Semesters
"""

def configure_styles():
    """Sets up custom visual styling with professional color palette"""
    st.markdown("""
        <style>
            :root {
                --primary: #2A5C82;    /* Professional Navy */
                --secondary: #4B8BB9;  /* Trustworthy Blue */
                --accent: #F5A623;     /* Confidence Gold */
                --light: #F0F4F8;      /* Clean Background */
                --dark: #1A2B3C;       /* Readable Text */
            }
            
            /* Main header styling */
            h1 {
                color: var(--primary) !important;
                border-bottom: 3px solid var(--secondary);
                padding-bottom: 0.8rem;
            }
            
            /* Editor styling */
            .stTextArea textarea {
                border: 2px solid var(--primary) !important;
                border-radius: 8px !important;
                padding: 1.5rem !important;
                background: var(--light) !important;
                color: var(--dark) !important;
                min-height: calc(100vh - 250px) !important;
            }
            
            /* Preview panel styling */
            .preview-panel {
                height: calc(100vh - 220px);
                overflow-y: auto;
                background: var(--light);
                border: 2px solid var(--primary);
                border-radius: 8px;
                padding: 2rem;
                margin-top: 1rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            /* Button styling */
            .stButton>button {
                background: var(--secondary) !important;
                color: white !important;
                border: none !important;
                transition: all 0.3s ease;
                font-weight: 500 !important;
            }
            
            .stButton>button:hover {
                background: var(--primary) !important;
                transform: translateY(-1px);
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            }
            
            /* Skill bullets coloring */
            ul li::marker {
                color: var(--accent) !important;
            }
            
            /* Section headers in preview */
            h1, h2, h3 {
                color: var(--primary) !important;
                margin-top: 1.5rem !important;
            }
            
            /* Timestamp styling */
            .refresh-time {
                color: var(--secondary);
                font-size: 0.85rem;
                margin-top: 1rem;
                text-align: right;
            }
            
            /* Company names in experience */
            strong {
                color: var(--dark);
            }
        </style>
    """, unsafe_allow_html=True)

def main():
    # Configure page and styles
    st.set_page_config(layout="wide", page_icon="📄", page_title="Professional Resume Builder")
    configure_styles()
    
    # Main header
    st.title("Professional Resume Builder")
    st.caption("Create • Preview • Download - All in Real Time")
    
    # Initialize session state
    if 'resume_content' not in st.session_state:
        st.session_state.resume_content = DEFAULT_TEMPLATE
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
    
    # Create two-column layout
    edit_col, preview_col = st.columns([1, 1], gap="large")
    
    # Editor Column
    with edit_col:
        st.session_state.resume_content = st.text_area(
            "Write your resume content:",
            value=st.session_state.resume_content,
            height=650,
            key="content_editor",
            help="Start typing to see instant preview. Use Markdown formatting for best results."
        )
    
    # Preview Column
    with preview_col:
        # Header with refresh button
        header_col, _ = st.columns([2, 5])
        with header_col:
            if st.button("🔄 Update Preview", key="refresh"):
                st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
        
        # Preview content
        preview_display = st.empty()
        if st.session_state.resume_content.strip():
            html_content = markdown.markdown(st.session_state.resume_content)
            preview_content = f"""
                <div class="preview-panel">
                    {html_content}
                    <div class="refresh-time">Last updated: {st.session_state.last_update}</div>
                </div>
            """
        else:
            preview_content = f"""
                <div class="preview-panel" style='color:var(--secondary); font-style:italic;'>
                    Your formatted preview will appear here...
                    <div class="refresh-time">Last updated: {st.session_state.last_update}</div>
                </div>
            """
        
        preview_display.markdown(preview_content, unsafe_allow_html=True)
    
    # Export Section
    st.divider()
    st.subheader("Download or Save Files")
    
    # Save Markdown File Locally and on Server
    if st.button("📥 Save Markdown (.md)", use_container_width=True):
        if st.session_state.resume_content.strip():
            # Save locally
            st.download_button(
                label="⬇️ Save Markdown to Computer",
                data=st.session_state.resume_content,
                file_name="resume.md",
                mime="text/markdown"
            )
            
            # Save on server
            md_file_path = os.path.join(SAVE_DIR, "resume.md")
            with open(md_file_path, "w") as f:
                f.write(st.session_state.resume_content)
            st.success(f"Markdown file saved on the server at: {md_file_path}")
        else:
            st.warning("Please add your resume content before saving.")
    
    # Save PDF File Locally and on Server
    if st.button("📥 Save PDF (.pdf)", type="primary", use_container_width=True):
        if st.session_state.resume_content.strip():
            try:
                with st.status("Creating Your Resume...", expanded=True):
                    # Save Markdown content temporarily
                    temp_md_path = os.path.join(SAVE_DIR, "temp_resume.md")
                    with open(temp_md_path, "w") as f:
                        f.write(st.session_state.resume_content)
                    
                    # Generate PDF
                    pdf_file_path = os.path.join(SAVE_DIR, OUTPUT_FILE)
                    subprocess.run(
                        ["pandoc", temp_md_path, "-o", pdf_file_path],
                        check=True
                    )
                    
                    # Offer download
                    with open(pdf_file_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Save PDF to Computer",
                            data=f.read(),
                            file_name="professional_resume.pdf",
                            mime="application/pdf"
                        )
                    
                    st.success(f"PDF file saved on the server at: {pdf_file_path}")
                    
                    # Cleanup temporary Markdown file
                    os.remove(temp_md_path)
            except Exception as error:
                st.error(f"⚠️ Oops! Something went wrong: {str(error)}")
        else:
            st.warning("Please add your resume content before saving.")

if __name__ == "__main__":
    main()
