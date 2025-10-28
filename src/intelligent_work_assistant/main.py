import subprocess

def main():
    app = __file__.replace('main.py', 'st_main.py')
    subprocess.run(f"streamlit run {app}", shell=True)