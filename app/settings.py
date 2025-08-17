from PyQt5.QtCore import QSettings, Qt, pyqtSignal, QObject

import logging
logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "AutoHotkey编译器路径": 'None'
}

class SettingsManager(QObject):
    settings_changed = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        logger.debug(f"SettingsManager initialized. File: {self.settings.fileName()}")

    def get(self, key, _type=None):
        if _type is None:
            value = self.settings.value(key, DEFAULT_SETTINGS[key])
        else:
            value = self.settings.value(key, DEFAULT_SETTINGS[key], type=_type)
        return value

    def set(self, keys: list, values: list):
        if len(keys) != len(values):
            raise ValueError("keys and values must have the same length")
        for key, value in zip(keys, values):
            self.settings.setValue(key, value)
        self.settings_changed.emit(keys)

    def recover_default(self):
        self.settings.clear()
        self.settings_changed.emit(list(DEFAULT_SETTINGS.keys()))

settings_manager = SettingsManager()
