import os

def run(**args):
    print("[*] Passwd")
    with open("/etc/passwd", "rb") as file:
        return file.read()
