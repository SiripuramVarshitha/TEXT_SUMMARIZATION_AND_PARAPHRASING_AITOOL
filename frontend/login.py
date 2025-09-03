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

#Backend server url
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Login", layout="centered")
st.title("Login Page")

#Filling the details (Login form)
with st.form("Login form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login = st.form_submit_button("Login")
#Handling the details of user
if login:
    if email and password:
        payload = {"email": email, "password": password}
        try:
            response = requests.post(f"{API_URL}/login", json=payload)
            #Handing respones
            if response.status_code == 200:
                data = response.json()
                st.session_state["logged_in"] = True
                st.session_state["token"] = data["access_token"]
                st.session_state["email"] = email
                st.success("Login Successful")
                st.switch_page("pages/summarizer.py")  
            else:
                st.error("Invalid email or password")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")
    else:
        st.error("Enter both email and password")

# Page switches
if st.button("Forgot Password"):
    st.switch_page("pages/forgotpass.py")  

st.write("New User?")
if st.button("Create account"):
    st.switch_page("pages/signup.py")          