#Requires AutoHotkey v2

winTitle := "微信"  ; 窗口标题，可根据需要修改
hwnd := WinExist(winTitle)
if hwnd {
    WinActivate(hwnd)             ; 激活窗口
    WinSetAlwaysOnTop(true, hwnd) ; 设置置顶
} else {
    MsgBox "未找到微信窗口！"
    Return
}

MsgBox "请把鼠标移动到微信的 '选择文件' 按钮上，然后按 Enter"
KeyWait "Enter", "D"
MouseGetPos &mx, &my
IniWrite mx, "./data/WeChatBtn.ini", "Button", "FileX"
IniWrite my, "./data/WeChatBtn.ini", "Button", "FileY"
MsgBox "坐标已保存: " mx "," my "请不要再次移动窗口，否则需要再次连接"