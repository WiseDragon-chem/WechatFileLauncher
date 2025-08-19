from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QFileDialog, QMenuBar)
import time
from ..utils import set_color
from ..core import ServiceManager
from ..settings import settings_manager
from ..settings_window import SettingsDialog

import logging
logger = logging.getLogger(__name__)

class MainWindow(QWidget):

    def __init__(self, service_manager: ServiceManager):
        super().__init__()
        self.setWindowTitle("WECHAT PHOTO LAUNCHER")
        self.setGeometry(200, 200, 800, 600)
        self.main_layout = QHBoxLayout()
        self._setup_ui()

        self.menu_bar = QMenuBar()
        self.settings_menu = self.menu_bar.addMenu("设置")
        self.settings_menu.addAction("打开设置", self.open_settings_window)
        self.settings_menu.addAction("恢复默认设置", settings_manager.recover_default)
        self.main_layout.setMenuBar(self.menu_bar)

        self.setLayout(self.main_layout)

        self.service_manager = service_manager
        self.service_manager.output_signal.connect(self.refresh_ouput_area)

    def _setup_ui(self):
        left_panel_layout = QVBoxLayout()
        self.folder_select_button = QPushButton("选择文件夹")
        self.folder_select_button.clicked.connect(self.select_folder)
        left_panel_layout.addWidget(self.folder_select_button)

        self.path_label = QLabel("路径：未选择任何文件夹")
        self.path_label.setWordWrap(True) 
        left_panel_layout.addWidget(self.path_label)

        self.connect_button = QPushButton("连接")
        self.connect_button.clicked.connect(self.try_connention)
        left_panel_layout.addWidget(self.connect_button)

        self.start_stop_button = QPushButton("启动")
        self.start_stop_button.clicked.connect(self.toggle_start_stop)
        self.start_stop_button.setStyleSheet('background-color: #75FC69')
        left_panel_layout.addWidget(self.start_stop_button)

        self.exit_button = QPushButton('退出程序')
        self.exit_button.clicked.connect(self.quit_application)
        left_panel_layout.addWidget(self.exit_button)

        left_panel_layout.addStretch()

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("输出信息将显示在这里...")

        self.main_layout.addLayout(left_panel_layout, 2)
        self.main_layout.addWidget(self.output_area, 3)

    def toggle_start_stop(self):
        if self.start_stop_button.text() == "启动":
            self.start_stop_button.setText("停止")
            self.start_stop_button.setStyleSheet('background-color: red')
            self.output_area.append(set_color('程序已启动...', 'green'))
            logger.debug('Start program')
            self.start_launch_photo()
        else:
            self.start_stop_button.setText("启动")
            self.output_area.append(set_color('程序已停止...', 'red'))
            self.start_stop_button.setStyleSheet('background-color: #75FC69')
            logger.debug('Stop program')
            # 在这里添加停止逻辑

    def quit_application(self):
        self.output_area.append(set_color('正在退出程序', "#FC69D2"))
        logger.debug('Exit main window.')
        time.sleep(0.5)
        QApplication.instance().quit()

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择一个文件夹", "./")

        if folder_path:
            self.path_label.setText(f"路径：{folder_path}")
        else:
            self.path_label.setText("路径：未选择任何文件夹")

        self.service_manager.set_work_path(folder_path)

    def refresh_ouput_area(self, message_type: str, message: str):
        if message_type == 'error':
            self.output_area.append(set_color(f'错误：{message}'))
        elif message_type == 'warning':
            self.output_area.append(set_color(f'警告：{message}', 'yellow'))
        elif message_type == 'info':
            self.output_area.append(set_color(message, "#002AFF"))
        else:
            self.output_area.append(message)

    def try_connention(self):
        compile_path = settings_manager.get("AutoHotkey编译器路径", _type=str)
        # compile_path = "C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe"  ##TODO: 换回settings
        self.service_manager.set_compiler_path(compile_path)
        self.service_manager.try_connection()

    def start_launch_photo(self):
        # compile_path = "C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe"  ##TODO: 换回settings
        compile_path = settings_manager.get("AutoHotkey编译器路径", _type=str)
        self.service_manager.set_compiler_path(compile_path)
        self.service_manager.launch_photos()

    def open_settings_window(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
