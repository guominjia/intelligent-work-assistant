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
    llm = st.session_state.llm

    if 'current_thread' not in st.session_state:
        st.session_state.current_thread = str(uuid.uuid4())

    sidebar_nav()
    history_chats()
    if prompt := st.chat_input("What can i help?"):
        full_response = real_chat(llm, prompt)
        add_chat_to_history([{"role": "user", "content": prompt}, {"role": "assistant", "content": full_response}], args.history_path)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help="The Text-Generation model")
    parser.add_argument('--embed-model', help="The Embedding model")
    parser.add_argument('--device', default="CPU", help="The device on where the model run, default CPU")
    parser.add_argument('--max-tokens', default=0, help="The max tokens to generate, default 0 mean no limitation")
    parser.add_argument('--history-path', default="threads-history", help="The path to where save the history")
    return parser.parse_args()

def sidebar_nav():
    with st.sidebar:
        st.markdown("### 🏠 Navigation")

        if st.button("New Conversation"):
            st.session_state.history = []

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