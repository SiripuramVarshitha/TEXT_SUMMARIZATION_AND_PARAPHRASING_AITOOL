import sys
import os
from io import StringIO
import streamlit as st
import httpx
import textstat
from PIL import Image
import pytesseract
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu
import json
import numpy as np
import matplotlib.pyplot as plt

# --------------------------- PATH SETUP ---------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
backend_dir = os.path.join(parent_dir, "backend")
sys.path.append(backend_dir)

# --------------------------- BACKEND IMPORTS ---------------------------
from backend.api.paraphrasing import generate_paraphrase, paraphrase_long_text
from backend.api.summarization import summarize_text_by_level
from backend.api.database import (
    save_generated_text, 
    fetch_all_users, 
    fetch_user_texts, 
    fetch_user_text_counts, 
    delete_user, 
    delete_user_text,
    save_user_feedback,
    fetch_all_feedback,
    delete_feedback
)
from forget_password import forgot_password_page
from auth import login as backend_login, logout
from profile import profile_page

API_URL = "http://localhost:8000"

# --------------------------- STYLING ---------------------------
st.markdown("""
<style>
    .stApp { background-color: #0A2239; color: #E0F7FA; font-family: 'Orbitron', sans-serif; }
    h1, h2, h3 { color: #E0F7FA; text-align: center; }
    .stTextInput > div > div > input, .stTextArea textarea { background-color: #05668D !important; color: #E0F7FA !important; border-radius: 6px; padding: 6px !important; }
    .stButton>button { background-color: #028090 !important; color: #E0F7FA !important; border-radius: 6px; font-weight: bold; padding: 10px 20px; }
    .stButton>button:hover { background-color: #00A896 !important; transform: scale(1.05); }
    [data-testid="stSidebar"] { background-color: #05668D; }
    [data-testid="stSidebar"] * { color: #E0F7FA !important; }
    .stTextArea textarea { height: 200px !important; }
</style>
""", unsafe_allow_html=True)

# --------------------------- METRICS ---------------------------
def compute_metrics(input_text, output_text):
    input_fog = textstat.gunning_fog(input_text)
    output_fog = textstat.gunning_fog(output_text)
    readability_delta = input_fog - output_fog
    semantic_sim = sentence_bleu([input_text.split()], output_text.split())
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    fact_pres_score = scorer.score(input_text, output_text)['rougeL'].fmeasure
    input_tokens = set(input_text.split())
    output_tokens = set(output_text.split())
    novelty = len(output_tokens - input_tokens) / max(1, len(output_tokens))
    radar_metrics = {
        "Coherence": max(0, min(1, 1 - abs(readability_delta) / 20)),
        "Fluency": max(0, min(1, 1 / (1 + abs(output_fog) / 20))),
        "Semantic Similarity": semantic_sim,
        "Diversity": novelty,
        "Fact Preservation": fact_pres_score
    }
    bottom_values = {
        "Readability Delta": readability_delta,
        "Semantic Similarity": semantic_sim,
        "Fact Preservation": fact_pres_score
    }
    return radar_metrics, bottom_values

def show_scores(flesch, fog, smog):
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Flesch-Kincaid", f"{flesch:.1f}")
    with col2: st.metric("Gunning Fog", f"{fog:.1f}")
    with col3: st.metric("SMOG Index", f"{smog:.1f}")

import matplotlib.pyplot as plt
import numpy as np

