from pynput import keyboard
from pynput.keyboard import Key, Controller
import time
import threading

# 创建键盘控制器
kb = Controller()
is_simulating = False

def simulate_keys():
    global is_simulating
    is_simulating = True
    for _ in range(20):
        kb.press(Key.f6)
        kb.release(Key.f6)
    is_simulating = False  # 模拟完成后直接重置标志

def on_press(key):
    try:
        if key == Key.f6 and not is_simulating:
            print("F6 pressed, simulating multiple F6 presses")
            # 创建新线程来处理按键模拟
            thread = threading.Thread(target=simulate_keys)
            thread.start()
    except AttributeError:
        pass

def on_release(key):
    if key == Key.esc:
        return False

# 设置监听器
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
