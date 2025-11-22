import unittest
from intelligent_work_assistant.index.mail import query_mail

class TestQueryMail(unittest.TestCase):
    def test_query_mail(self):
        embed_model = "Qwen3-Embedding-0.6B-int8-ov"
        print(query_mail("Summarize my work report", 3, embed_model, "chroma_database"))