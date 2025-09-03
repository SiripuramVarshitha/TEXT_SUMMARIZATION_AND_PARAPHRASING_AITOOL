import streamlit as st
import requests
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

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Signup", layout="centered")
st.title("Create Account & Profile")
#signup form
with st.form("Signup"):
    name = st.text_input("Fullname")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    language = st.selectbox("Language Preference", ["English", "Hindi"])
    signup = st.form_submit_button("Sign Up")
#handling form
if signup:
    if not name or not email or not password or not confirm_password:
        st.error("Please fill all details.")
    elif password != confirm_password:
        st.error("Passwords do not match")
        #Sending data to backend
    else:
        payload = {
            "name": name,
            "email": email,
            "password": password,
            "language": language
        }
        try:
            response = requests.post(f"{API_URL}/signup", json=payload)
            if response.status_code == 200:
                st.success("✅ Account created successfully! Please login now.")
                st.switch_page("login.py")  
            else:
                st.error(f"Signup failed: {response.json().get('detail')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")
#Switching pages
if st.button("Back to Login"):
    st.switch_page("login.py")      
