import streamlit as st
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

st.set_page_config(page_title="Forgot Password", layout="centered")
st.title("Forgot Password")

with st.form("forgot_form"):
    email = st.text_input("Enter your registered email")
    reset = st.form_submit_button("Reset Password")

if reset:
    if not email:
        st.error("Please enter your email.")
    else:
        # Mock logic; you can integrate backend later
        st.success(f"Password reset link sent to {email} (mock).")

if st.button("Back to Login"):
    st.switch_page("login.py")    
