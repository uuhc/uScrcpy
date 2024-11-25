from loguru import logger
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QWidget,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PyQt6.QtGui import QWindow
from PyQt6.QtCore import Qt
from core.adb_manager import ADBManager
from core.scrcpy_client import ScrcpyClient
from utils.window_manager import WindowManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("uScrcpy - 专业的投屏工具")
        self.resize(1200, 800)

        # 初始化核心功能
        self.adb_manager = ADBManager()
        self.scrcpy_clients = {}  # 保存设备和 Scrcpy 客户端的映射

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

    def closeEvent(self, event):
        """主窗口关闭事件"""
        # 弹出提示框以确认退出
        reply = QMessageBox.question(
            self,
            "退出",
            "确定要退出程序并关闭所有设备投屏吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup_scrcpy_clients()  # 清理所有 Scrcpy 客户端
            event.accept()  # 接受关闭事件
        else:
            event.ignore()  # 忽略关闭事件

    def cleanup_scrcpy_clients(self):
        """清理所有 Scrcpy 客户端"""
        for device_serial, client in self.scrcpy_clients.items():
            if client:
                client.stop_scrcpy()  # 停止 Scrcpy 客户端进程
                logger.info(f"Stopped Scrcpy for device {device_serial}")
        self.scrcpy_clients.clear()
        logger.info("All Scrcpy clients cleared.")

    def refresh_device_list(self):
        """刷新设备列表"""
        devices = self.adb_manager.refresh_devices()
        self.device_list.clear()
        self.device_list.addItems(devices)
        if devices:
            self.device_list.itemDoubleClicked.connect(
                self.start_device_projection
            )  # 改为双击触发

    def start_device_projection(self, item):
        """启动选中设备的投屏"""
        device_serial = item.text()
        logger.info(f"scrcpy_clients: {self.scrcpy_clients}")

        if device_serial in self.scrcpy_clients:
            logger.info(
                f"Device {device_serial} is already projected. scrcpy_clients: {self.scrcpy_clients}"
            )
            # 获取对应的 ScrcpyClient
            client = self.scrcpy_clients[device_serial]
            window_id = client.window_id

            if window_id:
                # 确认窗口是否仍然有效
                if not WindowManager.is_window_active(window_id):
                    logger.warning(
                        f"Window for device {device_serial} is no longer active. Restarting scrcpy..."
                    )
                    # 窗口失效，移除旧客户端并重新启动
                    del self.scrcpy_clients[device_serial]
                else:
                    # 窗口有效，将其置于前台
                    WindowManager.bring_window_to_front(window_id)
                    logger.info(
                        f"Window for device {device_serial} brought to the front."
                    )
                    return
            else:
                logger.warning(f"Window ID not found for device {device_serial}.")

        # 启动新的 Scrcpy 客户端
        logger.info(f"Starting new scrcpy for device {device_serial}")
        scrcpy_client = ScrcpyClient(device_serial)
        scrcpy_client.start_scrcpy()
        self.scrcpy_clients[device_serial] = scrcpy_client
        logger.info(
            f"Scrcpy started for device {device_serial},scrcpy_clients: {self.scrcpy_clients}"
        )

        # 嵌入窗口到 UI
        self.embed_scrcpy_window(scrcpy_client.window_id)

    def embed_scrcpy_window(self, window_id):
        """嵌入 Scrcpy 窗口到右侧布局"""
        if not window_id:
            return

        scrcpy_window = QWindow.fromWinId(window_id)
        container = self.screen_container.layout()
        if container:
            for i in reversed(range(container.count())):
                container.itemAt(i).widget().setParent(None)

        window_widget = QWidget.createWindowContainer(
            scrcpy_window, self.screen_container
        )
        layout = QVBoxLayout(self.screen_container)
        layout.addWidget(window_widget)
        layout.setContentsMargins(0, 0, 0, 0)
