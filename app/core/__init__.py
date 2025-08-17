from typing import Optional
import subprocess, pathlib
from PyQt5.QtCore import (QObject, QThread, pyqtSignal, Qt)

TMP_FILE_PATH = "app\\template\\current_work.ahk"

class ScriptRunner(QThread):
    finished_signal = pyqtSignal(bool)
    output_signal = pyqtSignal(str, str)

    def __init__(self, compiler_path: str, script: str):
        super().__init__()
        self.compiler_path = compiler_path
        self.script = script

    def run(self):
        with open(TMP_FILE_PATH, "w", encoding='utf-8') as f:
            f.write(self.script)

        self.output_signal.emit('info', '调用AutoHotKey解释器...')
        try:
            subprocess.run([self.compiler_path, TMP_FILE_PATH], check=True)
            self.output_signal.emit('info', '脚本执行完成')
            self.finished_signal.emit(True)
        except subprocess.CalledProcessError as e:
            self.output_signal.emit('error', str(e))
            self.finished_signal.emit(False)
        except FileNotFoundError:
            self.output_signal.emit('error', '临时文件丢失')
            self.finished_signal.emit(False)

class ServiceManager(QObject):

    output_signal = pyqtSignal(str, str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.compiler_path: Optional[str] = None
        self.workpath : Optional[str] = None

    def set_work_path(self, workpath : str):
        self.workpath = workpath

    def set_compiler_path(self, compiler_path: str):
        self.compiler_path = compiler_path

    def try_connection(self):
        if self.compiler_path is None:
            self.output_signal.emit('error','未选择编译器路径')
            return
        self.output_signal.emit('info', f'工作目录:{self.workpath}')

        try:
            with open("app\\template\\connect.ahk", "r", encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            self.output_signal.emit('error', '文件connect.ahk丢失')
            return
        
        self.runner = ScriptRunner(self.compiler_path, template_content)
        self.runner.output_signal.connect(self.output_signal)

        def _on_script_end(success):
            if not self._check_button_position() or not success:
                self.output_signal.emit('error', '连接失败')
            else:
                self.output_signal.emit('info', '微信按钮定位成功')

        self.runner.finished_signal.connect(_on_script_end)
        self.runner.start()


    # async def _run_script(self, script: str):
    #     with open(TMP_FILE_PATH, "w", encoding='utf-8') as f:
    #         f.write(script)
    #     proc = await asyncio.create_subprocess_exec(
    #         self.compiler_path, TMP_FILE_PATH,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE
    #     )
    #     stdout, stderr = await proc.communicate()
    #     if proc.returncode == 0:
    #         self.output_signal.emit('info', '脚本执行完成')
    #     else:
    #         self.output_signal.emit('error', stderr.decode())

    def _check_button_position(self) -> bool:
        file_path = pathlib.Path('app/template/data/WeChatBtn.ini')
        return file_path.exists()
        