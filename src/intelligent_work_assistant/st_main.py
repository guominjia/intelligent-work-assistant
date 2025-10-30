import argparse
import re
import os
import json
import uuid
import streamlit as st
from intelligent_work_assistant.model import OpenVinoLlm

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
            if '<think>' in message["content"]:
                think, body = extract_think_body(message["content"])
                with st.expander('think'):
                    st.write(think)
                st.markdown(body)
            else:
                st.markdown(message["content"])

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
        think_placeholder = st.expander('think')
        response_placeholder = st.empty()
        full_response = ""

        def stream():
            nonlocal full_response
            for c in llm.stream(prompt):
                full_response += c
                yield c

        llm.start_chat()
        response_placeholder.write_stream(stream())
        llm.finish_chat()

        think, body = extract_think_body(full_response)
        think_placeholder.write(think)
        response_placeholder.markdown(body)

    return full_response

def extract_think_body(full_response: str) -> str:
    match = re.search(r'<think>(.*?)</think>(.*)', full_response, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return ""

if __name__ == '__main__':
    main()