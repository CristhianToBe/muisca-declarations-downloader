import threading, time, pyautogui

def _anti_idle():
    while True:
        pyautogui.keyDown("ctrl")
        time.sleep(0.1)
        pyautogui.keyUp("ctrl")
        time.sleep(60)

def start():
    threading.Thread(target=_anti_idle, daemon=True).start()
