import win32gui
import win32api
import win32con
import time

def find_game_window(target_title="League of Legends (TM) Client"):
    """
    精确查找游戏窗口句柄
    """
    result_hwnd = None
    
    def callback(hwnd, target):
        nonlocal result_hwnd
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if window_title == target:
                result_hwnd = hwnd
                return False  # 找到后停止枚举
        return True
    
    win32gui.EnumWindows(callback, target_title)
    
    if result_hwnd is None:
        raise Exception(f"找不到窗口: {target_title}")
    
    print(f"找到窗口 - 句柄: {result_hwnd}, 标题: {target_title}")
    return result_hwnd

def send_message(text):
    try:
        # 获取游戏窗口句柄
        hwnd = find_game_window()
        
        # 确保窗口在前台
        if win32gui.GetForegroundWindow() != hwnd:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)  # 等待窗口切换
        
        # 按下回车打开聊天框
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        
        # 发送文本
        for c in text:
            win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(c), 0)
            time.sleep(0.05)
        
        # 按下回车发送
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        
    except Exception as e:
        print(f"发送消息时出错: {e}")

# 更完整的实现示例
class GameInput:
    def __init__(self, window_title="League of Legends (TM) Client"):
        self.window_title = window_title
        self.hwnd = None
    
    def ensure_window_handle(self):
        """
        确保有有效的窗口句柄
        """
        if self.hwnd is None or not win32gui.IsWindow(self.hwnd):
            self.hwnd = find_game_window(self.window_title)
        return self.hwnd
    
    def is_window_active(self):
        """
        检查游戏窗口是否在前台
        """
        try:
            return win32gui.GetForegroundWindow() == self.ensure_window_handle()
        except:
            return False
    
    def activate_window(self):
        """
        将游戏窗口切换到前台
        """
        try:
            hwnd = self.ensure_window_handle()
            if not self.is_window_active():
                # 尝试多种方式激活窗口
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    # 备用方法
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.1)
            return True
        except Exception as e:
            print(f"激活窗口失败: {e}")
            return False
    
    def send_key(self, vk_code, key_up=False):
        """
        发送按键
        """
        try:
            if self.activate_window():
                win32api.keybd_event(
                    vk_code, 
                    0, 
                    win32con.KEYEVENTF_KEYUP if key_up else 0, 
                    0
                )
                return True
            return False
        except Exception as e:
            print(f"发送按键失败: {e}")
            return False
    
    def send_text(self, text):
        """
        发送文本消息
        """
        try:
            if not self.activate_window():
                return False
            
            # 打开聊天框
            print("正在打开聊天框")
            self.send_key(win32con.VK_RETURN)
            time.sleep(0.1)
            self.send_key(win32con.VK_RETURN, True)
            time.sleep(0.1)
            
            # 发送文本
            print("正在发送文本")
            for c in text:
                win32api.PostMessage(self.hwnd, win32con.WM_CHAR, ord(c), 0)
                time.sleep(0.05)
            
            # 关闭聊天框
            print("正在关闭聊天框")
            self.send_key(win32con.VK_RETURN)
            time.sleep(0.05)
            self.send_key(win32con.VK_RETURN, True)
            
            return True
            
        except Exception as e:
            print(f"发送文本失败: {e}")
            return False

# 使用示例
def main():
    game_input = GameInput()
    
    try:
        # 发送测试消息
        game_input.send_text("Hello World!")
        
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    main()