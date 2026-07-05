import os
import json
import uuid
import streamlit as st
from typing import Any, List, Dict, Optional
from modes import MODES, LEVELS, get_system_prompt

CHATS_FILE = "chats.json"

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

DEFAULT_MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
FAST_MODEL = DEFAULT_MODEL

def load_all_chats() -> dict:
    if not os.path.exists(CHATS_FILE):
        return {}
    try:
        with open(CHATS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_chats(data: dict) -> None:
    with open(CHATS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_chats(username: str) -> dict:
    all_chats = load_all_chats()
    return all_chats.get(username, {})

def save_user_chats(username: str, user_chats: dict) -> None:
    all_chats = load_all_chats()
    all_chats[username] = user_chats
    save_all_chats(all_chats)

def get_client() -> Optional[Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or genai is None:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Client init error: {e}")
        return None

def is_valid_intent(client: Any, prompt: str, mode_name: str) -> bool:
    if mode_name == "General":
        return True
        
    mode_config = MODES[mode_name]
    validation_rule = mode_config["validation_rule"]
    
    schema = {"type": "OBJECT", "properties": {"valid": {"type": "BOOLEAN"}}}
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
        system_instruction=f"You are a strict intent classifier. Evaluate the user's prompt based strictly on this rule: {validation_rule}. Return JSON with valid=true if it matches, and valid=false if it should be rejected.",
        temperature=0.0
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
        return True

def format_messages_for_gemini(messages: List[Dict[str, str]]) -> List[Any]:
    contents = []
    # Using last 20 messages to keep context window manageable
    for msg in messages[-20:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
        )
    return contents

def stream_gemini_response(client: Any, contents: List[Any], mode_name: str, level_name: str, placeholder: Any) -> Optional[str]:
    system_prompt = get_system_prompt(mode_name, level_name)
    
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
            if any(k in err_msg for k in ["not found", "invalid model", "404", "429", "quota", "resource_exhausted"]):
                continue
            placeholder.error(f"⚠️ Error: {exc}")
            return None
            
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

def render_sidebar():
    username = st.session_state.username
    user_chats = get_user_chats(username)
    
    with st.sidebar:
        st.header(f"👤 {username}")
        if st.button("Profile & Settings", use_container_width=True):
            st.session_state.page = "profile"
            st.rerun()
            
        st.divider()
        
        st.header("⚙️ Chat Settings")
        selected_mode = st.selectbox(
            "Select AI Mode",
            options=list(MODES.keys()),
            index=list(MODES.keys()).index(st.session_state.get("mode", "General"))
        )
        st.session_state.mode = selected_mode
        st.caption(MODES[selected_mode]["description"])
        
        selected_level = st.selectbox(
            "Explanation Level",
            options=list(LEVELS.keys()),
            index=list(LEVELS.keys()).index(st.session_state.get("level", "Beginner"))
        )
        st.session_state.level = selected_level
        st.caption(LEVELS[selected_level])
        
        st.divider()
        
        st.header("🗂️ Chat History")
        if st.button("➕ New Chat", use_container_width=True):
            new_id = str(uuid.uuid4())
            user_chats[new_id] = {"title": "New Chat", "messages": []}
            save_user_chats(username, user_chats)
            st.session_state.current_chat_id = new_id
            st.rerun()
            
        chat_options = {cid: data["title"] for cid, data in user_chats.items()}
        if chat_options:
            selected_chat = st.radio("Your Chats", options=list(chat_options.keys()), format_func=lambda x: chat_options[x], label_visibility="collapsed")
            if selected_chat and selected_chat != st.session_state.get("current_chat_id"):
                st.session_state.current_chat_id = selected_chat
                st.rerun()
                
            current_id = st.session_state.get("current_chat_id")
            if current_id in user_chats:
                col1, col2 = st.columns(2)
                with col1:
                    chat_data = json.dumps(user_chats[current_id]["messages"], indent=2)
                    st.download_button("📥 Export", data=chat_data, file_name=f"chat_{current_id}.json", mime="application/json", use_container_width=True)
                with col2:
                    if st.button("🗑️ Delete", use_container_width=True):
                        del user_chats[current_id]
                        save_user_chats(username, user_chats)
                        st.session_state.current_chat_id = None
                        st.rerun()

def render_chat_page():
    client = get_client()
    if not client:
        st.error("🚨 `GEMINI_API_KEY` not found in `.env` or invalid. Please configure it to continue.")
        return
        
    username = st.session_state.username
    user_chats = get_user_chats(username)
    
    if not user_chats:
        new_id = str(uuid.uuid4())
        user_chats[new_id] = {"title": "New Chat", "messages": []}
        save_user_chats(username, user_chats)
        st.session_state.current_chat_id = new_id
        
    current_id = st.session_state.get("current_chat_id")
    if not current_id or current_id not in user_chats:
        current_id = list(user_chats.keys())[0] if user_chats else None
        st.session_state.current_chat_id = current_id
        
    render_sidebar()
    
    st.title("🎓 ChatWise AI Tutor")
    
    if not current_id:
        st.info("Click 'New Chat' to begin.")
        return
        
    messages = user_chats[current_id]["messages"]
    
    if not messages:
        st.info("🎓 Welcome! Select a mode and level, then ask a question.")
    
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    user_prompt = st.chat_input("Ask anything...")
    if user_prompt:
        # Generate title if it's the first message
        if len(messages) == 0:
            user_chats[current_id]["title"] = user_prompt[:30] + ("..." if len(user_prompt) > 30 else "")
            
        messages.append({"role": "user", "content": user_prompt})
        user_chats[current_id]["messages"] = messages
        save_user_chats(username, user_chats)
        
        with st.chat_message("user"):
            st.markdown(user_prompt)
            
        current_mode = st.session_state.get("mode", "General")
        current_level = st.session_state.get("level", "Beginner")
        
        with st.spinner("Validating request..."):
            is_valid = is_valid_intent(client, user_prompt, current_mode)
            
        if not is_valid:
            rejection_msg = MODES[current_mode]["rejection_msg"]
            messages.append({"role": "assistant", "content": rejection_msg})
            user_chats[current_id]["messages"] = messages
            save_user_chats(username, user_chats)
            with st.chat_message("assistant"):
                st.error(rejection_msg)
            return
            
        contents = format_messages_for_gemini(messages)
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("💭 Generating...")
            
            answer = stream_gemini_response(client, contents, current_mode, current_level, placeholder)
            
            if answer:
                messages.append({"role": "assistant", "content": answer})
                user_chats[current_id]["messages"] = messages
                save_user_chats(username, user_chats)
