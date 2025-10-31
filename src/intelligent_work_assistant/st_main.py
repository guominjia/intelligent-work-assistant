import argparse
import re
import os
import json
import uuid
from typing import List, Tuple
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

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': 'Get the current weather in a given city name.',
            'parameters': {
            'type': 'object',
            'properties': {
                'city': {
                'type': 'str',
                'description': 'City name'
                }
            },
            'required': ['city']
            }
        }
    }
]

import requests

def call_tool(tool_name: str, tool_args: dict) -> str:
    if tool_name == "get_weather":
        key_selection = {
            "current_condition": [
                "temp_C",
                "FeelsLikeC",
                "humidity",
                "weatherDesc",
                "observation_time",
            ],
        }
        resp = requests.get(f"https://wttr.in/{tool_args['city']}?format=j1")
        resp.raise_for_status()
        resp = resp.json()
        ret = {k: {_v: resp[k][0][_v] for _v in v} for k, v in key_selection.items()}
        return json.dumps(ret, ensure_ascii=False)
    
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
                for think, body in extract_think_body(message["content"]):
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

        def stream(prompt):
            nonlocal full_response
            for c in llm.stream(prompt):
                full_response += c
                yield c

        llm.start_chat()
        response_placeholder.write_stream(stream(st.session_state.llm.build_react_prompt(prompt, tools)))
        llm.finish_chat()
        tool = st.session_state.llm.parse_tool_call(full_response)
        if tool:
            result = call_tool(tool['name'], tool['arguments'])
            messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content":"", "tool_calls": [{"type": "function", "function": tool}]}, {"role": "tool", "content": result}]
            print(messages)
            llm.start_chat()
            response_placeholder.write_stream(stream(st.session_state.llm.build_react_prompt(messages, tools)))
            llm.finish_chat()

        for i, (think, body) in enumerate(extract_think_body(full_response)):
            if i==0:
                think_placeholder.write(think)
                response_placeholder.markdown(body)
            else:
                with st.expander('think'):
                    st.write(think)
                st.markdown(body)

    return full_response

def extract_think_body(full_response: str) -> List[Tuple[str, str]]:
    matches = re.findall(r'<think>(.*?)</think>(.*)', full_response, re.DOTALL)
    if matches:
        return [(think, body) for think, body in matches]
    return [("","")]

if __name__ == '__main__':
    main()