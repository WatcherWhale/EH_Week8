import urllib.request

def run(**args):
    print("[*] IP")
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    return external_ip.encode()

