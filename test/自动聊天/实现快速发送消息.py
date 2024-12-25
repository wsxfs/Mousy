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
    # 在新线程中模拟按键



    kb.press(Key.enter)
    kb.release(Key.enter)
    time.sleep(0.01)
    kb.type("maren ")
    kb.press(Key.enter)
    kb.release(Key.enter)


    is_simulating = False

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char == 'q' and not is_simulating:
            print("Q pressed, simulating multiple Q presses")
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
