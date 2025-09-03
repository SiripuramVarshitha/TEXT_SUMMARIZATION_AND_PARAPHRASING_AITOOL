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


st.set_page_config(page_title="Edit Profile", layout="centered")
st.title("Edit Profile")
API_URL = "http://127.0.0.1:8000"

if "token" not in st.session_state:
    st.warning("You are not logged in. Please login first.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

# Fetch user details
try:
    response = requests.get(f"{API_URL}/users/me", headers=headers)
    if response.status_code == 200:
        data = response.json()
        user = data.get("user", data)   
    else:
        st.error(f"Failed to fetch profile. Status: {response.status_code}, Msg: {response.text}")
        st.stop()
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to backend: {e}")
    st.stop()

with st.form("edit_profile"):
    name = st.text_input("Full Name", value=user.get("name", ""))
    email = st.text_input("Email", value=user.get("email", ""))
    language = st.selectbox(
        "Language Preference", ["English", "Hindi"],
        index=["English", "Hindi"].index(user.get("language", "English"))
    )
    update = st.form_submit_button("Update Profile")

if update:
    payload = {"name": name, "email": email, "language": language}
    try:
        response = requests.put(f"{API_URL}/users/me", json=payload, headers=headers)
        if response.status_code == 200:
            st.success("Profile updated successfully! ✅")
        else:
            st.error(f"Failed to update profile. {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {e}")

if st.button("Back to Main"):
    st.switch_page("pages/summarizer.py")
