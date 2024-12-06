import win32ui
import win32gui
import win32con
import win32api

def extract_icon(exe_path):
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
    
    large, small = win32gui.ExtractIconEx(exe_path, 0)
    win32gui.DestroyIcon(small[0])
    
    # 返回第一个图标
    return large[0]

if __name__ == "__main__":
    exe_path = r"release/0.0.0/win-unpacked/YourAppName.exe"
    icon = extract_icon(exe_path)
    
    # 获取系统图标实际尺寸
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
    
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    # 使用更大的尺寸，比如256x256或系统实际图标尺寸
    # hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
    hbmp.CreateCompatibleBitmap(hdc, 256, 256)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    # 使用实际尺寸绘制
    hdc.DrawIcon((0,0), icon)
    hbmp.SaveBitmapFile(hdc, r"C:\Users\wsxfs\Desktop\icon.ico")