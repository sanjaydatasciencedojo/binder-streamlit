import os
import streamlit as st
import subprocess
import markdown
from datetime import datetime

# Application Constants
APP_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of app.py
CSS_FILE = os.path.join(APP_DIR, "resume.css")  # Path to CSS file in the same folder as app.py
TEMPLATE_FILE = os.path.join(APP_DIR, "resume_template.md")  # Path to template file in the same folder as app.py
SAVE_DIR = "home/jovyan"  # Save .md and .pdf files in a subfolder named "streamlit"
os.makedirs(SAVE_DIR, exist_ok=True)  # Create the "streamlit" folder if it doesn't exist <button class="citation-flag" data-index="1">

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

def get_custom_css(theme_color, font_family, font_size, margin_top_bottom, margin_left_right, paragraph_spacing, line_spacing):
    """Generates custom CSS based on user input."""
    return f"""
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

def save_css_to_file(css_content, css_path):
    """Saves the CSS content to the specified file."""
    try:
        with open(css_path, "w") as css_file:
            css_file.write(css_content)
        st.sidebar.success(f"Custom CSS saved successfully at: {css_path}")
    except Exception as error:
        st.sidebar.error(f"⚠️ Oops! Something went wrong while saving CSS: {str(error)}")

def configure_styles(css_path):
    """Applies the CSS file to the Streamlit app."""
    try:
        with open(css_path, "r") as css_file:
            custom_css = css_file.read()
        st.markdown(f"""
        <style>
            {custom_css}
        </style>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.sidebar.warning("CSS file not found. Using default styles.")
    except Exception as error:
        st.sidebar.error(f"⚠️ Oops! Something went wrong while applying CSS: {str(error)}")

def main():
    # Configure page and styles
    st.set_page_config(layout="wide", page_icon="📄", page_title="Professional Resume Builder")

    # Initialize session state
    if 'resume_content' not in st.session_state:
        st.session_state.resume_content = load_template(TEMPLATE_FILE)  # Load template dynamically
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

    # Sidebar for Customization Options
    st.sidebar.subheader("🎨 Import / Export")
    uploaded_file = st.sidebar.file_uploader("Import Markdown", type=["md"])
    if uploaded_file:
        st.session_state.resume_content = uploaded_file.read().decode("utf-8")
        st.sidebar.success("Markdown file imported successfully!")

    st.sidebar.subheader("⚙️ Styling Options")
    theme_color = st.sidebar.color_picker("Theme Color", "#9C5BDE", key="theme_color")  # Color palette <button class="citation-flag" data-index="1">
    font_family = st.sidebar.selectbox("Font Family", ["Arial", "Verdana", "华康宋体"], index=0)
    font_size = st.sidebar.selectbox("Font Size", [12, 16, 20], index=1)
    margin_top_bottom = st.sidebar.selectbox("Margin (Top & Bottom)", [0, 50, 100], index=1)
    margin_left_right = st.sidebar.selectbox("Margin (Left & Right)", [0, 50, 100], index=1)
    paragraph_spacing = st.sidebar.selectbox("Paragraph Spacing", [0, 25, 50], index=1)
    line_spacing = st.sidebar.selectbox("Line Spacing", [1, 1.5, 2], index=1)

    # Generate and Save Custom CSS
    custom_css = get_custom_css(theme_color, font_family, font_size, margin_top_bottom, margin_left_right, paragraph_spacing, line_spacing)
    if st.sidebar.button("Save Custom CSS", use_container_width=True):
        save_css_to_file(custom_css, CSS_FILE)

    # Apply CSS to Live Preview
    configure_styles(CSS_FILE)

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

    # Export Section
    st.divider()
    st.subheader("💾 Save or Download Your Resume")

    # Custom File Name Input
    file_name = st.text_input("Enter a custom file name (without extension):", value="resume")
    md_file_name = f"{file_name}.md"
    pdf_file_name = f"{file_name}.pdf"

    # Save Markdown File Locally in "streamlit" Folder
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

    # Save PDF File Locally in "streamlit" Folder with Custom CSS
    if st.button("📥 Save PDF (.pdf)", use_container_width=True):
        if st.session_state.resume_content.strip():
            pdf_file_path = os.path.join(SAVE_DIR, pdf_file_name)
            temp_md_path = os.path.join(SAVE_DIR, "temp_resume.md")
            try:
                # Save Markdown content temporarily
                with open(temp_md_path, "w") as f:
                    f.write(st.session_state.resume_content)
                # Generate PDF with Pandoc and Custom CSS
                subprocess.run(
                    ["pandoc", temp_md_path, "-o", pdf_file_path, "--css", CSS_FILE],
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
