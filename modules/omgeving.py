import os

def run(**args):
    print("[*] In module omgeving")
    return str(os.environ).encode()
