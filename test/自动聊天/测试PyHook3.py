from ctypes import *
import PyHook3 as pyHook
import pythoncom
 
 
def onKeyboardEvent(event):
    print("onKeyboardEvent")
    pid = c_ulong(0)
    windowTitle = create_string_buffer(512)
    windll.user32.GetWindowTextA(event.Window, byref(windowTitle), 512)
    windll.user32.GetWindowThreadProcessId(event.Window, byref(pid))
    windowName = windowTitle.value.decode('gbk')
    print("当前您处于%s窗口" % windowName)
    print("当前窗口所属进程id %d" % pid.value)
    print("当前刚刚按下了%s键" % str(event.Ascii))
    return True
 
 
hm = pyHook.HookManager()
hm.KeyDown = onKeyboardEvent
hm.HookKeyboard()
pythoncom.PumpMessages()