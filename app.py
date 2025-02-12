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
    """Sets up custom visual styling with a modern and professional look"""
    st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f9f9f9;
            color: #333;
        }
        .stButton button {
            background-color: #007bff;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
            transition: background-color 0.3s ease, transform 0.3s ease;
        }
        .stButton button:hover {
            background-color: #0056b3;
            transform: scale(1.05);
        }
        .stTextInput input, .stTextArea textarea {
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #007bff;
            box-shadow: 0 0 8px rgba(0, 123, 255, 0.2);
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #007bff;
        }
        .stMarkdown p {
            line-height: 1.6;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;
            border-right: 1px solid #ddd;
        }
        .stAlert {
            border-radius: 8px;
            padding: 15px;
        }
        .stAlert.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .stAlert.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Configure page and styles
    st.set_page_config(layout="wide", page_icon="📄", page_title="Professional Resume Builder")
    configure_styles()

    # Main header
    st.title("📝 Professional Resume Builder")
    st.caption("Create • Preview • Download - All in Real Time")

    # Initialize session state
    if 'resume_content' not in st.session_state:
        st.session_state.resume_content = DEFAULT_TEMPLATE
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
    if 'pdf_generated' not in st.session_state:
        st.session_state.pdf_generated = False

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
            <small style="color: #888;">Last updated: {st.session_state.last_update}</small>
            """
        else:
            preview_content = f"""
            Your formatted preview will appear here...
            <small style="color: #888;">Last updated: {st.session_state.last_update}</small>
            """
        preview_display.markdown(preview_content, unsafe_allow_html=True)

    # Export Section
    st.divider()
    st.subheader("💾 Save and Download Your Resume")

    # Custom File Name Input
    file_name = st.text_input("Enter a custom file name (without extension):", value="resume")
    md_file_name = f"{file_name}.md"
    pdf_file_name = f"{file_name}.pdf"

    # Save Button
    if st.button("💾 Save & Generate PDF", use_container_width=True):
        if st.session_state.resume_content.strip():
            try:
                # Save Markdown Locally
                md_file_path = os.path.join(SAVE_DIR, md_file_name)
                with open(md_file_path, "w") as f:
                    f.write(st.session_state.resume_content)
                st.success(f"Markdown file saved locally at: {md_file_path}")

                # Generate PDF Locally
                pdf_file_path = os.path.join(SAVE_DIR, pdf_file_name)
                temp_md_path = os.path.join(SAVE_DIR, "temp_resume.md")
                with open(temp_md_path, "w") as f:
                    f.write(st.session_state.resume_content)
                subprocess.run(
                    ["pandoc", temp_md_path, "-o", pdf_file_path],
                    check=True
                )
                st.success(f"PDF file generated locally at: {pdf_file_path}")
                st.session_state.pdf_generated = True  # Mark PDF as generated

                # Cleanup temporary Markdown file
                os.remove(temp_md_path)
            except Exception as error:
                st.error(f"⚠️ Oops! Something went wrong: {str(error)}")
        else:
            st.warning("Please add your resume content before saving.")

    # Download Button (Appears Only After Saving)
    if st.session_state.pdf_generated:
        pdf_file_path = os.path.join(SAVE_DIR, pdf_file_name)
        try:
            with open(pdf_file_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            st.download_button(
                label="📥 Download PDF (.pdf)",
                data=pdf_data,
                file_name=pdf_file_name,
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as error:
            st.error(f"⚠️ Failed to load PDF for download: {str(error)}")

if __name__ == "__main__":
    main()
