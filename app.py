
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from datetime import date
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(page_title="Innoventure AI Studio", page_icon="💡",
                   layout="wide")

st.title("💡 Innoventure AI Studio")
st.caption("AI-powered content creation, distribution and analytics")

# ---------------- DATA STORAGE ----------------

os.makedirs("data", exist_ok=True)

CONTENT_FILE = "data/content.csv"
ANALYTICS_FILE = "data/analytics.csv"

if "drafts" not in st.session_state:
    st.session_state.drafts = {}

if "approved" not in st.session_state:
    st.session_state.approved = False

# ---------------- AUDIENCE CHANNELS ----------------

channels = {
    "School Leaders": [
        "LinkedIn", "School Email", "Newsletter"
    ],
    "Teachers": [
        "LinkedIn", "Instagram", "Teacher Groups", "Newsletter"
    ],
    "Students": [
        "YouTube Shorts", "School LMS",
        "Teacher Sharing", "Classroom Display"
    ],
    "Parents": [
        "Instagram", "Facebook",
        "Parent WhatsApp Groups", "Newsletter"
    ]
}

# ---------------- AI CONTENT GENERATION ----------------


def generate_content(idea, audience):
    import json
    from google import genai
    from google.genai import types

    prompt = f"""
    You are an educational content strategist for Innoventure.

    Campaign idea: {idea}
    Target audience: {audience}

    Generate four different platform-specific content drafts:
    1. LinkedIn post
    2. Instagram caption and 5-slide carousel
    3. YouTube Shorts title and 30-45 second script
    4. Newsletter subject, preview, body and CTA

    Adapt the content to this audience:
    School Leaders: school development and innovation education.
    Teachers: classroom activities and student creativity.
    Parents: children's curiosity and confidence.
    Students: simple, fun and exciting language.

    Return ONLY valid JSON with these exact keys:
    LinkedIn, Instagram, YouTube Shorts, Newsletter.
    """

    # Local backup content generator
    def local_backup():
        audience_messages = {
            "School Leaders": (
                "Create an innovation-focused learning environment "
                "where students develop creative thinking and problem-solving skills."
            ),
            "Teachers": (
                "Bring creativity into your classroom. Encourage students "
                "to ask questions, explore ideas and solve everyday problems."
            ),
            "Parents": (
                "Support your child's curiosity. Give them opportunities "
                "to explore, imagine and develop confidence through creativity."
            ),
            "Students": (
                "Have you ever wondered how to make something better? "
                "Ask questions, imagine new ideas and become a young innovator!"
            )
        }

        message = audience_messages.get(
            audience,
            "Encourage creativity, curiosity and innovation."
        )

        return {
            "LinkedIn": (
                f"{idea}\n\n{message}\n\n"
                "Let's inspire the next generation of innovators! "
                "#Innovation #Education #Innoventure"
            ),
            "Instagram": (
                f"✨ {idea}\n\n"
                f"{message}\n\n"
                "Slide 1: Every idea starts with curiosity.\n"
                "Slide 2: Ask questions.\n"
                "Slide 3: Think creatively.\n"
                "Slide 4: Explore solutions.\n"
                "Slide 5: Become an innovator!\n\n"
                "#YoungInnovators #CreativeLearning"
            ),
            "YouTube Shorts": (
                f"Title: Small Ideas, Big Innovations!\n\n"
                f"Script:\n"
                f"Have you ever had an amazing idea?\n"
                f"{message}\n"
                "Every big innovation starts with a small idea. "
                "Think, explore and create!"
            ),
            "Newsletter": (
                f"Subject: Inspire Innovation Through Small Ideas!\n\n"
                f"Preview: {message}\n\n"
                f"{idea}\n\n{message}\n\n"
                "Join us in encouraging the next generation of innovators!"
            )
        }

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=20000)
            )

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )

            result = response.text.strip()

            if result.startswith("```"):
                result = result.split("\n", 1)[1]
                result = result.rsplit("```", 1)[0]

            content = json.loads(result)

            required_keys = [
                "LinkedIn", "Instagram",
                "YouTube Shorts", "Newsletter"
            ]

            if not all(key in content for key in required_keys):
                raise ValueError("AI response is missing platform content.")

            st.success("Content generated successfully using Gemini AI!")
            return content, prompt

        except Exception as error:
            st.warning(
                "generation......."
            )
            print("Gemini error:", error)

    else:
        st.warning("API key unavailable. Using backup generation.")

    content = local_backup()
    
    return content, prompt

# ---------------- STEP 1 & 2 ----------------

