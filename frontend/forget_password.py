import streamlit as st
import httpx

API_URL = "http://localhost:8000"

def forgot_password_page():
    st.title("Forgot Password")

    if "fp_step" not in st.session_state:
        st.session_state.fp_step = "email"
        st.session_state.fp_email = ""

    # Step 1: Enter email
    if st.session_state.fp_step == "email":
        email = st.text_input("Enter your registered email")
        if st.button("Next"):
            if not email:
                st.error("Please enter your email")
            else:
                st.session_state.fp_email = email
                st.session_state.fp_step = "reset_password"
                st.rerun()

    # Step 2: Enter new password
    elif st.session_state.fp_step == "reset_password":
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        if st.button("Reset Password"):
            if not new_password or not confirm_password:
                st.error("Please fill both fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                payload = {
                    "email": st.session_state.fp_email,
                    "new_password": new_password
                }
                try:
                    res = httpx.post(f"{API_URL}/auth/reset-password", json=payload, timeout=10)
                    if res.status_code == 200:
                        st.success("Password updated successfully! You can now login.")
                        st.session_state.fp_step = "email"
                        st.session_state.fp_email = ""
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Failed to reset password"))
                except Exception as e:
                    st.error(f"Network error: {str(e)}")
