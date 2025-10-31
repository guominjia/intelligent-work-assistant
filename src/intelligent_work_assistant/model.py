import openvino_genai
from transformers import AutoTokenizer
from queue import Queue, Empty
from threading import Event, Thread
import json, re

token_queue = Queue()
generation_done = Event()

SYSTEM_PROMPT = "You are a helpful assistant."

class OpenVinoLlm:
    def __init__(self, model_dir: str, device: str, max_tokens=100, temperature=0.6, do_sample=True):
        self.pipe = openvino_genai.LLMPipeline(model_dir, device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)

        self.config = openvino_genai.GenerationConfig()
        if (max_tokens != 0): self.config.max_new_tokens = max_tokens
        self.config.do_sample = do_sample
        self.config.temperature = temperature

    def start_chat(self):
        self.pipe.start_chat()

    def stream(self, prompt, streamer=None):
        if streamer is None: streamer = self.streamer

        generation_done.clear()
        Thread(target=self.generate, args=(prompt, streamer,)).start()
        while not (generation_done.is_set() and token_queue.empty()):
            try:
                yield token_queue.get(timeout=0.1)
            except Empty:
                pass

    def generate(self, prompt, streamer):
        self.pipe.generate(prompt, self.config, streamer)
        generation_done.set()

    def streamer(self, subword):
        token_queue.put(subword)
        return False

    def finish_chat(self):
        self.pipe.finish_chat()

    def build_react_prompt(self, prompt,  tools, system_prompt=SYSTEM_PROMPT):
        messages = [{"role": "system", "content": system_prompt}]
        if not isinstance(prompt, str):
            messages += prompt 
        else:
            messages.append({"role": "user", "content": prompt})

        ids = self.tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True)
        prompt = self.tokenizer.decode(ids)

        return prompt
    
    def parse_tool_call(self, response):
        tool_call_text = response
        if '</think>' in response:
            tool_call_text = response.split('</think>')[-1]
        tool_call = re.search(r'<tool_call>(.*?)</tool_call>', tool_call_text, re.DOTALL)
        if tool_call:
            return json.loads(tool_call.group(1))