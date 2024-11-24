import platform
import subprocess
import re


class WindowManager:
    @staticmethod
    def get_window_id(window_title):
        """根据窗口标题获取窗口句柄，支持跨平台"""
        system = platform.system()

        if system == "Windows":
            return WindowManager._get_window_id_windows(window_title)
        elif system == "Linux":
            return WindowManager._get_window_id_linux(window_title)
        elif system == "Darwin":  # macOS
            return WindowManager._get_window_id_macos(window_title)
        else:
            raise NotImplementedError(f"Unsupported platform: {system}")

    @staticmethod
    def _get_window_id_windows(window_title):
        """Windows 平台获取窗口句柄"""
        try:
            import win32gui

            def callback(hwnd, result):
                if window_title in win32gui.GetWindowText(hwnd):
                    result.append(hwnd)

            result = []
            win32gui.EnumWindows(callback, result)
            return result[0] if result else None
        except ImportError:
            raise ImportError("请安装 pywin32：pip install pywin32")

    @staticmethod
    def _get_window_id_linux(window_title):
        """Linux 平台获取窗口句柄"""
        try:
            output = subprocess.check_output(
                ["xdotool", "search", "--name", window_title], text=True
            )
            return int(output.splitlines()[0])
        except Exception:
            return None

    @staticmethod
    def _get_window_id_macos(window_title):
        """macOS 平台获取窗口句柄"""
        try:
            script = f'tell application "System Events" to get the id of every window of (every process whose name contains "{window_title}")'
            output = subprocess.check_output(["osascript", "-e", script], text=True)
            match = re.search(r"\d+", output)
            return int(match.group(0)) if match else None
        except Exception:
            return None
