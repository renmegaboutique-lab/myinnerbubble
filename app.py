import streamlit as st
from datetime import datetime
import sqlite3
import html

st.set_page_config(
    page_title="Whisper Wall",
    page_icon="💌",
    layout="centered"
)

# ── Database ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect("whispers.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            text      TEXT NOT NULL,
            created   TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

def load_messages():
    conn = get_db()
    rows = conn.execute(
        "SELECT recipient, text, created FROM messages ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [
        {"to": row[0] or "", "text": row[1], "time": datetime.fromisoformat(row[2])}
        for row in rows
    ]

def save_message(recipient, text):
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (recipient, text, created) VALUES (?, ?, ?)",
        (recipient, text, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def clear_all_messages():
    conn = get_db()
    conn.execute("DELETE FROM messages")
    conn.commit()
    conn.close()

# ── Styles ───────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0d0d0f; }
    h1 { text-align:center; color:#c8a96e; font-family:Georgia,serif; margin-bottom:0; }
    .subtitle { text-align:center; color:#6b6570; margin-bottom:2rem; font-family:Georgia,serif; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1a1a24 !important;
        color: #e8e0d0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }
    .stFormSubmitButton > button {
        background-color: #c8a96e !important;
        color: #0d0d0f !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)

# ── RESET BUTTON (sidebar) ───────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Admin")
    if st.button("🗑️ Clear all messages", type="secondary"):
        clear_all_messages()
        st.success("All messages cleared!")
        st.rerun()

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
            save_message(recipient.strip(), message.strip())
            st.success("✦ Your message has been shared")
        else:
            st.error("Please write a message first.")

st.divider()

# ── Search ───────────────────────────────────────────────
search = st.text_input(
    "Find messages",
    placeholder="Type your name to see messages left for you…"
).strip().lower()

# ── Load & filter ─────────────────────────────────────────
all_messages = load_messages()
filtered = all_messages

if search:
    filtered = [m for m in all_messages if search in m["to"].lower()]

# ── Count ─────────────────────────────────────────────────
count = len(filtered)
label = f"{count} whisper{'s' if count != 1 else ''}"
if search and count > 0:
    label += f' for "{search}"'
st.caption(label)

# ── Display ───────────────────────────────────────────────
if filtered:
    for msg in filtered:
        to_name   = html.escape(msg["to"]) if msg["to"] else "Anonymous"
        body      = html.escape(msg["text"])
        timestamp = msg["time"].strftime("%b %d · %I:%M %p")

        st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #1a1a24, #1e1c2a);
    padding: 24px 28px; border-radius: 16px; margin-bottom: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 6px 28px rgba(0,0,0,0.3);
">
    <div style="color:#c8a96e; font-style:italic; font-size:1.05rem;
                margin-bottom:12px; font-family:Georgia,serif;">
        To: {to_name}
    </div>
    <div style="color:#e8e0d0; font-size:0.97rem; line-height:1.85;
                margin-bottom:16px; white-space:pre-wrap;
                word-break:break-word; font-family:Georgia,serif;">
        {body}
    </div>
    <div style="color:#6b6570; font-size:0.75rem;
                border-top:1px solid rgba(255,255,255,0.06);
                padding-top:10px; letter-spacing:0.06em;">
        ✦ Anonymous &nbsp;·&nbsp; {timestamp}
    </div>
</div>
        """, unsafe_allow_html=True)

else:
    if search:
        st.markdown(f"""
<div style="text-align:center; padding:40px 0; color:#6b6570;
            font-family:Georgia,serif; font-style:italic;">
    No messages found for "<strong style="color:#c8a96e">{html.escape(search)}</strong>" yet…<br>
    <span style="font-size:0.85rem">maybe someone's still writing one ✨</span>
</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="text-align:center; padding:40px 0; color:#6b6570;
            font-family:Georgia,serif; font-style:italic;">
    No whispers yet. Be the first to speak.
</div>
        """, unsafe_allow_html=True)
