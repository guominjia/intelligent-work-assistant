import openvino_genai
from queue import Queue, Empty
from threading import Event, Thread

token_queue = Queue()
generation_done = Event()

class OpenVinoLlm:
    def __init__(self, model_dir: str, device: str, max_tokens=100, temperature=0.6, do_sample=True):
        self.pipe = openvino_genai.LLMPipeline(model_dir, device)

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