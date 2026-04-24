import streamlit as st
from datetime import datetime
import json
import os
import html

# ── Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Whisper Wall",
    page_icon="💌",
    layout="centered"
)

MESSAGES_FILE = "messages.json"  # saved next to your app.py

# ── Persistence helpers ──────────────────────────────────
def load_messages():
    """Load messages from disk. Returns empty list if file doesn't exist yet."""
    if not os.path.exists(MESSAGES_FILE):
        return []
    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Convert stored ISO strings back to datetime objects
        for msg in data:
            if isinstance(msg["time"], str):
                msg["time"] = datetime.fromisoformat(msg["time"])
        return data
    except (json.JSONDecodeError, KeyError):
        return []

def save_messages(messages):
    """Save messages to disk, converting datetimes to ISO strings."""
    serialisable = []
    for msg in messages:
        serialisable.append({
            "to":   msg["to"],
            "text": msg["text"],
            "time": msg["time"].isoformat() if isinstance(msg["time"], datetime) else msg["time"],
        })
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(serialisable, f, ensure_ascii=False, indent=2)

# ── Load into session state once per session ─────────────
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

# ── Styles ───────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0d0d0f; }

    h1 {
        text-align: center;
        color: #c8a96e;
        font-family: Georgia, serif;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #6b6570;
        margin-bottom: 2rem;
        font-family: Georgia, serif;
    }

    /* Input / textarea overrides */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1a1a24 !important;
        color: #e8e0d0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }

    /* Submit button */
    .stFormSubmitButton > button {
        background-color: #c8a96e !important;
        color: #0d0d0f !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button:hover { opacity: 0.85 !important; }

    div[data-testid="stDivider"] { border-color: rgba(255,255,255,0.07); }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────
st.markdown("<h1>The Whisper Wall</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Leave your thoughts. No name. No judgment. Just words.</p>",
    unsafe_allow_html=True
)

# ── Compose form ─────────────────────────────────────────
with st.form("whisper_form", clear_on_submit=True):
    recipient = st.text_input("To", placeholder="Who is this for? (name, nickname…)")
    message   = st.text_area("Your Message", max_chars=500, placeholder="What's on your mind?")
    submitted = st.form_submit_button("✦ Send Anonymously")

    if submitted:
        if message.strip():
            new_msg = {
                "to":   recipient.strip(),
                "text": message.strip(),
                "time": datetime.now(),
            }
            st.session_state.messages.insert(0, new_msg)
            save_messages(st.session_state.messages)   # ← persist to disk
            st.success("✦ Your message has been shared")
        else:
            st.error("Please write a message first.")

st.divider()

# ── Search ───────────────────────────────────────────────
search = st.text_input(
    "Find messages",
    placeholder="Type your name to see messages left for you…"
).strip().lower()

# ── Filter ───────────────────────────────────────────────
filtered = st.session_state.messages
if search:
    filtered = [
        m for m in filtered
        if m["to"] and search in m["to"].lower()
    ]

# ── Count ────────────────────────────────────────────────
count = len(filtered)
label = f"{count} whisper{'s' if count != 1 else ''}"
if search and count > 0:
    label += f' for "{search}"'
st.caption(label)

# ── Display messages ─────────────────────────────────────
if filtered:
    for msg in filtered:
        to_name   = html.escape(msg["to"]) if msg["to"] else "Anonymous"
        body      = html.escape(msg["text"])
        timestamp = msg["time"].strftime("%b %d · %I:%M %p") if isinstance(msg["time"], datetime) else str(msg["time"])

        st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #1a1a24, #1e1c2a);
    padding: 24px 28px;
    border-radius: 16px;
    margin-bottom: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 6px 28px rgba(0,0,0,0.3);
    position: relative;
">
    <div style="
        color: #c8a96e;
        font-style: italic;
        font-size: 1.05rem;
        margin-bottom: 12px;
        font-family: Georgia, serif;
        letter-spacing: 0.02em;
    ">To: {to_name}</div>

    <div style="
        color: #e8e0d0;
        font-size: 0.97rem;
        line-height: 1.85;
        margin-bottom: 16px;
        white-space: pre-wrap;
        word-break: break-word;
        font-family: Georgia, serif;
    ">{body}</div>

    <div style="
        color: #6b6570;
        font-size: 0.75rem;
        border-top: 1px solid rgba(255,255,255,0.06);
        padding-top: 10px;
        letter-spacing: 0.06em;
    ">✦ Anonymous &nbsp;·&nbsp; {timestamp}</div>
</div>
        """, unsafe_allow_html=True)

else:
    if search:
        st.markdown(f"""
<div style="text-align:center; padding: 40px 0; color: #6b6570; font-family: Georgia, serif; font-style: italic;">
    No messages found for "<strong style="color:#c8a96e">{html.escape(search)}</strong>" yet…<br>
    <span style="font-size:0.85rem">maybe someone's still writing one ✨</span>
</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="text-align:center; padding: 40px 0; color: #6b6570; font-family: Georgia, serif; font-style: italic;">
    No whispers yet. Be the first to speak.
</div>
        """, unsafe_allow_html=True)
