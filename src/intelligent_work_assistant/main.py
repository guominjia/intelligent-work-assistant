import subprocess
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help="The Text-Generation model")
    parser.add_argument('--embed-model', help="The Embedding model")
    args = parser.parse_args()
    if not os.path.isdir(args.model) or not os.path.isdir(args.embed_model):
        raise FileNotFoundError('Error: Text-Generation or Embedding model not found, follow README to download model first')

    app = __file__.replace('main.py', 'st_main.py')
    subprocess.run(["streamlit", "run" , app, "--"] + sys.argv[1:], shell=True)