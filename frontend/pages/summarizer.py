import streamlit as st
import textstat
import pandas as pd
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        min-height: 100vh;
        padding: 2rem 3rem;
        box-sizing: border-box;
    }
    h1, h2, h3 {
        color: #eafff3;
    }
    .stFileUploader > div {
        background-color: #0e6655;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 5px 15px rgba(6, 77, 54, 0.7);
    }
    .stFileUploader button {
        background-color: #117a65 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
    }
    .stFileUploader button:hover {
        background-color: #0b5345 !important;
    }
    .stTextArea > div > textarea {
        background-color: #0b5345 !important;
        color: #eafff3 !important;
        border-radius: 8px !important;
        border: none !important;
        font-size: 1rem !important;
    }
    .stMetric > div {
        background-color: #148f77 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 12px rgba(0, 77, 54, 0.5) !important;
        color: #d5fff1 !important;
    }
</style>
""", unsafe_allow_html=True)



col1, col2 = st.columns([8, 2])
with col2:
    if st.button("✏ Edit Profile"):
        st.switch_page("pages/profile.py")


st.set_page_config(page_title="Summarizer", layout="wide")
st.title("Summarizer Main UI")

# Login check
if "token" not in st.session_state:
    st.warning("You are not logged in. Please login first.")
    st.stop()

uploaded_file = st.file_uploader("Upload a text file (.txt)", type=["txt"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    st.subheader("File Content")
    st.text_area("Preview", content, height=200)

    # Compute readability scores
    flesch = textstat.flesch_reading_ease(content)
    gunning = textstat.gunning_fog(content)
    smog = textstat.smog_index(content)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Flesch-Kincaid", round(flesch, 2))
    col2.metric("Gunning Fog", round(gunning, 2))
    col3.metric("SMOG Index", round(smog, 2))

    # Bar charts
    data = pd.DataFrame({
        "Level": ["Beginner", "Intermediate", "Advanced"],
        "Score": [flesch, gunning, smog]  
    })
    st.subheader("Readability Levels")
    st.bar_chart(data.set_index("Level"))