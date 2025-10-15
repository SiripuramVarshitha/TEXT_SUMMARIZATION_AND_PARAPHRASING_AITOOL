import httpx
import streamlit as st

API_URL = "http://localhost:8000"


# ------------------ Backend Calls ------------------
def get_profile():
    """
    Fetches the current user profile from backend /profile/read.
    Uses JWT token stored in session_state.
    Returns a dict or None.
    """
    token = st.session_state.get('access_token')
    if not token:
        st.error("Access token missing. Please login again.")
        return None

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = httpx.get(f"{API_URL}/profile/read", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Ensure defaults
            data.setdefault("age_group", 18)
            data.setdefault("language_preference", "English")
            return data
        elif response.status_code == 404:
            st.error("User not found")
            return None
        else:
            detail = response.json().get('detail', 'Unknown error')
            st.error(f"Error fetching profile: {detail}")
            return None
    except httpx.RequestError as e:
        st.error(f"Network error: {str(e)}")
        return None
    except Exception as ex:
        st.error(f"Unexpected error: {str(ex)}")
        return None


def update_profile(age_group, language_preference):
    """
    Sends updated profile to backend /profile/update.
    Returns True if successful, else False.
    """
    token = st.session_state.get('access_token')
    if not token:
        st.error("Access token missing. Please login again.")
        return False

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "age_group": age_group,
        "language_preference": language_preference
    }
    try:
        response = httpx.put(f"{API_URL}/profile/update", json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            st.success("Profile updated successfully!")
            return True
        else:
            detail = response.json().get('detail', 'Unknown error')
            st.error(f"Error updating profile: {detail}")
            return False
    except httpx.RequestError as e:
        st.error(f"Network error: {str(e)}")
        return False
    except Exception as ex:
        st.error(f"Unexpected error: {str(ex)}")
        return False


# ------------------ Streamlit Page ------------------
def profile_page():
    st.title("👤 User Profile")

    # Load profile if not already loaded
    if "profile_loaded" not in st.session_state or not st.session_state.profile_loaded:
        profile = get_profile()
        if not profile:
            st.warning("Could not load profile. Try again later.")
            return
        try:
            st.session_state.age_group = int(profile.get("age_group", 18))
        except (TypeError, ValueError):
            st.session_state.age_group = 18
        st.session_state.language_preference = profile.get("language_preference", "English")
        st.session_state.profile_loaded = True

    # Age input
    age_group = st.number_input(
        "Age",
        min_value=18,
        max_value=65,
        value=st.session_state.age_group,
        step=1
    )

    # Language preference
    language_preference = st.radio(
        "Language Preference",
        options=["English", "Hindi"],
        index=0 if st.session_state.language_preference == "English" else 1,
        horizontal=True
    )

    st.write(f"**Current Age:** {age_group}")
    st.write(f"**Current Language Preference:** {language_preference}")

    # Save selections to session state
    st.session_state.age_group = age_group
    st.session_state.language_preference = language_preference

    # Update profile button
    if st.button("💾 Save Profile"):
        success = update_profile(age_group, language_preference)
        if success:
            st.session_state.profile_loaded = False  # reload on next visit
