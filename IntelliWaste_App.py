import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

import streamlit as st
from PIL import Image
import requests
import re
import base64
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    st.error("❌ DASHSCOPE_API_KEY not found in .env file. Please add it.")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    timeout=60.0,
    max_retries=3,
)

MODEL_NAME = "qwen-vl-plus"


# ── HELPERS ───────────────────────────────────────────────────────────────────
def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def ask_model(prompt: str, image: Image.Image) -> str:
    img_b64 = image_to_base64(image)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    return response.choices[0].message.content


# ── EMAIL BODY GENERATOR (uses Qwen text model) ───────────────────────────────
def generate_email_body(username: str, waste_type: str, points_earned: int, total_score: int) -> str:
    major_type = waste_type.replace("Mixed (Major: ", "").replace(")", "").strip()

    prompt = f"""Write a short, friendly confirmation email body for a waste management app called IntelliWaste.

User details:
- Username: {username}
- Waste type submitted: {waste_type}
- Points earned this submission: {points_earned}
- New total honor score: {total_score}

Rules:
1. Start with: Hello {username},
2. Confirm the submission was processed, mention the waste type, points earned, and total score naturally
3. Add 1-2 sentences of an interesting fun fact about {major_type} waste recycling
4. End with: Thank you for supporting sustainable waste management.
5. Sign off as: Regards,\nIntelliWaste Team
6. Write ONLY the email body. No subject line. Keep it concise."""

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── AGENTS ────────────────────────────────────────────────────────────────────
def classifier_agent_process(image: Image.Image) -> str:
    prompt = (
        "You are a Classifier Agent. Classify the waste in this image as exactly one of: "
        "'biodegradable', 'non-biodegradable', 'mixed', or 'e-waste'. "
        "Give a one-sentence reason."
    )
    return ask_model(prompt, image)


def parse_classification(response_text: str) -> str:
    r = response_text.lower()
    if 'e-waste' in r or 'electronic' in r:
        return 'e-waste'
    if 'mixed' in r:
        return 'mixed'
    if 'non-biodegradable' in r or 'non biodegradable' in r:
        return 'non-biodegradable'
    if 'biodegradable' in r:
        return 'biodegradable'
    return 'unknown'


def component_identification_agent(image: Image.Image, waste_type: str) -> str:
    st.info(f"Component Identification Agent is analyzing the {waste_type} waste...")
    prompt = (
        f"You are a Component Identification Agent. Look at this image of {waste_type} waste. "
        "List the specific items you see as a simple bulleted list."
    )
    with st.spinner("Identifying components..."):
        return ask_model(prompt, image)


def separator_agent_process(image: Image.Image) -> str:
    prompt = (
        "You are a specialized Separator Agent. Identify each distinct item in this image. "
        "Provide a count for each category you find "
        "(e.g., '- 2 Plastic bottles', '- 1 Apple core')."
    )
    return ask_model(prompt, image)


def parse_separator_report(report_text: str):
    components = {'biodegradable': 0, 'non-biodegradable': 0, 'e-waste': 0}
    total_items = 0
    for line in report_text.strip().split('\n'):
        line_lower = line.lower()
        count_match = re.search(r'\d+', line_lower)
        count = int(count_match.group(0)) if count_match else 1
        total_items += count
        if any(kw in line_lower for kw in ['food', 'apple', 'peel', 'organic', 'paper']):
            components['biodegradable'] += count
        elif any(kw in line_lower for kw in ['plastic', 'bottle', 'can', 'metal', 'glass', 'wrapper']):
            components['non-biodegradable'] += count
        elif any(kw in line_lower for kw in ['electronic', 'battery', 'cable', 'phone', 'wire']):
            components['e-waste'] += count
    active = {k: v for k, v in components.items() if v > 0}
    if not active:
        return {}, None, 0
    return active, max(active, key=active.get), total_items


def recycling_agent_process(image: Image.Image, component_report: str) -> str:
    st.info("Recycling Agent is identifying recyclable items and providing a protocol...")
    prompt = (
        f"You are a Recycling Agent. Based on the following list of items:\n{component_report}\n"
        "Identify all recyclable items, provide a count for each type, "
        "give a step-by-step recycling protocol for the most dominant recyclable material, "
        "and describe what the recycled material could become."
    )
    with st.spinner("Generating recycling report..."):
        return ask_model(prompt, image)


def count_items_from_report(report_text: str) -> int:
    return len(report_text.strip().split('\n'))


def calculate_honor_score(item_count: int, waste_type: str) -> int:
    return item_count * {'e-waste': 25, 'non-biodegradable': 15, 'biodegradable': 10}.get(waste_type, 5)


