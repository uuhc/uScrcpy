import subprocess
import threading
from loguru import logger
from utils.window_manager import WindowManager


class ScrcpyClient:
    def __init__(self, device_serial):
        self.device_serial = device_serial
        self.process = None
        self.window_id = None

    def start_scrcpy(self):
        """启动 Scrcpy 并获取窗口 ID"""
        # 启动 scrcpy 的命令
        command = [
            "scrcpy",
            "--serial",
            self.device_serial,
            "--window-title",
            f"scrcpy-{self.device_serial}",
        ]

        # 使用子线程启动 Scrcpy 进程
        def run_scrcpy():
            self.process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            logger.info(f"Scrcpy process started for device {self.device_serial}")
            # 等待 Scrcpy 启动完成后获取窗口 ID
            self._fetch_window_id()

        threading.Thread(target=run_scrcpy, daemon=True).start()

    def _fetch_window_id(self):
        """根据窗口标题获取 Scrcpy 的 window_id"""
        window_title = f"scrcpy-{self.device_serial}"
        self.window_id = WindowManager.get_window_id(window_title)
        logger.info(f"Window ID for device {self.device_serial}: {self.window_id}")

    def stop_scrcpy(self):
        """停止 Scrcpy"""
        if self.process:
            self.process.terminate()
            self.process = None
