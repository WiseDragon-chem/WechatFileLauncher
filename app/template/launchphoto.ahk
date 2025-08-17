#Requires AutoHotkey v2

iniFile := "data/WeChatBtn.ini"
wechatTitle := "微信"
files := $__file_path_list__  ; 文件路径列表

fileX := IniRead(iniFile, "Button", "FileX", 0)
fileY := IniRead(iniFile, "Button", "FileY", 0)
if !fileX || !fileY {
    MsgBox("未找到选择文件按钮坐标，请先记录坐标")
    ExitApp
}

if WinExist(wechatTitle) {
    hwnd := WinExist(wechatTitle)
    WinActivate(hwnd)
    WinWaitActive(hwnd, 2)
} else {
    MsgBox("未找到微信窗口")
    ExitApp
}
Sleep(500)

flag:=$__flag__

If flag{
    Send("^ ")   ; Ctrl+Space
}
Sleep(1800)  ; 等待输入法切换

for index, path in files {
    Click(fileX, fileY)
    Sleep(500)
    SendInput(path)
    Sleep(500)
    SendInput("!o")
    Sleep(1500)
}
Send("!s")
