import os
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv
import streamlit as st

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
load_dotenv()

st.set_page_config(page_title="ChatWise", page_icon="🤖", layout="wide")

DEFAULT_MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
FAST_MODEL = DEFAULT_MODEL  # Use the default working model for validation to prevent 404 errors

# Define the precise modes and their validation rules
MODES = {
    "General Assistant": {
        "description": "You are a helpful AI assistant. Answer any general questions.",
        "validation_rule": "Accept everything. Return true for any topic.",
        "rejection_msg": ""
    },
    "Coding": {
        "description": "You are an expert software engineer. Provide clean, efficient code.",
        "validation_rule": "Accept only programming, software development, debugging, algorithms, DSA, Git, Linux, and tech-related queries (Python, Java, C++, JS, HTML, CSS, SQL). Reject History, Politics, Movies, Sports, Medical, Travel, etc.",
        "rejection_msg": "❌ This question is outside Coding Mode.\n\nPlease switch to General Assistant Mode if you want answers outside programming."
    },
    "Student": {
        "description": "You are a helpful tutor for school and college subjects. Explain clearly.",
        "validation_rule": "Accept only School, College, Math, Physics, Chemistry, Biology, English, Assignments, and Homework topics. Reject Politics, Movies, Cricket, Entertainment.",
        "rejection_msg": "❌ This question is outside Student Mode.\n\nPlease switch to General Assistant Mode if you want answers outside academic studies."
    },
    "Teacher": {
        "description": "You explain concepts like an experienced teacher, using structured breakdowns.",
        "validation_rule": "Accept only educational, pedagogical, and academic topics. Reject unrelated casual topics.",
        "rejection_msg": "❌ This question is outside Teacher Mode.\n\nPlease switch to General Assistant Mode for non-educational queries."
    },
    "Writer": {
        "description": "You are a professional content writer and grammar expert.",
        "validation_rule": "Accept only Blogs, Emails, Essays, Stories, Grammar, and Writing tasks. Reject everything else.",
        "rejection_msg": "❌ This question is outside Writer Mode.\n\nPlease switch to General Assistant Mode for non-writing tasks."
    },
    "Translator": {
        "description": "You are a professional translator. Translate text accurately.",
        "validation_rule": "Accept only translation requests, language learning, and linguistics. Reject all other queries.",
        "rejection_msg": "❌ This question is outside Translator Mode.\n\nPlease switch to General Assistant Mode for tasks other than translation."
    },
    "Math": {
        "description": "You are a mathematics expert. Solve math problems accurately.",
        "validation_rule": "Accept only mathematics, algebra, calculus, geometry, and arithmetic. Reject all other queries.",
        "rejection_msg": "❌ This question is outside Math Mode.\n\nPlease switch to General Assistant Mode for non-mathematical queries."
    },
    "Career": {
        "description": "You are a career coach and placement expert.",
        "validation_rule": "Accept only Resume, Interview, Placement, Internship, and Career guidance topics. Reject unrelated topics.",
        "rejection_msg": "❌ This question is outside Career Mode.\n\nPlease switch to General Assistant Mode for non-career queries."
    }
}

# -----------------------------------------------------------------------------
# Core State Management
# -----------------------------------------------------------------------------
def init_session_state() -> None:
    """Initialize necessary session state variables for ChatWise."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mode" not in st.session_state:
        st.session_state.mode = "General Assistant"

# -----------------------------------------------------------------------------
# Gemini API Interaction
# -----------------------------------------------------------------------------
def get_client() -> Optional[Any]:
    """Retrieve the Gemini client using the environment API key."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or genai is None:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Client init error: {e}")
        return None


def is_valid_intent(client: Any, prompt: str, mode_name: str) -> bool:
    """
    Perform a strict validation check on the user's prompt using a lightweight
    structured API call. If it returns False, the prompt is rejected.
    """
    if mode_name == "General Assistant":
        return True
        
    mode_config = MODES[mode_name]
    validation_rule = mode_config["validation_rule"]
    
    # We use structured output to enforce a boolean return
    schema = {"type": "OBJECT", "properties": {"valid": {"type": "BOOLEAN"}}}
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
        system_instruction=f"You are an intent classifier. Evaluate the user's prompt based strictly on this rule: {validation_rule}. Return JSON with valid=true if it matches, and valid=false if it should be rejected.",
        temperature=0.0 # Strict classification
    )
    
    try:
        response = client.models.generate_content(
            model=FAST_MODEL,
            contents=prompt,
            config=config
        )
        if response.text and "false" in response.text.lower():
            return False
        return True
    except Exception:
        # If classification fails (e.g., rate limit), fail open so the user isn't blocked completely
        return True


