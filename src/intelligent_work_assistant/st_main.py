import argparse
import re
import os
import json
import uuid
from typing import List, Tuple
import streamlit as st
from intelligent_work_assistant.model import OpenVinoLlm
from intelligent_work_assistant.tools import tools, call_tool

def main():
    args = parse_args()

    if 'llm' not in st.session_state:
        st.session_state.llm = OpenVinoLlm(args.model, args.device, max_tokens=args.max_tokens)

    if 'current_thread' not in st.session_state:
        st.session_state.current_thread = str(uuid.uuid4())

    if 'history_path' not in st.session_state:
        st.session_state.history_path = args.history_path

    sidebar_nav(args.history_path)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help="The Text-Generation model")
    parser.add_argument('--embed-model', help="The Embedding model")
    parser.add_argument('--device', default="CPU", help="The device on where the model run, default CPU")
    parser.add_argument('--max-tokens', default=0, help="The max tokens to generate, default 0 mean no limitation")
    parser.add_argument('--history-path', default="threads-history", help="The path to where save the history")
    return parser.parse_args()

def sidebar_nav(history_path):
    home_pg = st.Page(home, title="Home", icon=":material/home:")
    new_chat = st.Page(new_conversation, title="new", icon=":material/add:", url_path="new")
    login_pg = st.Page(login, title="Log in", icon=":material/login:")
    logout_pg = st.Page(logout, title="Log out", icon=":material/logout:")
    pg = st.navigation({"Home":[home_pg], "Chat":[new_chat], "History": create_thread_pages(history_path), "Log in/out":[login_pg, logout_pg]})
    pg.run()

def home():
    history_chats()
    if prompt := st.chat_input("What can i help?"):
        full_response = real_chat(st.session_state.llm, prompt)
        add_chat_to_history([{"role": "user", "content": prompt}, {"role": "assistant", "content": full_response}], st.session_state.history_path)

def login():
    st.write("log in")

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

def new_conversation():
    st.session_state.history = []
    st.session_state.current_thread = str(uuid.uuid4())
    home()

def create_thread_pages(history_path):
    pages = []
    for history in os.listdir(history_path):
        with open(f"{history_path}/{history}", encoding="utf8") as rf:
            title = json.load(rf)[0]["content"]
        pages.append(st.Page(lambda: history_page(history_path), title=title, url_path=f"chats-{history}"))
    return pages

def history_page(history_path):
    history = st.context.url.split('/')[-1][len('chats-'):]
    with open(f"{history_path}/{history}", encoding="utf8") as rf:
        st.session_state.history = json.load(rf)
        st.session_state.current_thread = history
    home()

def history_chats():
    if 'history' not in st.session_state:
        st.session_state.history = []
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            content = message["content"]

            thinks, tool_calls, body = extract_response_components(content)

            for i, tool_call in enumerate(tool_calls):
                with st.expander(f"🔧 Tool Call {i+1}", expanded=False):
                    st.code(tool_call, language="json")

            for i, think in enumerate(thinks):
                with st.expander(f"💭 Think {i+1}", expanded=False):
                    st.write(think)

            if body:
                st.markdown(body)

def add_chat_to_history(chat, history_path):
    for c in chat:
        st.session_state.history.append(c)
    save_history_to_file(history_path)

def save_history_to_file(history_path):
    if not os.path.isdir(history_path):
        os.mkdir(history_path)
    
    with open(f'{history_path}/{st.session_state.current_thread}', 'w', encoding='utf8') as wf:
        json.dump(st.session_state.history, wf)

def real_chat(llm, prompt):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        def stream(prompt):
            nonlocal full_response
            llm.start_chat()
            for c in llm.stream(prompt):
                full_response += c
                yield c
            llm.finish_chat()

        response_placeholder.write_stream(stream(st.session_state.llm.build_react_prompt(prompt, tools)))
        while tool := st.session_state.llm.parse_tool_call(full_response):
            result = call_tool(tool['name'], tool['arguments'])
            messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content":"", "tool_calls": [{"type": "function", "function": tool}]}, {"role": "tool", "content": result}]
            response_placeholder.write_stream(stream(st.session_state.llm.build_react_prompt(messages, tools)))

        thinks, tool_calls, body = extract_response_components(full_response)

        for i, tool_call in enumerate(tool_calls):
            with st.expander(f"🔧 Tool Call {i+1}", expanded=False):
                st.code(tool_call, language="json")

        for i, think in enumerate(thinks):
            with st.expander(f"💭 Think {i+1}", expanded=False):
                st.write(think)

        response_placeholder.markdown(body)

    return full_response

def extract_response_components(full_response: str) -> Tuple[List[str], List[str], str]:
    """
    Extract think blocks, tool_call blocks, and the main body from the response.
    Returns: (list of thinks, list of tool_calls, main body text)
    """
    thinks = []
    tool_calls = []
    body = full_response
    
    # Extract all <think> blocks
    think_matches = re.findall(r'<think>(.*?)</think>', full_response, re.DOTALL)
    thinks = [match.strip() for match in think_matches]
    
    # Extract all <tool_call> blocks
    tool_call_matches = re.findall(r'<tool_call>(.*?)</tool_call>', full_response, re.DOTALL)
    tool_calls = [match.strip() for match in tool_call_matches]
    
    # Remove all <think> and <tool_call> blocks from body
    body = re.sub(r'<think>.*?</think>', '', full_response, flags=re.DOTALL)
    body = re.sub(r'<tool_call>.*?</tool_call>', '', body, flags=re.DOTALL)
    body = body.strip()
    
    return thinks, tool_calls, body

if __name__ == '__main__':
    main()