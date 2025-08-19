#Requires AutoHotkey v2

winTitle := "微信"  
hwnd := WinExist(winTitle)
if not hwnd {
    MsgBox "未找到微信窗口！"
    Return
}

MsgBox "请把鼠标移动到微信的 '选择文件' 按钮上，然后按 Enter"

WinActivate(hwnd)             
WinSetAlwaysOnTop(true, hwnd)

KeyWait "Enter", "D"
MouseGetPos &mx, &my
IniWrite mx, "./data/WeChatBtn.ini", "Button", "FileX"
IniWrite my, "./data/WeChatBtn.ini", "Button", "FileY"

WinMinimize(winTitle)
WinSetAlwaysOnTop(false, hwnd)

MsgBox "坐标已保存: " mx "," my "请不要再次移动窗口，否则需要再次连接"