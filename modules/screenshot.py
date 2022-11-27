import os
import pyautogui

def run(**args):
    print("[*] Taking screenshot.")

    image = pyautogui.screenshot()
    image.save("test.jpg")

    with open("test.jpg", "rb") as file:
        im_bytes = file.read()

    os.remove("test.jpg")

    return im_bytes