st.header("1. Create a Campaign")

idea = st.text_area(
    "Enter your campaign idea",
    placeholder="Example: Every Child Can Become an Innovator"
)

audience = st.selectbox(
    "Choose Target Audience",
    ["School Leaders", "Teachers", "Students", "Parents"]
)

if st.button("Generate AI Content"):

    if not idea.strip():
        st.warning("Please enter a campaign idea.")

    else:
        try:
            with st.spinner("AI is generating content..."):
                drafts, prompt = generate_content(idea, audience)

            if drafts is None:
                st.error("Add your Gemini API key in the .env file.")
            else:
                st.session_state.drafts = drafts
                st.session_state.idea = idea
                st.session_state.audience = audience
                st.session_state.prompt = prompt
                st.session_state.approved = False
                st.success("Content generated successfully!")

        except Exception as e:
            st.error(f"Generation failed: {e}")


# ---------------- STEP 3 & 4 ----------------

if st.session_state.drafts:

    st.header("2. Review AI-Generated Content")

    with st.expander("View AI Prompt"):
        st.code(st.session_state.prompt)

    edited = {}

    for platform, content in st.session_state.drafts.items():
        edited[platform] = st.text_area(
            platform,
            value=content,
            height=180,
            key="edit_" + platform
        )

    if st.button("Approve and Save Content"):

        rows = []

        for platform, content in edited.items():
            rows.append({
                "Idea": st.session_state.idea,
                "Audience": st.session_state.audience,
                "Platform": platform,
                "Content": content,
                "Approval": "Approved",
                "Date": str(date.today())
            })

        df = pd.DataFrame(rows)

        df.to_csv(
            CONTENT_FILE,
            mode="a",
            header=not os.path.exists(CONTENT_FILE),
            index=False
        )

        st.session_state.drafts = edited
        st.session_state.approved = True
        st.success("Human approval completed and content saved!")


# ---------------- STEP 5: DISTRIBUTION ----------------

if st.session_state.approved:

    st.header("3. Audience-Aware Distribution")

    audience = st.session_state.audience

    st.write("Selected audience:", audience)

    selected_channels = st.multiselect(
        "Choose distribution channels",
        channels[audience],
        default=channels[audience]
    )

    st.info(
        "Student content is distributed through schools, "
        "teachers, parents and approved public channels."
    )

    if st.button("Record Distribution"):

        distribution = pd.DataFrame([
            {
                "Audience": audience,
                "Channel": channel,
                "Status": "Scheduled / Manual Publishing"
            }
            for channel in selected_channels
        ])

        distribution.to_csv(
            "data/distribution.csv",
            mode="a",
            header=not os.path.exists("data/distribution.csv"),
            index=False
        )

        st.success("Distribution plan saved!")

        st.caption(
            "This prototype records distribution. "
            "Actual publishing requires platform integrations."
        )


# ---------------- STEP 6: ANALYTICS ----------------

st.header("4. Performance Analytics Dashboard")

st.caption("Enter actual results from platform analytics or use sample data.")

if st.button("Load Illustrative Sample Data"):

    sample = pd.DataFrame([
        ["LinkedIn", "School Leaders", 3200, 850, 120, 65],
        ["Instagram", "Parents", 4800, 4200, 620, 180],
        ["YouTube Shorts", "Students", 3500, 7000, 400, 90],
        ["Newsletter", "Teachers", 1000, 800, 100, 55]
    ], columns=[
        "Platform", "Audience", "Reach", "Views",
        "Engagement", "Clicks"
    ])

    sample.to_csv(ANALYTICS_FILE, index=False)
    st.success("Illustrative data loaded.")

if os.path.exists(ANALYTICS_FILE):

    analytics = pd.read_csv(ANALYTICS_FILE)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Reach", int(analytics["Reach"].sum()))
    c2.metric("Total Views", int(analytics["Views"].sum()))
    c3.metric("Engagement", int(analytics["Engagement"].sum()))
    c4.metric("Total Clicks", int(analytics["Clicks"].sum()))

    st.subheader("Platform Performance")

    fig = px.bar(
        analytics,
        x="Platform",
        y="Reach",
        color="Platform",
        title="Reach by Platform"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Audience Performance")

    fig2 = px.bar(
        analytics,
        x="Audience",
        y="Engagement",
        color="Audience",
        title="Engagement by Audience"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Analytics Records")
    st.dataframe(analytics, use_container_width=True)

else:
    st.info("Load sample data or add actual analytics to view the dashboard.")
