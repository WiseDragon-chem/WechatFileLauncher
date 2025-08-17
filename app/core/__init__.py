from typing import Optional
import subprocess, pathlib, string, re
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
            print(self.compiler_path, TMP_FILE_PATH)
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
        self.script_queue = []
        self.runner = None

    def set_work_path(self, workpath : str):
        self.workpath = workpath

    def set_compiler_path(self, compiler_path: str):
        self.compiler_path = compiler_path

    def try_connection(self):
        if self.compiler_path is None:
            self.output_signal.emit('error','未选择编译器路径')
            return
        # self.output_signal.emit('info', f'工作目录:{self.workpath}')

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

    def get_all_file(self):
        path = pathlib.Path(self.workpath)
        ret = []
        if not path.is_dir():
            self.output_signal.emit('warning', '当前工作目录无文件')
            return []
        files = [item for item in path.iterdir() if item.is_file()]
        for f in files:
            path_str = str(f)
            path_str_fixed = re.sub(r"\\+", r"\\", path_str)
            ret.append(fr'{path_str_fixed}')
        return ret
    
    def launch_photos(self):
        if self.workpath is None:
            self.output_signal.emit('error', '未选择上传文件目录')
            return
        
        self.output_signal.emit('info',f'上传路径: {self.workpath}')
        file_paths = self.get_all_file()
        for i in file_paths:
            print(i)
        self.output_signal.emit('info', '以下文件将被发送：')
        cnt = 1
        for file_path in file_paths:
            self.output_signal.emit('info', f'[{cnt}]{file_path}')
            cnt += 1
        
        try:
            with open("app\\template\\launchphoto.ahk", "r", encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            self.output_signal.emit('error', '文件launchphoto.ahk丢失')
            return
        
        cyr = 'True'
        while len(file_paths) > 0:
            file_to_launch = file_paths[:9]
            tmp_str = r''
            for i in file_to_launch:
                tmp_str += rf"'{i}', "
            dic = {'__file_path_list__': rf'[{tmp_str}]', '__flag__': cyr}
            rendered_code = string.Template(template_content)
            self.script_queue.append(rf'{rendered_code.safe_substitute(dic)}')
            file_paths = file_paths[9:]
            cyr = 'False'

        self._run_next_script()

    def _run_next_script(self):
        if not self.script_queue:
            self.output_signal.emit('info', '所有文件上传完毕')
            return

        next_script = self.script_queue.pop(0)
        self.runner = ScriptRunner(self.compiler_path, next_script)
        self.runner.output_signal.connect(self.output_signal)
        self.runner.finished_signal.connect(self._on_script_finished)
        self.runner.start()

    def _on_script_finished(self, success: bool):
        if success == False:
            self.output_signal.emit('error', '运行错误.')
        self._run_next_script()
            

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
        