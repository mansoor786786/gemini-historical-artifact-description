import os
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------ Config ------------------
st.set_page_config(
    page_title="Gemini Historical Artifact Description",
    page_icon="🏺",
    layout="centered",
)

# Load API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("Please set GEMINI_API_KEY in your .env file.")
    st.stop()

genai.configure(api_key=API_KEY)

# Use a multimodal model (supports image + text)
MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# ------------------ Styles ------------------
st.markdown("""
<style>
/* Background */
.stApp {
    background: linear-gradient(180deg, #0b0f1a 0%, #111827 100%);
    color: #e5e7eb;
}

/* Title */
.title {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 10px;
}

/* Section labels */
.label {
    font-weight: 600;
    margin-top: 12px;
    margin-bottom: 6px;
}

/* Upload box look */
.upload-card {
    background: #0f172a;
    border: 1px dashed #374151;
    border-radius: 14px;
    padding: 16px;
}

/* Button */
.stButton>button {
    background: transparent;
    border: 2px solid #f59e0b;
    color: #f59e0b;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
}
.stButton>button:hover {
    background: #f59e0b;
    color: #111827;
}

/* Output card */
.output-card {
    background: #0f172a;
    border: 1px solid #374151;
    border-radius: 16px;
    padding: 18px 20px;
    margin-top: 14px;
}

/* Bullet spacing */
ul { margin-top: 6px; }
li { margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# ------------------ Header ------------------
st.markdown('<div class="title">🏺 Gemini Historical Artifact Description App</div>', unsafe_allow_html=True)

# ------------------ Inputs ------------------
st.markdown('<div class="label">Input Prompt:</div>', unsafe_allow_html=True)
prompt_text = st.text_input(
    "",
    placeholder="Describe the artifact..."
)

st.markdown('<div class="label">Choose an image of an artifact...</div>', unsafe_allow_html=True)
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drag and drop file here (Limit 200MB per file) - JPG, JPEG, PNG",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption=f"{uploaded_file.name} • {round(uploaded_file.size/1024, 1)} KB", use_container_width=True)

# ------------------ Generate Button ------------------
generate = st.button("🚀 Generate Artifact Description", use_container_width=True)

# ------------------ Helper: Build Prompt ------------------
def build_prompt(user_prompt: str) -> str:
    base = """
You are an expert museum curator and historian.

Analyze the provided artifact image and the user prompt (if any). Generate a structured, concise description in the exact format below.

Return ONLY the following sections:

- Name:
- Origin:
- Time Period:
- Historical Significance:
- Interesting Facts:
    • Fact 1
    • Fact 2
    • Fact 3

Guidelines:
- If the exact artifact is uncertain, make the best reasonable identification.
- Keep it informative, neutral, and engaging.
- 120–180 words total.
"""
    if user_prompt:
        base += f"\nUser prompt/context: {user_prompt}\n"
    return base

# ------------------ Generate Output ------------------
if generate:
    if image is None and not prompt_text:
        st.warning("Please provide an image or enter a prompt to generate the description.")
    else:
        with st.spinner("Generating description..."):
            try:
                content_parts = []
                # If image exists, pass it along with the prompt
                if image is not None:
                    content_parts.append(image)

                content_parts.append(build_prompt(prompt_text))

                response = model.generate_content(content_parts)
                raw_text = response.text.strip() if hasattr(response, "text") else ""

                # ------------------ Output Card ------------------
                st.markdown('<div class="output-card">', unsafe_allow_html=True)
                st.markdown("📜 **Description of the Artifact:**")
                if raw_text:
                    # Display as markdown to preserve bullets/format
                    st.markdown(raw_text)
                else:
                    st.info("No content generated. Try a clearer image or add more context in the prompt.")
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Generation failed: {e}")