def format_messages_for_gemini(messages: List[Dict[str, str]]) -> List[Any]:
    """Convert session state messages into google-genai Content format, clipping to last 50."""
    contents = []
    # Retain only the last 50 messages to optimize context window and tokens
    for msg in messages[-50:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
        )
    return contents


def stream_gemini_response(client: Any, contents: List[Any], mode_name: str, placeholder: Any) -> Optional[str]:
    """
    Stream the response from the Gemini API, attempting fallback models automatically
    if quota or availability errors occur.
    """
    system_prompt = MODES[mode_name]["description"]
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
    )
    
    models_to_try = [DEFAULT_MODEL] + FALLBACK_MODELS
    last_error = None
    
    for model_name in models_to_try:
        try:
            full_text = ""
            stream = client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=config,
            )
            for chunk in stream:
                if getattr(chunk, "text", None):
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
            
            final_text = full_text.strip() if full_text else "No response generated."
            placeholder.markdown(final_text)
            return final_text
            
        except Exception as exc:
            last_error = exc
            err_msg = str(exc).lower()
            # Suppress hard quota or unavailable model errors to trigger fallback
            if any(k in err_msg for k in ["not found", "invalid model", "404", "429", "quota", "resource_exhausted"]):
                continue
            # Break immediately on critical auth errors
            placeholder.error(f"⚠️ Error: {exc}")
            return None
            
    # If all models exhausted
    if last_error:
        err_str = str(last_error).lower()
        if "quota" in err_str or "429" in err_str:
            placeholder.error("📊 API quota exceeded across all models. Please check your Google AI Studio usage limits.")
        elif "api key" in err_str or "401" in err_str or "unauthenticated" in err_str:
            placeholder.error("🔑 Invalid API key. Please check your .env file.")
        else:
            placeholder.error(f"🤖 All models failed. Last error: {last_error}")
    else:
        placeholder.error("🤖 An unknown error occurred.")
        
    return None

# -----------------------------------------------------------------------------
# UI Rendering
# -----------------------------------------------------------------------------
def render_sidebar() -> None:
    """Render the configuration sidebar."""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        selected_mode = st.selectbox(
            "Select AI Mode",
            options=list(MODES.keys()),
            index=list(MODES.keys()).index(st.session_state.mode)
        )
        
        # If mode changed, update state (we could clear chat here if desired, but user didn't ask)
        st.session_state.mode = selected_mode
        st.caption(MODES[selected_mode]["description"])
        
        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_chat_history() -> None:
    """Render the existing chat messages."""
    if not st.session_state.messages:
        st.info("👋 Welcome to ChatWise! Type a message below to start.")
        return
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def process_user_input(client: Any) -> None:
    """Handle the chat input submission natively top-down without redundant reruns."""
    user_prompt = st.chat_input("Ask anything...")
    
    if not user_prompt:
        return
        
    # Append and render user message immediately
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
        
    current_mode = st.session_state.mode
    
    # 1. STRICT MODE VALIDATION
    with st.spinner("Validating request..."):
        is_valid = is_valid_intent(client, user_prompt, current_mode)
        
    if not is_valid:
        # Reject without generation
        rejection_msg = MODES[current_mode]["rejection_msg"]
        st.session_state.messages.append({"role": "assistant", "content": rejection_msg})
        with st.chat_message("assistant"):
            st.error(rejection_msg)
        return
        
    # 2. PROCEED TO GEMINI GENERATION
    contents = format_messages_for_gemini(st.session_state.messages)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("💭 Generating...")
        
        answer = stream_gemini_response(client, contents, current_mode, placeholder)
        
        if answer:
            st.session_state.messages.append({"role": "assistant", "content": answer})


def main() -> None:
    """Main application loop."""
    init_session_state()
    
    st.title("🤖 ChatWise")
    st.caption("Professional Gemini AI Assistant with Strict Roles")
    
    client = get_client()
    if not client:
        st.error("🚨 `GEMINI_API_KEY` not found in `.env` or invalid. Please configure it to continue.")
        st.stop()
        
    render_sidebar()
    render_chat_history()
    process_user_input(client)


if __name__ == "__main__":
    main()