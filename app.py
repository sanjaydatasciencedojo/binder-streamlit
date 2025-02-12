import os
import streamlit as st
import subprocess
import markdown
from datetime import datetime

# Application Constants
SAVE_DIR = "/home/jovyan/streamlit"  # Directory to save files on the server
os.makedirs(SAVE_DIR, exist_ok=True)  # Create the directory if it doesn't exist 

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
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f9;
            color: #333;
        }
        .stButton button {
            background-color: #007bff;
            color: white;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .stButton button:hover {
            background-color: #0056b3;
        }
        .stTextInput input {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 8px;
        }
        .stTextArea textarea {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 8px;
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

    # Create two-column layout with better proportions
    edit_col, preview_col = st.columns([2, 3], gap="large")  # Adjusted column widths for better focus 

    # Editor Column
    with edit_col:
        st.subheader("📝 Write Your Resume Content")
        st.session_state.resume_content = st.text_area(
            "",
            value=st.session_state.resume_content,
            height=500,  # Reduced height for better scrolling experience
            key="content_editor",
            help="Start typing to see instant preview. Use Markdown formatting for best results."
        )
        # Update button for preview
        if st.button("🔄 Update Preview", key="refresh"):
            st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

    # Preview Column
    with preview_col:
        st.subheader("🔍 Live Preview")
        preview_display = st.empty()
        if st.session_state.resume_content.strip():
            html_content = markdown.markdown(st.session_state.resume_content)
            preview_content = f"""
            {html_content}
            Last updated: {st.session_state.last_update}
            """
        else:
            preview_content = f"""
            Your formatted preview will appear here...
            Last updated: {st.session_state.last_update}
            """
        preview_display.markdown(preview_content, unsafe_allow_html=True)

    # Export Section
    st.divider()
    st.subheader("💾 Save or Download Your Resume")

    # Custom File Name Input
    file_name = st.text_input("Enter a custom file name (without extension):", value="resume")
    md_file_name = f"{file_name}.md"
    pdf_file_name = f"{file_name}.pdf"

    # Save Markdown File Locally and on Server
    if st.button("📥 Save Markdown (.md)", use_container_width=True):
        if st.session_state.resume_content.strip():
            md_file_path = os.path.join(SAVE_DIR, md_file_name)
            # Check if file already exists
            if os.path.exists(md_file_path):
                overwrite = st.checkbox(f"A file named '{md_file_name}' already exists. Overwrite?")
                if overwrite:
                    with open(md_file_path, "w") as f:
                        f.write(st.session_state.resume_content)
                    st.success(f"Markdown file overwritten on the server at: {md_file_path}")
                else:
                    st.info("Operation canceled. Please choose a different file name.")
            else:
                with open(md_file_path, "w") as f:
                    f.write(st.session_state.resume_content)
                st.success(f"Markdown file saved on the server at: {md_file_path}")
        else:
            st.warning("Please add your resume content before saving.")

    # Save PDF File Locally and on Server
    if st.button("📥 Save PDF (.pdf)", type="primary", use_container_width=True):
        if st.session_state.resume_content.strip():
            try:
                pdf_file_path = os.path.join(SAVE_DIR, pdf_file_name)
                # Check if file already exists
                if os.path.exists(pdf_file_path):
                    overwrite = st.checkbox(f"A file named '{pdf_file_name}' already exists. Overwrite?")
                    if overwrite:
                        with st.status("Creating Your Resume...", expanded=True):
                            # Save Markdown content temporarily
                            temp_md_path = os.path.join(SAVE_DIR, "temp_resume.md")
                            with open(temp_md_path, "w") as f:
                                f.write(st.session_state.resume_content)
                            # Generate PDF
                            subprocess.run(
                                ["pandoc", temp_md_path, "-o", pdf_file_path],
                                check=True
                            )
                            st.success(f"PDF file overwritten on the server at: {pdf_file_path}")
                            # Cleanup temporary Markdown file
                            os.remove(temp_md_path)
                    else:
                        st.info("Operation canceled. Please choose a different file name.")
                else:
                    with st.status("Creating Your Resume...", expanded=True):
                        # Save Markdown content temporarily
                        temp_md_path = os.path.join(SAVE_DIR, "temp_resume.md")
                        with open(temp_md_path, "w") as f:
                            f.write(st.session_state.resume_content)
                        # Generate PDF
                        subprocess.run(
                            ["pandoc", temp_md_path, "-o", pdf_file_path],
                            check=True
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
