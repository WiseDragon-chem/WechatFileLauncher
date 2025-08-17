from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QAction, QMenu, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QStandardPaths
from pathlib import Path
import logging
from logging.config import dictConfig

class Application(QApplication):
    
    def __init__(self, argv):
        super().__init__(argv)

        self.setApplicationName("WechatPhotoLauncher")
        self.setOrganizationName("wise_dragon")

        log_dir: Path = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
        self.setup_logging(log_dir)
        self.logger: logging.Logger = logging.getLogger('app')
        self.logger.info(f"Logging configured. Dir: {log_dir}")

        #launch service_manager
        from .core import ServiceManager
        self.service_manager : ServiceManager = ServiceManager()

        #create settings
        from .settings import settings_manager
        self.logger.debug('Setting manager created.')
        _ = settings_manager

        #launch main_window
        from .mainwindow import MainWindow
        self.main_window: MainWindow = MainWindow(self.service_manager)
        self.main_window.show()
        self.logger.debug("Main window created.")

    def setup_logging(self, log_dir: Path):
        log_dir.mkdir(parents=True, exist_ok=True)
        debug_log_file = log_dir / "debug.log"
        error_log_file = log_dir / "error.log"
        debug_log_file.touch(exist_ok=True)
        error_log_file.touch(exist_ok=True)
        LOGGING_CONFIG = {
            "version": 1,
            "formatters": {
                "standard": {
                    "format": "----- %(asctime)s ------\n ### %(levelname)s ### [%(name)s]: %(message)s\n"
                }
            },
            "handlers": {
                "debug": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "standard",
                    "filename": debug_log_file,
                    "maxBytes": 5 * 1024 * 1024, # 5MB
                    "backupCount": 3,
                    "encoding": "utf-8"
                },
                "error": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "standard",
                    "filename": error_log_file,
                    "maxBytes": 5 * 1024 * 1024, # 5MB
                    "backupCount": 3,
                    "encoding": "utf-8"
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                }
            },
            "root": {
                "level": "DEBUG",
                "handlers": ["debug", "error", "console"]
            }
        }

        dictConfig(LOGGING_CONFIG)