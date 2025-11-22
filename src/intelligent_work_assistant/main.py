import subprocess
import argparse
import os
import sys
import multiprocessing

from .index import index

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help="The Text-Generation model")
    parser.add_argument('--embed-model', help="The Embedding model")
    parser.add_argument('--index-only', action="store_true", help="Only index the document, mail, onenote, etc. Skip start web app. It is used to index in backend")
    args = parser.parse_args()
    if not os.path.isdir(args.model) or not os.path.isdir(args.embed_model):
        raise FileNotFoundError('Error: Text-Generation or Embedding model not found, follow README to download model first')

    if args.index_only:
        index(args.embed_model)
        exit(0)

    process = multiprocessing.Process(target=index, args=(args.embed_model,))
    process.start()

    app = __file__.replace('main.py', 'st_main.py')
    subprocess.run(["streamlit", "run" , app, "--"] + sys.argv[1:], shell=True)