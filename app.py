import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Whisper Wall",
    page_icon="💌",
    layout="centered"
)

# Initialise session state
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
<style>
    .main {
        background-color: #0d0d0f;
        color: #e8e0d0;
    }

    .stApp {
        background-color: #0d0d0f;
    }

    h1 {
        text-align: center;
        color: #c8a96e;
        font-family: serif;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #6b6570;
        margin-bottom: 2rem;
    }

    .message-card {
        background: #1a1a24;
        padding: 25px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .message-to {
        color: #c8a96e;
        font-style: italic;
        font-size: 1.1rem;
        margin-bottom: 12px;
    }

    .message-text {
        color: #e8e0d0;
        line-height: 1.8;
        margin-bottom: 15px;
    }

    .message-meta {
        color: #6b6570;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1>The Whisper Wall</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Leave your thoughts. No name. No judgment. Just words.</p>",
    unsafe_allow_html=True
)

# Message Form
with st.form("whisper_form", clear_on_submit=True):
    recipient = st.text_input(
        "To",
        placeholder="Who is this for?"
    )

    message = st.text_area(
        "Your Message",
        max_chars=500,
        placeholder="What's on your mind?"
    )

    submitted = st.form_submit_button("Send Anonymously")

    if submitted:
        if message.strip():
            st.session_state.messages.insert(0, {
                "to": recipient.strip(),
                "text": message.strip(),
                "time": datetime.now()
            })
            st.success("✦ Your message has been shared")
        else:
            st.error("Please write a message first.")

st.divider()

# Search
search = st.text_input(
    "Find messages",
    placeholder="Type a name..."
).strip().lower()

# Filter messages
filtered_messages = st.session_state.messages

if search:
    filtered_messages = [
        msg for msg in filtered_messages
        if msg["to"] and search in msg["to"].lower()
    ]

# Results count
count = len(filtered_messages)
st.caption(f"{count} whisper{'s' if count != 1 else ''}")

# Display messages
# Replace your current message display section with this

if filtered_messages:
    for msg in filtered_messages:
        recipient = msg["to"] if msg["to"] else "Anonymous"
        timestamp = msg["time"].strftime("%b %d · %I:%M %p")

        with st.container():
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1a1a24, #202032);
                padding: 25px;
                border-radius: 18px;
                margin-bottom: 20px;
                border: 1px solid rgba(255,255,255,0.08);
                box-shadow: 0 8px 30px rgba(0,0,0,0.25);
            ">
                <div style="
                    color: #c8a96e;
                    font-style: italic;
                    font-size: 1.15rem;
                    margin-bottom: 15px;
                    font-family: Georgia, serif;
                ">
                    To: {recipient}
                </div>

                <div style="
                    color: #e8e0d0;
                    font-size: 1rem;
                    line-height: 1.8;
                    margin-bottom: 18px;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                ">
                    {msg["text"]}
                </div>

                <div style="
                    color: #8a8490;
                    font-size: 0.8rem;
                    border-top: 1px solid rgba(255,255,255,0.06);
                    padding-top: 12px;
                ">
                    ✦ Anonymous • {timestamp}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    if search:
        st.info(f'No messages found for "{search}".')
    else:
        st.info("No whispers yet. Be the first to speak.")
