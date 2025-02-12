import os
import shutil
import streamlit as st
import subprocess
import markdown
from datetime import datetime

# Application Constants
APP_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of app.py
CSS_FILE_SOURCE = os.path.join(APP_DIR, "resume.css")  # Path to CSS file in the app directory
TEMPLATE_FILE = os.path.join(APP_DIR, "resume_template.md")  # Path to template file
SAVE_DIR = "/home/jovyan/streamlit"  # Save .md and .pdf files in a subfolder named "streamlit"
CSS_FILE_DESTINATION = os.path.join(SAVE_DIR, "resume.css")  # Destination path for CSS
os.makedirs(SAVE_DIR, exist_ok=True)  # Create the "streamlit" folder if it doesn't exist <button class="citation-flag" data-index="3">


def copy_css_on_startup():
    """Copies the CSS file to the target directory if it doesn't already exist."""
    if not os.path.exists(CSS_FILE_DESTINATION):
        try:
            shutil.copy2(CSS_FILE_SOURCE, CSS_FILE_DESTINATION)  # Copy file with metadata <button class="citation-flag" data-index="8">
            print(f"CSS file copied successfully to: {CSS_FILE_DESTINATION}")
        except FileNotFoundError:
            print("Source CSS file not found. Please ensure 'resume.css' exists in the app directory.")
        except Exception as error:
            print(f"⚠️ Oops! Something went wrong while copying the CSS file: {str(error)}")
    else:
        print("CSS file already exists in the target directory. Skipping copy.")


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


def load_css(css_path):
    """Loads CSS content from a file."""
    try:
        with open(css_path, "r") as css_file:
            return css_file.read()
    except FileNotFoundError:
        st.sidebar.warning("CSS file not found. Using default styles.")
        return ""
    except Exception as error:
        st.sidebar.error(f"⚠️ Oops! Something went wrong while loading CSS: {str(error)}")
        return ""


def configure_styles(css_content):
    """Applies the CSS content to the Streamlit app."""
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def initialize_session_state():
    """Initializes session state variables."""
    if 'resume_content' not in st.session_state:
        st.session_state.resume_content = load_template(TEMPLATE_FILE)
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")


def handle_import_export():
    """Handles file import/export functionality."""
    uploaded_file = st.sidebar.file_uploader("Import Markdown", type=["md"])
    if uploaded_file:
        st.session_state.resume_content = uploaded_file.read().decode("utf-8")
        st.sidebar.success("Markdown file imported successfully!")


def render_editor_column():
    """Renders the editor column."""
    st.subheader("📝 Write Your Resume Content")
    st.session_state.resume_content = st.text_area(
        "",
        value=st.session_state.resume_content,
        height=500,
        key="content_editor",
        help="Start typing to see instant preview. Use Markdown formatting for best results."
    )
    if st.button("🔄 Update Preview", key="refresh"):
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")


def render_preview_column(css_content):
    """Renders the preview column with CSS applied."""
    st.subheader("🔍 Live Preview")
    preview_display = st.empty()

    if st.session_state.resume_content.strip():
        html_content = markdown.markdown(st.session_state.resume_content)
        preview_content = f"""
        <style>
            {css_content}
        </style>
        {html_content}
        <small style="color: #888;">Last updated: {st.session_state.last_update}</small>
        """
    else:
        preview_content = f"""
        Your formatted preview will appear here...
        <small style="color: #888;">Last updated: {st.session_state.last_update}</small>
        """
    preview_display.markdown(preview_content, unsafe_allow_html=True)


def export_resume(file_name, css_path):
    """Handles exporting the resume as Markdown or PDF."""
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

    # Generate PDF and Provide Download Option
    if st.button("📥 Generate PDF (.pdf)", use_container_width=True):
        if st.session_state.resume_content.strip():
            pdf_file_path = os.path.join(SAVE_DIR, pdf_file_name)
            temp_md_path = os.path.join(SAVE_DIR, "temp_resume.md")
            try:
                with open(temp_md_path, "w") as f:
                    f.write(st.session_state.resume_content)
                subprocess.run(
                    ["pandoc", temp_md_path, "-o", pdf_file_path, "--css", css_path],
                    check=True
                )
                st.success(f"PDF file generated successfully at: {pdf_file_path}")

                # Provide Download Option
                with open(pdf_file_path, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_file,
                        file_name=pdf_file_name,
                        mime="application/pdf"
                    )
                os.remove(temp_md_path)
            except Exception as error:
                st.error(f"⚠️ Oops! Something went wrong: {str(error)}")
        else:
            st.warning("Please add your resume content before generating the PDF.")


def main():
    # Copy CSS file during program startup
    copy_css_on_startup()

    # Configure page and styles
    st.set_page_config(layout="wide", page_icon="📄", page_title="Professional Resume Builder")

    # Initialize session state
    initialize_session_state()

    # Sidebar for Customization Options
    st.sidebar.subheader("🎨 Import / Export")
    handle_import_export()

    # Load CSS content for embedding in the preview
    css_content = load_css(CSS_FILE_DESTINATION)

    # Apply CSS to Live Preview
    configure_styles(css_content)

    # Main header
    st.title("📝 Professional Resume Builder")
    st.caption("Create • Preview • Download - All in Real Time")

    # Create two-column layout
    edit_col, preview_col = st.columns([2, 3], gap="large")

    # Editor Column
    with edit_col:
        render_editor_column()

    # Preview Column
    with preview_col:
        render_preview_column(css_content)

    # Export Section
    st.divider()
    st.subheader("💾 Save or Download Your Resume")
    file_name = st.text_input("Enter a custom file name (without extension):", value="resume")
    export_resume(file_name, CSS_FILE_DESTINATION)


if __name__ == "__main__":
    main()
