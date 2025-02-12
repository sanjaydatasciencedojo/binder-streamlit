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

def configure_styles(custom_css):
    """Sets up custom visual styling with professional color palette"""
    st.markdown(f"""
    <style>
        {custom_css}
    </style>
    """, unsafe_allow_html=True)

def main():
    # Configure page and styles
    st.set_page_config(layout="wide", page_icon="📄", page_title="Professional Resume Builder")

    # Initialize session state
    if 'resume_content' not in st.session_state:
        st.session_state.resume_content = DEFAULT_TEMPLATE
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
    if 'pdf_generated' not in st.session_state:
        st.session_state.pdf_generated = False
    if 'custom_css' not in st.session_state:
        st.session_state.custom_css = ""

    # Sidebar for Customization Options
    st.sidebar.subheader("🎨 Import / Export")
    uploaded_file = st.sidebar.file_uploader("Import Markdown", type=["md"])
    if uploaded_file:
        st.session_state.resume_content = uploaded_file.read().decode("utf-8")
        st.sidebar.success("Markdown file imported successfully!")

    st.sidebar.subheader("⚙️ Export Options")
    export_format = st.sidebar.selectbox("Export Format", ["PDF", "Markdown"])
    paper_size = st.sidebar.selectbox("Paper Size", ["A4", "Letter"], index=0)
    theme_color = st.sidebar.color_picker("Theme Color", "#9C5BDE", key="theme_color")
    font_family = st.sidebar.selectbox("Font Family", ["华康宋体", "Verdana", "Arial"], index=0)
    font_size = st.sidebar.selectbox("Font Size", [12, 16, 20], index=1)
    margin_top_bottom = st.sidebar.selectbox("Margin (Top & Bottom)", [0, 50, 100], index=1)
    margin_left_right = st.sidebar.selectbox("Margin (Left & Right)", [0, 50, 100], index=1)
    paragraph_spacing = st.sidebar.selectbox("Paragraph Spacing", [0, 25, 50], index=1)
    line_spacing = st.sidebar.selectbox("Line Spacing", [1, 1.5, 2], index=1)

    # Generate Custom CSS Based on User Input
    custom_css = f"""
    body {{
        background-color: #ffffff;
        color: #333333;
        font-family: '{font_family}', sans-serif;
        font-size: {font_size}px;
        line-height: {line_spacing};
        margin-top: {margin_top_bottom}px;
        margin-bottom: {margin_top_bottom}px;
        margin-left: {margin_left_right}px;
        margin-right: {margin_left_right}px;
    }}
    h1, h2, h3 {{
        color: {theme_color};
    }}
    p {{
        margin-bottom: {paragraph_spacing}px;
    }}
    """
    st.session_state.custom_css = custom_css
    configure_styles(custom_css)

    # Export Buttons in Sidebar
    st.sidebar.subheader("📤 Export Resume")
    if st.sidebar.button("Export Markdown (.md)", use_container_width=True):
        md_file_name = "resume.md"
        md_file_path = os.path.join(SAVE_DIR, md_file_name)
        try:
            with open(md_file_path, "w") as f:
                f.write(st.session_state.resume_content)
            st.sidebar.success(f"Markdown file saved locally at: {md_file_path}")
        except Exception as error:
            st.sidebar.error(f"⚠️ Oops! Something went wrong: {str(error)}")

    if st.sidebar.button("Export PDF (.pdf)", use_container_width=True):
        pdf_file_name = "resume.pdf"
        pdf_file_path = os.path.join(SAVE_DIR, pdf_file_name)
        temp_md_path = os.path.join(SAVE_DIR, "temp_resume.md")
        css_path = os.path.join(SAVE_DIR, "styles.css")
        try:
            # Save Markdown content temporarily
            with open(temp_md_path, "w") as f:
                f.write(st.session_state.resume_content)
            # Write Custom CSS for Consistent Colors
            with open(css_path, "w") as css_file:
                css_file.write(st.session_state.custom_css)
            # Generate PDF with Pandoc and Custom CSS
            subprocess.run(
                ["pandoc", temp_md_path, "-o", pdf_file_path, "--css", css_path, "--pdf-engine=xelatex", f"--variable=papersize:{paper_size.lower()}"],
                check=True
            )
            st.sidebar.success(f"PDF file saved locally at: {pdf_file_path}")
            # Cleanup temporary Markdown and CSS files
            os.remove(temp_md_path)
            os.remove(css_path)
        except Exception as error:
            st.sidebar.error(f"⚠️ Oops! Something went wrong: {str(error)}")

    # Main header
    st.title("📝 Professional Resume Builder")
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
            <small style="color: #888;">Last updated: {st.session_state.last_update}</small>
            """
        else:
            preview_content = f"""
            Your formatted preview will appear here...
            <small style="color: #888;">Last updated: {st.session_state.last_update}</small>
            """
        preview_display.markdown(preview_content, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