def display_treatment_protocol(waste_type: str):
    st.subheader("B. Automated Treatment Protocol")
    if waste_type == 'biodegradable':
        st.markdown("""
        **1. Mechanical Shredding:** Waste is first shredded into smaller, uniform pieces.
        **2. Anaerobic Digestion:** Shredded material is moved into an oxygen-free digester to produce biogas and digestate.
        **3. Curing and Maturation:** The digestate is stabilized to create high-quality compost.
        """)
    elif waste_type == 'non-biodegradable':
        st.markdown("""
        **1. AI-Powered Optical Sorting:** AI identifies and sorts materials on conveyors.
        **2. Cleaning and Granulation:** Sorted materials are washed and shredded into flakes.
        **3. Extrusion and Pelletizing:** Flakes are melted and turned into pellets for manufacturing.
        """)
    elif waste_type == 'e-waste':
        st.warning("**CRITICAL:** E-waste contains toxic heavy metals like lead and mercury.")
        st.markdown("""
        **1. Robotic Dismantling:** Automated arms remove high-risk components like batteries.
        **2. Secure Shredding:** The remaining components are shredded in an enclosed environment.
        **3. Material Separation:** Magnets and eddy currents separate metals and plastics.
        **4. Precious Metal Recovery:** A specialized process extracts valuable metals for reuse.
        """)


# ── UPDATED: SEND TO RELAY ────────────────────────────────────────────────────
def send_to_relay_app(user_email: str, waste_type: str, honor_score: int):
    relay_url = "your_relay_webhook_url_here"

    # Use email prefix as username (e.g. u2692422 from u2692422@gmail.com)
    username = user_email.split("@")[0]

    # Generate dynamic AI email body
    with st.spinner("✍️ Generating personalized email..."):
        email_body = generate_email_body(
            username=username,
            waste_type=waste_type,
            points_earned=honor_score,
            total_score=honor_score
        )

    payload = {
        "email_to":    user_email,
        "honor_score": honor_score,
        "waste_type":  waste_type,
        "email_body":  email_body      # ← relay will use this as the full email body
    }

    try:
        with st.spinner("Sending confirmation..."):
            r = requests.post(relay_url, json=payload, timeout=10)
        if r.status_code in [200, 201]:
            st.success("✅ Process confirmation sent successfully.")
            # Show preview of the email that was sent
            with st.expander("📧 Preview of email sent"):
                st.text(email_body)
        else:
            st.error(f"❌ Confirmation could not be sent (Status: {r.status_code}).")
    except requests.exceptions.RequestException:
        st.error("❌ Connection Error: Could not connect to the confirmation service.")


# ── TREATMENT PROCESS ─────────────────────────────────────────────────────────
def run_treatment_process(image: Image.Image, waste_type: str, user_email: str):
    st.subheader("A. Component Identification")
    component_report = component_identification_agent(image, waste_type)
    st.markdown(component_report)

    display_treatment_protocol(waste_type)

    st.subheader("C. Recycling Agent Report (Final Step)")
    recycling_report = recycling_agent_process(image, component_report)
    st.markdown(recycling_report)

    honor_score = calculate_honor_score(count_items_from_report(component_report), waste_type)
    st.success(f"**PROCESS COMPLETE:** {waste_type.replace('_', ' ').title()} waste fully treated.")
    st.markdown("---")
    send_to_relay_app(user_email, waste_type, honor_score)


# ── UI ────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Multi-Agent Waste AI", page_icon="♻️")
st.title("♻️ Automated Multi-Agent Waste Processing System")
st.write("Upload an image of waste to simulate the automated treatment workflow.")

st.sidebar.header("⚙️ Settings")
st.sidebar.info(f"Model: **{MODEL_NAME}**")

user_email = st.text_input("Enter Your Email Address for Confirmation")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("Initiate Automated Treatment"):
        if not user_email:
            st.error("❗ Please enter your email address to proceed.")
        else:
            with st.spinner("Classifier Agent is analyzing the image..."):
                classifier_response = classifier_agent_process(image)
                category = parse_classification(classifier_response)

            st.header("1. Classifier Agent Report")
            st.write(f"**Determined Category:** {category.upper()}")
            st.write(classifier_response)
            st.markdown("---")
            st.header("2. Automated Treatment Workflow")

            if category in ['biodegradable', 'non-biodegradable', 'e-waste']:
                run_treatment_process(image, category, user_email)

            elif category == 'mixed':
                st.warning("🟡 Classifier identified MIXED waste. Routing to Separator Agent...")
                with st.spinner("Separator Agent is performing detailed analysis..."):
                    separator_report = separator_agent_process(image)

                st.subheader("A. Separator Agent Report")
                st.markdown(separator_report)

                components, major_category, total_items = parse_separator_report(separator_report)

                if not components:
                    st.error("Separator Agent could not identify specific items to route.")
                else:
                    st.subheader("B. Routing Plan")
                    for comp_cat, count in components.items():
                        st.write(f"🔹 **{count} {comp_cat.replace('_', ' ')}** item(s) → {comp_cat.upper()} workflow.")

                    st.subheader(f"C. Primary Treatment Protocol ({major_category.replace('_', ' ').title()})")
                    display_treatment_protocol(major_category)

                    st.subheader("D. Recycling Agent Report (Final Step)")
                    recycling_report = recycling_agent_process(image, separator_report)
                    st.markdown(recycling_report)

                    honor_score = calculate_honor_score(total_items, major_category)
                    st.success(f"**PROCESS COMPLETE:** Primary treatment for {major_category.replace('_', ' ').title()} finished.")
                    st.markdown("---")
                    send_to_relay_app(
                        user_email,
                        f"Mixed (Major: {major_category.replace('_', ' ').title()})",
                        honor_score
                    )

            else:
                st.error(f"❌ Could not determine waste category. Model response was: '{classifier_response}'")