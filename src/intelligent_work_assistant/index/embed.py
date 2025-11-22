from optimum.intel import OVModelForFeatureExtraction

import torch
import torch.nn.functional as F

from torch import Tensor
from transformers import AutoTokenizer

def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    left_padding = attention_mask[:, -1].sum() == attention_mask.shape[0]
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


def get_detailed_instruct(task_description: str, query: str) -> str:
    return f"Instruct: {task_description}\nQuery:{query}"

# Each query must come with a one-sentence instruction that describes the task
task = "Given a web search query, retrieve relevant passages that answer the query"

def embedding_function(texts, model_dir, max_length=8192):
    model = OVModelForFeatureExtraction.from_pretrained(model_dir, device="CPU", export=False, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_dir, padding_side="left", trust_remote_code=True)

    batch_dict = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
    )
    batch_dict.to(model.device)
    outputs = model(**batch_dict)
    embeddings = last_token_pool(outputs.last_hidden_state, batch_dict["attention_mask"])
    # normalize embeddings
    embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings.tolist()

def query_function(query, model_dir, max_length=8192, task=task):
    queries = [get_detailed_instruct(task, query)]
    return embedding_function(queries, model_dir, max_length=max_length)