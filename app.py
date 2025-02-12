import os
import streamlit as st
import subprocess
import markdown
from datetime import datetime

# Application Constants
APP_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of app.py
TEMPLATE_FILE = os.path.join(APP_DIR, "resume_template.md")  # Path to the template file
SAVE_DIR = APP_DIR  # Save files in the same folder as app.py
os.makedirs(SAVE_DIR, exist_ok=True)  # Create the directory if it doesn't exist 

def load_template(template_path):
    """Loads the resume template from an external file."""
    try:
        with open(template_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        st.sidebar.warning("Template file not found. Using a default placeholder.")
        return "# Default Resume Template\n\nAdd your content here."
    except Exception as error:
        st.sidebar.error(f"⚠️ Oops! Something went wrong while loading the template: {str(error)}")
        return "# Error Loading Template"

def configure_styles():
    """Sets up custom visual styling with professional color palette"""
    st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f9;
            color: #333;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Configure page and styles
    st.set_page_config(layout="wide", page_icon="📄", page_title="Professional Resume Builder")
    configure_styles()

    # Load the default template
    DEFAULT_TEMPLATE = load_template(TEMPLATE_FILE)

    # Initialize session state
    if 'resume_content' not in st.session_state:
        st.session_state.resume_content = DEFAULT_TEMPLATE
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

    # Main header
    st.title("Professional Resume Builder")
    st.caption("Create • Preview • Download - All in Real Time")

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

    # Save Markdown File Locally
    if st.button("📥 Save Markdown (.md)", use_container_width=True):
        if st.session_state.resume_content.strip():
            md_file_path = os.path.join(SAVE_DIR, md_file_name)
            try:
                with open(md_file_path, "w") as f:
                    f.write(st.session_state.resume_content)
                st.success(f"Markdown file saved locally at: {md_file_path}")
            except Exception as error:
                st.error(f"⚠️ Oops! Something went wrong: {str(error)}")
        else:
            st.warning("Please add your resume content before saving.")

    # Save PDF File Locally
    if st.button("📥 Save PDF (.pdf)", type="primary", use_container_width=True):
        if st.session_state.resume_content.strip():
            pdf_file_path = os.path.join(SAVE_DIR, pdf_file_name)
            temp_md_path = os.path.join(SAVE_DIR, "temp_resume.md")
            try:
                # Save Markdown content temporarily
                with open(temp_md_path, "w") as f:
                    f.write(st.session_state.resume_content)
                # Generate PDF
                subprocess.run(
                    ["pandoc", temp_md_path, "-o", pdf_file_path],
                    check=True
                )
                st.success(f"PDF file saved locally at: {pdf_file_path}")
                # Cleanup temporary Markdown file
                os.remove(temp_md_path)
            except Exception as error:
                st.error(f"⚠️ Oops! Something went wrong: {str(error)}")
        else:
            st.warning("Please add your resume content before saving.")

if __name__ == "__main__":
    main()
