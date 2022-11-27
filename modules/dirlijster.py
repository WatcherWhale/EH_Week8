import os

def run(**args):
    print("[*] In de dirlijster module.")
    files = os.listdir('.')
    return str(files)