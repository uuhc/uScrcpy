from PyQt6.QtWidgets import (QMainWindow, QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from core.adb_manager import ADBManager
from core.scrcpy_client import ScrcpyClient

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("uScrcpy - 专业的投屏工具")
        self.resize(1200, 800)

        # 初始化核心功能
        self.adb_manager = ADBManager()

        # 左侧设备列表
        self.device_list = QListWidget()
        self.refresh_button = QPushButton("刷新设备")
        self.refresh_button.clicked.connect(self.refresh_device_list)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.refresh_button)
        left_layout.addWidget(self.device_list)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # 右侧投屏画面
        self.screen_label = QLabel("投屏窗口")
        self.screen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.screen_label)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # 主布局
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 3)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 初始化设备列表
        self.refresh_device_list()

    def refresh_device_list(self):
        """刷新设备列表"""
        devices = self.adb_manager.refresh_devices()
        self.device_list.clear()
        self.device_list.addItems(devices)
        if devices:
            self.device_list.itemClicked.connect(self.start_device_projection)

    def start_device_projection(self, item):
        """启动选中设备的投屏"""
        device_serial = item.text()
        scrcpy_client = ScrcpyClient(device_serial)
        scrcpy_client.start_scrcpy()
