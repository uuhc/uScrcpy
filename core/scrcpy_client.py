import subprocess
from utils.window_manager import WindowManager


class ScrcpyClient:
    def __init__(self, device_serial):
        self.device_serial = device_serial
        self.process = None
        self.window_id = None

    def start_scrcpy(self):
        """启动 Scrcpy，并获取窗口句柄"""
        self.process = subprocess.Popen(
            [
                "scrcpy",
                "-s",
                self.device_serial,
                "--window-title",
                f"scrcpy-{self.device_serial}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # 等待窗口启动
        self.window_id = WindowManager.get_window_id(f"scrcpy-{self.device_serial}")
