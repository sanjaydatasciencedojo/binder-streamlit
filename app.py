import os
import shutil
import streamlit as st
import subprocess
import markdown
from datetime import datetime

# Application Constants
APP_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of app.py
TEMPLATE_FILE = os.path.join(APP_DIR, "resume_template.md")  # Path to template file
SAVE_DIR = "/home/jovyan/streamlit"  # Save .md and .pdf files in a subfolder named "streamlit"
os.makedirs(SAVE_DIR, exist_ok=True)  # Create the "streamlit" folder if it doesn't exist

def initialize_session_state():
    """Initializes session state variables."""
    if 'resume_content' not in st.session_state:
        st.session_state.resume_content = load_file(TEMPLATE_FILE)
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

def load_file(file_path, default_content="# Default Resume Template\n\nAdd your content here.", error_message="⚠️ Oops! Something went wrong while loading the file"):
    """Generic function to load file content."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        st.sidebar.warning("File not found. Using default content.")
        return default_content
    except Exception as error:
        st.sidebar.error(f"{error_message}: {str(error)}")
        return default_content

def save_file(file_path, content, success_message="File saved successfully.", error_message="⚠️ Oops! Something went wrong while saving the file"):
    """Generic function to save content to a file."""
    try:
        with open(file_path, "w") as file:
            file.write(content)
        st.sidebar.success(success_message)
    except Exception as error:
        st.sidebar.error(f"{error_message}: {str(error)}")

def handle_import_export():
    """Handles file import/export functionality."""
    uploaded_file = st.sidebar.file_uploader("Import Markdown", type=["md"])
    if uploaded_file:
        st.session_state.resume_content = uploaded_file.read().decode("utf-8")
        st.sidebar.success("Markdown file imported successfully!")

def configure_styling_options():
    """Configures styling options in the sidebar."""
    st.sidebar.subheader("⚙️ Styling Options")
    theme_color = st.sidebar.color_picker("Theme Color for Headers", "#9C5BDE", key="theme_color")  # Default purple
    font_family = st.sidebar.selectbox("Font Family", ["Arial", "Verdana", "华康宋体"], index=0)
    font_size = st.sidebar.selectbox("Font Size", [12, 16, 20], index=1)
    margin_top_bottom = st.sidebar.selectbox("Margin (Top & Bottom)", [0, 50, 100], index=1)
    margin_left_right = st.sidebar.selectbox("Margin (Left & Right)", [0, 50, 100], index=1)
    paragraph_spacing = st.sidebar.selectbox("Paragraph Spacing", [0, 25, 50], index=1)
    line_spacing = st.sidebar.selectbox("Line Spacing", [1, 1.5, 2], index=1)
    return {
        "theme_color": theme_color,
        "font_family": font_family,
        "font_size": font_size,
        "margin_top_bottom": margin_top_bottom,
        "margin_left_right": margin_left_right,
        "paragraph_spacing": paragraph_spacing,
        "line_spacing": line_spacing,
    }

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
        <div style="all: initial;">
            <style>{css_content}</style>
            {html_content}
        </div>
        Last updated: {st.session_state.last_update}
        """
    else:
        preview_content = f"""
        Your formatted preview will appear here...
        Last updated: {st.session_state.last_update}
        """
    preview_display.markdown(preview_content, unsafe_allow_html=True)

def export_resume(file_name, css_content):
    """Handles exporting the resume as Markdown or PDF."""
    md_file_name = f"{file_name}.md"
    pdf_file_name = f"{file_name}.pdf"
    # Save Markdown File Locally
    if st.button("📥 Save Markdown (.md)", use_container_width=True):
        if st.session_state.resume_content.strip():
            save_file(
                os.path.join(SAVE_DIR, md_file_name),
                st.session_state.resume_content,
                success_message=f"Markdown file saved locally at: {os.path.join(SAVE_DIR, md_file_name)}"
            )
        else:
            st.warning("Please add your resume content before saving.")
    # Generate PDF and Provide Download Option
    if st.button("📥 Generate PDF (.pdf)", use_container_width=True):
        if st.session_state.resume_content.strip():
            temp_md_path = os.path.join(SAVE_DIR, "temp_resume.md")
            pdf_file_path = os.path.join(SAVE_DIR, pdf_file_name)
            try:
                # Embed CSS into Markdown content
                styled_html = f"<style>{css_content}</style>\n{markdown.markdown(st.session_state.resume_content)}"
                save_file(temp_md_path, styled_html)  # Save styled HTML as Markdown
                subprocess.run(
                    ["pandoc", temp_md_path, "-o", pdf_file_path],
                    check=True
                )
                st.success(f"PDF file generated successfully at: {pdf_file_path}")
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
    # Configure page and styles
    st.set_page_config(layout="wide", page_icon="📄", page_title="Professional Resume Builder")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for Customization Options
    st.sidebar.subheader("🎨 Import / Export")
    handle_import_export()
    
    # Configure Styling Options
    styling_options = configure_styling_options()
    
    # Dynamically generate inline CSS based on user inputs
    inline_css = f"""
    body {{
        background-color: #ffffff !important;
        color: #333333 !important;
        font-family: '{styling_options['font_family']}', sans-serif !important;
        font-size: {styling_options['font_size']}px !important;
        line-height: {styling_options['line_spacing']} !important;
        margin-top: {styling_options['margin_top_bottom']}px !important;
        margin-bottom: {styling_options['margin_top_bottom']}px !important;
        margin-left: {styling_options['margin_left_right']}px !important;
        margin-right: {styling_options['margin_left_right']}px !important;
    }}
    h1, h2, h3 {{
        color: {styling_options['theme_color']} !important;
        font-weight: bold !important;
        margin-top: 20px !important;
        margin-bottom: 10px !important;
    }}
    p {{
        margin-bottom: {styling_options['paragraph_spacing']}px !important;
        text-align: justify !important;
    }}
    a {{
        color: #1E90FF !important;
        text-decoration: none !important;
    }}
    a:hover {{
        color: #FF4500 !important;
        text-decoration: underline !important;
    }}
    ul, ol {{
        margin-left: 20px !important;
        margin-bottom: 20px !important;
    }}
    li {{
        margin-bottom: 10px !important;
    }}
    table {{
        width: 100% !important;
        border-collapse: collapse !important;
        margin-bottom: 20px !important;
    }}
    th, td {{
        border: 1px solid #ddd !important;
        padding: 8px !important;
        text-align: left !important;
    }}
    th {{
        background-color: #f4f4f4 !important;
        color: #333333 !important;
    }}
    pre {{
        background-color: #f4f4f4 !important;
        padding: 10px !important;
        border-radius: 5px !important;
        overflow-x: auto !important;
        font-family: monospace !important;
        font-size: 14px !important;
        margin-bottom: 20px !important;
    }}
    code {{
        background-color: #f4f4f4 !important;
        padding: 2px 5px !important;
        border-radius: 3px !important;
        font-family: monospace !important;
        font-size: 14px !important;
    }}
    """
    
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
        render_preview_column(inline_css)
    
    # Export Section
    st.divider()
    st.subheader("💾 Save or Download Your Resume")
    file_name = st.text_input("Enter a custom file name (without extension):", value="resume")
    export_resume(file_name, inline_css)

if __name__ == "__main__":
    main()