def show_radar_chart(metrics):
    labels = list(metrics.keys())
    values = list(metrics.values())
    num_vars = len(labels)

    # Repeat the first value to close the circle
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color="blue", linewidth=2, linestyle='solid')
    ax.fill(angles, values, color="blue", alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2","0.4","0.6","0.8","1.0"])
    ax.set_ylim(0,1)

    st.pyplot(fig)


# --------------------------- AUTH ---------------------------
def show_login():
    st.title("SmartText Summarizer and Paraphraser")
    st.header("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        success, user_data, token = backend_login(email, password)
        if success:
            st.session_state.user_id = user_data['id']
            st.session_state.username = user_data['username']
            st.session_state.email = user_data['email']
            st.session_state.access_token = token
            st.session_state.logged_in = True
            st.success(f"Logged in successfully as {user_data['username']}")
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid email or password")
    if st.button("Forgot Password?"):
        st.session_state.page = "forgot_password"
        st.rerun()
    if st.button("Create a new account"):
        st.session_state.page = "register"
        st.rerun()

def show_register():
    st.title("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    language_preference = st.selectbox("Language Preference", ["English", "Hindi"])

    if st.button("Register"):
        if username and email and password:
            url = f"{API_URL}/auth/register"
            data = {
                "username": username,
                "email": email,
                "password": password,
                "language_preference": language_preference
            }
            try:
                response = httpx.post(url, json=data, timeout=10)
                if response.status_code == 201:
                    st.success("✅ Registration successful! Please login now.")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(f"Failed to register: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.error("Please fill in all fields.")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

def sidebar_menu():
    st.sidebar.title("Menu")
    if st.sidebar.button("Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    if st.sidebar.button("Profile"):
        st.session_state.page = "profile"
        st.rerun()
    if st.sidebar.button("Logout"):
        logout()
        st.session_state.page = "login"
        st.session_state.logged_in = False
        st.rerun()

# --------------------------- DASHBOARD ---------------------------
from deep_translator import GoogleTranslator

def show_dashboard():
    st.title("Dashboard - Smart Text Tools")

    # ---------------- INPUT SECTION ----------------
    st.subheader("Enter Your Input Text or Upload a File")

    user_input_text = st.text_area("Type or paste text here:", height=200)
    uploaded_file = st.file_uploader("Or upload a text/image file", type=["txt", "png", "jpg", "jpeg"])

    text = ""

    if uploaded_file is not None:
        if uploaded_file.type.startswith("text"):
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            text = stringio.read()
        else:
            image = Image.open(uploaded_file)
            text = pytesseract.image_to_string(image)
    elif user_input_text.strip():
        text = user_input_text.strip()

    if not text:
        st.warning("⚠️ Please provide some input text or upload a file to continue.")
        st.stop()

    st.markdown("### What would you like to do?")
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Summarize", "🔄 Paraphrase", "📊 Readability", "📈 Evaluation"])

    # Supported languages for translation
    languages = {"Hindi": "hi", "Spanish": "es", "French": "fr", "German": "de", "Chinese": "zh-CN",
                 "Telugu": "te", "Tamil": "ta", "Bengali": "bn", "Urdu": "ur"}

    # ---------------- TAB 1: SUMMARIZE ----------------
    with tab1:
        st.subheader("Select Summary Level:")
        levels = ["Easy", "Medium", "Long"]

        for lvl in levels:
            if st.button(f"Generate {lvl} Summary"):
                summary = summarize_text_by_level(text, lvl)
                st.session_state[f"summary_{lvl}"] = summary

            if f"summary_{lvl}" in st.session_state:
                st.text_area("Generated Summary", st.session_state[f"summary_{lvl}"], height=200, key=f"summary_box_{lvl}")

                # 🌐 Translation Section
                with st.expander(f"🌍 Translate {lvl} Summary"):
                    lang_key = f"lang_summary_{lvl}_{st.session_state.user_id}"
                    lang = st.selectbox(f"Select Language", list(languages.keys()), key=lang_key)
                    if st.button(f"Translate {lvl}", key=f"translate_btn_summary_{lvl}_{st.session_state.user_id}"):
                        translated_text = GoogleTranslator(source='auto', target=languages[lang]).translate(
                            st.session_state[f"summary_{lvl}"]
                        )
                        st.text_area(f"{lvl} Summary ({lang})", translated_text, height=200)

                # 🔍 Compare with Input
                if st.button(f"Compare {lvl} Summary with Input", key=f"compare_sum_{lvl}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_area("Original Input", text, height=200, disabled=True)
                    with col2:
                        st.text_area("Generated Summary", st.session_state[f"summary_{lvl}"], height=200)

                # ⭐ Feedback Section
                fb_key = f"feedback_summary_{lvl}"
                rate_key = f"rating_summary_{lvl}"
                if fb_key not in st.session_state:
                    st.session_state[fb_key] = ""
                if rate_key not in st.session_state:
                    st.session_state[rate_key] = 0

                st.session_state[fb_key] = st.text_area(
                    "Provide your feedback (optional):",
                    st.session_state[fb_key],
                    key=f"fb_summary_{lvl}"
                )

                st.markdown("Rate the summary (optional):")
                cols = st.columns(5)
                rating = st.session_state[rate_key]
                for i in range(5):
                    if cols[i].button("⭐", key=f"star{i+1}_summary_{lvl}"):
                        rating = i + 1
                st.session_state[rate_key] = rating
                st.markdown(f"*Current Rating:* {rating} ⭐" if rating else "No rating yet")

                if st.button(f"Submit Feedback for {lvl} Summary"):
                    if st.session_state[fb_key] or st.session_state[rate_key]:
                        feedback_str = f"Rating: {rating}, Feedback: {st.session_state[fb_key]}"
                        save_user_feedback(st.session_state.user_id, feedback_str)
                        st.success("✅ Thank you for your feedback!")

    # ---------------- TAB 2: PARAPHRASE ----------------
    with tab2:
        st.subheader("Select Paraphrase Level:")
        levels = {"Easy": {"max_length": 100}, "Advanced": {"max_length": 150}, "Expert": {"max_length": 200}}

        for lvl, params in levels.items():
            if st.button(f"Generate {lvl} Paraphrase"):
                paraphrased = generate_paraphrase(text, **params)
                st.session_state[f"paraphrase_{lvl}"] = paraphrased

            if f"paraphrase_{lvl}" in st.session_state:
                st.text_area("Paraphrased Text", st.session_state[f"paraphrase_{lvl}"], height=200)

                # 🌐 Translation Section
                with st.expander(f"🌍 Translate {lvl} Paraphrase"):
                    lang_key = f"lang_paraphrase_{lvl}_{st.session_state.user_id}"
                    lang = st.selectbox(f"Select Language", list(languages.keys()), key=lang_key)
                    if st.button(f"Translate {lvl}", key=f"translate_btn_paraphrase_{lvl}_{st.session_state.user_id}"):
                        translated_text = GoogleTranslator(source='auto', target=languages[lang]).translate(
                            st.session_state[f"paraphrase_{lvl}"]
                        )
                        st.text_area(f"{lvl} Paraphrase ({lang})", translated_text, height=200)

                # 🔍 Compare with Input
                if st.button(f"Compare {lvl} Paraphrase with Input"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_area("Original Input", text, height=200, disabled=True)
                    with col2:
                        st.text_area("Generated Paraphrase", st.session_state[f"paraphrase_{lvl}"], height=200)

                # ⭐ Feedback Section
                fb_key = f"feedback_paraphrase_{lvl}"
                rate_key = f"rating_paraphrase_{lvl}"
                if fb_key not in st.session_state:
                    st.session_state[fb_key] = ""
                if rate_key not in st.session_state:
                    st.session_state[rate_key] = 0

                st.session_state[fb_key] = st.text_area(
                    "Provide your feedback (optional):",
                    st.session_state[fb_key],
                    key=f"fb_paraphrase_{lvl}"
                )

                st.markdown("Rate the paraphrase (optional):")
                cols = st.columns(5)
                rating = st.session_state[rate_key]
                for i in range(5):
                    if cols[i].button("⭐", key=f"star{i+1}_paraphrase_{lvl}"):
                        rating = i + 1
                st.session_state[rate_key] = rating
                st.markdown(f"*Current Rating:* {rating} ⭐" if rating else "No rating yet")

                if st.button(f"Submit Feedback for {lvl} Paraphrase"):
                    if st.session_state[fb_key] or st.session_state[rate_key]:
                        feedback_str = f"Rating: {rating}, Feedback: {st.session_state[fb_key]}"
                        save_user_feedback(st.session_state.user_id, feedback_str)
                        st.success("✅ Thank you for your feedback!")

    # ---------------- TAB 3: READABILITY ----------------
    with tab3:
        st.subheader("Readability Analysis")
        if st.button("Analyze Readability"):
            flesch = textstat.flesch_reading_ease(text)
            fog = textstat.gunning_fog(text)
            smog = textstat.smog_index(text)

            st.markdown("### Readability Scores")
            show_scores(flesch, fog, smog)

            st.markdown("### Readability Score Comparison")
            scores = {"Flesch Ease": flesch, "Gunning Fog": fog, "SMOG Index": smog}
            fig, ax = plt.subplots()
            ax.bar(scores.keys(), scores.values())
            ax.set_ylabel("Score Value")
            ax.set_xlabel("Readability Metrics")
            ax.set_title("Readability Analysis Bar Graph")
            ax.set_ylim(0, max(scores.values()) + 10)
            st.pyplot(fig)

    # ---------------- TAB 4: EVALUATION ----------------
    with tab4:
        st.subheader("Evaluation")

        # --- Summary Evaluation ---
        if st.button("Generate Evaluation Summary"):
            candidate = summarize_text_by_level(text, "Medium")
            st.session_state.eval_summary_candidate = candidate
            st.text_area("Generated Summary", candidate, height=200)

        # 🌐 Translate Evaluation Summary
        with st.expander("🌍 Translate Evaluation Summary"):
            lang_key = f"lang_eval_summary_{st.session_state.user_id}"
            lang = st.selectbox("Select Language", list(languages.keys()), key=lang_key)
            if st.button("Translate Summary", key=f"translate_eval_summary_btn_{st.session_state.user_id}"):
                if "eval_summary_candidate" in st.session_state:
                    translated_text = GoogleTranslator(
                        source='auto', target=languages[lang]
                    ).translate(st.session_state.eval_summary_candidate)
                    st.text_area(f"Translated Summary ({lang})", translated_text, height=200)
                else:
                    st.warning("Generate the summary first before translating.")

        # --- Compare with Reference Summary ---
        if "eval_summary_candidate" in st.session_state and st.button("Compare with Reference Summary"):
            reference = summarize_text_by_level(text, "Long")
            candidate = st.session_state.eval_summary_candidate
            radar_metrics, bottom_values = compute_metrics(reference, candidate)

            col1, col2, col3 = st.columns(3)
            with col1: st.text_area("Original Input", text, height=200, disabled=True)
            with col2: st.text_area("Generated Summary", candidate, height=200)
            with col3: st.text_area("Reference Summary", reference, height=200, disabled=True)
            show_radar_chart(radar_metrics)

            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Readability Δ", f"{bottom_values['Readability Delta']:.2f}")
            with col2: st.metric("Semantic Similarity", f"{bottom_values['Semantic Similarity']:.2f}")
            with col3: st.metric("Fact Preservation", f"{bottom_values['Fact Preservation']*100:.0f}%")

        # --- Paraphrase Evaluation ---
        if st.button("Generate Evaluation Paraphrase"):
            candidate = generate_paraphrase(text, max_length=120)
            st.session_state.eval_paraphrase_candidate = candidate
            st.text_area("Generated Paraphrase", candidate, height=200)

        # 🌐 Translate Evaluation Paraphrase
        with st.expander("🌍 Translate Evaluation Paraphrase"):
            lang_key = f"lang_eval_paraphrase_{st.session_state.user_id}"
            lang = st.selectbox("Select Language", list(languages.keys()), key=lang_key)
            if st.button("Translate Paraphrase", key=f"translate_eval_paraphrase_btn_{st.session_state.user_id}"):
                if "eval_paraphrase_candidate" in st.session_state:
                    translated_text = GoogleTranslator(
                        source='auto', target=languages[lang]
                    ).translate(st.session_state.eval_paraphrase_candidate)
                    st.text_area(f"Translated Paraphrase ({lang})", translated_text, height=200)
                else:
                    st.warning("Generate the paraphrase first before translating.")

        # --- Compare with Reference Paraphrase ---
        if "eval_paraphrase_candidate" in st.session_state and st.button("Compare with Reference Paraphrase"):
            reference = generate_paraphrase(text, max_length=200)
            candidate = st.session_state.eval_paraphrase_candidate
            radar_metrics, bottom_values = compute_metrics(reference, candidate)

            col1, col2, col3 = st.columns(3)
            with col1: st.text_area("Original Input", text, height=200, disabled=True)
            with col2: st.text_area("Generated Paraphrase", candidate, height=200)
            with col3: st.text_area("Reference Paraphrase", reference, height=200, disabled=True)
            show_radar_chart(radar_metrics)

            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Readability Δ", f"{bottom_values['Readability Delta']:.2f}")
            with col2: st.metric("Semantic Similarity", f"{bottom_values['Semantic Similarity']:.2f}")
            with col3: st.metric("Fact Preservation", f"{bottom_values['Fact Preservation']*100:.0f}%")

# ----------------- Helper -----------------
def rerun_app():
    st.session_state.page = st.session_state.page
def main():
    import matplotlib.pyplot as plt
    from streamlit_autorefresh import st_autorefresh

    # -------------------- Session Setup --------------------
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "admin_tab" not in st.session_state:
        st.session_state.admin_tab = "users"

    st.title("SmartText Summarizer & Paraphraser")

    # -------------------- Admin Login Button --------------------
    if st.button("🔑 Login as Admin"):
        st.session_state.page = "admin_login"
        st.rerun()

    # -------------------- Admin Login --------------------
    if st.session_state.page == "admin_login":
        st.title("Admin Login")
        email = st.text_input("Admin Email")
        password = st.text_input("Admin Password", type="password")
        if st.button("Submit"):
            if email == "varshithasiripuram@gmail.com" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.page = "admin_dashboard"
                st.success("✅ Admin logged in successfully")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    # -------------------- Admin Dashboard --------------------
    elif st.session_state.page == "admin_dashboard":
        st.sidebar.title("📊 Admin Menu")
        if st.sidebar.button("👥 Users"): st.session_state.admin_tab = "users"
        if st.sidebar.button("🗂️ Content"): st.session_state.admin_tab = "content"
        if st.sidebar.button("📈 Analytics"): st.session_state.admin_tab = "analytics"
        if st.sidebar.button("💬 Feedback"): st.session_state.admin_tab = "feedback"
        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

        st.title("👩‍💻 Admin Dashboard")

        # -------------------- Users Tab --------------------
        if st.session_state.admin_tab == "users":
            st.subheader("User Management")
            search_user = st.text_input("Search Users")
            users = fetch_all_users()
            if search_user:
                users = [u for u in users if search_user.lower() in u["username"].lower()]

            for user in users:
                col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                with col1: st.text(user["username"])
                with col2: st.text(user["email"])
                with col3:
                    if st.button(f"Delete {user['id']}", key=f"del_{user['id']}"):
                        if delete_user(user["id"]):
                            st.success(f"Deleted {user['username']}")
                            st.rerun()
                        else:
                            st.error("Deletion failed")
                with col4:
                    st.text("Active" if user.get("active", True) else "Inactive")

        # -------------------- Content Tab --------------------
        elif st.session_state.admin_tab == "content":
            st.subheader("Content Management")
            contents = fetch_user_texts()
            for content in contents:
                st.text_area(
                    f"{content['username']} ({content['content_type']})",
                    content["content_text"],
                    height=80,
                    key=f"content_{content['id']}"
                )
                if st.button(f"Delete Content {content['id']}", key=f"delc_{content['id']}"):
                    if delete_user_text(content["id"]):
                        st.success("Deleted content successfully")
                        st.rerun()
                    else:
                        st.error("Deletion failed")

        # -------------------- Analytics Tab --------------------
        elif st.session_state.admin_tab == "analytics":
            st.subheader("📈 Platform Analytics (Real-Time)")
            st_autorefresh(interval=15000, key="data_refresh")

            counts = fetch_user_text_counts()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("👥 Total Users", counts.get("total_users", 0))
            col2.metric("⚡ Active Users", counts.get("active_users", 0))
            col3.metric("📝 Total Summaries", counts.get("total_summaries", 0))
            col4.metric("🔁 Total Paraphrases", counts.get("total_paraphrases", 0))

            st.divider()
            st.markdown("### 📊 Content Distribution")
            labels = ["Summaries", "Paraphrases"]
            sizes = [counts.get("total_summaries", 0), counts.get("total_paraphrases", 0)]
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#4CAF50','#2196F3'])
            ax.axis('equal')
            st.pyplot(fig)

            st.markdown("### 🕓 Recent Activities")
            recent_texts = fetch_user_texts()[:5]
            for t in recent_texts:
                st.write(
                    f"**{t['username']}** created a *{t['content_type']}* on {t['created_at'].strftime('%Y-%m-%d %H:%M')}"
                )

        # -------------------- Feedback Tab --------------------
        elif st.session_state.admin_tab == "feedback":
            st.subheader("💬 User Feedback Insights")
            feedbacks = fetch_all_feedback()
            if not feedbacks:
                st.info("No feedback available.")
            else:
                st.markdown("### 🧾 All Feedbacks")
                for fb in feedbacks:
                    col1, col2, col3 = st.columns([2, 5, 2])
                    with col1:
                        st.text(fb["username"])
                    with col2:
                        st.text_area("Feedback", fb["feedback_text"], height=60, key=f"fb_{fb['id']}")
                    with col3:
                        if st.button(f"Delete {fb['id']}", key=f"delfb_{fb['id']}"):
                            if delete_feedback(fb["id"]):
                                st.success("Feedback deleted successfully")
                                st.rerun()
                            else:
                                st.error("Failed to delete feedback")
    # -------------------- User Pages --------------------
    else:
        if st.session_state.logged_in:
            sidebar_menu()
            if st.session_state.page == "dashboard":
                show_dashboard()
            elif st.session_state.page == "profile":
                profile_page()
        else:
            if st.session_state.page == "login":
                show_login()
            elif st.session_state.page == "register":
                show_register()
            elif st.session_state.page == "forgot_password":
                forgot_password_page()

if __name__ == "__main__":
    main()
