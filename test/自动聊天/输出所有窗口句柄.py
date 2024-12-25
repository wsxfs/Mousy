import win32gui

def list_all_windows():
    """
    列出所有可见窗口的句柄、标题和类名
    """
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            window_class = win32gui.GetClassName(hwnd)
            if window_title:  # 只显示有标题的窗口
                windows.append({
                    "句柄": hwnd,
                    "标题": window_title,
                    "类名": window_class
                })
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    
    # 按句柄排序并打印
    for window in sorted(windows, key=lambda x: x["句柄"]):
        print(f'句柄: {window["句柄"]:10} | 标题: {window["标题"][:50]:50} | 类名: {window["类名"]}')

if __name__ == "__main__":
    list_all_windows()