import pyautogui
import time
import pyperclip

# 将中文复制到剪贴板
pyperclip.copy("你\n好")
time.sleep(3)
pyautogui.hotkey('Ctrl', 'V')

# time.sleep(1)
# pyautogui.press('enter')
time.sleep(3)
pyautogui.write('123456这是测试')
time.sleep(1)
# pyautogui.press('enter')
