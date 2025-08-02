import streamlit as st
from groq_api import generate_email, generate_hashtags_and_description
from email_sender import send_email, send_email_custom

# Get secrets from Streamlit Cloud
API_KEY = st.secrets["API_KEY"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
SENDER_EMAIL = st.secrets["SENDER_EMAIL"]

st.set_page_config(page_title="Marketing Tools", layout="centered")
st.title("📧 Marketing / Collaboration Email Generator & Hashtag Tool")

# ------------------------- TOOL SELECTION -------------------------
tool = st.radio("Select Tool", ["Email Generator", "Hashtag & Description Generator"])

# ------------------------- EMAIL GENERATOR -------------------------
if tool == "Email Generator":
    st.header("✉️ Email Generator")

    topic = st.text_input("Enter the product, service, or event name")

    email_type = st.selectbox("Choose the type of email", [
        "Product Promotion", "Collaboration Request", "Service Offering", "Event Invitation",
        "Follow-up Message", "Sponsorship Request", "Feedback/Review Request"
    ])

    tone = st.selectbox("Select a tone", ["Formal", "Friendly", "Casual"])

    def build_prompt(topic, email_type, tone):
        base = f"Write a {tone.lower()} "
        instruction = "Only write the email content starting with the subject line. Do NOT include any introductory explanation or extra text."
        prompts = {
            "Product Promotion": f"{base}marketing email to promote the product: {topic}. {instruction}",
            "Collaboration Request": f"{base}email requesting collaboration regarding: {topic}. {instruction}",
            "Service Offering": f"{base}email to offer a service related to: {topic}. {instruction}",
            "Event Invitation": f"{base}email inviting someone to attend an event called: {topic}. {instruction}",
            "Follow-up Message": f"{base}follow-up email regarding the topic: {topic}. {instruction}",
            "Sponsorship Request": f"{base}email requesting sponsorship for: {topic}. {instruction}",
            "Feedback/Review Request": f"{base}email requesting feedback or a review for: {topic}. {instruction}"
        }
        return prompts.get(email_type, f"{base}email about: {topic}. {instruction}")

    if st.button("Generate Email"):
        if not topic:
            st.warning("Please enter a topic first.")
        else:
            prompt = build_prompt(topic, email_type, tone)
            with st.spinner("Generating email..."):
                try:
                    email = generate_email(prompt, api_key=API_KEY)
                    st.session_state.generated_email = email
                    st.success("Email generated successfully!")
                except Exception as e:
                    st.error(f"Failed to generate email: {e}")

    email = st.text_area("Generated Email (edit if needed)",
                         value=st.session_state.get('generated_email', ''),
                         height=300)

    st.subheader("📤 Send Generated Email")
    recipient = st.text_input("Recipient Email Address")

    use_custom_sender = st.checkbox("Use different sender email (optional)")

    if use_custom_sender:
        custom_sender_email = st.text_input("Your Email (Gmail only)")
        custom_app_password = st.text_input("App Password", type="password")
    else:
        custom_sender_email = SENDER_EMAIL
        custom_app_password = EMAIL_PASSWORD

    if st.button("Send Email"):
        if not email.strip():
            st.warning("Please generate an email first or edit the email before sending.")
        elif not recipient:
            st.warning("Please enter recipient email to send the email.")
        elif use_custom_sender and (not custom_sender_email or not custom_app_password):
            st.warning("Please enter both email and app password if using custom sender.")
        else:
            subject = f"{email_type} regarding {topic}"
            if use_custom_sender:
                result = send_email_custom(custom_sender_email, custom_app_password, recipient, subject, email)
            else:
                result = send_email(custom_sender_email, custom_app_password, recipient, subject, email)

            if result is True:
                st.success("Email sent successfully!")
            else:
                st.error(f"Failed to send email: {result}")

# ------------------- HASHTAG & DESCRIPTION GENERATOR -------------------
elif tool == "Hashtag & Description Generator":
    st.header("🏷️ Hashtag & Description Generator")

    category = st.text_input("Enter category or topic (e.g., skincare, gadgets)")
    target_audience = st.selectbox("Select Target Audience", [
        "Teenagers", "Young Adults", "Professionals", "Fitness Enthusiasts",
        "Beauty Lovers", "Tech Geeks", "General Audience"
    ])
    platform = st.selectbox("Select Platform", ["Instagram", "Twitter", "LinkedIn"])
    tone_hd = st.selectbox("Select Tone", ["Formal", "Friendly", "Casual"])
    purpose = st.selectbox("Purpose", ["Promote Product", "Announce Event", "Share Tips", "Raise Awareness"])

    if "description" not in st.session_state:
        st.session_state.description = ""
    if "hashtags" not in st.session_state:
        st.session_state.hashtags = ""

    if st.button("Generate Hashtags & Description"):
        if not category:
            st.warning("Please enter a category or topic.")
        else:
            prompt_hd = (
                f"Generate a {tone_hd.lower()} social media description and relevant hashtags "
                f"for {purpose.lower()} about {category}, targeting {target_audience} on {platform}. "
                f"Return the description first, then a list of hashtags separated by commas. Separate both with a blank line."
            )
            with st.spinner("Generating..."):
                try:
                    result = generate_hashtags_and_description(prompt_hd, api_key=API_KEY)
                    if "\n\n" in result:
                        desc_part, hash_part = result.strip().split("\n\n", 1)
                    else:
                        desc_part = result.strip()
                        hash_part = ""

                    st.session_state.description = desc_part
                    st.session_state.hashtags = hash_part
                    st.success("Generated successfully!")
                except Exception as e:
                    st.error(f"Failed to generate hashtags and description: {e}")

# ------------------- OUTPUT: DESCRIPTION & HASHTAGS -------------------
if st.session_state.get("description") or st.session_state.get("hashtags"):
    st.subheader("📝 Description")
    st.text_area("Description", value=st.session_state.description, height=150, key="desc_output")

    st.subheader("🔖 Hashtags")
    st.text_area("Hashtags", value=st.session_state.hashtags, height=100, key="hash_output")

# ---------------------------- FOOTER ----------------------------
st.markdown("---")
st.markdown("<center>Made with ❤️ by Team SEM | www.sem.com</center>", unsafe_allow_html=True)
